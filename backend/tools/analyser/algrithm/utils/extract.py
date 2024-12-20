import torch
import torchvision
from torchvision import transforms
from pathlib import Path

##############################################################################################################################

def _extractFrames(
    mediaPath: str,
):
    if Path(mediaPath).suffix in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'):
        frameRate = 1
        timestamp = float(0)
        frameTensor = torchvision.io.read_image(mediaPath)
        yield timestamp, frameTensor, frameRate

    if Path(mediaPath).suffix in ('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'):
        # Read stream from video file (frame by frame)
        reader = torchvision.io.VideoReader(mediaPath, stream = "video")
        metaData = reader.get_metadata()
        frameRate = metaData.get('video')['fps'][0]
        # Get metadata to determine rotation
        rotation_degrees = metaData.get('rotation', 0)
        # Calculate number of 90 degree rotations needed
        k = (rotation_degrees // 90) % 4
        # Save viedo frames to outputFolder as JPEG images
        for frame in reader:
            timestamp = float(frame['pts'])
            frameTensor = torch.rot90(frame['data'], k = k, dims = [1, 2]) if k > 0 else frame['data'] # Rotate based on metadata rotation value
            yield timestamp, frameTensor, frameRate


def extractFrames(
    mediaPath: str,
):
    frameTensors = {}
    frameRate = None
    for timestamp, frameTensor, frameRate in _extractFrames(mediaPath):
        frameTensors[timestamp] = frameTensor
        frameRate = frameRate
    return frameTensors, frameRate

##############################################################################################################################