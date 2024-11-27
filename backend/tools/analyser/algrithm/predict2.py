import threading
import os
import shutil
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import torchvision
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
from datetime import datetime
from pathlib import Path

from .utils import *

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


# Class names mapping for 2pic model
class_names_2pic = ['N', 'Y']

##############################################################################################################################

# Allow GPU acceleration if available
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")


# Define transformations - same as training
transform = transforms.Compose([
    transforms.Resize((640, 640)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

##############################################################################################################################

def loadModel(modelPath: str, classes: list):
    # Load pre-trained EfficientNet model
    model = models.efficientnet_b1(weights = None)
    model.classifier[1] = nn.Linear(
        in_features = model.classifier[1].in_features,
        out_features = len(classes)
    )
    # Load trained weights
    model.load_state_dict(torch.load(modelPath, weights_only = True))
    # Move model to GPU if available
    model.to(device)
    # Set model to evaluation mode
    model.eval()
    return model


def predict1_image_num(model: torchvision.models.EfficientNet, image_path = ...) -> int:
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)

    return int(predicted.item()) #return class_names[predicted.item()]


def predict2_image_str(model: torchvision.models.EfficientNet, image_path = ...) -> str:
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)

    return class_names_2pic[predicted.item()]

##############################################################################################################################

# [2024-11-18] 找到连续的序列
def find_cons_seq(lst_type: list, target: int = 2, min_length: int = 3) -> list[tuple[int, int]]:
    lst_all_range = []
    i = 0
    while i <= len(lst_type)-min_length:
        if lst_type[i:i+min_length] == [target]*min_length:
            # Found start of sequence, find end
            start = i
            while i < len(lst_type) and lst_type[i] == target:
                i += 1
            end = i - 1
            lst_all_range.append((start, end))
            # Look for next sequence starting after this one
        else:
            i += 1
    return lst_all_range


def merge_and_predict_flicker(model2, file1, file2, outputFolder, mergeFolder, i)->str:
    # Read the two images using torchvision
    img1 = torchvision.io.read_image(Path(outputFolder).joinpath(file1).as_posix())
    img2 = torchvision.io.read_image(Path(outputFolder).joinpath(file2).as_posix())

    # Make sure both images have same height
    if img1.shape[1] != img2.shape[1]:
        # Resize to match height of first image
        transform = torchvision.transforms.Resize((img1.shape[1], img2.shape[2]))
        img2 = transform(img2)

    # Concatenate images horizontally
    merged_img = torch.cat([img1, img2], dim=2)
    # Save merged image
    torchvision.io.write_jpeg(merged_img, Path(mergeFolder).joinpath(f"{i:04d}_{i+1:04d}.jpg").as_posix(), quality=100)
    return predict2_image_str(model2, Path(mergeFolder).joinpath(f"{i:04d}_{i+1:04d}.jpg").as_posix())


predictResult = {}
def analyseFrames(model1, model2, chkTypes, outputFolder, mergeFolder):
    global predictResult

    lst_all_type = [predict1_image_num(model1, pic.as_posix()) for pic in Path(outputFolder).glob('*.jpg')]
    #print(Fore.GREEN + 'lst_all_type:' + Fore.RESET, lst_all_type)

    if 'bChkGlich' in chkTypes:
        lst_tup_seq_glich = find_cons_seq(lst_all_type, target=5, min_length=1)

        for start, end in lst_tup_seq_glich:
            lst_output_glich = []
            for i in range(start, end):
                lst_output_glich.append(i)
            UpdateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_glich': lst_output_glich}
            ) if lst_output_glich.__len__() > 0 else None

    if 'bChkFlick' in chkTypes:
        # 'camOn', #2
        # Find sequences of consecutive 'camOn' frames
        lst_tup_seq_camOn = find_cons_seq(lst_all_type, target=2, min_length=3)
        # print(Fore.GREEN + f"Found {len(lst_tup_seq_camOn)} sequences of consecutive 'camOn' frames" + Fore.RESET)
        # print(Fore.GREEN + f"camOn_sequences: {lst_tup_seq_camOn}" + Fore.RESET)
        # lst_tup_seq_camOn = find_cons_seq(lst_all_type, target=2, min_length=3)
        lst_tup_seq_floatWin = find_cons_seq(lst_all_type, target=4, min_length=3)

        for i, (start, end) in enumerate(lst_tup_seq_floatWin):
            # 在这序列的end后面,有多少个连续的0
            # Count consecutive zeros after the sequence end
            zeros_count = 0
            curr_pos = end + 1

            # Check if next 5 frames are all zeros
            skip = 0
            if curr_pos + 5 <= len(lst_all_type) and lst_all_type[curr_pos:curr_pos+5] == [0]*5:
                zeros_count = 5
                curr_pos += 5
                skip = 5
                print(Fore.RED + f"floatWin frame {start:04d} to {end:04d} Followed by {zeros_count} MORE cons zeros" + Fore.RESET)
            else:
                print(Fore.BLUE + f"floatWin frame {start:04d} to {end:04d} Not followed by 5 cons zeros" + Fore.RESET)
                # 考虑跳掉几帧,
                try:
                    if lst_all_type[end+4] == 0:
                        skip = 4
                    elif lst_all_type[end+3] == 0:
                        skip = 3
                    elif lst_all_type[end+2] == 0:
                        skip = 2
                    elif lst_all_type[end+1] == 0:
                        skip = 1
                except:
                    pass

            lst_output_flick = []
            # 对下一个range之间的其他类型,进行检测
            if i+1 < len(lst_tup_seq_floatWin):
                next_start, next_end = lst_tup_seq_floatWin[i+1]
                # next_type = lst_all_type[next_end]
                # print(Fore.YELLOW + f"next_type: {class_names[next_type]}" + Fore.RESET)
                # 对下一个range之间的其他图像(是否要考虑类型问题),进行检测
                for j in range(end+skip+1, next_start):
                    file1 = f"{j:04d}.jpg"
                    file2 = f"{j+1:04d}.jpg"
                    flick_type = merge_and_predict_flicker(model2, file1, file2, outputFolder, mergeFolder, j)
                    if flick_type == 'Y':
                        print(Fore.RED, 'in 2 floatWin range:', f"{j:04d}_{j+1:04d}.jpg: {flick_type}", Fore.RESET)
                        lst_output_flick.extend([j, j+1])
            UpdateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick}
            ) if lst_output_flick.__len__() > 0 else None

        # 在floatWin的序列中,合并图片,并预测,主要是procVw中的窗口显示问题
        for start, end in lst_tup_seq_floatWin:
            lst_output_flick = []
            for i in range(start, end):
                file1 = f"{i:04d}.jpg"
                file2 = f"{i+1:04d}.jpg"
                flick_type = merge_and_predict_flicker(model2, file1, file2, outputFolder, mergeFolder, i)
                if flick_type == 'Y':
                    print(Fore.RED, 'floatWin flicker:', f"{i:04d}_{i+1:04d}.jpg: {flick_type}", Fore.RESET)
                    lst_output_flick.extend([i, i+1])
            UpdateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick}
            ) if lst_output_flick.__len__() > 0 else None

        # 遍历每个序列camOn
        for start, end in lst_tup_seq_camOn:
            lst_output_flick = []
            for i in range(start, end):
                # print(lst_all_type[i])
                file1 = f"{i:04d}.jpg"
                file2 = f"{i+1:04d}.jpg"
                flick_type = merge_and_predict_flicker(model2, file1, file2, outputFolder, mergeFolder, i)
                if flick_type == 'Y':
                    print(f"{i:04d}_{i+1:04d}.jpg: {flick_type}")
                    lst_output_flick.extend([i, i+1])
            UpdateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick}
            ) if lst_output_flick.__len__() > 0 else None

        if len(lst_tup_seq_camOn) == 0 and len(lst_tup_seq_floatWin) == 0:
            print(Fore.RED + 'No camOn2/floatWin4 found,check 6.other type', Fore.RESET)
            # 没有找到camOn2/floatWin4,则需要考虑其他类型
            # 例如883_Screen_Recording_20240507_111135,(notebook)fixed:现在全是类型6
            # 这里有类型判断问题,需要考虑增加训练数据,other里面数据还是太少
            # lst_all_type
            # TODO: 假设这里对6进行全量检测
            lst_tup_seq_other = find_cons_seq(lst_all_type, target=6, min_length=3)
            for start, end in lst_tup_seq_other:
                lst_output_flick = []
                print(Fore.GREEN + f"6.other frames {start:04d} to {end:04d}" + Fore.RESET)
                for i in range(start, end):
                    file1 = f"{i:04d}.jpg"
                    file2 = f"{i+1:04d}.jpg"
                    flick_type = merge_and_predict_flicker(model2, file1, file2, outputFolder, mergeFolder, i)
                    if flick_type == 'Y':
                        print(f"{i:04d}_{i+1:04d}.jpg: {flick_type}")
                        lst_output_flick.extend([i, i+1])
                UpdateDict(
                    Dict1 = predictResult,
                    Dict2 = {'lst_output_flick': lst_output_flick}
                ) if lst_output_flick.__len__() > 0 else None


def predict(
    videoPath: str,
    chkTypes: list,
    outputFolder: str,
    modelDir: str,
    stopEvent: Optional[threading.Event] = None
):
    """
    """
    global predictResult

    predictResult.clear()

    print(Fore.GREEN, 'analysis_video', videoPath, Style.RESET_ALL)

    # Set output dir
    outputDir = Path(outputFolder).joinpath(Path(videoPath).stem)

    # Set extract folder
    extractFolder = outputDir.joinpath('extract').as_posix()
    shutil.rmtree(extractFolder, ignore_errors = True) if Path(extractFolder).exists() else None
    os.makedirs(extractFolder, exist_ok = True)
    # Extract frames
    extract_frames(videoPath, extractFolder)

    # Set merge folder
    mergeFolder = outputDir.joinpath('merge').as_posix()
    shutil.rmtree(mergeFolder, ignore_errors = True) if Path(mergeFolder).exists() else None
    os.makedirs(mergeFolder, exist_ok = True)

    # Load models
    model1 = loadModel(Path(modelDir).joinpath('effNet_b1_cls_flicker_best.pth'), class_names)
    model2 = loadModel(Path(modelDir).joinpath('effNet_v2_b1_cls_flicker2pic_best.pth'), class_names_2pic)

    # Analyse frames
    analyseFrames(model1, model2, chkTypes, extractFolder, mergeFolder)

##############################################################################################################################