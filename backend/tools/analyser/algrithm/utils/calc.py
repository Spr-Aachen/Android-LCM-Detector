import random
import numpy

##############################################################################################################################

def is_mostly_black(frame: numpy.ndarray, sample_size = 1000) -> bool:
    """
    使用蒙特卡罗采样方法判断一帧图像的绝大部分是否为黑色
    """
    # 获取图像的高度和宽度
    height, width = frame.shape[:2]
    if height == 0 or width == 0:
        return False
    # 进行 sample_size 次随机采样
    black_pixels = 0
    for _ in range(sample_size):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        pixel = frame[y, x]  # 注意：numpy数组是[y, x]，而不是[x, y]
        # 如果像素值的 B、G、R 都小于 50，则认为是黑色
        if all(p < 50 for p in pixel):
            black_pixels += 1
    # 计算黑色像素占总采样的比例
    black_ratio = black_pixels / sample_size
    # 如果黑色像素占比大于 0.9，则认为图片的绝大部分是黑色
    return black_ratio > 0.9


def is_black_img(frame: numpy.ndarray, sample_size = 1000) -> bool:
    # 获取图像的高度和宽度
    height, width = frame.shape[:2]
    if height == 0 or width == 0:
        return False
    # 进行 sample_size 次随机采样
    black_pixels = 0
    for _ in range(sample_size):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        pixel = frame[y, x]  # 注意：numpy数组是[y, x]，而不是[x, y]
        # 如果像素值的 R、G、B 都小于 50,则认为是黑色
        if sum(pixel) < 50 * 3:
            black_pixels += 1
    # 计算黑色像素占总采样的比例
    black_ratio = black_pixels / sample_size
    # 如果黑色像素占比大于 0.9,则认为图片的绝大部分是黑色
    return black_ratio > 0.9

##############################################################################################################################