import os
import glob
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random

# ---------- 1. 数据加载 ----------
def load_images_from_dir(base_dir):
    """从 dataset(1) 或 sample_data 加载图像和标签, 文件夹名即标签"""
    images, labels = [], []
    for digit in range(10):
        folder = os.path.join(base_dir, str(digit))
        if not os.path.exists(folder):
            continue
        for ext in ['*.png', '*.jpg', '*.jpeg']:
            for path in glob.glob(os.path.join(folder, ext)):
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                img = cv2.resize(img, (28, 28))
                images.append(img)
                labels.append(digit)
    return images, labels

def load_images_from_sample_data(base_dir):
    """从 sample_data 加载：sample_data/{group}/{digit}/*.png"""
    images, labels = [], []
    for group in os.listdir(base_dir):
        group_path = os.path.join(base_dir, group)
        if not os.path.isdir(group_path):
            continue
        for digit in range(10):
            folder = os.path.join(group_path, str(digit))
            if not os.path.exists(folder):
                continue
            for path in glob.glob(os.path.join(folder, '*.png')):
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is None:
                    continue
                img = cv2.resize(img, (28, 28))
                images.append(img)
                labels.append(digit)
    return images, labels

class DigitDataset(Dataset):
    def __init__(self, images, labels):
        self.X = torch.FloatTensor(np.array(images, dtype=np.float32)).unsqueeze(1) / 255.0
        self.y = torch.LongTensor(np.array(labels, dtype=np.int64))

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

# ---------- 2. CNN 模型 ----------
class CNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.Conv2d(32, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 3 * 3, 256),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        return self.classifier(x)

# ---------- 3. 训练 ----------
def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct, total = 0, 0, 0
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        optimizer.zero_grad()
        loss = criterion(model(x), y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * x.size(0)
        pred = model(x).argmax(1)
        correct += (pred == y).sum().item()
        total += x.size(0)
    return total_loss / total, correct / total

@torch.no_grad()
def evaluate(model, loader, criterion, device):
    model.eval()
    total_loss, correct, total = 0, 0, 0
    all_preds, all_labels = [], []
    for x, y in loader:
        x, y = x.to(device), y.to(device)
        loss = criterion(model(x), y)
        total_loss += loss.item() * x.size(0)
        pred = model(x).argmax(1)
        correct += (pred == y).sum().item()
        total += x.size(0)
        all_preds.extend(pred.cpu().numpy())
        all_labels.extend(y.cpu().numpy())
    return total_loss / total, correct / total, all_preds, all_labels

# ---------- 4. 主流程 ----------
def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')

    # 加载数据
    print('Loading dataset(1)...')
    imgs1, labels1 = load_images_from_dir('/app/dataset')
    print(f'  dataset(1): {len(imgs1)} images')

    print('Loading sample_data...')
    imgs2, labels2 = load_images_from_sample_data('/app/sample_data')
    print(f'  sample_data: {len(imgs2)} images')

    all_images = imgs1 + imgs2
    all_labels = labels1 + labels2
    print(f'Total: {len(all_images)} images')

    dataset = DigitDataset(all_images, all_labels)

    # 划分数据集 7:2:1
    total = len(dataset)
    test_len = total // 10
    val_len = total // 5
    train_len = total - val_len - test_len

    generator = torch.Generator().manual_seed(42)
    train_set, val_set, test_set = random_split(
        dataset, [train_len, val_len, test_len], generator=generator
    )
    print(f'Train: {len(train_set)}, Val: {len(val_set)}, Test: {len(test_set)}')

    train_loader = DataLoader(train_set, batch_size=128, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_set, batch_size=128, shuffle=False, num_workers=2)
    test_loader = DataLoader(test_set, batch_size=128, shuffle=False, num_workers=2)

    # 模型
    model = CNN(num_classes=10).to(device)
    print(f'Parameters: {sum(p.numel() for p in model.parameters()):,}')

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)

    # 训练
    epochs = 50
    best_val_loss = float('inf')
    patience_counter = 0
    history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}

    for epoch in range(epochs):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc, _, _ = evaluate(model, val_loader, criterion, device)
        scheduler.step(val_loss)

        history['train_loss'].append(train_loss)
        history['train_acc'].append(train_acc)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)

        print(f'Epoch {epoch+1:2d}/{epochs} | '
              f'Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | '
              f'Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | '
              f'LR: {optimizer.param_groups[0]["lr"]:.6f}')

        # Early stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
            torch.save(model.state_dict(), '/app/output/best_model.pth')
        else:
            patience_counter += 1
            if patience_counter >= 8:
                print(f'Early stopping at epoch {epoch+1}')
                break

    # 测试
    model.load_state_dict(torch.load('/app/output/best_model.pth', weights_only=True))
    test_loss, test_acc, test_preds, test_labels = evaluate(model, test_loader, criterion, device)
    print(f'\nTest Loss: {test_loss:.4f}  Accuracy: {test_acc:.4f}')

    # 评估报告
    print('\n' + classification_report(test_labels, test_preds, digits=4))

    # 混淆矩阵
    cm = confusion_matrix(test_labels, test_preds)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm, cmap='Blues')
    for i in range(10):
        for j in range(10):
            ax.text(j, i, cm[i, j], ha='center', va='center', fontsize=8)
    ax.set_xlabel('Predicted'); ax.set_ylabel('True')
    ax.set_xticks(range(10)); ax.set_yticks(range(10))
    ax.set_title('Confusion Matrix')
    plt.colorbar(im)
    plt.tight_layout()
    plt.savefig('/app/output/confusion_matrix.png', dpi=150)

    # 训练曲线
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.plot(history['train_loss'], label='Train')
    ax1.plot(history['val_loss'], label='Val')
    ax1.set_title('Loss'); ax1.set_xlabel('Epoch'); ax1.legend()
    ax2.plot(history['train_acc'], label='Train')
    ax2.plot(history['val_acc'], label='Val')
    ax2.set_title('Accuracy'); ax2.set_xlabel('Epoch'); ax2.legend()
    plt.tight_layout()
    plt.savefig('/app/output/training_curves.png', dpi=150)

    # 错误样本可视化
    test_indices = test_set.indices
    errors = [(i, t, p) for i, (t, p) in enumerate(zip(test_labels, test_preds)) if t != p]
    if errors:
        n = min(25, len(errors))
        fig, axes = plt.subplots(5, 5, figsize=(10, 10), facecolor='white')
        for ax, (idx, true_label, pred_label) in zip(axes.flat, random.sample(errors, n)):
            img = dataset[test_indices[idx]][0].squeeze().numpy()
            ax.imshow(img, cmap='gray')
            ax.set_title(f'True:{true_label} Pred:{pred_label}', fontsize=9)
            ax.axis('off')
        fig.suptitle('Misclassified Samples', fontsize=14)
        plt.tight_layout()
        plt.savefig('/app/output/misclassified.png', dpi=150)

    print('Results saved to /app/output/')

if __name__ == '__main__':
    main()
