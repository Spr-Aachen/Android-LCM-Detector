import threading
import os
import shutil
import torch
import torch.nn as nn
from torchvision import transforms, models
import torchvision
from typing import List, Dict, Optional
from colorama import Fore, Style
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
transform_normalize = transforms.Compose([
    transforms.Resize((640, 640)),
    #移除了ToTensor()步骤
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


transform2pic_normalize = transforms.Compose([
    transforms.Resize((640, 1280)),
    #移除了ToTensor()步骤
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

##############################################################################################################################

def loadModel(effNetVersion: str, modelPath: str, classes: list):
    # Load pre-trained EfficientNet model
    model: torchvision.models.EfficientNet = getattr(models, f"efficientnet_{effNetVersion}")(weights = None)
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
    # OpenCV读取为BGR格式
    image = cv2.imread(image_path)
    # 转换为RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # 转换为tensor
    image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
    image = transform_normalize(image).unsqueeze(0).to(device)

    with torch.inference_mode():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)

    return int(predicted.item()) #return class_names[predicted.item()]


# [2024-11-28] 性能大概提高了4倍,500秒->135秒
def predict1_image_num_tv_io(model: torchvision.models.EfficientNet, image_path) -> int:
    # 直接读取为tensor，避免PIL转换步骤
    image = torchvision.io.read_image(image_path).float() / 255.0  # 归一化到0-1
    # Ensure the image tensor is on the same device as the model
    image = image.to(device)  # Move image to the correct device
    # Normalize and add batch dimension
    image = transform_normalize(image).unsqueeze(0).to(device)

    with torch.inference_mode():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)

    return int(predicted.item()) #return class_names[predicted.item()]


def predict2_image_str(model: torchvision.models.EfficientNet, image_path = ...) -> str:
    # OpenCV读取为BGR格式
    image = cv2.imread(image_path)
    # 转换为RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # 转换为tensor
    image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
    image = transform2pic_normalize(image).unsqueeze(0).to(device)

    with torch.inference_mode():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)

    return class_names_2pic[predicted.item()]


# [2024-11-28] 实验,使用torchvision.io读取
def predict2_image_str_tv_io(model: torchvision.models.EfficientNet, image_path) -> str:
    # 直接读取为tensor，避免PIL转换步骤
    image = torchvision.io.read_image(image_path).float() / 255.0  # 归一化到0-1
    # Normalize and add batch dimension
    image = transform2pic_normalize(image).unsqueeze(0).to(device)

    with torch.inference_mode():
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
    return predict2_image_str_tv_io(model2, Path(mergeFolder).joinpath(f"{i:04d}_{i+1:04d}.jpg").as_posix())


predictResult = {}
def analyseFrames(model1, model2, chkTypes, outputFolder, mergeFolder):
    global predictResult

    lst_all_type = [predict1_image_num(model1, pic.as_posix()) for pic in getFiles(outputFolder, ('.jpg', '.png'))]
    #print(Fore.GREEN + 'lst_all_type:' + Fore.RESET, lst_all_type)

    b_found_err_before :bool = False

    if 'bChkGlich' in chkTypes:
        # [2024-11-23] 由于model1添加了hua类型,所以需要调整（之前的类型5,half_quarter_black,现在改为hua）
        '''
        lst_tup_seq_glich = find_cons_seq(lst_all_type, target=5, min_length=1)

        for start, end in lst_tup_seq_glich:
            lst_output_glich = []
            for i in range(start, end):
                lst_output_glich.append(i)
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_glich': lst_output_glich}
            ) if lst_output_glich.__len__() > 0 else None
        if len(lst_output_glich) > 0:
            print(Fore.RED, 'in 5.hua IDX:', lst_output_glich, Fore.RESET)
            b_found_err_before = True
        '''
        lst_output_glich = []
        for i, type in enumerate(lst_all_type):
            if type == 5:
                lst_output_glich.append(i)
        if len(lst_output_glich) > 0:
            print(Fore.RED, 'in 5.hua IDX:', lst_output_glich, Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_glich': lst_output_glich}
            )

    if 'bChkFlick' in chkTypes:
        '''
        # [2024-11-29] 测试发现,类型0的图片,black_white_etc
        lst_output_flick = []
        for i, type in enumerate(lst_all_type):
            if type == 0: 
                lst_output_flick.append(i)
        if len(lst_output_flick) > 0:
            print(Fore.RED,' in 0.black_white_etc IDX:', lst_output_flick, Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_glich': lst_output_flick}
            )
        '''

        # [2024-11-25] 测试发现,类型3的图片,desktop_black_half_etc
        lst_output_flick = []
        for i, type in enumerate(lst_all_type):
            if type == 3:
                lst_output_flick.append(i)
        if len(lst_output_flick) > 0:
            print(Fore.RED, 'in 3.desktop_black_half_etc IDX:', lst_output_flick, Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_glich': lst_output_flick}
            )

        # 'camOn', #2
        # Find sequences of consecutive 'camOn' frames
        lst_tup_seq_camOn = find_cons_seq(lst_all_type, target=2, min_length=3)
        #print(Fore.GREEN + f"Found {len(lst_tup_seq_camOn)} sequences of consecutive 'camOn' frames" + Fore.RESET)
        #print(Fore.GREEN + f"camOn_sequences: {lst_tup_seq_camOn}" + Fore.RESET)
        #lst_tup_seq_camOn = find_cons_seq(lst_all_type, target=2, min_length=3)
        lst_tup_seq_floatWin = find_cons_seq(lst_all_type, target=4, min_length=3)

        for i, (start, end) in enumerate(lst_tup_seq_floatWin):
            # Count consecutive zeros after the sequence end
            zeros_count = 0
            curr_pos = end + 1

            # Check if next 5 frames are all zeros
            # TODO:或者也可能是1.camOffWhite
            if curr_pos + 5 <= len(lst_all_type) and lst_all_type[curr_pos:curr_pos+5] == [0]*5:
                zeros_count = 5
                curr_pos += 5
                skip = 5
                print(Fore.RED + f"floatWin frame {start:04d} to {end:04d} Followed by {zeros_count} MORE cons zeros" + Fore.RESET)
                b_found_err_before = True
            else:
                print(Fore.BLUE + f"floatWin frame {start:04d} to {end:04d} Not followed by 5 cons zeros" + Fore.RESET)
                if len(lst_all_type) > end+4 and lst_all_type[end+4] == 0:
                    skip = 4
                elif len(lst_all_type) > end+3 and lst_all_type[end+3] == 0:
                    skip = 3
                elif len(lst_all_type) > end+2 and lst_all_type[end+2] == 0:
                    skip = 2
                elif len(lst_all_type) > end+1 and lst_all_type[end+1] == 0:
                    skip = 1
                else:
                    skip = 0

            lst_output_flick = []
            # 对下一个range之间的其他类型,进行检测
            if i+1 < len(lst_tup_seq_floatWin):
                next_start, next_end = lst_tup_seq_floatWin[i+1]
                #next_type = lst_all_type[next_end]
                #print(Fore.YELLOW + f"next_type: {class_names[next_type]}" + Fore.RESET)
                # 对下一个range之间的其他图像(是否要考虑类型问题),进行检测
                for j in range(end+skip+1, next_start):
                    file1 = f"{j:04d}.jpg"
                    file2 = f"{j+1:04d}.jpg"
                    flick_type = merge_and_predict_flicker(model2, file1, file2, outputFolder, mergeFolder, j)
                    if flick_type == 'Y':
                        print(Fore.RED, 'in 2 floatWin range:', f"{j:04d}_{j+1:04d}.jpg: {flick_type}", Fore.RESET)
                        lst_output_flick.extend([j, j+1])
                        b_found_err_before = True
            updateDict(
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
                    b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick}
            ) if lst_output_flick.__len__() > 0 else None

        # 遍历每个序列camOn
        for start, end in lst_tup_seq_camOn:
            lst_output_flick = []
            for i in range(start, end):
                file1 = f"{i:04d}.jpg"
                file2 = f"{i+1:04d}.jpg"
                flick_type = merge_and_predict_flicker(model2, file1, file2, outputFolder, mergeFolder, i)
                if flick_type == 'Y':
                    print(Fore.RED, f"{i:04d}_{i+1:04d}.jpg: {flick_type}", Fore.RESET)
                    lst_output_flick.extend([i, i+1])
                    b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick}
            ) if lst_output_flick.__len__() > 0 else None

        # NOTE:有camOn但没有问题,所以要检测其他类型,因此,这里if判断要拿掉
        # if len(lst_tup_seq_camOn) == 0 and len(lst_tup_seq_floatWin) == 0:
        print(Fore.RED + 'No camOn2/floatWin4 found,check 6.other type', Fore.RESET)
        # 没有找到camOn2/floatWin4,则需要考虑其他类型
        # 例如883_Screen_Recording_20240507_111135,(notebook)fixed:现在全是类型6
        # 这里有类型判断问题,需要考虑增加训练数据,other里面数据还是太少
        # lst_flick_type
        # 假设这里对6进行全量检测
        if b_found_err_before == False:
            lst_tup_seq_other = find_cons_seq(lst_all_type, target=6, min_length=3)
            print(Fore.GREEN + f"6.other range count: {len(lst_tup_seq_other)}" + Fore.RESET)
            for start, end in lst_tup_seq_other:
                lst_output_flick = []
                print(Fore.GREEN + f"6.other frames {start:04d} to {end:04d}" + Fore.RESET)
                for i in range(start, end):
                    file1 = f"{i:04d}.jpg"
                    file2 = f"{i+1:04d}.jpg"
                    flick_type = merge_and_predict_flicker(model2, file1, file2, outputFolder, mergeFolder, i)
                    if flick_type == 'Y':
                        print(Fore.RED, f"{i:04d}_{i+1:04d}.jpg: {flick_type}", Fore.RESET)
                        lst_output_flick.extend([i, i+1])
                updateDict(
                    Dict1 = predictResult,
                    Dict2 = {'lst_output_flick': lst_output_flick}
                ) if lst_output_flick.__len__() > 0 else None

        print('\n')


frameRate = 0
def predict(
    mediaPath: str,
    chkTypes: list,
    outputFolder: str,
    modelDir: str,
    stopEvent: Optional[threading.Event] = None
):
    """
    """
    global predictResult, frameRate

    predictResult.clear()

    print(Fore.GREEN, 'analysis media', mediaPath, Style.RESET_ALL)

    # Set output dir
    outputDir = Path(outputFolder).joinpath(Path(mediaPath).stem)

    # Set extract folder
    extractFolder = outputDir.joinpath('extract').as_posix()
    shutil.rmtree(extractFolder, ignore_errors = True) if Path(extractFolder).exists() else None
    os.makedirs(extractFolder, exist_ok = True)
    # Extract frames
    frameRate = extractFrames(mediaPath, extractFolder)

    # Set merge folder
    mergeFolder = outputDir.joinpath('merge').as_posix()
    shutil.rmtree(mergeFolder, ignore_errors = True) if Path(mergeFolder).exists() else None
    os.makedirs(mergeFolder, exist_ok = True)

    # Load models
    model1 = loadModel('b3', Path(modelDir).joinpath('effNet_b3_cls_flicker_best.pth'), class_names)
    #model1 = torch.jit.script(model1)
    model2 = loadModel('b1', Path(modelDir).joinpath('effNet_v2_b1_cls_flicker2pic_best.pth'), class_names_2pic)
    #model2 = torch.jit.script(model2)

    # Analyse frames
    analyseFrames(model1, model2, chkTypes, extractFolder, mergeFolder)

##############################################################################################################################