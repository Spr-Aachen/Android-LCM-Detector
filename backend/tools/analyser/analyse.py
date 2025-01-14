import threading
from typing import Optional

from .algrithm import ExtractType

##############################################################################################################################

class analyserVersion:
    V1 = 0
    V2 = 1


result = {}
def mediaAnalyse(
    mediaPath: str,
    chkTypes: list,
    outputFolder: str,
    modelDir: str,
    camCrop: bool = False,
    extractType: ExtractType = ExtractType.TENSOR,
    stopEvent: Optional[threading.Event] = None,
    version: analyserVersion = analyserVersion.V2
):
    """
    检测屏幕录像/图像
    Args:
        mediaPath (str): 录像/图像文件路径
        chkTypes (list): 检测类型
        outputFolder (str): 结果输出路径
        modelDir (str): 模型路径
        camCrop (bool): 是否启用录像边缘裁剪
        extractType (ExtractType): 视频帧提取方案
    """
    global result

    result.clear()

    if version == analyserVersion.V1:
        from .algrithm import predict1 as predict
    if version == analyserVersion.V2:
        from .algrithm import predict2 as predict

    predict.predict(mediaPath, chkTypes, outputFolder, modelDir, camCrop, extractType, stopEvent)
    result.update(predict.predictResult)
    return result

##############################################################################################################################