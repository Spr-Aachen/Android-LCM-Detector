import psutil
import shutil
import cv2
import torch
import torchvision
from ultralytics import YOLO
from pathlib import Path
from typing import Union, Optional

##############################################################################################################################

def detectRect(model: YOLO, imageTensor: torch.Tensor):
    img = imageTensor.permute(1, 2, 0).cpu().numpy().astype('uint8')[:, :, ::-1]

    height, width = img.shape[:2]
    print(f'height: {height}, width: {width}')

    results = model.predict(img, save = True)

    if results is not None:
        print('yolo results[0].boxes.xyxy = %s' % results.boxes.xyxy)
        boxes = results[0].boxes.xyxy.cpu().numpy() # Get bounding box coordinates from YOLO results
        try:
            x1, y1, x2, y2 = map(int, boxes[0]) #只取第一个box
        except:
            x1, y1, x2, y2 = 0, 0, width, height

    return x1, y1, x2, y2

##############################################################################################################################

def saveImage(
    timeStamp: str,
    frame: Union[torch.Tensor, cv2.typing.MatLike],
    outputFolder: str,
    subdirName: Optional[str] = None,
    quality: int = 90
):
    formatted_n = f"{timeStamp:04}"
    outputPath = Path(outputFolder).joinpath(subdirName if subdirName is not None else "", f"{formatted_n}.jpeg")
    outputPath.parent.mkdir(parents = True, exist_ok = True)
    if isinstance(frame, torch.Tensor):
        torchvision.io.write_jpeg(frame.cpu(), filename = outputPath, quality = quality)
    if isinstance(frame, cv2.typing.MatLike):
        cv2.imencode(Path(outputPath).suffix, img = frame, params = [cv2.IMWRITE_WEBP_QUALITY, quality])[1].tofile(outputPath)
    return outputPath

##############################################################################################################################

def resizeTensor(
    tensor: torch.Tensor,
    scaleFactor: float = 0.5,
    desiredSize: tuple[int, int] = (640, 640)
):
    # Check if frame size is too large
    if tensor.shape[1] > (desiredSize[0] / scaleFactor) or tensor.shape[2] > (desiredSize[1] / scaleFactor):
        # Resize frame
        return torchvision.transforms.Resize(
            size = (
                int(tensor.shape[1] * scaleFactor),
                int(tensor.shape[2] * scaleFactor)
            )
        )(tensor)

##############################################################################################################################

class ExtractType:
    TENSOR = 0
    PATH = 1


def extractFrames(
    mediaPath: str,
    camCropModel: Optional[YOLO] = None,
    type: ExtractType = ExtractType.TENSOR,
    outputDir: Optional[str] = None,
):
    isCamCropped = False
    x1, y1, x2, y2 = 0, 0, 0, 0

    if Path(mediaPath).suffix in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'):
        #frameRate = 1
        timestamp = float(0)
        if type == ExtractType.TENSOR:
            frameTensor = torchvision.io.read_image(mediaPath)
            returnValue = resizeTensor(frameTensor) # Downscale frameTensor
        if type == ExtractType.PATH:
            shutil.copy(mediaPath, outputDir)
            returnValue = Path(outputDir).joinpath(Path(mediaPath).name).as_posix()
        yield timestamp, returnValue#, frameRate

    if Path(mediaPath).suffix in ('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'):
        reader = torchvision.io.VideoReader(mediaPath, stream = "video")
        firstFrame = next(reader) # Skip first frame
        try:
            metaData = reader.get_metadata()
        except:
            print("Info: Could not read metadata from video file, using calculations instead.")
            # Calculate frame rate through frame timestamps
            #frameRate = 1 / (next(reader)['pts'] - firstFrame['pts'])
            isFrameVertical = firstFrame['data'].shape[1] > firstFrame['data'].shape[2]
            rotationDegrees = 0 if isFrameVertical else 90
        else:
            #frameRate = metaData.get('video')['fps'][0]
            rotationDegrees = metaData.get('rotation', 0)
        finally:
            del firstFrame
            k = (rotationDegrees // 90) % 4 # Calculate number of 90 degree rotations needed
        # Read stream from video file (frame by frame)
        for frameCount, frame in enumerate(reader):
            timestamp = float(frame['pts'])
            frameTensor = frame['data']
            # Detect crop rect
            if camCropModel is not None and not isCamCropped:
                k = 270 // 90
                x1, y1, x2, y2 = detectRect(camCropModel, frameTensor)
                isCamCropped = True
            if isCamCropped:
                frameTensor = frameTensor[:, y1:y2, x1:x2] # Crop frame
                saveImage(timestamp, frameTensor, outputDir, 'cropped') if frameCount == 0 else None # Save cropped image (only first frame)
            # Rotate based on rotation value
            frameTensor = torch.rot90(frameTensor, k, dims = [1, 2]) if k > 0 else frameTensor
            # Downscale frame or save to disk
            if type == ExtractType.TENSOR:
                returnValue = resizeTensor(frameTensor) # Downscale frameTensor
            if type == ExtractType.PATH:
                outputPath = saveImage(timestamp, frameTensor, outputDir) # Save frame to disk
                returnValue = outputPath
            yield timestamp, returnValue#, frameRate

##############################################################################################################################