import os
import cv2
import random
from PIL import Image, ImageFile

##############################################################################################################################

def extract_frames(video_path, output_folder, filename_no_ext, enable_imagesave=False):
    # Load the video
    cap = cv2.VideoCapture(video_path)

    # Initialize frame counter
    frame_count = 0
    # 创建文件夹
    os.makedirs(os.path.join(output_folder, filename_no_ext), exist_ok=True)
    # Loop through each frame in the video
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Break the loop if there are no frames left to read

        formatted_n = f"{frame_count:04}"
        frame_filename = os.path.join(output_folder, filename_no_ext, f"{formatted_n}.webp")  # Save each frame as an image
        cv2.imwrite(frame_filename, frame,[cv2.IMWRITE_WEBP_QUALITY, 90]) if enable_imagesave else None
        frame_count += 1

    # Release the video capture object
    cap.release()


def is_mostly_black(image_path, sample_size=1000) -> bool:
    """
    使用蒙特卡罗采样方法判断一张图片的绝大部分是否为黑色
    """
    image = Image.open(image_path)
    width, height = image.size
    # 进行 sample_size 次随机采样
    black_pixels = 0
    for _ in range(sample_size):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        pixel = image.getpixel((x, y))
        # 如果像素值的 R、G、B 都小于 50,则认为是黑色
        if sum(pixel) < 50 * 3:
            black_pixels += 1
    # 计算黑色像素占总采样的比例
    black_ratio = black_pixels / sample_size
    # 如果黑色像素占比大于 0.9,则认为图片的绝大部分是黑色
    return black_ratio > 0.9


# [2024-8-14]
def is_black_img(image:ImageFile, sample_size=1000)-> bool:
    width, height = image.size
    # print(Fore.GREEN, f"Image size: {width} x {height}", Fore.RESET)
    # 进行 sample_size 次随机采样
    black_pixels = 0
    for _ in range(sample_size):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        pixel = image.getpixel((x, y))
        # print(Fore.MAGENTA + f"({x}, {y}) = {pixel}" + Style.RESET_ALL)
        # 如果像素值的 R、G、B 都小于 50,则认为是黑色
        if sum(pixel) < 50 * 3:
            black_pixels += 1
    # 计算黑色像素占总采样的比例
    black_ratio = black_pixels / sample_size
    print('black_ratio=', black_ratio)
    # 如果黑色像素占比大于 0.9,则认为图片的绝大部分是黑色
    return black_ratio > 0.9


def nobar_split_half_black(image_path, sample_sz=1000) -> bool:
    image = Image.open(image_path)
    width, height = image.size
    # 获取图像的一半宽度和高度
    half_width = width // 2
    half_height = height // 2
    # 裁剪出图像的左半部分
    L_half = image.crop((0, 0, half_width, height))
    R_half = image.crop((half_width, 0, width, height))
    U_half = image.crop((0, 0, width, half_height))
    D_half = image.crop((0, half_height, width, height))
    return is_black_img(L_half, sample_sz) or is_black_img(R_half, sample_sz) or is_black_img(U_half, sample_sz) or is_black_img(D_half, sample_sz)

##############################################################################################################################