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
def save_images(
    cap: cv2.VideoCapture,
    model_cls: str,
    model_clsBw: str,
    model_detect_splitScreen: str,
    bChkH: bool,
    bChkBW: bool,
    bChkSplit_then_BW: bool,
    bChkNobarSplit_then_BW: bool,
    bChkBlackback: bool,
    output_folder, subdir,
    stopEvent: threading.Event
):
    global Result

    # Initialize frame counter
    frame_count = 0
    # Start capturing frames
    while not stopEvent.is_set():
        ret, frame = cap.read()
        if not ret:
            break  # Break the loop if there are no frames left to read

        # 检查花屏
        lst_outputH:List[str] = []
        if bChkH:
            # 分析当前帧
            result_class = model_cls(frame, verbose=False)[0]
            # 如果检测到异常（花屏），保存图像
            if result_class.probs.top1 == 0:
                file = save_image(frame_count, frame, output_folder, subdir)
                lst_outputH.append(file)
            UpdateDict(
                Dict1 = Result,
                Dict2 = {'lst_outputH': lst_outputH}
            )

        # 检查黑白
        lst_outputB:List[str] = []
        lst_outputW:List[str] = []
        if bChkBW:
            # 分析当前帧
            result_class = model_clsBw(frame, verbose=False)[0]
            # 如果检测到异常（黑白），保存图像
            if result_class.probs.top1 == 0:
                file = save_image(frame_count, frame, output_folder, subdir)
                lst_outputB.append(file)
            elif result_class.probs.top1 == 2:
                # 由于特殊图像造成模型的判断问题,这里先用蒙特卡罗判断一下是否是白色
                isBlack = is_mostly_black(ret)
                if isBlack:
                    file = save_image(frame_count, frame, output_folder, subdir)
                    lst_outputB.append(file)
                else:
                    file = save_image(frame_count, frame, output_folder, subdir)
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
            height, width = frame.shape[:2]
            # 分析当前帧
            result_class = model_detect_splitScreen(frame, verbose=False)[0]
            # print(f'height: {height}, width: {width}')
            for n, r in enumerate(result_class):
                # print(r.boxes)  # print the Boxes object containing the detection bounding boxes
                for i, box in enumerate(r.boxes):
                    if box is not None:
                        cords = box.xywh[0].tolist()
                        conf = box.conf[0].item()
                        n_cords = [int(num) for num in cords] #convert float to int
                        # [2024-2-22]增加一段,对类型的判断
                        x,y,w,h = n_cords
                        # print(Fore.MAGENTA, f'box{i}: {n_cords}, conf: {conf}', Style.RESET_ALL)
                        # 注意下面LR和UD的判断,是分开写的.
                        if w < h:
                            # 竖向,从上到下分割
                            L_img = frame[0:height, 0:int(x)]
                            R_img = frame[0:height, int(x+w):width]
                            isBlack = is_mostly_black(L_img) | is_mostly_black(R_img)
                            if isBlack:
                                file = save_image(frame_count, frame, output_folder, subdir)
                                lst_outputSplitB.append(file)
                        else:
                            # 横向,从左到右分割,这时y和h是有用的
                            # cropped_img = frame[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
                            upper_img = frame[0:int(y), 0:width]
                            downer_img = frame[int(y):height, 0:width]
                            isBlack = is_mostly_black(upper_img) | is_mostly_black(downer_img)
                            if isBlack:
                                file = save_image(frame_count, frame, output_folder, subdir)
                                lst_outputSplitB.append(file)
            UpdateDict(
                Dict1 = Result,
                Dict2 = {'lst_outputSplitB': lst_outputSplitB}
            )

        # [2024-8-15]无bar分屏+检查黑白
        lst_outputNobarSplitB:List[str] = []
        if bChkNobarSplit_then_BW:
            if nobar_split_half_black(frame):
                file = save_image(frame_count, frame, output_folder, subdir)
                lst_outputNobarSplitB.append(file)
            UpdateDict(
                Dict1 = Result,
                Dict2 = {'lst_outputNobarSplitB': lst_outputNobarSplitB}
            )

        # [2024-8-15]桌面来电底色
        lst_outputBlackback:List[str] = []
        if bChkBlackback:
            if is_mostly_black(frame):
                file = save_image(frame_count, frame, output_folder, subdir)
                lst_outputBlackback.append(file)
            UpdateDict(
                Dict1 = Result,
                Dict2 = {'lst_outputBlackback':lst_outputBlackback}
            )

        frame_count += 1
        print(f'frame_count: {frame_count}')
    print('Result:', Result)


def videoAnalyser(
    video_path: str,
    bChkH: bool,
    bChkBW: bool,
    bChkSplit_then_BW: bool,
    bChkNobarSplit_then_BW: bool,
    bChkBlackback: bool,
    output_folder: str,
    ModelDir: str,
    toOnnx: bool,
    stopEvent: threading.Event
):
    global Result

    print(Fore.GREEN, 'analysis_video', Style.RESET_ALL)
    print(Fore.GREEN, 'analysis_video', video_path, bChkH, bChkBW, bChkSplit_then_BW, Style.RESET_ALL)

    # 设置输出文件夹
    subdir = Path(video_path).parent.stem
    #os.makedirs(os.path.join(output_folder, subdir), exist_ok=True)

    # 加载视频流
    cap = cv2.VideoCapture(0 if video_path is None else video_path)

    # Setup the YOLO models' paths
    model_cls_path = Path(ModelDir).joinpath('models_cls_videoHua.pt').as_posix()
    model_clsBw_path = Path(ModelDir).joinpath('modelm-cls_screen_w_rec_basic.pt').as_posix()
    model_detect_splitScreen_path = Path(ModelDir).joinpath("model_splitScreen.pt").as_posix()
    # Load the YOLO models
    model_cls = YOLO(model_cls_path)
    if toOnnx and not Path(f"{Path(model_cls_path).stem}.onnx").exists() and not stopEvent.is_set():
        model_cls = YOLO(model_cls.export(format="onnx", dynamic = True), task='detect')
    model_clsBw = YOLO(model_clsBw_path)
    if toOnnx and not Path(f"{Path(model_clsBw_path).stem}.onnx").exists() and not stopEvent.is_set():
        model_clsBw = YOLO(model_clsBw.export(format="onnx", dynamic = True), task='detect')
    model_detect_splitScreen = YOLO(model_detect_splitScreen_path) #[2024-8-6]model_splitScreen.pt
    if toOnnx and not Path(f"{Path(model_detect_splitScreen_path).stem}.onnx").exists() and not stopEvent.is_set():
        model_detect_splitScreen = YOLO(model_detect_splitScreen.export(format="onnx", dynamic = True), task='detect')

    # 启动图像处理线程
    thread = threading.Thread(
        target=save_images,
        args=(
            cap,
            model_cls,
            model_clsBw,
            model_detect_splitScreen,
            bChkH,
            bChkBW,
            bChkSplit_then_BW,
            bChkNobarSplit_then_BW,
            bChkBlackback,
            output_folder,
            subdir,
            stopEvent
        )
    )
    thread.start()
    thread.join()

    # 释放视频捕获对象
    cap.release()


adbRecord = None
StopRecordEvent = threading.Event()
StopAllEvent = threading.Event()
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
    toOnnx,
    RecPeriod: int = 180,
):
    global adbRecord
    global StopRecordEvent
    global StopAllEvent
    i = 0
    analysingThreads = []
    while not (StopRecordEvent.is_set() or StopAllEvent.is_set()) :
        try:
            adbRecord = Record(SavePath_AD, RecPeriod)
            adbRecord.wait()
            adbPull = Pull(SavePath_AD, SaveDir_PC)
            adbPull.wait()
            i += 1
            OldName = Path(SaveDir_PC).joinpath(Path(SavePath_AD).name).as_posix()
            NewName = Path(SaveDir_PC).joinpath(f"{i}{Path(SavePath_AD).suffix}").as_posix()
            if Path(OldName).exists():
                if Path(NewName).exists():
                    os.remove(NewName)
                os.rename(OldName, NewName)
        except Exception as e:
            print(f"RecordAndPull error: {e}")
        finally:
            if not Path(NewName).exists():
                continue
            analysingThread = threading.Thread(
                target = videoAnalyser,
                args = (NewName, bChkH, bChkBW, bChkSplit_then_BW, bChkNobarSplit_then_BW, bChkBlackback, output_folder, ModelDir, toOnnx, StopAllEvent)
            )
            analysingThreads.append(analysingThread)
            analysingThread.start()
    else:
        if not StopAllEvent.is_set():
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
    toOnnx: bool = False,
    RecPeriod: int = 180,
):
    global adbRecord
    global StopRecordEvent
    global StopAllEvent
    global Result

    # Set the save location
    SavePath_AD = "/sdcard/testcase.mp4"
    Path(SaveDir_PC).mkdir(parents = True) if not Path(SaveDir_PC).exists() else None

    # Reboot server
    adbReboot = Reboot()
    adbReboot.wait()

    # Start the screen recording thread
    recordingThread = threading.Thread(
        target = RecordAndPull,
        args = (SavePath_AD, SaveDir_PC, bChkH, bChkBW, bChkSplit_then_BW, bChkNobarSplit_then_BW, bChkBlackback, output_folder, ModelDir, toOnnx, RecPeriod)
    )
    recordingThread.start()

    # Execute the main task
    adbTask = subprocess.Popen(
        TaskCMD,
        shell = True
    )
    # Wait for the task to finish or for the stop event to be set
    while not StopAllEvent.is_set():
        if adbTask.poll() is not None:
            break
    else:
        adbTask.terminate()

    # Signal the recording thread to stop and wait for it to finish
    StopRecordEvent.set()
    if adbRecord is not None:
        adbRecord.terminate()
    recordingThread.join()

    return Result

##############################################################################################################################