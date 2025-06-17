import os
import random
from tqdm import tqdm
import pandas as pd
from PIL import Image, ImageEnhance
from decord import VideoReader, cpu

import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from torchvision import transforms


class WebVid(Dataset):
    """
    WebVid Dataset.
    Assumes webvid data is structured as follows.
    Webvid/
        videos/
            000001_000050/      ($page_dir)
                1.mp4           (videoid.mp4)
                ...
                5000.mp4
            ...
    """
    def __init__(self,
                 meta_path,
                 data_dir,
                 subsample=None,
                 video_length=16,
                 resolution=[256, 512],
                 frame_stride=1,
                 frame_stride_min=1,
                 spatial_transform=None,
                 crop_resolution=None,
                 fps_max=None,
                 load_raw_resolution=False,
                 fixed_fps=None,
                 random_fs=False,
                 ):
        self.meta_path = meta_path
        self.data_dir = data_dir
        self.subsample = subsample
        self.video_length = video_length
        self.resolution = [resolution, resolution] if isinstance(resolution, int) else resolution
        self.fps_max = fps_max
        self.frame_stride = frame_stride
        self.frame_stride_min = frame_stride_min
        self.fixed_fps = fixed_fps
        self.load_raw_resolution = load_raw_resolution
        self.random_fs = random_fs
        self._load_metadata()
        if spatial_transform is not None:
            if spatial_transform == "random_crop":
                self.spatial_transform = transforms.RandomCrop(crop_resolution)
            elif spatial_transform == "center_crop":
                self.spatial_transform = transforms.Compose([
                    transforms.CenterCrop(resolution),
                    ])            
            elif spatial_transform == "resize_center_crop":
                # assert(self.resolution[0] == self.resolution[1])
                self.spatial_transform = transforms.Compose([
                    transforms.Resize(min(self.resolution)),
                    transforms.CenterCrop(self.resolution),
                    ])
            elif spatial_transform == "resize":
                self.spatial_transform = transforms.Resize(self.resolution)
            else:
                raise NotImplementedError
        else:
            self.spatial_transform = None
            

    
    def __getitem__(self, index):
        if self.random_fs:
            frame_stride = random.randint(self.frame_stride_min, self.frame_stride)
        else:
            frame_stride = self.frame_stride

        ## get frames until success
        while True:
            index = index % len(self.metadata)
            sample = self.metadata.iloc[index]
            video_path = self._get_video_path(sample)
            ## video_path should be in the format of "....../WebVid/videos/$page_dir/$videoid.mp4"
            caption = sample['caption']

            try:
                if self.load_raw_resolution:
                    video_reader = VideoReader(video_path, ctx=cpu(0))
                else:
                    video_reader = VideoReader(video_path, ctx=cpu(0), width=530, height=300)
                if len(video_reader) < self.video_length:
                    print(f"video length ({len(video_reader)}) is smaller than target length({self.video_length})")
                    index += 1
                    continue
                else:
                    pass
            except:
                index += 1
                print(f"Load video failed! path = {video_path}")
                continue
            
            fps_ori = video_reader.get_avg_fps()
            if self.fixed_fps is not None:
                frame_stride = int(frame_stride * (1.0 * fps_ori / self.fixed_fps))

            ## to avoid extreme cases when fixed_fps is used
            frame_stride = max(frame_stride, 1)
            
            ## get valid range (adapting case by case)
            required_frame_num = frame_stride * (self.video_length-1) + 1
            frame_num = len(video_reader)
            if frame_num < required_frame_num:
                ## drop extra samples if fixed fps is required
                if self.fixed_fps is not None and frame_num < required_frame_num * 0.5:
                    index += 1
                    continue
                else:
                    frame_stride = frame_num // self.video_length
                    required_frame_num = frame_stride * (self.video_length-1) + 1

            ## select a random clip
            random_range = frame_num - required_frame_num
            start_idx = random.randint(0, random_range) if random_range > 0 else 0

            ## calculate frame indices
            frame_indices = [start_idx + frame_stride*i for i in range(self.video_length)]
            try:
                frames = video_reader.get_batch(frame_indices)
                break
            except:
                print(f"Get frames failed! path = {video_path}; [max_ind vs frame_total:{max(frame_indices)} / {frame_num}]")
                index += 1
                continue
        
        ## process data
        assert(frames.shape[0] == self.video_length),f'{len(frames)}, self.video_length={self.video_length}'
        frames = torch.tensor(frames.asnumpy()).permute(3, 0, 1, 2).float() # [t,h,w,c] -> [c,t,h,w]
        
        if self.spatial_transform is not None:
            frames = self.spatial_transform(frames)
        
        if self.resolution is not None:
            assert (frames.shape[2], frames.shape[3]) == (self.resolution[0], self.resolution[1]), f'frames={frames.shape}, self.resolution={self.resolution}'
        
        ## turn frames tensors to [-1,1]
        frames = (frames / 255 - 0.5) * 2
        fps_clip = fps_ori // frame_stride
        if self.fps_max is not None and fps_clip > self.fps_max:
            fps_clip = self.fps_max

        data = {'video': frames, 'caption': caption, 'path': video_path, 'fps': fps_clip, 'frame_stride': frame_stride}
        return data
    
    def __len__(self):
        return len(self.metadata)



class CornDataset(Dataset):
    def __init__(self,
                 root_dir,
                 video_length=16,
                 resolution=[320, 512],
                 frame_stride=1,
                 frame_stride_min=1,
                 spatial_transform=None,
                 crop_resolution=None,
                 fps_max=None,
                 fixed_fps=None,
                 random_fs=False,
                 ):
        self.root_dir = root_dir
        self.video_folders = [os.path.join(root_dir, d) for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))]
        # crop_resolution
        # # 定义转换（不包括裁剪）
        self.fixed_fps = fixed_fps
        self.to_tensor = transforms.ToTensor()
        # if spatial_transform is not None:
        #     if spatial_transform == "random_crop":
        #         self.spatial_transform = transforms.RandomCrop(crop_resolution)
        #     elif spatial_transform == "center_crop":
        #         self.spatial_transform = transforms.Compose([
        #             transforms.CenterCrop(resolution),
        #             ])            
        #     elif spatial_transform == "resize_center_crop":
        #         # assert(self.resolution[0] == self.resolution[1])
        #         self.spatial_transform = transforms.Compose([
        #             transforms.Resize(min(self.resolution)),
        #             transforms.CenterCrop(self.resolution),
        #             ])
        #     elif spatial_transform == "resize":
        #         self.spatial_transform = transforms.Resize(self.resolution)
        #     else:
        #         raise NotImplementedError
        # else:
        #     self.spatial_transform = None

    def __len__(self):
        return len(self.video_folders)

    def __getitem__(self, idx):
        video_path = self.video_folders[idx]
        video_name = video_path.split('/')[-1]
        fps_stride = video_name.split('_')[1]
        #frame_files = sorted([os.path.join(video_path, f) for f in os.listdir(video_path) if f.endswith('.jpg', '.jpeg', '.png')])
        frame_files = sorted([os.path.join(video_path, f) for f in os.listdir(video_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
        # 确保每个文件夹中有 16 张图像
        if len(frame_files) != 16:
            raise ValueError(f"Folder {video_path} does not contain exactly 16 frames.")
        
        # 加载并处理每一帧
        frames = []
        for frame_file in frame_files:
            img = Image.open(frame_file).convert("RGB")
            
            # 在 __getitem__ 中进行中心裁剪到 320x512
            img = transforms.CenterCrop((320, 512))(img)
            img = self.adjust_exposure(img, factor=0.9)
            # 增加饱和度
            img = self.increase_saturation(img, saturation_scale=1.5)
            img = self.to_tensor(img)  # 转换为 Tensor 并归一化到 [0, 1]
            img = (img - 0.5) * 2
            frames.append(img)
        
        # 将帧列表转换为 tensor, [t, c, h, w] -> [c, t, h, w]
        frames = torch.stack(frames, dim=0).permute(1, 0, 2, 3)
        if self.fixed_fps:
            frame_stride = int(fps_stride)
            fps = 30 / frame_stride
        else:
            fps = 6
            frame_stride = 5
        # print(frames)
        # print(frames.shape)

        data = {'video': frames, 'caption': "time-lapse of crops growing in the fields", 'path': video_path, 'fps': fps, 'frame_stride': frame_stride}
        return data
    
    def adjust_exposure(self, image, factor=0.9):
        """
        检测并调整图像的曝光度
        :param image: 输入的PIL Image对象
        :param threshold: 判定过曝的亮度阈值（0-255）
        :param factor: 曝光降低系数，越小越暗
        :return: 调整曝光后的PIL Image对象
        """
        # 转换为灰度并检测亮度
        #grayscale = image.convert("L")
        #pixels = np.array(grayscale)
            # 调整曝光度
        enhancer = ImageEnhance.Brightness(image)
        image = enhancer.enhance(factor)
        return image

    def increase_saturation(self, image, saturation_scale=1.5):
        """
        增加色彩饱和度
        :param image: 输入的PIL Image对象
        :param saturation_scale: 饱和度增益系数，默认1.5
        :return: 增加饱和度后的PIL Image对象
        """
        enhancer = ImageEnhance.Color(image)
        image = enhancer.enhance(saturation_scale)
        return image






if __name__== "__main__":
    meta_path = "" ## path to the meta file
    data_dir = "" ## path to the data directory
    save_dir = "" ## path to the save directory
    dataset = WebVid(meta_path,
                 data_dir,
                 subsample=None,
                 video_length=16,
                 resolution=[256,448],
                 frame_stride=4,
                 spatial_transform="resize_center_crop",
                 crop_resolution=None,
                 fps_max=None,
                 load_raw_resolution=True
                 )
    dataloader = DataLoader(dataset,
                    batch_size=1,
                    num_workers=0,
                    shuffle=False)

    
    import sys
    sys.path.insert(1, os.path.join(sys.path[0], '..', '..'))
    from utils.save_video import tensor_to_mp4
    for i, batch in tqdm(enumerate(dataloader), desc="Data Batch"):
        video = batch['video']
        name = batch['path'][0].split('videos/')[-1].replace('/','_')
        tensor_to_mp4(video, save_dir+'/'+name, fps=8)

