import threading
import cv2
from ultralytics import YOLO
from typing import List, Dict, Optional
from colorama import Fore, Style

from .utils import *

##############################################################################################################################

result = {}
def save_images(
    cap: cv2.VideoCapture,
    model_cls: str,
    model_clsBw: str,
    model_detect_splitScreen: str,
    chkTypes: list,
    outputFolder, subdir,
    stopEvent: Optional[threading.Event]
):
    global result

    # Initialize frame counter
    frame_count = 0
    # Start capturing frames
    while not (stopEvent is None or stopEvent.is_set()):
        ret, frame = cap.read()
        if not ret:
            break  # Break the loop if there are no frames left to read

        timeStamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

        # 检查花屏
        lst_outputH:List[str] = []
        if 'bChkH' in chkTypes:
            # 分析当前帧
            result_class = model_cls(frame, verbose=False)[0]
            # 如果检测到异常（花屏），保存图像
            if result_class.probs.top1 == 0:
                file = save_image(frame_count, frame, outputFolder, subdir)
                lst_outputH.append(file)
            UpdateDict(
                Dict1 = result,
                Dict2 = {'lst_outputH': [timeStamp]} #Dict2 = {'lst_outputH': lst_outputH}
            )

        # 检查黑白
        lst_outputB:List[str] = []
        lst_outputW:List[str] = []
        if 'bChkBW' in chkTypes:
            # 分析当前帧
            result_class = model_clsBw(frame, verbose=False)[0]
            # 如果检测到异常（黑白），保存图像
            if result_class.probs.top1 == 0:
                file = save_image(frame_count, frame, outputFolder, subdir)
                lst_outputB.append(file)
            elif result_class.probs.top1 == 2:
                # 由于特殊图像造成模型的判断问题,这里先用蒙特卡罗判断一下是否是白色
                isBlack = is_mostly_black(ret)
                if isBlack:
                    file = save_image(frame_count, frame, outputFolder, subdir)
                    lst_outputB.append(file)
                else:
                    file = save_image(frame_count, frame, outputFolder, subdir)
                    lst_outputW.append(file)
            else:
                pass
            UpdateDict(
                Dict1 = result,
                Dict2 = {'lst_outputB': [timeStamp], 'lst_outputW': [timeStamp]} #Dict2 = {'lst_outputB': lst_outputB, 'lst_outputW': lst_outputW}
            )

        # 分屏+检查黑白
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
                                file = save_image(frame_count, frame, outputFolder, subdir)
                                lst_outputSplitB.append(file)
                        else:
                            # 横向,从左到右分割,这时y和h是有用的
                            # cropped_img = frame[int(y-h/2):int(y+h/2), int(x-w/2):int(x+w/2)]
                            upper_img = frame[0:int(y), 0:width]
                            downer_img = frame[int(y):height, 0:width]
                            isBlack = is_mostly_black(upper_img) | is_mostly_black(downer_img)
                            if isBlack:
                                file = save_image(frame_count, frame, outputFolder, subdir)
                                lst_outputSplitB.append(file)
            UpdateDict(
                Dict1 = result,
                Dict2 = {'lst_outputSplitB': [timeStamp]} #Dict2 = {'lst_outputSplitB': lst_outputSplitB}
            )

        # 无bar分屏+检查黑白
        lst_outputNobarSplitB:List[str] = []
        if 'bChkNobarSplit_then_BW' in chkTypes:
            if nobar_split_half_black(frame):
                file = save_image(frame_count, frame, outputFolder, subdir)
                lst_outputNobarSplitB.append(file)
            UpdateDict(
                Dict1 = result,
                Dict2 = {'lst_outputNobarSplitB': [timeStamp]} #Dict2 = {'lst_outputNobarSplitB': lst_outputNobarSplitB}
            )

        # 桌面来电底色
        lst_outputBlackback:List[str] = []
        if 'bChkBlackback' in chkTypes:
            if is_mostly_black(frame):
                file = save_image(frame_count, frame, outputFolder, subdir)
                lst_outputBlackback.append(file)
            UpdateDict(
                Dict1 = result,
                Dict2 = {'lst_outputBlackback': [timeStamp]} #Dict2 = {'lst_outputBlackback': lst_outputBlackback}
            )

        frame_count += 1
        print(f'frame_count: {frame_count}')
    print('result:', result)


def videoAnalyser(
    videoPath: str,
    chkTypes: list,
    outputFolder: str,
    modelDir: str,
    toOnnx: bool,
    stopEvent: Optional[threading.Event] = None
):
    """
    检测屏幕录像
    Args:
        videoPath (str): 录像文件路径
        chkTypes (list): 检测类型
        outputFolder (str): 结果输出路径
        modelDir (str): 模型路径
        toOnnx (bool): 是否转换为onnx格式
        stopEvent (threading.Event): 结束信号
    """
    global result

    print(Fore.GREEN, 'analysis_video', Style.RESET_ALL)
    print(Fore.GREEN, 'analysis_video', videoPath, chkTypes, Style.RESET_ALL)

    # 设置输出文件夹
    subdir = Path(videoPath).parent.stem

    # 加载视频流
    cap = cv2.VideoCapture(0 if videoPath is None else videoPath)

    # Setup the YOLO models' paths
    model_cls_path = Path(modelDir).joinpath('models_cls_videoHua.pt').as_posix()
    model_clsBw_path = Path(modelDir).joinpath('modelm-cls_screen_w_rec_basic.pt').as_posix()
    model_detect_splitScreen_path = Path(modelDir).joinpath("model_splitScreen.pt").as_posix()
    # Load the YOLO models
    model_cls = YOLO(model_cls_path)
    if toOnnx and not Path(f"{Path(model_cls_path).stem}.onnx").exists() and not stopEvent.is_set():
        model_cls = YOLO(model_cls.export(format = "onnx", dynamic = True), task = 'detect')
    model_clsBw = YOLO(model_clsBw_path)
    if toOnnx and not Path(f"{Path(model_clsBw_path).stem}.onnx").exists() and not stopEvent.is_set():
        model_clsBw = YOLO(model_clsBw.export(format = "onnx", dynamic = True), task = 'detect')
    model_detect_splitScreen = YOLO(model_detect_splitScreen_path)
    if toOnnx and not Path(f"{Path(model_detect_splitScreen_path).stem}.onnx").exists() and not stopEvent.is_set():
        model_detect_splitScreen = YOLO(model_detect_splitScreen.export(format = "onnx", dynamic = True), task = 'detect')

    # 启动图像处理线程
    thread = threading.Thread(
        target = save_images,
        args = (
            cap,
            model_cls,
            model_clsBw,
            model_detect_splitScreen,
            chkTypes,
            outputFolder,
            subdir,
            stopEvent
        )
    )
    thread.start()
    thread.join()

    # 释放视频捕获对象
    cap.release()

##############################################################################################################################