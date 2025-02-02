import torch
import os

def save_checkpoint(model, optimizer, epoch, path='checkpoints/'):
    os.makedirs(path, exist_ok=True)
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }
    torch.save(checkpoint, os.path.join(path, f'checkpoint_epoch_{epoch}.pth'))
    print(f"Checkpoint saved at epoch {epoch}.")

def load_checkpoint(model, optimizer, path):
    checkpoint = torch.load(path)
    model.load_state_dict(checkpoint['model_state_dict'])
    optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
    print(f"Loaded checkpoint from {path} (Epoch {checkpoint['epoch']}).")

def accuracy(output, target):
    preds = torch.argmax(output, dim=1)
    correct = (preds == target).sum().item()
    return correct / target.size(0)

