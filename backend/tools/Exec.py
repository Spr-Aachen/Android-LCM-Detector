import subprocess
import threading
import os
import sys
import shutil
import cv2
from ultralytics import YOLO
from pathlib import Path
from typing import List, Tuple, Dict
from colorama import Fore, Style

from utils.cv import *
from utils.adb import *

##############################################################################################################################

# Get current directory
CurrentDir = sys.path[0]

##############################################################################################################################

def UpdateDict(Dict1, Dict2):
    for key, value in Dict2.items():
        if key in Dict1:
            Dict1[key] += value
        else:
            Dict1[key] = value
    return Dict1


Result = {}
def videoAnalyser(
    video_path: str,
    bChkH: bool,
    bChkBW: bool,
    bChkSplit_then_BW: bool,
    bChkNobarSplit_then_BW: bool,
    bChkBlackback: bool,
    output_folder: str,
    ModelDir: str
):
    global Result

    print(Fore.GREEN, 'analysis_video', Style.RESET_ALL)

    print(Fore.GREEN, 'analysis_video', video_path, bChkH, bChkBW, bChkSplit_then_BW, Style.RESET_ALL)

    # 展开得到frame
    subdir = os.path.basename(video_path).split('.')[0]
    extract_frames(video_path, output_folder, subdir)

    # 检查花屏
    lst_file = os.listdir(Path(output_folder).joinpath(subdir).as_posix())
    # lst_mapH = {0:'hua',1:'off',2:'onGood'}
    lst_outputH:List[str] = []
    if bChkH:
        model_clsHua = YOLO(Path(ModelDir).joinpath('models_cls_videoHua.pt').as_posix())
        for file in lst_file:
            result_class = model_clsHua(Path(output_folder).joinpath(subdir, file).as_posix(), verbose=False)[0]
            # print(file, result_class.probs.top1)
            if result_class.probs.top1 == 0:
                lst_outputH.append(file)
            else:
                pass
        UpdateDict(
            Dict1 = Result,
            Dict2 = {'lst_outputH': lst_outputH}
        )

    # 检查黑白
    # lst_mapBW = {0:'black',1:'good',2:'white'}
    lst_outputB:List[str] = []
    lst_outputW:List[str] = []
    if bChkBW:
        model_clsBw = YOLO(Path(ModelDir).joinpath('modelm-cls_screen_w_rec_basic.pt').as_posix())
        for file in lst_file:
            result_class = model_clsBw(Path(output_folder).joinpath(subdir, file).as_posix(), verbose=False)[0]
            if result_class.probs.top1 == 0:
                lst_outputB.append(file)
            elif result_class.probs.top1 == 2:
                # 由于特殊图像造成模型的判断问题,这里先用蒙特卡罗判断一下是否是白色
                isBlack = is_mostly_black(Path(output_folder).joinpath(subdir, file))
                if isBlack:
                    lst_outputB.append(file)
                else:
                    lst_outputW.append(file)
            else:
                pass
        UpdateDict(
            Dict1 = Result,
            Dict2 = {'lst_outputB': lst_outputB, 'lst_outputW': lst_outputW}
        )

    # 分屏+检查黑白
    lst_outputSplitB:List[str] = []
    # lst_outputSplitW:List[str] = [] # 暂不考虑
    if bChkSplit_then_BW:
        # 这里需要对frame进行分割，然后对分割后的图像进行白色判断
        model_detect_splitScreen = YOLO(Path(ModelDir).joinpath("model_splitScreen.pt").as_posix()) #[2024-8-6]model_splitScreen.pt
        for file in lst_file:
            path_pic = Path(output_folder).joinpath(subdir, file).as_posix()
            dir_splitTmp = Path(CurrentDir).joinpath('tmp/clsW_split_train_pred/test_output').as_posix()
            #
            shutil.rmtree(dir_splitTmp, ignore_errors=True)
            os.makedirs(dir_splitTmp, exist_ok=True)

            img = cv2.imread(path_pic)
            height, width = img.shape[:2]
            # print(f'height: {height}, width: {width}')
            #
            results = model_detect_splitScreen(path_pic, verbose=False)[0] #, save=True
            for n, r in enumerate(results):
                # print(r.boxes)  # print the Boxes object containing the detection bounding boxes
                for i, box in enumerate(r.boxes):
                    if box is not None:
                        cords = box.xywh[0].tolist()
                        conf = box.conf[0].item()
                        n_cords = [int(num) for num in cords] #convert float to int
                        # [2024-2-22]增加一段,对类型的判断
                        x,y,w,h = n_cords
                        # print(Fore.MAGENTA, f'box{i}: {n_cords}, conf: {conf}', Style.RESET_ALL)
                        # 注意下面LR和UD的判断,是分开写的.但如果保存成一样的文件名,其实可以合并
                        if w < h:
                            # 竖向,从上到下分割
                            L_img = img[0:height, 0:int(x)]
                            R_img = img[0:height, int(x+w):width]
                            cv2.imwrite(Path(dir_splitTmp).joinpath(f'det_r{n}_{i}_L.jpg').as_posix(),L_img)
                            cv2.imwrite(Path(dir_splitTmp).joinpath(f'det_r{n}_{i}_R.jpg').as_posix(),R_img)
                            isBlack = is_mostly_black(Path(dir_splitTmp).joinpath(f'det_r{n}_{i}_L.jpg').as_posix()) | is_mostly_black(Path(dir_splitTmp).joinpath(f'det_r{n}_{i}_R.jpg').as_posix())
                            if isBlack:
                                lst_outputSplitB.append(file)
                        else:
                            # 横向,从左到右分割,这时y和h是有用的
                            # cropped_img = img[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
                            #
                            upper_img = img[0:int(y), 0:width]
                            downer_img = img[int(y):height, 0:width]
                            # U_img = img[0:height, 0:x]
                            # D_img = img[0:height, x+w:width]
                            cv2.imwrite(Path(dir_splitTmp).joinpath(f'det_r{n}_{i}_upper.jpg').as_posix(), upper_img)
                            cv2.imwrite(Path(dir_splitTmp).joinpath(f'det_r{n}_{i}_downer.jpg').as_posix(), downer_img)
                            isBlack = is_mostly_black(Path(dir_splitTmp).joinpath(f'det_r{n}_{i}_upper.jpg').as_posix()) | is_mostly_black(Path(dir_splitTmp).joinpath(f'det_r{n}_{i}_downer.jpg').as_posix())
                            if isBlack:
                                lst_outputSplitB.append(file)
        UpdateDict(
            Dict1 = Result,
            Dict2 = {'lst_outputSplitB': lst_outputSplitB}
        )

    # [2024-8-15]无bar分屏+检查黑白
    lst_outputNobarSplitB:List[str] = []
    if bChkNobarSplit_then_BW:
        for file in lst_file:
            if nobar_split_half_black(Path(output_folder).joinpath(subdir, file).as_posix()):
                lst_outputNobarSplitB.append(file)
        UpdateDict(
            Dict1 = Result,
            Dict2 = {'lst_outputNobarSplitB': lst_outputNobarSplitB}
        )

    # [2024-8-15]桌面来电底色
    lst_outputBlackback:List[str] = []
    if bChkBlackback:
        for file in lst_file:
            if is_mostly_black(Path(output_folder).joinpath(subdir, file).as_posix()):
                lst_outputBlackback.append(file)
        UpdateDict(
            Dict1 = Result,
            Dict2 = {'lst_outputBlackback':lst_outputBlackback}
        )


adbRecord = None
StopEvent = None
def RecordAndPull(
    SavePath_AD: str,
    SaveDir_PC: str,
    bChkH,
    bChkBW,
    bChkSplit_then_BW,
    bChkNobarSplit_then_BW,
    bChkBlackback,
    output_folder,
    ModelDir,
    RecPeriod: int = 180,
):
    global adbRecord
    global StopEvent
    i = 0
    analysingThreads = []
    while not StopEvent.is_set():
        try:
            adbRecord = Record(SavePath_AD, RecPeriod)
            adbRecord.wait()
            adbPull = Pull(SavePath_AD, SaveDir_PC)
            adbPull.wait()
            i += 1
            OldName = Path(SaveDir_PC).joinpath(Path(SavePath_AD).name).as_posix()
            NewName = Path(SaveDir_PC).joinpath(f"{i}{Path(SavePath_AD).suffix}").as_posix()
            if Path(NewName).exists():
                os.remove(NewName)
            os.rename(OldName, NewName)
        except Exception as e:
            print(f"RecordAndPull error: {e}")
        finally:
            analysingThread = threading.Thread(
                target = videoAnalyser,
                args = (NewName, bChkH, bChkBW, bChkSplit_then_BW, bChkNobarSplit_then_BW, bChkBlackback, output_folder, ModelDir)
            )
            analysingThreads.append(analysingThread)
            analysingThread.start()
    else:
        for analysingThread in analysingThreads:
            try:
                analysingThread.join()
            except:
                pass


def Exec(
    TaskCMD,
    SaveDir_PC,
    bChkH,
    bChkBW,
    bChkSplit_then_BW,
    bChkNobarSplit_then_BW,
    bChkBlackback,
    output_folder,
    ModelDir,
    RecPeriod: int = 180,
):
    global adbRecord
    global StopEvent
    global Result

    # Set the save location
    SavePath_AD = "/sdcard/testcase.mp4"
    Path(SaveDir_PC).mkdir(parents = True) if not Path(SaveDir_PC).exists() else None

    # Reboot server
    adbReboot = Reboot()
    adbReboot.wait()

    # Event to signal the recording thread to stop
    StopEvent = threading.Event()

    # Start the screen recording thread
    recordingThread = threading.Thread(
        target = RecordAndPull,
        args = (SavePath_AD, SaveDir_PC, bChkH, bChkBW, bChkSplit_then_BW, bChkNobarSplit_then_BW, bChkBlackback, output_folder, ModelDir, RecPeriod)
    )
    recordingThread.start()

    # Execute the main task
    adbTask = subprocess.Popen(
        TaskCMD,
        shell = True
    )
    adbTask.wait()

    # Signal the recording thread to stop and wait for it to finish
    StopEvent.set()
    if adbRecord is not None:
        adbRecord.terminate()
    recordingThread.join()

    return Result

##############################################################################################################################