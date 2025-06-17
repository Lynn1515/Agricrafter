from PIL import Image
import numpy as np
import shutil
import cv2
import os

def center_crop_resize(image_path, output_path, target_width=512, target_height=320):
    # 打开图像
    img = Image.open(image_path)
    
    # 获取图像尺寸
    width, height = img.size
    
    # 计算中心裁剪区域
    new_width = min(width, height * target_width // target_height)
    new_height = min(height, width * target_height // target_width)
    
    # 计算裁剪的左上角和右下角坐标
    left = (width - new_width) / 2
    top = (height - new_height) / 2
    right = (width + new_width) / 2
    bottom = (height + new_height) / 2
    
    # 裁剪图像
    img_cropped = img.crop((left, top, right, bottom))
    
    # 调整为目标分辨率
    img_resized = img_cropped.resize((target_width, target_height), Image.ANTIALIAS)
    
    # 保存结果
    img_resized.save(output_path)

# # 使用示例
# image_path = '/home/cx_wchn/lnwang/DynamiCrafter-main/prompts/512_corn/0007.jpg'
# output_path = '/home/cx_wchn/lnwang/DynamiCrafter-main/prompts/512_corn/0007.jpg'
# center_crop_resize(image_path, output_path)

def center_crop_resize2(image, target_width=512, target_height=320):
    # 打开图像
    img = image
    if isinstance(img, np.ndarray):
        img = Image.fromarray(img)

    
    # 获取图像尺寸
    width, height = img.size
    
    # 计算中心裁剪区域
    new_width = min(width, height * target_width // target_height)
    new_height = min(height, width * target_height // target_width)
    
    # 计算裁剪的左上角和右下角坐标
    left = (width - new_width) / 2
    top = (height - new_height) / 2
    right = (width + new_width) / 2
    bottom = (height + new_height) / 2
    
    # 裁剪图像
    img_cropped = img.crop((left, top, right, bottom))
    
    # 调整为目标分辨率
    img_resized = img_cropped.resize((target_width, target_height), Image.ANTIALIAS)
    img_np = np.array(img_resized)
    # 保存结果
    return img_np




def resize_to_target(input_folder, output_folder, target_width=512, target_height=320):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)

            # 打开图片
            with Image.open(input_path) as img:
                # 计算缩放比例以适应 target_width x target_height
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

                # 保存处理后的图片
                img_cropped.save(output_path, quality=95)


def decrease_exposure(image_path, output_path, factor=0.5):
    """
    降低图像曝光度
    :param image_path: 输入图像路径
    :param output_path: 输出路径
    :param factor: 曝光度系数 (0-1)，默认0.5
    """
    output_frame_name = image_path.split("/")[-1]
    output_frame_path = os.path.join(output_path, output_frame_name)
    #shutil.copy(image_path, output_frame_path)

    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print("无法加载图像，请检查文件路径。")
        return

    # 处理图像曝光度
    image = image.astype(np.float32) / 255.0
    adjusted_image = np.clip(image * factor, 0, 1)
    adjusted_image = (adjusted_image * 255).astype(np.uint8)
    
    # 保存处理后的图像
    output_path = os.path.join(output_path, "low_" + output_frame_name)
    cv2.imwrite(output_path, adjusted_image)
    print(f"曝光度调整后的图像已保存到 {output_path}")

def increase_saturation(image_path, output_path, saturation_scale=1.5):
    """
    增加色彩饱和度
    :param image_path: 输入图像路径
    :param output_path: 输出路径
    :param saturation_scale: 饱和度增益系数，默认1.5
    """
    output_frame_name = image_path.split("/")[-1]
    output_frame_path = os.path.join(output_path, output_frame_name)
    shutil.copy(image_path, output_frame_path)

    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print("无法加载图像，请检查文件路径。")
        return

    # 增加饱和度
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv_image[..., 1] *= saturation_scale
    hsv_image[..., 1] = np.clip(hsv_image[..., 1], 0, 255)
    saturated_image = cv2.cvtColor(hsv_image.astype(np.uint8), cv2.COLOR_HSV2BGR)

    # 保存处理后的图像
    output_path = os.path.join(output_path, "saturated_" + output_frame_name)
    cv2.imwrite(output_path, saturated_image)
    print(f"饱和度增加后的图像已保存到 {output_path}")

def increase_contrast(image_path, output_path, contrast=1.1, brightness=-20):
    """
    增强图像对比度
    :param image_path: 输入图像路径
    :param output_path: 输出路径
    :param contrast: 对比度增益系数，默认1.5
    :param brightness: 亮度调节值，默认20
    """
    output_frame_name = image_path.split("/")[-1]
    output_frame_path = os.path.join(output_path, output_frame_name)
    shutil.copy(image_path, output_frame_path)

    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print("无法加载图像，请检查文件路径。")
        return

    # 增强对比度和亮度
    contrasted_image = cv2.convertScaleAbs(image, alpha=contrast, beta=brightness)
    
    # 保存处理后的图像
    output_path = os.path.join(output_path, "contrast_" + output_frame_name)
    cv2.imwrite(output_path, contrasted_image)
    print(f"对比度增强后的图像已保存到 {output_path}")

def undistort_image(image_path, output_path, camera_matrix=None, dist_coeffs=None):
    """
    校正图像边缘畸变
    :param image_path: 输入图像路径
    :param output_path: 输出图像路径
    :param camera_matrix: 相机内参矩阵（3x3）
    :param dist_coeffs: 畸变系数（1x5或1x4），如果未知则使用默认值
    """
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print("无法加载图像，请检查文件路径。")
        return

    h, w = image.shape[:2]
    
    # 如果没有提供相机矩阵和畸变系数，设置一些默认值
    if camera_matrix is None:
        # 近似的焦距（取图片宽度的0.8倍）
        focal_length = w * 0.8
        camera_matrix = np.array([[focal_length, 0, w / 2],
                                  [0, focal_length, h / 2],
                                  [0, 0, 1]], dtype=np.float32)
    
    if dist_coeffs is None:
        # 通用的桶形畸变系数，可以根据相机特性微调
        dist_coeffs = np.array([-0.3, 0.1, 0, 0], dtype=np.float32)

    # 生成新的校正后的相机矩阵
    new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # 校正图像
    undistorted_image = cv2.undistort(image, camera_matrix, dist_coeffs, None, new_camera_matrix)

    # 保存处理后的图像
    output_path = os.path.join(output_path, "undistorted_" + image_path.split("/")[-1])
    cv2.imwrite(output_path, undistorted_image)
    print(f"校正后的图像已保存到 {output_path}")

def undistort_image(image_path, output_path, camera_matrix=None, dist_coeffs=None):
    """
    校正图像边缘畸变
    :param image_path: 输入图像路径
    :param output_path: 输出图像路径
    :param camera_matrix: 相机内参矩阵（3x3）
    :param dist_coeffs: 畸变系数（1x5或1x4），如果未知则使用默认值
    """
    # 读取图像
    image = cv2.imread(image_path)
    if image is None:
        print("无法加载图像，请检查文件路径。")
        return

    h, w = image.shape[:2]
    
    # 如果没有提供相机矩阵和畸变系数，设置一些默认值
    if camera_matrix is None:
        # 近似的焦距（取图片宽度的0.8倍）
        focal_length = w * 0.8
        camera_matrix = np.array([[focal_length, 0, w / 2],
                                  [0, focal_length, h / 2],
                                  [0, 0, 1]], dtype=np.float32)
    
    if dist_coeffs is None:
        # 通用的桶形畸变系数，可以根据相机特性微调
        dist_coeffs = np.array([-0.3, 0.1, 0, 0], dtype=np.float32)

    # 生成新的校正后的相机矩阵
    new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # 校正图像
    undistorted_image = cv2.undistort(image, camera_matrix, dist_coeffs, None, new_camera_matrix)

    # 保存处理后的图像
    output_path = os.path.join(output_path, "undistorted_" + image_path.split("/")[-1])
    cv2.imwrite(output_path, undistorted_image)
    print(f"校正后的图像已保存到 {output_path}")

image_path = '/home/cx_wchn/lnwang/Data/corn6/001/0016.jpg'
output_path = '/home/cx_wchn/lnwang/Data/demo'  # 替换为你的输出路径
undistort_image(image_path, output_path)

image_path = '/home/cx_wchn/lnwang/Data/corn6_crop/007_006/0011.png'
output_path = '/home/cx_wchn/lnwang/Data/demo'
decrease_exposure(image_path, output_path, factor=0.8)
increase_saturation(image_path, output_path, saturation_scale=1.5)
increase_contrast(image_path, output_path, contrast=1.1, brightness=-20)
decrease_exposure('/home/cx_wchn/lnwang/Data/demo/saturated_0011.png', output_path, factor=0.9)



# input_folder = '/home/cx_wchn/lnwang/DynamiCrafter-main/assets/test_proj'  # 输入高分辨率图像文件夹
# output_folder = '/home/cx_wchn/lnwang/DynamiCrafter-main/assets/test_crop'  # 输出文件夹
# resize_to_target(input_folder, output_folder)