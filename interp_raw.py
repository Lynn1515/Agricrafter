import cv2
import argparse
import os
#from natsort import natsorted
#from moviepy.video.io.ffmpeg_tools import ffmpeg_concat
from moviepy.editor import VideoFileClip, concatenate_videoclips


def extract_frames_from_folder(video_folder, output_folder):
    """
    将文件夹中的所有视频拆解为帧，并保存为按滑动窗口组成的片段图片文件，并生成描述的文本文件。
    
    :param video_folder: str, 包含多个视频的文件夹路径
    :param output_folder: str, 保存帧的文件夹路径
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    if not video_files:
        print(f"文件夹 {video_folder} 中没有找到视频文件。")
        return
    pair_count = 0
    for video_file in video_files:
        video_path = os.path.join(video_folder, video_file)
        video_name, _ = os.path.splitext(video_file)  # 获取视频文件名（不含扩展名）
        pair_count += process_video(video_path, output_folder, video_name)
        
        # 创建描述文件
    create_description_file(output_folder, video_name, pair_count)

def process_video(video_path, output_folder, video_name):
    """
    处理单个视频文件，将其拆解为滑动窗口形式的片段帧，并保存为图片文件。
    
    :param video_path: str, 视频文件路径
    :param output_folder: str, 保存帧的文件夹路径
    :param video_name: str, 视频的基础文件名
    :return: int, 生成的片段数量
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"无法打开视频文件: {video_path}")
        return 0

    frames = []  # 用于存储当前已读取的帧
    pair_idx = 1  # 记录生成片段的编号

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

        if len(frames) == 2:
            # 保存滑动窗口的两帧
            prefix = f"{video_name}-{pair_idx:02d}"
            prefix = prefix.replace("_","-")
            frame1_filename = os.path.join(output_folder, f"{prefix}_01.jpg")
            frame2_filename = os.path.join(output_folder, f"{prefix}_02.jpg")
            cv2.imwrite(frame1_filename, frames[0])
            cv2.imwrite(frame2_filename, frames[1])

            print(f"保存片段 {prefix} -> 第一帧: {frame1_filename}, 第二帧: {frame2_filename}")

            # 滑动窗口，移除第一帧
            frames.pop(0)
            pair_idx += 1

    cap.release()
    return pair_idx - 1  # 返回生成的片段数量

def create_description_file(output_folder, video_name, pair_count):
    """
    创建一个文本文件，每行包含固定描述内容，行数与生成片段数相同。
    
    :param output_folder: str, 保存文本文件的文件夹路径
    :param video_name: str, 视频的基础文件名
    :param pair_count: int, 生成的片段数量
    """
    description_file_path = os.path.join(output_folder, "test_prompts.txt")
    with open(description_file_path, 'w') as file:
        for _ in range(pair_count):
            file.write("time-lapse of crops growing in the fields\n")
    print(f"描述文件已保存: {description_file_path}")


def group_videos_by_prefix(input_folder):
    """
    将视频按照前缀分组。
    
    :param input_folder: str, 包含多个视频的文件夹路径
    :return: dict, {前缀: [视频文件路径]}
    """
    video_files = [f for f in os.listdir(input_folder) if f.endswith('.mp4')]
    grouped_videos = {}

    for video_file in video_files:
        prefix = "_".join(video_file.split('_')[0])  # 提取前缀，如 example_01
        if prefix not in grouped_videos:
            grouped_videos[prefix] = []
        grouped_videos[prefix].append(os.path.join(input_folder, video_file))

    # 确保每组内的视频按照编号排序
    for prefix in grouped_videos:
        grouped_videos[prefix].sort()
    
    return grouped_videos

def concatenate_videos(video_list, output_path):
    """
    拼接一组视频文件成一个长视频。
    
    :param video_list: list, 待拼接的视频文件路径列表
    :param output_path: str, 输出拼接视频的路径
    """
    if len(video_list) == 1:
        # 如果只有一个视频，直接复制
        os.rename(video_list[0], output_path)
        print(f"只有一个视频，直接保存为: {output_path}")
        return

    # 使用 moviepy 进行视频拼接
    try:
        ffmpeg_concat(video_list, output_path)
        print(f"拼接完成，保存为: {output_path}")
    except Exception as e:
        print(f"拼接失败: {e}")

def merge_videos_by_prefix(input_folder, output_folder):
    """
    按照前缀分组并拼接视频，保存到指定文件夹。
    
    :param input_folder: str, 包含多个视频的文件夹路径
    :param output_folder: str, 拼接后视频保存的文件夹路径
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    grouped_videos = group_videos_by_prefix(input_folder)
    for prefix, video_list in grouped_videos.items():
        output_path = os.path.join(output_folder, f"{prefix}_merged.mp4")
        concatenate_videos(video_list, output_path)






def merge_videos(input_folder, output_folder):
    if not os.path.exists(input_folder):
        print(f"输入文件夹 {input_folder} 不存在")
        return

    video_files = [f for f in os.listdir(input_folder) if f.endswith(".mp4")]
    if not video_files:
        print(f"输入文件夹 {input_folder} 中没有 MP4 文件")
        return

    # 按前缀分组
    prefix_groups = {}
    for video_file in video_files:
        prefix = "_".join(video_file.split("-")[:-1])
        prefix_groups.setdefault(prefix, []).append(video_file)

    for prefix, files in prefix_groups.items():
        files.sort()  # 确保按照名称顺序拼接
        #clips = [VideoFileClip(os.path.join(input_folder, file)) for file in files]
        clips = []
        # 使用 MoviePy 的高层方法拼接视频
        for idx, file in enumerate(files):
            file_path = os.path.join(input_folder, file)
            video_clip = VideoFileClip(file_path)

            # 如果是第一个视频，直接使用
            if idx == 0:
                clips.append(video_clip)
            else:
                # 去掉视频的第一帧（从第二帧开始）
                video_clip = video_clip.subclip(1 / video_clip.fps, video_clip.duration)
                clips.append(video_clip)
        final_clip = concatenate_videoclips(clips, method="compose")
        output_path = os.path.join(output_folder, f"{prefix}_merged.mp4")

        # 保存合并后的视频
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
        print(f"合并完成: {output_path}")

        # 关闭所有 Clip（释放资源）
        for clip in clips:
            clip.close()



if __name__ == "__main__":
    # 定义参数解析器
    parser = argparse.ArgumentParser(description="合并视频片段")
    parser.add_argument("--mode", required=True, help="输出文件夹路径，用于保存合并后的视频")
    parser.add_argument("--input", required=True, help="输入文件夹路径，包含要合并的视频文件")
    parser.add_argument("--output", required=True, help="输出文件夹路径，用于保存合并后的视频")
    
    args = parser.parse_args()

    # 创建输出文件夹（如果不存在）
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    if args.mode == "merge":
        # 调用合并函数
        merge_videos(args.input, args.output)

        # 示例用法
        #input_folder = "split_videos"  # 替换为包含分段视频的文件夹路径
        #output_folder = "merged_videos"  # 替换为保存拼接视频的文件夹路径
        #merge_videos_by_prefix(args.input, args.output)
    elif args.mode == "interp_prep":
        # 示例用法
        #video_folder = "input_videos"  # 替换为包含多个视频文件的文件夹路径
        #output_folder = "frames_output"  # 替换为保存拆解帧的文件夹路径
        extract_frames_from_folder(args.input, args.output)
    else:
        print('模式错误')