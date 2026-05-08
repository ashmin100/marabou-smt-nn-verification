"""
train_model.py

Trains a small fully-connected network on MNIST and exports it to ONNX format.
Architecture: 784 -> 64 -> 32 -> 10 (ReLU activations)

The exported ONNX model is used by test.py for Marabou verification.
"""

import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# ── Reproducibility ──────────────────────────────────────────────────────────
torch.manual_seed(42)

# ── Paths ─────────────────────────────────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
ONNX_PATH = os.path.join(MODEL_DIR, "mnist_fc.onnx")
SAMPLE_PATH = os.path.join(MODEL_DIR, "sample_inputs.npy")
SAMPLE_LABELS_PATH = os.path.join(MODEL_DIR, "sample_labels.npy")
os.makedirs(MODEL_DIR, exist_ok=True)

# ── Model definition ─────────────────────────────────────────────────────────
class MnistFC(nn.Module):
    """Small fully-connected network for MNIST (784 -> 64 -> 32 -> 10)."""

    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(784, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 10),
        )

    def forward(self, x):
        return self.net(x)


# ── Data loading ──────────────────────────────────────────────────────────────
def get_loaders(batch_size=256):
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,)),  # MNIST mean/std
    ])
    train_data = datasets.MNIST("./data", train=True, download=True, transform=transform)
    test_data  = datasets.MNIST("./data", train=False, download=True, transform=transform)
    train_loader = DataLoader(train_data, batch_size=batch_size, shuffle=True)
    test_loader  = DataLoader(test_data,  batch_size=batch_size, shuffle=False)
    return train_loader, test_loader


# ── Training ──────────────────────────────────────────────────────────────────
def train(model, loader, optimizer, criterion, device):
    model.train()
    total_loss = 0.0
    for images, labels in loader:
        images = images.view(-1, 784).to(device)
        labels = labels.to(device)
        optimizer.zero_grad()
        loss = criterion(model(images), labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(loader)


def evaluate(model, loader, device):
    model.eval()
    correct = 0
    with torch.no_grad():
        for images, labels in loader:
            images = images.view(-1, 784).to(device)
            preds = model(images).argmax(dim=1)
            correct += (preds.cpu() == labels).sum().item()
    return correct / len(loader.dataset)


# ── ONNX export ───────────────────────────────────────────────────────────────
def export_onnx(model, path, device):
    model.eval()
    dummy = torch.zeros(1, 784, device=device)
    torch.onnx.export(
        model,
        dummy,
        path,
        input_names=["input"],
        output_names=["output"],
        opset_version=11,       # Marabou supports opset 11
        dynamic_axes=None,      # Fixed batch size=1 for verifier
    )
    print(f"ONNX model saved → {path}")


# ── Save sample inputs for test.py ───────────────────────────────────────────
def save_samples(model, loader, device, n_samples=10):
    """
    Save n correctly-classified samples per class for use in verification.
    Saves normalized pixel values in [-1, ~3] range (post-normalization).
    """
    model.eval()
    samples, s_labels = [], []
    with torch.no_grad():
        for images, labels in loader:
            flat = images.view(-1, 784)
            preds = model(flat.to(device)).argmax(dim=1).cpu()
            correct_mask = (preds == labels)
            flat_correct = flat[correct_mask]
            labels_correct = labels[correct_mask]
            samples.append(flat_correct)
            s_labels.append(labels_correct)
            if sum(len(s) for s in samples) >= 100:
                break
    all_samples = torch.cat(samples).numpy()[:100]
    all_labels  = torch.cat(s_labels).numpy()[:100]
    np.save(SAMPLE_PATH, all_samples)
    np.save(SAMPLE_LABELS_PATH, all_labels)
    print(f"Sample inputs saved → {SAMPLE_PATH}  (shape: {all_samples.shape})")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    device = torch.device("cpu")   # keep deterministic; no GPU needed for small net
    model = MnistFC().to(device)
    train_loader, test_loader = get_loaders()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

    print("Training MNIST FC network (784→64→32→10) for 5 epochs...")
    for epoch in range(1, 6):
        loss = train(model, train_loader, optimizer, criterion, device)
        acc  = evaluate(model, test_loader, device)
        print(f"  Epoch {epoch}/5 | Loss: {loss:.4f} | Test Acc: {acc*100:.2f}%")

    export_onnx(model, ONNX_PATH, device)
    save_samples(model, test_loader, device)
    print("\nDone. Run `python test.py` to execute Marabou verification.")


if __name__ == "__main__":
    main()
