import shutil
import torch
import torchvision
from tqdm import tqdm
from pathlib import Path

##############################################################################################################################

def extractFrames(mediaPath: str, outputFolder: str) -> None:
    if Path(mediaPath).suffix in ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'):
        shutil.copy(mediaPath, outputFolder)
        frameCount = 1

    if Path(mediaPath).suffix in ('.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'):
        # Read stream from video file (frame by frame)
        reader = torchvision.io.VideoReader(mediaPath, stream = "video")
        # Get metadata to determine rotation
        rotation_degrees = reader.get_metadata().get('rotation', 0)
        # Calculate number of 90 degree rotations needed
        k = (rotation_degrees // 90) % 4

        frame = next(reader)

        # Save viedo frames to outputFolder as JPEG images
        frameCount = 0
        timestamps = []
        for frame in tqdm(reader):
            rotFrame = torch.rot90(frame['data'], k = k, dims = [1, 2]) if k > 0 else frame['data'] # Rotate based on metadata rotation value
            torchvision.io.write_jpeg(
                rotFrame,
                filename = Path(outputFolder).joinpath(f"{frameCount:04d}.jpg").as_posix(),
                quality = 90
            )
            timestamp = str(frame['pts'])
            timestamps.append(timestamp)
            frameCount += 1

    return timestamps, torchvision.io.read_video(mediaPath, pts_unit = 'sec')[2]['video_fps']

##############################################################################################################################