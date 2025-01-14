import torch
import torchvision

##############################################################################################################################

def loadEffNetModel(effNetVersion: str, modelPath: str, classes: list, device: torch.device):
    # Load pre-trained EfficientNet model
    model: torchvision.models.EfficientNet = getattr(torchvision.models, f"efficientnet_{effNetVersion}")(weights = None)
    model.classifier[1] = torch.nn.Linear(
        in_features = model.classifier[1].in_features,
        out_features = len(classes)
    )
    # Load trained weights
    model.load_state_dict(torch.load(modelPath, weights_only = True))
    # Move model to GPU if available
    model.to(device)
    # Set model to evaluation mode
    model.eval()
    return model


def loadR2plus1dModel(modelPath: str, classes: list, device: torch.device):
    # Load pre-trained EfficientNet model
    model = torchvision.models.video.r2plus1d_18(weights = None)
    model.fc = torch.nn.Linear(
        in_features = model.fc.in_features,
        out_features = len(classes)
    )
    # Load trained weights
    model.load_state_dict(torch.load(modelPath, weights_only = True))
    # Move model to GPU if available
    model.to(device)
    # Set model to evaluation mode
    model.eval()
    return model

##############################################################################################################################