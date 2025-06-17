import os
import shutil
from PIL import Image, ImageEnhance
import numpy as np



def adjust_exposure(image, factor=0.9):
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

def increase_saturation(image, saturation_scale=1.5):
    """
    增加色彩饱和度
    :param image: 输入的PIL Image对象
    :param saturation_scale: 饱和度增益系数，默认1.5
    :return: 增加饱和度后的PIL Image对象
    """
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(saturation_scale)
    return image

def process_image(image_path, output_path, saturation_scale=1.5, exposure_factor=0.9):
    """
    检测曝光并调整，再增加色彩饱和度
    :param image_path: 输入图像路径
    :param output_path: 输出路径
    :param saturation_scale: 饱和度增益系数
    :param exposure_threshold: 过曝检测的亮度阈值
    :param exposure_factor: 曝光调整系数
    """
    # 读取图像
    image = Image.open(image_path)

    # 检测并调整曝光度
    image = adjust_exposure(image, factor=exposure_factor)

    # 增加饱和度
    image = increase_saturation(image, saturation_scale=saturation_scale)
    return image


def create_new_dataset(input_folder, output_folder, folder_count=1, interval=1, target_frame_count=16):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    #folder_count = 1  # 用于命名输出文件夹

    # 遍历输入文件夹中的每个子文件夹
    for subfolder in sorted(os.listdir(input_folder)):
        subfolder_path = os.path.join(input_folder, subfolder)
        
        if os.path.isdir(subfolder_path):
            # 获取所有帧图片并按文件名排序
            frames = sorted(os.listdir(subfolder_path))
            frame_count = len(frames)
            
            # 计算每次抽帧的间隔
            if frame_count < target_frame_count:
                print(f"Skipping folder {subfolder} as it has less than {target_frame_count} frames.")
                continue
            
            #interval = int(0.66 * frame_count) // target_frame_count
            num_extractions = frame_count // target_frame_count
            start_index_list = []
            for idx in range(frame_count):
                if (idx % (0.5 * target_frame_count) in range(interval)) and (idx + target_frame_count * interval < frame_count): 
                    start_index_list.append(idx)
            # 抽取并保存多个 16 帧的子文件夹
            print(start_index_list)
            for i in start_index_list:
                start_index = i
                selected_frames = frames[start_index:start_index + target_frame_count * interval:interval]
                
                if len(selected_frames) < target_frame_count:
                    continue
                
                # 创建新的子文件夹，并格式化为 3 位数
                new_subfolder_name = f"{folder_count:03d}_{interval:02d}"
                new_subfolder_path = os.path.join(output_folder, new_subfolder_name)
                os.makedirs(new_subfolder_path, exist_ok=True)
                
                # 复制抽取的帧到新的子文件夹，并命名为 0001.jpg, 0002.jpg 等
                for idx, frame_name in enumerate(selected_frames):
                    frame_path = os.path.join(subfolder_path, frame_name)
                    output_frame_name = f"{idx + 1:04d}.jpg"
                    output_frame_path = os.path.join(new_subfolder_path, output_frame_name)
                    shutil.copy(frame_path, output_frame_path)
                
                # 增加文件夹计数
                folder_count += 1
            
            print(f"Processed folder {subfolder}, extracted {len(start_index_list)} sets of frames.")
    return folder_count

def center_crop_image(img, crop_width, crop_height):
    """
    将图像按中心裁剪成指定的宽度和高度。
    
    Args:
        img (Image): PIL Image对象。
        crop_width (int): 裁剪后的图像宽度。
        crop_height (int): 裁剪后的图像高度。
        
    Returns:
        cropped_img (Image): 裁剪后的图像。
    """
    img_width, img_height = img.size
    left = (img_width - crop_width) // 2
    top = (img_height - crop_height) // 2
    right = left + crop_width
    bottom = top + crop_height
    return img.crop((left, top, right, bottom))


def resize_img(img, target_width=512, target_height=320):
    aspect_ratio = img.width / img.height
    target_aspect_ratio = target_width / target_height

    # 根据宽高比调整图像大小
    if aspect_ratio > target_aspect_ratio:
        # 图像过宽，按高适应，缩放宽度
        new_height = target_height
        new_width = int(aspect_ratio * new_height)
    else:
        # 图像过高，按宽适应，缩放高度
        new_width = target_width
        new_height = int(new_width / aspect_ratio)

    # 缩放图像
    img_resized = img.resize((new_width, new_height), Image.LANCZOS)

    # 中心裁剪到 target_width x target_height
    left = (new_width - target_width) / 2
    top = (new_height - target_height) / 2
    right = left + target_width
    bottom = top + target_height

    img_cropped = img_resized.crop((left, top, right, bottom))
    return img_cropped

def crop_image_sequence(input_folder, output_folder, crop_width=512, crop_height=320, step_x=256, step_y=160):
    """
    对图像序列在相同位置裁剪为多个512x320的小块序列，存入新的子文件夹。
    
    Args:
        input_folder (str): 输入图像数据文件夹路径。
        output_folder (str): 裁剪后图像保存的输出文件夹路径。
        crop_width (int): 裁剪图像的宽度（默认512）。
        crop_height (int): 裁剪图像的高度（默认320）。
        step_x (int): 裁剪窗口在x方向上的步长。
        step_y (int): 裁剪窗口在y方向上的步长。
    """
    os.makedirs(output_folder, exist_ok=True)

    # 遍历每个视频子文件夹
    for subfolder in sorted(os.listdir(input_folder)):
        #data_id = int(subfolder)
        subfolder_path = os.path.join(input_folder, subfolder)

        if not os.path.isdir(subfolder_path):
            continue

        # 加载所有帧并确保按顺序排列
        image_files = sorted([f for f in os.listdir(subfolder_path) if f.endswith(('.jpg', '.jpeg', '.png'))])

        # 打开第一张图片以确定裁剪位置范围
        sample_image_path = os.path.join(subfolder_path, image_files[0])


        with Image.open(sample_image_path) as img:
            img = center_crop_image(img,2560,1600)
            img_width, img_height = img.size

        crop_idx = 1  # 用于生成新子文件夹名称
        # 滑动窗口裁剪到指定位置
        for y in range(0, img_height - crop_height + 1, step_y):
            for x in range(0, img_width - crop_width + 1, step_x):
                
                # 创建每个裁剪块的新子文件夹，命名格式如 001_1, 001_2, etc.
                output_subfolder = os.path.join(output_folder, f"{subfolder}_{crop_idx:03}")
                os.makedirs(output_subfolder, exist_ok=True)

                # 遍历图像序列，按相同位置裁剪并保存
                for idx, image_file in enumerate(image_files):
                    image_path = os.path.join(subfolder_path, image_file)
                    with Image.open(image_path) as img:
                        # 裁剪图像
                        img = center_crop_image(img,2560,1600)
                        # if data_id >=65 and data_id <=81:
                        #     print("<<<<<<<<<<<prosessing Corn_1 !!!>>>>>>>>>>>")
                        #     img = center_crop_image(img,3072,1600)
                        # elif data_id > 81:
                        #     print("<<<<<<<<<<<prosessing Corn_2 !!!>>>>>>>>>>>")
                        #     img = center_crop_image(img,3072,1600)


                        cropped_img = img.crop((x, y, x + crop_width, y + crop_height))

                        if cropped_img.size != (crop_width, crop_height):
                            cropped_img = resize_img(cropped_img)
                        # 保存裁剪后的图像，文件名以0001, 0002格式命名
                        crop_filename = f"{idx + 1:04}.png"
                        cropped_img.save(os.path.join(output_subfolder, crop_filename))
                print(f"Processed folder {subfolder}, extracted {crop_idx} sets of frames.")
                crop_idx += 1  # 更新裁剪区域编号
                

def enhance_image_sequence(input_folder, output_folder):
    """
    对图像序列在相同位置裁剪为多个512x320的小块序列，存入新的子文件夹。
    
    Args:
        input_folder (str): 输入图像数据文件夹路径。
        output_folder (str): 裁剪后图像保存的输出文件夹路径。
    """
    os.makedirs(output_folder, exist_ok=True)

    # 遍历每个视频子文件夹
    for subfolder in sorted(os.listdir(input_folder)):
        data_id = int(subfolder)
        subfolder_path = os.path.join(input_folder, subfolder)

        if not os.path.isdir(subfolder_path):
            continue

        # 加载所有帧并确保按顺序排列
        image_files = sorted([f for f in os.listdir(subfolder_path) if f.endswith(('.jpg', '.jpeg', '.png'))])

        # 打开第一张图片以确定裁剪位置范围
        #sample_image_path = os.path.join(subfolder_path, image_files[0])
        for idx, image_file in enumerate(image_files):
            image_path = os.path.join(subfolder_path, image_file)
            with Image.open(image_path) as img:
                img = process_image(img)
            img.save(os.path.join(output_folder, subfolder, image_file))



def create_new_dataset2(input_folder, output_folder, interval=3, group_size=16):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    folder_count = 1  # 用于命名输出文件夹

    # 遍历输入文件夹中的每个子文件夹
    for subfolder in sorted(os.listdir(input_folder)):
        subfolder_path = os.path.join(input_folder, subfolder)
        
        if os.path.isdir(subfolder_path):
            # 获取所有帧图片并按文件名排序
            frames = sorted(os.listdir(subfolder_path))
            frame_count = len(frames)
            
            # 从不同的起始点进行抽取，以3为间隔
            all_selected_frames = []
            for start in range(interval):  # 从第1帧、第2帧等不同起点开始
                selected_frames = frames[start::interval]
                all_selected_frames.extend(selected_frames)
            
            # 按 16 张为一组进行分组
            num_groups = len(all_selected_frames) // group_size
            
            for i in range(num_groups):
                # 创建新的子文件夹并格式化为 3 位数
                new_subfolder_name = f"{folder_count:03d}_{interval}"
                new_subfolder_path = os.path.join(output_folder, new_subfolder_name)
                os.makedirs(new_subfolder_path, exist_ok=True)
                
                # 获取当前组的 16 张图片
                group_frames = all_selected_frames[i * group_size: (i + 1) * group_size]
                
                # 复制抽取的帧到新的子文件夹，并命名为 0001.jpg, 0002.jpg 等
                for idx, frame_name in enumerate(group_frames):
                    frame_path = os.path.join(subfolder_path, frame_name)
                    output_frame_name = f"{idx + 1:04d}.png"
                    output_frame_path = os.path.join(new_subfolder_path, output_frame_name)
                    shutil.copy(frame_path, output_frame_path)
                
                # 增加文件夹计数
                folder_count += 1
            
            print(f"Processed folder {subfolder}, created {num_groups} sets of frames.")


def is_mostly_black(image, threshold=0.1, black_pixel_value=10):
    """
    判断图像是否主要为黑色区域。
    
    Args:
        image (PIL.Image): 图像文件。
        threshold (float): 黑色像素占图像总像素的比例阈值。
        black_pixel_value (int): 低于此值的像素视为黑色（默认为20）。
        
    Returns:
        bool: 如果黑色区域占比超过阈值，返回True；否则返回False。
    """
    # 转换图像为灰度模式
    grayscale_image = image.convert('L')
    image_array = np.array(grayscale_image)
    #print(image_array)

    # 计算黑色像素的数量
    black_pixels = np.sum(image_array < black_pixel_value)
    total_pixels = image_array.size

    # 计算黑色区域占比
    black_ratio = black_pixels / total_pixels
    return black_ratio >= threshold

def remove_folders_with_black_images(dataset_folder, threshold=0.1, black_pixel_value=10):
    """
    遍历数据集，如果子文件夹中存在大量黑色区域的图片，则删除整个子文件夹。
    
    Args:
        dataset_folder (str): 数据集文件夹路径。
        threshold (float): 判断黑色区域过多的比例阈值（默认为0.8）。
        black_pixel_value (int): 低于此值的像素视为黑色（默认为20）。
    """
    # 遍历每个子文件夹
    for subfolder in sorted(os.listdir(dataset_folder)):
        # if int(subfolder.split('_')[0]) < 65:
        #     continue
        subfolder_path = os.path.join(dataset_folder, subfolder)


        # 检查是否是文件夹
        if not os.path.isdir(subfolder_path):
            continue

        delete_folder = False

        # 遍历子文件夹中的图像文件
        for image_file in os.listdir(subfolder_path):
            image_path = os.path.join(subfolder_path, image_file)
            print(image_path)
                # 打开图像并检查是否主要为黑色区域
            with Image.open(image_path) as img:
                if is_mostly_black(img, threshold=0.1, black_pixel_value=2):
                    delete_folder = True
            print(delete_folder)
            break
        # 删除子文件夹
        if delete_folder:
            print(f"Deleting folder {subfolder_path} due to mostly black images.")
            shutil.rmtree(subfolder_path)

# 使用示例
#dataset_folder = '/home/cx_wchn/lnwang/Data/corn6_crop'  # 数据集文件夹路径
#remove_folders_with_black_images(dataset_folder, threshold=0.1, black_pixel_value=2)

# 使用示例
input_folder = "/home/cx_wchn/lnwang/Data/corn_mulstride"   # 原始数据文件夹路径
output_folder = "/home/cx_wchn/lnwang/Data/corn_mulstride_crop"  # 生成的数据文件夹路径
# folder_count = 1
# for interval in range(1,7):
#     folder_count = create_new_dataset(input_folder, output_folder, folder_count=folder_count, interval=interval)
    

crop_image_sequence(input_folder, output_folder, crop_width=1024, crop_height=640, step_x=512, step_y=320)

# count = 0
# for subfolder in sorted(os.listdir(dataset_folder)):
#     count +=1
# print(count)