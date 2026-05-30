"""
MLP-RF Fusion Model — Stacking Ensemble
=========================================
Level-1: Random Forest + Multi-Layer Perceptron (trained on tabular data)
Level-2: Ridge meta-learner combines both predictions (stacking)

Evaluates against solo RF, XGBoost, and LSTM with the 5 standard metrics.
"""

import os, gc, warnings, pickle, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings("ignore")
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150, "font.size": 11
})

BASE = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(BASE, "data", "processed")
OUT  = os.path.join(BASE, "output"); os.makedirs(OUT, exist_ok=True)
MODELS_DIR = os.path.join(OUT, "models"); os.makedirs(MODELS_DIR, exist_ok=True)
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TARGET = "Global_active_power"
SEQ_LEN = 24  # for LSTM alignment later

# ===================== Helpers =====================
def reg_metrics(y_true, y_pred):
    y_t, y_p = np.asarray(y_true).ravel(), np.asarray(y_pred).ravel()
    mse  = mean_squared_error(y_t, y_p)
    mae  = mean_absolute_error(y_t, y_p)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_t - y_p) / np.clip(y_t, 1e-8, None))) * 100
    r2   = r2_score(y_t, y_p)
    return {"MSE": mse, "MAE": mae, "RMSE": rmse, "MAPE(%)": mape, "R²": r2}

# ===================== 1. Load Data =====================
print("=" * 60)
print("1. Loading tabular data …")

train = pd.read_pickle(os.path.join(PROC, "train_tabular.pkl"))
val   = pd.read_pickle(os.path.join(PROC, "val_tabular.pkl"))
test  = pd.read_pickle(os.path.join(PROC, "test_tabular.pkl"))

EXCLUDE = {TARGET, "Global_intensity", "Global_reactive_power"}
feature_cols = [c for c in train.columns if c not in EXCLUDE]
print(f"   Features: {len(feature_cols)},  Train: {len(train)}, Test: {len(test)}")

X_train = train[feature_cols].values.astype("float32")
y_train = train[TARGET].values.astype("float32").ravel()
X_val   = val[feature_cols].values.astype("float32")
y_val   = val[TARGET].values.astype("float32").ravel()
X_test  = test[feature_cols].values.astype("float32")
y_test  = test[TARGET].values.astype("float32").ravel()

# Align with LSTM (drop first SEQ_LEN samples for fair comparison)
y_test_aligned = y_test[SEQ_LEN:]

# ===================== 2. Random Forest (Base) =====================
print("\n" + "=" * 60)
print("2. Training base Random Forest …")

# Use best params from earlier search
rf_kwargs = {"n_estimators": 200, "max_depth": 25, "min_samples_split": 5,
             "min_samples_leaf": 4, "max_features": 0.5,
             "random_state": 42, "n_jobs": -1}
rf = RandomForestRegressor(**rf_kwargs)

X_train_full = np.concatenate([X_train, X_val])
y_train_full = np.concatenate([y_train, y_val])

t0 = time.time()
rf.fit(X_train_full, y_train_full)
print(f"   RF trained in {time.time()-t0:.0f}s")

rf_test_pred = rf.predict(X_test)
print(f"   RF solo  →  {reg_metrics(y_test, rf_test_pred)}")

# ===================== 3. MLP (Base) =====================
print("\n" + "=" * 60)
print("3. Training base MLP …")

class MLP(nn.Module):
    def __init__(self, in_dim, hidden=[256, 128, 64], dropout=0.3):
        super().__init__()
        layers = []
        prev = in_dim
        for h in hidden:
            layers.extend([nn.Linear(prev, h), nn.BatchNorm1d(h), nn.ReLU(), nn.Dropout(dropout)])
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x).squeeze(-1)

mlp = MLP(len(feature_cols)).to(DEVICE)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(mlp.parameters(), lr=1e-3, weight_decay=1e-5)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="min", factor=0.5, patience=8)

# Prepare data loaders
train_ds = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
val_ds   = TensorDataset(torch.FloatTensor(X_val),   torch.FloatTensor(y_val))
train_loader = DataLoader(train_ds, batch_size=256, shuffle=True)
val_loader   = DataLoader(val_ds,   batch_size=512)

best_val, patience_left = float("inf"), 15

t0 = time.time()
for epoch in range(200):
    mlp.train()
    for xb, yb in train_loader:
        xb, yb = xb.to(DEVICE), yb.to(DEVICE)
        optimizer.zero_grad()
        loss = criterion(mlp(xb), yb)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(mlp.parameters(), 1.0)
        optimizer.step()

    mlp.eval()
    with torch.no_grad():
        val_loss = criterion(mlp(torch.FloatTensor(X_val).to(DEVICE)),
                             torch.FloatTensor(y_val).to(DEVICE)).item()
    scheduler.step(val_loss)

    if val_loss < best_val:
        best_val = val_loss
        patience_left = 15
        torch.save(mlp.state_dict(), os.path.join(MODELS_DIR, "mlp_best.pt"))
    else:
        patience_left -= 1
        if patience_left == 0:
            break

    if (epoch + 1) % 20 == 0:
        print(f"   Epoch {epoch+1:3d} | Val MSE: {val_loss:.6f} | LR: {optimizer.param_groups[0]['lr']:.2e}")

# Restore best and eval on test
mlp.load_state_dict(torch.load(os.path.join(MODELS_DIR, "mlp_best.pt"), weights_only=True))
mlp.eval()
with torch.no_grad():
    mlp_test_pred = mlp(torch.FloatTensor(X_test).to(DEVICE)).cpu().numpy()

mlp_metrics = reg_metrics(y_test, mlp_test_pred)
print(f"\n   MLP solo  →  MAE={mlp_metrics['MAE']:.4f}  MAPE={mlp_metrics['MAPE(%)']:.1f}%  R²={mlp_metrics['R²']:.4f}")
print(f"   MLP trained in {time.time()-t0:.0f}s")

# ===================== 4. Stacking Ensemble =====================
print("\n" + "=" * 60)
print("4. Stacking: RF + MLP → Ridge meta-learner …")

# Cross-validation style: use val predictions from RF & MLP as meta-features
# RF predictions on val
rf_val_pred = rf.predict(X_val)
# MLP predictions on val
mlp.eval()
with torch.no_grad():
    mlp_val_pred = mlp(torch.FloatTensor(X_val).to(DEVICE)).cpu().numpy()

# Meta-features: stack base model predictions
meta_X_train = np.column_stack([rf_val_pred, mlp_val_pred])
meta_y_train = y_val

# Train meta-learner (Ridge regression — simple, robust, prevents overfitting)
meta = Ridge(alpha=1.0)
meta.fit(meta_X_train, meta_y_train)
print(f"   Ridge coefficients: RF={meta.coef_[0]:.4f},  MLP={meta.coef_[1]:.4f}")
print(f"   Ridge intercept: {meta.intercept_:.4f}")

# Meta-features for test
meta_X_test = np.column_stack([rf_test_pred, mlp_test_pred])
fusion_pred = meta.predict(meta_X_test)
fusion_metrics = reg_metrics(y_test, fusion_pred)
print(f"\n   MLP-RF Fusion  →  {fusion_metrics}")

# ===================== 5. Full Comparison =====================
print("\n" + "=" * 60)
print("5. Full Model Comparison (aligned to LSTM) …")

# Recompute all on aligned test set
rf_aligned  = rf_test_pred[SEQ_LEN:]
mlp_aligned = mlp_test_pred[SEQ_LEN:]
fusion_aligned = fusion_pred[SEQ_LEN:]

# Load LSTM predictions
lstm_pred_df = pd.read_pickle(os.path.join(OUT, "lstm_predictions.pkl"))
lstm_aligned = lstm_pred_df["lstm_predicted"].values  # already 5098 samples (aligned)

# Load XGB predictions
xgb_pred = pd.read_pickle(os.path.join(OUT, "rf_xgb_predictions.pkl"))["xgb_predicted"].values
xgb_aligned = xgb_pred[SEQ_LEN:]

avg_aligned = (rf_aligned + mlp_aligned) / 2.0   # simple average of RF + MLP

all_metrics = pd.DataFrame({
    "Random Forest":     reg_metrics(y_test_aligned, rf_aligned),
    "XGBoost":           reg_metrics(y_test_aligned, xgb_aligned),
    "MLP":               reg_metrics(y_test_aligned, mlp_aligned),
    "LSTM":              reg_metrics(y_test_aligned, lstm_aligned),
    "MLP-RF Fusion":     reg_metrics(y_test_aligned, fusion_aligned),
    "MLP-RF Avg":        reg_metrics(y_test_aligned, avg_aligned),
}).T

print(all_metrics.round(4).to_string())
all_metrics.round(4).to_csv(os.path.join(OUT, "all_models_final_metrics.csv"))

# ===================== 6. Visualization =====================
print("\n" + "=" * 60)
print("6. Generating comparison plots …")

test_index = pd.read_pickle(os.path.join(OUT, "rf_xgb_predictions.pkl")).index[SEQ_LEN:]

# --- 6a  All-model overlay (7 days) ---
N_7D = 24 * 7
models = [
    (rf_aligned,     "Random Forest",  "#2C5F2D"),
    (xgb_aligned,    "XGBoost",        "#065A82"),
    (mlp_aligned,    "MLP",            "#B85042"),
    (lstm_aligned,   "LSTM",           "#6D2E46"),
    (avg_aligned,    "MLP-RF Avg",     "#F96167"),
    (fusion_aligned, "MLP-RF Fusion",  "#028090"),
]

fig, axes = plt.subplots(len(models), 1, figsize=(18, 2.2 * len(models)), sharex=True)
for ax, (pred, label, color) in zip(axes, models):
    ax.plot(test_index[:N_7D], y_test_aligned[:N_7D], "o-", color="grey",
            markersize=2.5, linewidth=0.7, alpha=0.5, label="Observed")
    ax.plot(test_index[:N_7D], pred[:N_7D], "s-", color=color,
            markersize=2.5, linewidth=0.7, alpha=0.85, label=label)
    m = reg_metrics(y_test_aligned, pred)
    ax.set_ylabel("Power\n(norm.)", fontsize=8)
    ax.set_title(f"{label}  |  MAPE={m['MAPE(%)']:.1f}%  R²={m['R²']:.4f}", fontsize=10)
    ax.legend(loc="upper right", fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())
plt.tight_layout()
fig.savefig(os.path.join(OUT, "all_models_7days.png"))
plt.close()
print("   → all_models_7days.png")

# --- 6b  Scatter matrix (2×3 for 6 models) ---
fig, axes = plt.subplots(2, 3, figsize=(18, 12))
axes = axes.flat
for ax, (pred, label, color) in zip(axes, models):
    m = reg_metrics(y_test_aligned, pred)
    ax.scatter(y_test_aligned, pred, alpha=0.2, s=5, color=color, edgecolors="none")
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    ax.set_xlabel("Observed"); ax.set_ylabel("Predicted")
    ax.set_title(f"{label}\nR²={m['R²']:.4f}  MAPE={m['MAPE(%)']:.1f}%", fontsize=10)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect("equal")
# Hide extra subplot if odd number
if len(models) < len(axes):
    axes[-1].set_visible(False)
plt.tight_layout()
fig.savefig(os.path.join(OUT, "all_models_scatter.png"))
plt.close()
print("   → all_models_scatter.png")

# --- 6c  Bar chart of metrics ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
names = all_metrics.index.tolist()
colors = ["#2C5F2D", "#065A82", "#B85042", "#6D2E46", "#F96167", "#028090"]

axes[0].barh(names, all_metrics["MAPE(%)"].values, color=colors, edgecolor="white")
axes[0].set_xlabel("MAPE (%)"); axes[0].set_title("MAPE — Lower is Better")
for i, v in enumerate(all_metrics["MAPE(%)"]):
    axes[0].text(v + 1, i, f"{v:.1f}%", va="center", fontsize=9)

axes[1].barh(names, all_metrics["R²"].values, color=colors, edgecolor="white")
axes[1].set_xlabel("R²"); axes[1].set_title("R² — Higher is Better")
for i, v in enumerate(all_metrics["R²"]):
    axes[1].text(v + 0.02, i, f"{v:.4f}", va="center", fontsize=9)

plt.tight_layout()
fig.savefig(os.path.join(OUT, "all_models_barchart.png"))
plt.close()
print("   → all_models_barchart.png")

# ===================== 7. Save =====================
with open(os.path.join(MODELS_DIR, "mlp_rf_meta.pkl"), "wb") as f:
    pickle.dump({"rf": rf, "mlp": mlp, "meta": meta}, f)

print("\n" + "=" * 60)
print("MLP-RF Fusion complete.")
print("=" * 60)
