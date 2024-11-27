import torch
import torchvision
from tqdm import tqdm
from pathlib import Path

##############################################################################################################################

def extract_frames(videoPath: str, outputFolder: str) -> None:
    # Read stream from video file (frame by frame)
    reader = torchvision.io.VideoReader(videoPath, stream = "video")
    # Get metadata to determine rotation
    rotation_degrees = reader.get_metadata().get('rotation', 0)
    # Calculate number of 90 degree rotations needed
    k = (rotation_degrees // 90) % 4

    frame = next(reader)

    # Save viedo frames to outputFolder as JPEG images
    frame_count = 0
    for frame in tqdm(reader):
        frame = torch.rot90(frame['data'], k = k, dims = [1, 2]) if k > 0 else frame['data'] # Rotate based on metadata rotation value
        torchvision.io.write_jpeg(
            frame,
            filename = Path(outputFolder).joinpath(f"{frame_count:04d}.jpg").as_posix(),
            quality = 90
        )
        frame_count += 1

##############################################################################################################################