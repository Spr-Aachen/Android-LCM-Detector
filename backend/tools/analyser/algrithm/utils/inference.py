import os
import torch
import torchvision
from typing import Union

##############################################################################################################################

# [2024-11-28] 性能大概提高了4倍,500秒->135秒
def predict_image(model: torch.nn.Module, transform: torchvision.transforms.Compose, image: Union[torch.Tensor, str], device: torch.device) -> int:
    """
    """
    """
    # 转为BGR格式
    imageTensor = imageTensor.permute(1, 2, 0) # [C,H,W] -> [H,W,C]
    image = imageTensor.numpy().astype('uint8')
    # 转换为RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # 转换为tensor
    image = torch.from_numpy(image).permute(2, 0, 1).float() / 255.0
    image = transform(image).unsqueeze(0).to(device)
    """
    # Ensure the image tensor is on the same device as the model
    imageTensor = (torchvision.io.read_image(image) if isinstance(image, str) else image).to(device)
    # Transform the image tensor to the format expected by the model
    image = transform(
        (imageTensor.float() / 255.0).clamp(0.0, 1.0) # Normalize to 0~1
    ).unsqueeze(0)

    with torch.inference_mode():
        outputs = model(image)
        _, predictedTensor = torch.max(outputs, 1)

    return int(predictedTensor.item())

##############################################################################################################################