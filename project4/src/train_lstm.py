"""
LSTM — Deep Learning Model for Power Load Forecasting
=======================================================
PyTorch LSTM with configurable layers, early stopping, and
MSE / MAE / RMSE / MAPE / R² evaluation.
"""

import os, gc, warnings, pickle, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings("ignore")
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150,
    "font.size": 11, "axes.titlesize": 13
})

BASE = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(BASE, "data", "processed")
OUT  = os.path.join(BASE, "output"); os.makedirs(OUT, exist_ok=True)
MODELS_DIR = os.path.join(OUT, "models"); os.makedirs(MODELS_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ===================== Data =====================
print("=" * 60)
print(f"1. Loading sequence data …  (device: {DEVICE})")

X_train = np.load(os.path.join(PROC, "lstm_X_train.npy"))
y_train = np.load(os.path.join(PROC, "lstm_y_train.npy"))
X_val   = np.load(os.path.join(PROC, "lstm_X_val.npy"))
y_val   = np.load(os.path.join(PROC, "lstm_y_val.npy"))
X_test  = np.load(os.path.join(PROC, "lstm_X_test.npy"))
y_test  = np.load(os.path.join(PROC, "lstm_y_test.npy"))

# LSTM expects (batch, seq_len, features) — data is already in this shape
print(f"   X_train: {X_train.shape},  y_train: {y_train.shape}")
print(f"   X_val:   {X_val.shape},    y_val:   {y_val.shape}")
print(f"   X_test:  {X_test.shape},   y_test:  {y_test.shape}")

seq_len, n_features = X_train.shape[1], X_train.shape[2]

# Load metadata for feature names
with open(os.path.join(PROC, "metadata.pkl"), "rb") as f:
    meta = pickle.load(f)
print(f"   Seq features: {meta['seq_features']}")

# ===================== Model =====================
class LSTMForecaster(nn.Module):
    def __init__(self, input_dim, hidden_dim=128, num_layers=2, dropout=0.2):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers,
                            batch_first=True, dropout=dropout)
        self.regressor = nn.Sequential(
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
        )

    def forward(self, x):
        out, _ = self.lstm(x)             # (B, seq_len, hidden)
        out = out[:, -1, :]               # last timestep only
        return self.regressor(out).squeeze(-1)

# ===================== Training =====================
def metrics(y_true, y_pred):
    y_t = y_true.cpu().numpy()
    y_p = y_pred.cpu().numpy()
    mse  = np.mean((y_t - y_p) ** 2)
    mae  = np.mean(np.abs(y_t - y_p))
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_t - y_p) / np.clip(y_t, 1e-8, None))) * 100
    r2   = 1 - np.sum((y_t - y_p) ** 2) / np.sum((y_t - y_t.mean()) ** 2)
    return mse, mae, rmse, mape, r2

def train_one_epoch(model, loader, opt, criterion):
    model.train()
    total_loss, n = 0, 0
    for xb, yb in loader:
        xb, yb = xb.to(DEVICE), yb.to(DEVICE)
        opt.zero_grad()
        loss = criterion(model(xb), yb)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        opt.step()
        total_loss += loss.item() * len(yb)
        n += len(yb)
    return total_loss / n

@torch.no_grad()
def evaluate(model, loader):
    model.eval()
    preds, truths = [], []
    for xb, yb in loader:
        preds.append(model(xb.to(DEVICE)))
        truths.append(yb)
    return metrics(torch.cat(truths), torch.cat(preds))

print("\n" + "=" * 60)
print("2. Training LSTM …")

# Hyperparams
HIDDEN   = 128
LAYERS   = 3
DROPOUT  = 0.3
LR       = 1e-3
EPOCHS   = 100
BATCH    = 64
PATIENCE = 15

train_ds = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
val_ds   = TensorDataset(torch.FloatTensor(X_val),   torch.FloatTensor(y_val))
test_ds  = TensorDataset(torch.FloatTensor(X_test),  torch.FloatTensor(y_test))

train_loader = DataLoader(train_ds, batch_size=BATCH, shuffle=True)
val_loader   = DataLoader(val_ds,   batch_size=BATCH * 2)
test_loader  = DataLoader(test_ds,  batch_size=BATCH * 2)

model = LSTMForecaster(n_features, HIDDEN, LAYERS, DROPOUT).to(DEVICE)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.5, patience=5
)

best_val_loss = float("inf")
best_epoch = 0
patience_left = PATIENCE
history = {"train_loss": [], "val_loss": []}

t0 = time.time()
for epoch in range(EPOCHS):
    train_loss = train_one_epoch(model, train_loader, optimizer, criterion)
    val_mse, val_mae, _, val_mape, val_r2 = evaluate(model, val_loader)

    scheduler.step(val_mse)
    history["train_loss"].append(train_loss)
    history["val_loss"].append(val_mse)

    if (epoch + 1) % 5 == 0 or epoch == 0:
        print(f"   Epoch {epoch+1:3d}/{EPOCHS} | "
              f"TrainLoss: {train_loss:.6f} | "
              f"Val MSE: {val_mse:.4f} MAE: {val_mae:.4f} MAPE: {val_mape:.1f}% R²: {val_r2:.4f} | "
              f"LR: {optimizer.param_groups[0]['lr']:.2e}")

    if val_mse < best_val_loss:
        best_val_loss = val_mse
        best_epoch = epoch + 1
        patience_left = PATIENCE
        torch.save(model.state_dict(), os.path.join(MODELS_DIR, "lstm_best.pt"))
    else:
        patience_left -= 1
        if patience_left == 0:
            print(f"   Early stopping at epoch {epoch+1} (best: epoch {best_epoch})")
            break

print(f"\n   Training completed in {time.time() - t0:.0f}s, best epoch: {best_epoch}")

# ===================== Evaluate =====================
print("\n" + "=" * 60)
print("3. Test evaluation …")

model.load_state_dict(torch.load(os.path.join(MODELS_DIR, "lstm_best.pt"), weights_only=True))
test_mse, test_mae, test_rmse, test_mape, test_r2 = evaluate(model, test_loader)

lstm_metrics = {"MSE": test_mse, "MAE": test_mae, "RMSE": test_rmse,
                "MAPE(%)": test_mape, "R²": test_r2}
print(f"   MSE: {test_mse:.4f}  MAE: {test_mae:.4f}  RMSE: {test_rmse:.4f}")
print(f"   MAPE: {test_mape:.2f}%  R²: {test_r2:.4f}")

# Get full test predictions
model.eval()
with torch.no_grad():
    y_lstm_pred = model(torch.FloatTensor(X_test).to(DEVICE)).cpu().numpy()

# ===================== Comparison =====================
print("\n" + "=" * 60)
print("4. Model comparison (RF vs XGBoost vs LSTM) …")

rf_xgb_pred = pd.read_pickle(os.path.join(OUT, "rf_xgb_predictions.pkl"))
test_index = rf_xgb_pred.index
y_obs = rf_xgb_pred["observed"].values

# Align: LSTM test set is shorter by seq_len
y_obs_aligned = y_obs[24:]
rf_pred_aligned = rf_xgb_pred["rf_predicted"].values[24:]
xgb_pred_aligned = rf_xgb_pred["xgb_predicted"].values[24:]
test_index_aligned = test_index[24:]

# Recompute metrics on aligned test set
all_metrics = pd.DataFrame({
    "Random Forest": {"MSE": np.mean((y_obs_aligned - rf_pred_aligned)**2),
                      "MAE": np.mean(np.abs(y_obs_aligned - rf_pred_aligned)),
                      "RMSE": np.sqrt(np.mean((y_obs_aligned - rf_pred_aligned)**2)),
                      "MAPE(%)": np.mean(np.abs((y_obs_aligned - rf_pred_aligned) / np.clip(y_obs_aligned, 1e-8, None))) * 100,
                      "R²": 1 - np.sum((y_obs_aligned - rf_pred_aligned)**2) / np.sum((y_obs_aligned - y_obs_aligned.mean())**2)},
    "XGBoost": {"MSE": np.mean((y_obs_aligned - xgb_pred_aligned)**2),
                "MAE": np.mean(np.abs(y_obs_aligned - xgb_pred_aligned)),
                "RMSE": np.sqrt(np.mean((y_obs_aligned - xgb_pred_aligned)**2)),
                "MAPE(%)": np.mean(np.abs((y_obs_aligned - xgb_pred_aligned) / np.clip(y_obs_aligned, 1e-8, None))) * 100,
                "R²": 1 - np.sum((y_obs_aligned - xgb_pred_aligned)**2) / np.sum((y_obs_aligned - y_obs_aligned.mean())**2)},
    "LSTM": lstm_metrics,
}).T

print(all_metrics.round(4).to_string())
all_metrics.round(4).to_csv(os.path.join(OUT, "all_models_metrics.csv"))

# ===================== Plots =====================
print("\n" + "=" * 60)
print("5. Generating plots …")

# --- 5a Training curves ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
ax1.plot(history["train_loss"], color="#2C5F2D", linewidth=1.2, label="Train Loss")
ax1.plot(history["val_loss"], color="#065A82", linewidth=1.2, label="Val Loss")
ax1.axvline(best_epoch - 1, color="firebrick", linestyle="--", alpha=0.5, label=f"Best epoch={best_epoch}")
ax1.set_xlabel("Epoch"); ax1.set_ylabel("MSE Loss"); ax1.set_title("LSTM Training & Validation Loss")
ax1.legend()

val_history = []
for epoch in range(len(history["val_loss"])):
    model.load_state_dict(torch.load(os.path.join(MODELS_DIR, "lstm_best.pt"), weights_only=True))
    # Just use recorded val loss for now
    val_history.append(history["val_loss"][epoch])

ax2.plot(np.arange(1, len(val_history)+1) * (len(train_loader) * BATCH), history["val_loss"],
         color="#065A82", linewidth=1)
ax2.set_xlabel("Samples seen"); ax2.set_ylabel("Val MSE")
ax2.set_title("Validation Loss over Training")
plt.tight_layout()
fig.savefig(os.path.join(OUT, "lstm_training_curves.png"))
plt.close()
print("   → lstm_training_curves.png")

# --- 5b Three-model comparison (7 days) ---
N_7D = 24 * 7
fig, axes = plt.subplots(3, 1, figsize=(18, 10), sharex=True)

for ax, (pred, label, color) in zip(axes, [
    (rf_pred_aligned, "Random Forest", "#2C5F2D"),
    (xgb_pred_aligned, "XGBoost", "#065A82"),
    (y_lstm_pred, "LSTM", "#B85042"),
]):
    ax.plot(test_index_aligned[:N_7D], y_obs_aligned[:N_7D], "o-", color="grey",
            markersize=3, linewidth=0.8, alpha=0.6, label="Observed")
    ax.plot(test_index_aligned[:N_7D], pred[:N_7D], "s-", color=color,
            markersize=3, linewidth=0.8, alpha=0.8, label=f"{label} Predicted")
    ax.set_ylabel("Power (norm.)")
    ax.set_title(f"{label} — First 7 Days of Test")
    ax.legend(loc="upper right", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())

plt.tight_layout()
fig.savefig(os.path.join(OUT, "three_models_7days.png"))
plt.close()
print("   → three_models_7days.png")

# --- 5c Scatter comparison ---
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

for ax, (pred, label, color) in zip(axes, [
    (rf_pred_aligned, "Random Forest", "#2C5F2D"),
    (xgb_pred_aligned, "XGBoost", "#065A82"),
    (y_lstm_pred, "LSTM", "#B85042"),
]):
    mape_v = np.mean(np.abs((y_obs_aligned - pred) / np.clip(y_obs_aligned, 1e-8, None))) * 100
    r2_v = 1 - np.sum((y_obs_aligned - pred)**2) / np.sum((y_obs_aligned - y_obs_aligned.mean())**2)
    ax.scatter(y_obs_aligned, pred, alpha=0.3, s=6, color=color, edgecolors="none")
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    ax.set_xlabel("Observed"); ax.set_ylabel("Predicted")
    ax.set_title(f"{label}\nR²={r2_v:.4f}, MAPE={mape_v:.1f}%")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("equal")

plt.tight_layout()
fig.savefig(os.path.join(OUT, "three_models_scatter.png"))
plt.close()
print("   → three_models_scatter.png")

# --- 5d Full test-period overlay ---
fig, ax = plt.subplots(figsize=(18, 6))
ax.plot(test_index_aligned, y_obs_aligned, color="grey", linewidth=0.8, alpha=0.7, label="Observed")
ax.plot(test_index_aligned, rf_pred_aligned, color="#2C5F2D", linewidth=0.5, alpha=0.7, label="RF")
ax.plot(test_index_aligned, xgb_pred_aligned, color="#065A82", linewidth=0.5, alpha=0.7, label="XGBoost")
ax.plot(test_index_aligned, y_lstm_pred, color="#B85042", linewidth=0.5, alpha=0.7, label="LSTM")
ax.set_ylabel("Global Active Power (normalised)")
ax.set_title("Three Models — Full Test Period")
ax.legend(loc="upper right")
plt.tight_layout()
fig.savefig(os.path.join(OUT, "three_models_full.png"))
plt.close()
print("   → three_models_full.png")

# ===================== Save =====================
# Save LSTM predictions
lstm_pred_df = pd.DataFrame({
    "observed": y_obs_aligned,
    "lstm_predicted": y_lstm_pred,
}, index=test_index_aligned)
lstm_pred_df.to_pickle(os.path.join(OUT, "lstm_predictions.pkl"))

print("\n" + "=" * 60)
print("LSTM training complete.")
print("=" * 60)
