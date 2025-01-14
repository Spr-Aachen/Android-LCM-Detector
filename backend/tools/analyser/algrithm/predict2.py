import threading
import os
import gc
import random
import torch
import torchvision
from ultralytics import YOLO
from typing import List, Dict, Union, Optional
from colorama import Fore, Style
from pathlib import Path
from memory_profiler import profile

from .utils import *

##############################################################################################################################

# Allow GPU acceleration if available
isCudaAvailable = torch.cuda.is_available()
device = torch.device("cuda:0" if isCudaAvailable else "cpu")

##############################################################################################################################

# Class names mapping (from training)
class_names = [
    'blackWhiteGrayBlue', #0
    'camOffWhite', #1
    'camOn', #2
    'desktop_black_half_etc', #3
    'floating_to_rect', #4
    'hua', #5
    'other', #6
    'overlap', #7
    'startEndIcon', #8
    'wallpaper' #9
]

##############################################################################################################################

# Define transformations - same as training
transform_normalize = torchvision.transforms.Compose([
    torchvision.transforms.Resize((640, 640)),
    #移除了ToTensor()步骤
    torchvision.transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


transform_yolo = torchvision.transforms.Compose([
    torchvision.transforms.Resize((640, 640)),
    #移除了ToTensor()步骤
])

##############################################################################################################################

# [2024-12-09] 使用yolo的detect模型, 得到floatWindow的坐标, 输入图片, 输出floatWindow的坐标
def detect_floatWin(model: YOLO, pic: Optional[Union[torch.Tensor, str]] = None) -> Union[bool, None]:
    if pic is None:
        return None

    # Ensure the image tensor is on the same device as the model
    picTensor = (torchvision.io.read_image(pic) if isinstance(pic, str) else pic).to(device)
    # Transform the image tensor to the format expected by the model
    image = transform_yolo(
        (picTensor.float() / 255.0).clamp(0.0, 1.0) # Normalize to 0~1
    ).unsqueeze(0)

    results = model(image, verbose = False, conf = 0.7)[0] #save=True,
    # print('results len=', len(results), type(results))
    #
    if len(results) == 0:
        # print(Fore.RED, f'no floatWin detected', Style.RESET_ALL)
        return None

    # [2024-12-09] 简化一下, 只取第一个floatWin
    cords = results[0].boxes[0].xywh[0].tolist()
    n_cords = [int(num) for num in cords] #convert float to int
    x,y,w,h = n_cords
    # x,y,w,h 判断是否黑白, 如果是则返回TRUE, 否则返回FALSE
    # Extract the float window region
    picTensor = picTensor.permute(1, 2, 0) # [C,H,W] -> [H,W,C]
    img = picTensor.cpu().numpy().astype('uint8')
    float_win = img[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
    #
    num_samples = 500 # Monte Carlo sampling - randomly sample points
    height_fw, width_fw = float_win.shape[:2]

    if height_fw == 0 or width_fw == 0:
        return False

    black_count = 0
    white_count = 0

    for _ in range(num_samples):
        # Random point coordinates
        px = random.randint(0, width_fw-1)
        py = random.randint(0, height_fw-1)

        # Get BGR pixel values at random point
        b, g, r = float_win[py, px]
        # Check if pixel is black-ish (all channels < 20) or white-ish (all channels > 230)
        if b < 20 and g < 20 and r < 20:
            black_count += 1
        elif b > 230 and g > 230 and r > 230:
            white_count += 1

    # Calculate percentages
    black_percent = black_count / num_samples
    white_percent = white_count / num_samples

    # If >95% pixels are either black or white, consider it black&white
    if black_percent > 0.95 or white_percent > 0.95:
        return True
    else:
        return False

##############################################################################################################################

predictResult = {}
def analyseFrames(mediaPath, model_camCrop, model_classify, model_detectFloatWin, chkTypes, outputDir, extractType):
    global predictResult

    # Define frameAnalyser
    timestamps = []
    frames = []
    lst_all_type = []
    lst_flick_idxType: list[tuple[int, int]] = [] # 保存idx和type
    def analyse():
        """
        Analyse frames and save the results.
        """
        indexList = [indexType[0] for indexType in lst_flick_idxType]

        if 'bChkGlich' in chkTypes:
            # [2024-11-23] 由于model1添加了hua类型,所以需要调整（之前的类型5,half_quarter_black,现在改为hua）
            lst_output_glich = []
            for i, type in enumerate(lst_all_type):
                if type == 5:
                    lst_output_glich.append(i)
            if len(lst_output_glich) > 0:
                print(Fore.RED, f'[model_classify] 5.{class_names[5]}: {lst_output_glich}', Fore.RESET)
                for frameCount in lst_output_glich:
                    index = indexList[frameCount]
                    saveImage(timestamps[index], frames[index], outputDir, class_names[5])
                updateDict(
                    dict1 = predictResult,
                    dict2 = {'lst_output_glich': lst_output_glich}
                )

        if 'bChkFlick' in chkTypes:
            # [2024-12-09] 判断有无几个连续的type4.floatWindow,当有10+时,判断floatWindow是否是黑白
            lst_output_flick_0 = []
            lst_flick_idxType_floatWin = [x for x in lst_flick_idxType if x[1] == 4]
            if len(lst_flick_idxType_floatWin) > 0:
                # Find sequences of 10 or more consecutive indices
                consecutive_sequences:list[list[tuple[int, int]]] = []
                current_sequence:list[tuple[int, int]] = []

                # Sort by index to ensure we process in order
                sorted_floatwin = sorted(lst_flick_idxType_floatWin, key=lambda x: x[0])

                for i in range(len(sorted_floatwin)):
                    if not current_sequence:
                        # Start new sequence
                        current_sequence.append(sorted_floatwin[i])
                    else:
                        # Check if current index is consecutive with last index in sequence
                        if sorted_floatwin[i][0] == current_sequence[-1][0] + 1:
                            current_sequence.append(sorted_floatwin[i])
                        else:
                            # Sequence broken, check if length >= 10 before starting new
                            if len(current_sequence) >= 10:
                                consecutive_sequences.append(current_sequence)
                            current_sequence = [sorted_floatwin[i]]

                # Check final sequence
                if len(current_sequence) >= 10:
                    consecutive_sequences.append(current_sequence)

                for seq in consecutive_sequences:
                    # step2, 使用yolo的detect模型, 得到floatWindow的坐标, 使用阈值判断, 判断floatWindow是否black_white_etc
                    for tup in seq:
                        i = tup[0]
                        is_black_white = detect_floatWin(model_detectFloatWin, frames[i])
                        if is_black_white is not None:
                            if is_black_white:
                                lst_output_flick_0.append(i)
            if len(lst_output_flick_0) > 0:
                print(Fore.RED, f'[model_detectFloatWin] 0.{class_names[0]}: {lst_output_flick_0}', Fore.RESET)
                for frameCount in lst_output_flick_0:
                    index = indexList[frameCount]
                    saveImage(timestamps[index], frames[index], outputDir, class_names[0])
                updateDict(
                    dict1 = predictResult,
                    dict2 = {'lst_output_flick': lst_output_flick_0}
                )

            # [2024-12-08] 输出两段作为对比, 判断有无几个连续的type4.floatWin
            # [2024-12-08] 遍历lst_all_type, 当遇到type=0时, 向前查看有多少个type=4, 向后查看还有少type=0
            lst_output_flick_4 = []
            lst_output_flick_0 = []
            i = 0
            while i < len(lst_all_type):
                if lst_all_type[i] == 0:
                    # Found type 0, look backwards for type 4
                    count_type4_before = 0
                    j = i - 1
                    while j >= 0 and lst_all_type[j] == 4:
                        count_type4_before += 1
                        j -= 1

                    # Look forward for consecutive type 0
                    count_type0_after = 0
                    j = i + 1
                    while j < len(lst_all_type) and lst_all_type[j] == 0:
                        count_type0_after += 1
                        j += 1

                    # 两种情况, 1.count_type4_before > 0, 2.count_type0_after == 0
                    if count_type4_before > 0:
                        # 或者考虑if timestamps[i-count_type4_before+1] - timestamps[i] > 0.7:
                        diff_tm = timestamps[i]-timestamps[i-count_type4_before]
                        if diff_tm > 0.7:
                            #print(Fore.RED, f"Type4 indices: {list(range(i-count_type4_before, i))}", Fore.RESET)
                            lst_output_flick_4.append(i)
                        else:
                            print(Fore.GREEN, f"after{count_type0_after} type0 {count_type4_before} type4, diff_tm:{diff_tm}", Fore.RESET)
                    else:
                        #print(Fore.RED, f"range {i},{j}: Found type0", Fore.RESET)
                        lst_output_flick_0.extend([num for num in range(i, j)])

                    # Skip past the consecutive type 0s we found
                    i = i + count_type0_after + 1
                else:
                    i += 1
            if len(lst_output_flick_4) > 0:
                print(Fore.RED, f'[model_classify] 4.{class_names[4]}: {lst_output_flick_4}', Fore.RESET)
                for frameCount in lst_output_flick_4:
                    index = indexList[frameCount]
                    saveImage(timestamps[index], frames[index], outputDir, class_names[4])
                updateDict(
                    dict1 = predictResult,
                    dict2 = {'lst_output_flick': lst_output_flick_4}
                )
            if len(lst_output_flick_0) > 0:
                print(Fore.RED, f'[model_classify] 0.{class_names[0]}: {lst_output_flick_0}', Fore.RESET)
                for frameCount in lst_output_flick_0:
                    index = indexList[frameCount]
                    saveImage(timestamps[index], frames[index], outputDir, class_names[0])
                updateDict(
                    dict1 = predictResult,
                    dict2 = {'lst_output_flick': lst_output_flick_0}
                )

            # [2024-11-25] 测试发现,类型3的图片,desktop_black_half_etc
            lst_output_flick_3 = []
            for i, type in enumerate(lst_all_type):
                if type == 3:
                    lst_output_flick_3.append(i)
            if len(lst_output_flick_3) > 0:
                print(Fore.RED, f'[model_classify] 3.{class_names[3]}: {lst_output_flick_3}', Fore.RESET)
                for frameCount in lst_output_flick_3:
                    index = indexList[frameCount]
                    saveImage(timestamps[index], frames[index], outputDir)
                updateDict(
                    dict1 = predictResult,
                    dict2 = {'lst_output_flick': lst_output_flick_3}
                )

    # Extract frames
    idx = 0
    for timestamp, frame in extractFrames(mediaPath, model_camCrop, extractType, outputDir):
        class_num_1 = predict_image(model_classify, transform_normalize, frame, device)
        lst_flick_idxType.append((idx, class_num_1))
        lst_all_type.append(class_num_1)
        if class_num_1 == 6: # 'other'
            frame = None # Filter out specific frames
        frames.append(frame)
        timestamps.append(timestamp)
        idx += 1
        # Start analyse while memory is not enough
        if psutil.virtual_memory().available < 3*(1024**3): # 3GB
            analyse()
            # Release memory
            frameNumber = len(frames)
            if frameNumber >= 10:
                # Keep only the last 10 frames and relevant info
                lst_flick_idxType = [flick_idxType for flick_idxType in lst_flick_idxType if flick_idxType[0] in range(frameNumber - 10, frameNumber)]
                lst_all_type = [flick_idxType[1] for flick_idxType in lst_flick_idxType]
                frames = frames[-10:]
                timestamps = timestamps[-10:]
            else:
                lst_flick_idxType.clear()
                lst_all_type.clear()
                frames.clear()
                timestamps.clear()
    # analyse
    analyse()


@profile(stream = open('./%s_memoryProfiler.log' % Path(__file__).stem, mode = 'w+'), precision = 3)
def predict(
    mediaPath: str,
    chkTypes: list,
    outputFolder: str,
    modelDir: str,
    camCrop: bool = True,
    extractType: ExtractType = ExtractType.TENSOR,
    stopEvent: Optional[threading.Event] = None
):
    """
    """
    global predictResult

    predictResult.clear()

    print(Fore.GREEN, 'analysis media', mediaPath, Style.RESET_ALL)

    # Set output dir
    outputDir = Path(outputFolder).joinpath(Path(mediaPath).stem)
    shutil.rmtree(outputDir, ignore_errors = True) if Path(outputDir).exists() else None
    os.makedirs(outputDir, exist_ok = True)

    # Load models
    model_camCrop = YOLO(Path(modelDir).joinpath('model_camCrop.pt').as_posix()) if camCrop else None
    model_classify = loadEffNetModel('b3', Path(modelDir).joinpath('effNet_b3_cls_flicker_best.pth'), class_names, device)
    #model_classify = torch.jit.script(model_classify)
    model_detectFloatWin = YOLO(Path(modelDir).joinpath('model_detect_float_window2_best.pt').as_posix(), task = 'detect')

    # Analyse frames
    analyseFrames(mediaPath, model_camCrop, model_classify, model_detectFloatWin, chkTypes, outputDir, extractType)

    # Release memory
    local_vars = list(locals().items())
    for name, val in local_vars:
        if isinstance(val, torch.Tensor):
            #if val.is_cuda:
                #val.cpu()
            del val
    torch.cuda.empty_cache() if isCudaAvailable else None
    gc.collect()

##############################################################################################################################