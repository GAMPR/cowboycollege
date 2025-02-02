import torch.nn as nn
import torchvision.models as models

class ImageClassifier(nn.Module):
    def __init__(self, num_classes=10):  # Default to CIFAR-10
        super(ImageClassifier, self).__init__()
        # Use pre-trained ResNet50
        self.model = models.resnet50(pretrained=True)
        
        # Replace the final fully connected layer
        self.model.fc = nn.Linear(self.model.fc.in_features, num_classes)

    def forward(self, x):
        return self.model(x)

