import threading
import os
import gc
import torch
import cv2
from ultralytics import YOLO
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
from datetime import datetime
from pathlib import Path

from .utils import *

##############################################################################################################################

predictResult = {}
def analyseFrame(
    frame: cv2.typing.MatLike,
    timeStamp: str,
    model_cls: str,
    model_clsBw: str,
    model_detect_splitScreen: str,
    chkTypes: list,
    outputFolder, subdir,
):
    global predictResult

    # 检查花屏
    lst_outputH:List[str] = []
    if 'bChkH' in chkTypes:
        # 分析当前帧
        result_class = model_cls(frame, verbose=False)[0]
        # 如果检测到异常（花屏），保存图像
        if result_class.probs.top1 == 0:
            file = save_image(timeStamp, frame, outputFolder, subdir)
            lst_outputH.append(file)
            print(Fore.RED, f"[花屏] 时间戳: {timeStamp}", Style.RESET_ALL)
        updateDict(
            Dict1 = predictResult,
            Dict2 = {'lst_outputH': [timeStamp]} #Dict2 = {'lst_outputH': lst_outputH}
        )

    # 检查黑白屏
    lst_outputB:List[str] = []
    lst_outputW:List[str] = []
    if 'bChkBW' in chkTypes:
        # 分析当前帧
        result_class = model_clsBw(frame, verbose=False)[0]
        # 如果检测到异常（黑白屏），保存图像
        if result_class.probs.top1 == 0:
            file = save_image(timeStamp, frame, outputFolder, subdir)
            lst_outputB.append(file)
            print(Fore.RED, f"[黑白屏] 时间戳: {timeStamp}", Style.RESET_ALL)
        elif result_class.probs.top1 == 2:
            # 由于特殊图像造成模型的判断问题,这里先用蒙特卡罗判断一下是否是白色
            isBlack = is_mostly_black(frame)
            if isBlack:
                file = save_image(timeStamp, frame, outputFolder, subdir)
                lst_outputB.append(file)
                print(Fore.RED, f"[黑屏] 时间戳: {timeStamp}", Style.RESET_ALL)
            else:
                file = save_image(timeStamp, frame, outputFolder, subdir)
                lst_outputW.append(file)
                print(Fore.RED, f"[白屏] 时间戳: {timeStamp}", Style.RESET_ALL)
        else:
            pass
        updateDict(
            Dict1 = predictResult,
            Dict2 = {'lst_outputB': [timeStamp], 'lst_outputW': [timeStamp]} #Dict2 = {'lst_outputB': lst_outputB, 'lst_outputW': lst_outputW}
        )

    # 分屏+检查黑白屏
    lst_outputSplitB:List[str] = []
    if 'bChkSplit_then_BW' in chkTypes:
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
                            file = save_image(timeStamp, frame, outputFolder, subdir)
                            lst_outputSplitB.append(file)
                            print(Fore.RED, f"[黑屏] 时间戳: {timeStamp}", Style.RESET_ALL)
                    else:
                        # 横向,从左到右分割,这时y和h是有用的
                        # cropped_img = frame[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
                        upper_img = frame[0:int(y), 0:width]
                        downer_img = frame[int(y):height, 0:width]
                        isBlack = is_mostly_black(upper_img) | is_mostly_black(downer_img)
                        if isBlack:
                            file = save_image(timeStamp, frame, outputFolder, subdir)
                            lst_outputSplitB.append(file)
                            print(Fore.RED, f"[黑屏] 时间戳: {timeStamp}", Style.RESET_ALL)
        updateDict(
            Dict1 = predictResult,
            Dict2 = {'lst_outputSplitB': [timeStamp]} #Dict2 = {'lst_outputSplitB': lst_outputSplitB}
        )

    # 无bar分屏+检查黑白屏
    lst_outputNobarSplitB:List[str] = []
    if 'bChkNobarSplit_then_BW' in chkTypes:
        if nobar_split_half_black(frame):
            file = save_image(timeStamp, frame, outputFolder, subdir)
            lst_outputNobarSplitB.append(file)
            print(Fore.RED, f"[黑屏] 时间戳: {timeStamp}", Style.RESET_ALL)
        updateDict(
            Dict1 = predictResult,
            Dict2 = {'lst_outputNobarSplitB': [timeStamp]} #Dict2 = {'lst_outputNobarSplitB': lst_outputNobarSplitB}
        )

    # 桌面来电底色
    lst_outputBlackback:List[str] = []
    if 'bChkBlackback' in chkTypes:
        if is_mostly_black(frame):
            file = save_image(timeStamp, frame, outputFolder, subdir)
            lst_outputBlackback.append(file)
            print(Fore.RED, f"[黑屏] 时间戳: {timeStamp}", Style.RESET_ALL)
        updateDict(
            Dict1 = predictResult,
            Dict2 = {'lst_outputBlackback': [timeStamp]} #Dict2 = {'lst_outputBlackback': lst_outputBlackback}
        )


class YOLOManager:
    """
    Manage yolo model
    """
    def __init__(self, model_path, task):
        self.model_path = model_path
        self.task = task

    def __enter__(self):
        self.model = YOLO(self.model_path, task = self.task)
        return self.model

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.model
        torch.cuda.empty_cache() if torch.cuda.is_available() else None
        gc.collect()


frameRate = 0
def predict(
    mediaPath: str,
    chkTypes: list,
    outputFolder: str,
    modelDir: str,
    stopEvent: Optional[threading.Event] = None
):
    """
    检测屏幕录像/图像
    Args:
        mediaPath (str): 录像/图像文件路径
        chkTypes (list): 检测类型
        outputFolder (str): 结果输出路径
        modelDir (str): 模型路径
        stopEvent (threading.Event): 结束信号
    """
    global predictResult, frameRate

    predictResult.clear()

    print(Fore.GREEN, 'analysis media', mediaPath, chkTypes, Style.RESET_ALL)

    # 加载视频流
    cap = cv2.VideoCapture(0 if mediaPath is None else mediaPath, cv2.CAP_FFMPEG)

    # Setup the YOLO models' paths
    model_cls_path = Path(modelDir).joinpath('models_cls_videoHua.pt').as_posix()
    model_clsBw_path = Path(modelDir).joinpath('modelm-cls_screen_w_rec_basic.pt').as_posix()
    model_detect_splitScreen_path = Path(modelDir).joinpath("model_splitScreen.pt").as_posix()
    # Load the YOLO models
    with YOLOManager(model_cls_path, 'classify') as model_cls, \
         YOLOManager(model_clsBw_path, 'classify') as model_clsBw, \
         YOLOManager(model_detect_splitScreen_path, 'classify') as model_detect_splitScreen:
        # 启动图像处理线程池
        executor = ThreadPoolExecutor(max_workers = None)
        threads = []
        while stopSignal(stopEvent) == False:
            # Start capturing frames
            ret, frame = cap.read()
            if not ret:
                break # Break the loop if there are no frames left to read
            # Get the timestamp of the frame
            timeStamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            # Start a new thread to process the frame
            thread = executor.submit(analyseFrame,
                frame,
                timeStamp,
                model_cls,
                model_clsBw,
                model_detect_splitScreen,
                chkTypes,
                outputFolder,
                datetime.now().strftime("%Y%m%d%H%M%S"),
            )
            threads.append(thread)
            # 当累积一定数量的任务后，等待它们完成并释放资源
            if len(threads) >= os.cpu_count()*2:
                for thread in threads:
                    thread.result()
                threads.clear()
                gc.collect()
        # Wait for all threads to complete
        for thread in threads:
            thread.result()
        executor.shutdown(wait = True)

    # 释放视频捕获对象
    cap.release()

##############################################################################################################################