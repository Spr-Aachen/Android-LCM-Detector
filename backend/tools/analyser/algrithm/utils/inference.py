import torch
from torchvision import transforms

##############################################################################################################################

# [2024-11-28] 性能大概提高了4倍,500秒->135秒
def predict_image(model: torch.nn.Module, transform: transforms.Compose, device: torch.device, imageTensor: torch.Tensor) -> int:
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
    # 归一化到0-1
    image = (imageTensor.float() / 255.0).clamp(0.0, 1.0)
    # Add batch dimension
    image = transform(image).unsqueeze(0)
    # Ensure the image tensor is on the same device as the model
    image = image.to(device)

    with torch.inference_mode():
        outputs = model(image)
        _, predictedTensor = torch.max(outputs, 1)

    return int(predictedTensor.item())

##############################################################################################################################