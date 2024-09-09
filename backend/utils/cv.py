import os
import cv2
import random
import numpy as np

##############################################################################################################################

def save_image(frame_count, frame, output_folder, subdir):
    formatted_n = f"{frame_count:04}"
    frame_filename = os.path.join(output_folder, subdir, f"{formatted_n}.webp")
    cv2.imwrite(frame_filename, frame, [cv2.IMWRITE_WEBP_QUALITY, 90])
    return frame_filename


def is_mostly_black(frame: np.ndarray, sample_size=1000) -> bool:
    """
    使用蒙特卡罗采样方法判断一帧图像的绝大部分是否为黑色
    """
    height, width = frame.shape[:2]
    # 进行 sample_size 次随机采样
    black_pixels = 0
    for _ in range(sample_size):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        pixel = frame[y, x]  # 注意：numpy数组是[y, x]，而不是[x, y]
        # 如果像素值的 B、G、R 都小于 50，则认为是黑色
        if sum(pixel) < 50 * 3:
            black_pixels += 1
    # 计算黑色像素占总采样的比例
    black_ratio = black_pixels / sample_size
    # 如果黑色像素占比大于 0.9，则认为图片的绝大部分是黑色
    return black_ratio > 0.9


# [2024-8-14]
def is_black_img(image: np.ndarray, sample_size=1000) -> bool:
    height, width = image.shape[:2]
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


def nobar_split_half_black(frame: np.ndarray, sample_sz=1000) -> bool:
    height, width = frame.shape[:2]
    # 获取图像的一半宽度和高度
    half_width = width // 2
    half_height = height // 2
    # 裁剪出图像的左半部分
    L_half = frame[:, :half_width]
    R_half = frame[:, half_width:]
    U_half = frame[:half_height, :]
    D_half = frame[half_height:, :]
    return is_black_img(L_half, sample_sz) or is_black_img(R_half, sample_sz) or is_black_img(U_half, sample_sz) or is_black_img(D_half, sample_sz)

##############################################################################################################################