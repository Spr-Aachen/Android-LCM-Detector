import threading
import os
import shutil
import torch
import torch.nn as nn
from torchvision import transforms, models
import torchvision
from ultralytics import YOLO
from typing import List, Dict, Union, Optional
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


def merge_and_predict_flicker(model_classify2, file1, file2, outputFolder, mergeFolder, i)->str:
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
    return predict2_image_str_tv_io(model_classify2, Path(mergeFolder).joinpath(f"{i:04d}_{i+1:04d}.jpg").as_posix())


# [2024-12-09] 使用yolo的detect模型, 得到floatWindow的坐标, 输入图片, 输出floatWindow的坐标
def detect_floatWin(model: YOLO, picPath: str) -> Union[bool, None]:
    results = model(picPath, verbose = False, conf = 0.7)[0] #save=True, 
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
    img = cv2.imread(picPath)
    float_win = img[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
    # 
    num_samples = 500 # Monte Carlo sampling - randomly sample points
    height_fw, width_fw = float_win.shape[:2]
    
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


predictResult = {}
def analyseFrames(model_classify1, model_classify2, model_detectFloatWin, timestamps, chkTypes, outputFolder, mergeFolder):
    global predictResult

    lst_pic = [pic for pic in getFiles(outputFolder, ('.jpg', '.png'))]

    # [2024-12-08] 这里比较郁闷,因为以前产生的目录不能用了,要补充timestamp信息
    # 测试发现,类型0的图片,black_white_etc, 需要判断是否连续的type4.floatWin
    # 因此,需要补充timestamp信息
    lst_f_timestamp = [float(str_timestamp) for str_timestamp in timestamps]

    lst_all_type = []
    lst_flick_idxType: list[tuple[int, int]] = [] # 保存idx和type
    for i, pic in enumerate(lst_pic):
        class_num_1 = predict1_image_num_tv_io(model_classify1, pic.as_posix())
        lst_flick_idxType.append((i, class_num_1))
        lst_all_type.append(class_num_1)
    print(Fore.GREEN, f'lst_all_type: {lst_all_type}', Fore.RESET)

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
            print(Fore.RED, 'in 5.hua:', lst_output_glich, Fore.RESET)
            b_found_err_before = True
        '''
        lst_output_glich = []
        for i, type in enumerate(lst_all_type):
            if type == 5:
                lst_output_glich.append(i)
        if len(lst_output_glich) > 0:
            print(Fore.RED, f'[model_classify1] 5.hua: {lst_output_glich}', Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_glich': lst_output_glich}
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
                    is_black_white = detect_floatWin(model_detectFloatWin, Path(outputFolder).joinpath(lst_pic[i]).as_posix())
                    if is_black_white is not None:
                        if is_black_white:
                            lst_output_flick_0.append(i)
        if len(lst_output_flick_0) > 0:
            print(Fore.RED, f'[model_detectFloatWin] 0.Black&White: {lst_output_flick_0}', Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick_0}
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
                    # 或者考虑if lst_f_timestamp[i-count_type4_before+1] - lst_f_timestamp[i] > 0.7:
                    diff_tm = lst_f_timestamp[i]-lst_f_timestamp[i-count_type4_before] 
                    if diff_tm > 0.7:
                        #print(Fore.RED, f"Type4 indices: {list(range(i-count_type4_before, i))}", Fore.RESET)
                        lst_output_flick_4.append(i)
                    else:
                        print(Fore.GREEN, f"after{count_type0_after} type0 {count_type4_before} type4, diff_tm:{diff_tm}", Fore.RESET)
                else:
                    #print(Fore.RED, f"range {i},{j}: Found type0", Fore.RESET)
                    lst_output_flick_0.extend([num for num in range(i, j+1)])

                # Skip past the consecutive type 0s we found
                i = i + count_type0_after + 1
            else:
                i += 1
        if len(lst_output_flick_4) > 0:
            print(Fore.RED, f'[model_classify1] 4.floatWin: {lst_output_flick_4}', Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick_4}
            )
        if len(lst_output_flick_0) > 0:
            print(Fore.RED, f'[model_classify1] 0.Black&White: {lst_output_flick_0}', Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick_0}
            )

        # [2024-11-25] 测试发现,类型3的图片,desktop_black_half_etc
        lst_output_flick_3 = []
        for i, type in enumerate(lst_all_type):
            if type == 3:
                lst_output_flick_3.append(i)
        if len(lst_output_flick_3) > 0:
            print(Fore.RED, f'[model_classify1] 3.desktop_black_half_etc: {lst_output_flick_3}', Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick_3}
            )

        # 'camOn', #2
        # Find sequences of consecutive 'camOn' frames
        lst_tup_seq_camOn = find_cons_seq(lst_all_type, target=2, min_length=3)
        #lst_tup_seq_camOn = find_cons_seq(lst_all_type, target=2, min_length=3)
        lst_output_flick_4 = []
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

            # 对下一个range之间的其他类型,进行检测
            if i+1 < len(lst_tup_seq_floatWin):
                next_start, next_end = lst_tup_seq_floatWin[i+1]
                #next_type = lst_all_type[next_end]
                # 对下一个range之间的其他图像(是否要考虑类型问题),进行检测
                for j in range(end+skip+1, next_start):
                    file1 = f"{j:04d}.jpg"
                    file2 = f"{j+1:04d}.jpg"
                    flick_type = merge_and_predict_flicker(model_classify2, file1, file2, outputFolder, mergeFolder, j)
                    if flick_type == 'Y':
                        #print(Fore.RED, 'in 2 floatWin range:', f"{j:04d}_{j+1:04d}.jpg: {flick_type}", Fore.RESET)
                        lst_output_flick_4.extend([j, j+1])
        if len(lst_output_flick_4) > 0:
            print(Fore.RED, f'[model_classify2] 4.floatWin: {lst_output_flick_4}', Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick_4}
            )

        # 在floatWin的序列中,合并图片,并预测,主要是procVw中的窗口显示问题
        lst_output_flick_4 = []
        for start, end in lst_tup_seq_floatWin:
            for i in range(start, end):
                file1 = f"{i:04d}.jpg"
                file2 = f"{i+1:04d}.jpg"
                flick_type = merge_and_predict_flicker(model_classify2, file1, file2, outputFolder, mergeFolder, i)
                if flick_type == 'Y':
                    #print(Fore.RED, 'floatWin flicker:', f"{i:04d}_{i+1:04d}.jpg: {flick_type}", Fore.RESET)
                    lst_output_flick_4.extend([i, i+1])
        if len(lst_output_flick_4) > 0:
            print(Fore.RED, f'[model_classify2] 4.floatWin: {lst_output_flick_4}', Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick_4}
            )

        # 遍历每个序列camOn
        lst_output_flick_2 = []
        for start, end in lst_tup_seq_camOn:
            for i in range(start, end):
                file1 = f"{i:04d}.jpg"
                file2 = f"{i+1:04d}.jpg"
                flick_type = merge_and_predict_flicker(model_classify2, file1, file2, outputFolder, mergeFolder, i)
                if flick_type == 'Y':
                    #print(Fore.RED, f"{i:04d}_{i+1:04d}.jpg: {flick_type}", Fore.RESET)
                    lst_output_flick_2.extend([i, i+1])
        if len(lst_output_flick_2) > 0:
            print(Fore.RED, f'[model_classify2] 2.camOn: {lst_output_flick_2}', Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick_2}
            )

        # NOTE:有camOn但没有问题,所以要检测其他类型,因此,这里if判断要拿掉
        # if len(lst_tup_seq_camOn) == 0 and len(lst_tup_seq_floatWin) == 0:
        print(Fore.RED + 'No camOn2/floatWin4 found,check 6.other type', Fore.RESET)
        # 没有找到camOn2/floatWin4,则需要考虑其他类型
        # 例如883_Screen_Recording_20240507_111135,(notebook)fixed:现在全是类型6
        # 这里有类型判断问题,需要考虑增加训练数据,other里面数据还是太少
        # lst_all_type
        # 假设这里对6进行全量检测
        lst_output_flick_6 = []
        if b_found_err_before == False:
            lst_tup_seq_other = find_cons_seq(lst_all_type, target=6, min_length=3)
            print(Fore.GREEN + f"6.other range count: {len(lst_tup_seq_other)}" + Fore.RESET)
            for start, end in lst_tup_seq_other:
                print(Fore.GREEN + f"6.other frames {start:04d} to {end:04d}" + Fore.RESET)
                for i in range(start, end):
                    file1 = f"{i:04d}.jpg"
                    file2 = f"{i+1:04d}.jpg"
                    flick_type = merge_and_predict_flicker(model_classify2, file1, file2, outputFolder, mergeFolder, i)
                    if flick_type == 'Y':
                        #print(Fore.RED, f"{i:04d}_{i+1:04d}.jpg: {flick_type}", Fore.RESET)
                        lst_output_flick_6.extend([i, i+1])
        if len(lst_output_flick_6) > 0:
            print(Fore.RED, f'[model_classify2] 6.other: {lst_output_flick_6}', Fore.RESET)
            b_found_err_before = True
            updateDict(
                Dict1 = predictResult,
                Dict2 = {'lst_output_flick': lst_output_flick_6}
            )

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
    timestamps, frameRate = extractFrames(mediaPath, extractFolder)

    # Set merge folder
    mergeFolder = outputDir.joinpath('merge').as_posix()
    shutil.rmtree(mergeFolder, ignore_errors = True) if Path(mergeFolder).exists() else None
    os.makedirs(mergeFolder, exist_ok = True)

    # Load models
    model_classify1 = loadModel('b3', Path(modelDir).joinpath('effNet_b3_cls_flicker_best.pth'), class_names)
    #model_classify1 = torch.jit.script(model_classify1)
    model_classify2 = loadModel('b1', Path(modelDir).joinpath('effNet_v2_b1_cls_flicker2pic_best.pth'), class_names_2pic)
    #model_classify2 = torch.jit.script(model_classify2)
    model_detectFloatWin = YOLO(Path(modelDir).joinpath('effNet_v2_b1_cls_flicker2pic_best.pth').as_posix())

    # Analyse frames
    analyseFrames(model_classify1, model_classify2, model_detectFloatWin, timestamps, chkTypes, extractFolder, mergeFolder)

##############################################################################################################################