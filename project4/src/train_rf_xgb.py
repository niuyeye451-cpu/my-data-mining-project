"""
Random Forest & XGBoost — Baseline Models
==========================================
Loads tabular features, performs hyperparameter tuning via RandomizedSearchCV,
evaluates with MSE / MAE / RMSE / MAPE / R², and saves predictions + plots.
"""

import os, gc, warnings, pickle, time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb

warnings.filterwarnings("ignore")
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150,
    "font.size": 11, "axes.titlesize": 13, "axes.labelsize": 11
})

BASE = os.path.join(os.path.dirname(__file__), "..")
PROC = os.path.join(BASE, "data", "processed")
OUT  = os.path.join(BASE, "output"); os.makedirs(OUT, exist_ok=True)
MODELS = os.path.join(OUT, "models"); os.makedirs(MODELS, exist_ok=True)

TARGET = "Global_active_power"

# ===================== Helpers =====================

def load_tabular(name):
    """Load one of train/val/test tabular pickle files."""
    return pd.read_pickle(os.path.join(PROC, f"{name}_tabular.pkl"))

def metrics(y_true, y_pred):
    mse  = mean_squared_error(y_true, y_pred)
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((y_true - y_pred) / np.clip(y_true, 1e-8, None))) * 100
    r2   = r2_score(y_true, y_pred)
    return {"MSE": mse, "MAE": mae, "RMSE": rmse, "MAPE(%)": mape, "R²": r2}

def print_metrics(name, d):
    print(f"\n   --- {name} ---")
    for k, v in d.items():
        print(f"   {k:12s}: {v:.4f}")

# ===================== 1. Load data =====================
print("=" * 60)
print("1. Loading tabular data …")

train = load_tabular("train")
val   = load_tabular("val")
test  = load_tabular("test")

EXCLUDE = {TARGET, "Global_intensity", "Global_reactive_power"}
feature_cols = [c for c in train.columns if c not in EXCLUDE]
print(f"   Features after removing leaks: {len(feature_cols)}")

X_train, y_train = train[feature_cols].values.astype("float32"), train[TARGET].values.astype("float32")
X_val,   y_val   = val[feature_cols].values.astype("float32"),   val[TARGET].values.astype("float32")
X_test,  y_test  = test[feature_cols].values.astype("float32"),  test[TARGET].values.astype("float32")

print(f"   X_train: {X_train.shape},  y_train: {y_train.shape}")
print(f"   X_val:   {X_val.shape},    y_val:   {y_val.shape}")
print(f"   X_test:  {X_test.shape},   y_test:  {y_test.shape}")

# Combine train+val for final model (more data = better generalisation)
X_train_full = np.concatenate([X_train, X_val], axis=0)
y_train_full = np.concatenate([y_train, y_val], axis=0)
print(f"   Train+Val (final fit): {X_train_full.shape[0]} samples")

# ===================== 2. Random Forest =====================
print("\n" + "=" * 60)
print("2. Random Forest — hyperparameter tuning …")

rf_base = RandomForestRegressor(random_state=42, n_jobs=1)
rf_grid = {
    "n_estimators":     [100, 200, 300],
    "max_depth":        [10, 15, 20, 25, None],
    "min_samples_split":[2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features":     [0.5, 0.7, 1.0],
}

rf_search = RandomizedSearchCV(
    rf_base, rf_grid, n_iter=15, cv=3,
    scoring="neg_mean_absolute_error",
    random_state=42, n_jobs=-1, verbose=1
)
t0 = time.time()
rf_search.fit(X_train, y_train)
print(f"   Search completed in {time.time() - t0:.0f}s")
print(f"   Best params: {rf_search.best_params_}")
print(f"   Best CV MAE: {-rf_search.best_score_:.4f}")

# Evaluate on validation set
rf_val_pred = rf_search.predict(X_val)
print_metrics("RF on Validation", metrics(y_val, rf_val_pred))

# Refit on train+val with best params
print("   Fitting final RF on train+val …")
rf_final = RandomForestRegressor(**rf_search.best_params_, random_state=42, n_jobs=-1)
rf_final.fit(X_train_full, y_train_full)
gc.collect()

# Test evaluation
y_rf_pred = rf_final.predict(X_test)
rf_metrics = metrics(y_test, y_rf_pred)
print_metrics("RF on Test (final)", rf_metrics)

# Feature importance
rf_imp = pd.DataFrame({
    "feature": feature_cols,
    "importance": rf_final.feature_importances_
}).sort_values("importance", ascending=False).head(15)

print(f"\n   Top-15 features:\n{rf_imp.to_string(index=False)}")

# ===================== 3. XGBoost =====================
print("\n" + "=" * 60)
print("3. XGBoost — hyperparameter tuning …")

xgb_base = xgb.XGBRegressor(
    objective="reg:squarederror", random_state=42,
    n_jobs=-1, tree_method="hist", verbosity=0
)
xgb_grid = {
    "n_estimators":     [100, 200, 400, 600],
    "max_depth":        [4, 6, 8, 10, 12],
    "learning_rate":    [0.01, 0.03, 0.05, 0.1],
    "subsample":        [0.7, 0.8, 0.9, 1.0],
    "colsample_bytree": [0.7, 0.8, 0.9, 1.0],
    "reg_alpha":        [0, 0.1, 1.0],
    "reg_lambda":       [1.0, 1.5, 2.0],
}

xgb_search = RandomizedSearchCV(
    xgb_base, xgb_grid, n_iter=20, cv=3,
    scoring="neg_mean_absolute_error",
    random_state=42, n_jobs=-1, verbose=1
)
t0 = time.time()
xgb_search.fit(X_train, y_train)
print(f"   Search completed in {time.time() - t0:.0f}s")
print(f"   Best params: {xgb_search.best_params_}")
print(f"   Best CV MAE: {-xgb_search.best_score_:.4f}")

xgb_val_pred = xgb_search.predict(X_val)
print_metrics("XGBoost on Validation", metrics(y_val, xgb_val_pred))

# Refit on train+val
print("   Fitting final XGBoost on train+val …")
xgb_final = xgb.XGBRegressor(
    **xgb_search.best_params_,
    objective="reg:squarederror", random_state=42,
    n_jobs=-1, tree_method="hist", verbosity=0
)
xgb_final.fit(X_train_full, y_train_full)
gc.collect()

y_xgb_pred = xgb_final.predict(X_test)
xgb_metrics = metrics(y_test, y_xgb_pred)
print_metrics("XGBoost on Test (final)", xgb_metrics)

xgb_imp = pd.DataFrame({
    "feature": feature_cols,
    "importance": xgb_final.feature_importances_
}).sort_values("importance", ascending=False).head(15)
print(f"\n   Top-15 features:\n{xgb_imp.to_string(index=False)}")

# ===================== 4. Comparison Summary =====================
print("\n" + "=" * 60)
print("4. Model Comparison Table …")

results_df = pd.DataFrame({
    "Random Forest": rf_metrics,
    "XGBoost":       xgb_metrics,
}).T
results_df.index.name = "Model"
print(results_df.round(4).to_string())
results_df.round(4).to_csv(os.path.join(OUT, "rf_xgb_metrics.csv"))

# ===================== 5. Prediction Plots =====================
print("\n" + "=" * 60)
print("5. Generating prediction plots …")

test_index = test.index

# --- 5a  Full test-period comparison ---
fig, axes = plt.subplots(2, 1, figsize=(18, 9), sharex=True)

for ax, (pred, label, color) in zip(axes, [
    (y_rf_pred,  "Random Forest", "#2C5F2D"),
    (y_xgb_pred, "XGBoost",       "#065A82"),
]):
    ax.plot(test_index, y_test, color="grey", linewidth=0.8, alpha=0.7, label="Observed")
    ax.plot(test_index, pred, color=color, linewidth=0.6, alpha=0.9, label=f"{label} Predicted")
    ax.set_ylabel("Global Active Power (normalised)")
    ax.set_title(f"{label} — Full Test Period")
    ax.legend(loc="upper right", fontsize=9)

plt.tight_layout()
fig.savefig(os.path.join(OUT, "rf_xgb_full.png"))
plt.close()
print("   → rf_xgb_full.png")

# --- 5b  First 7 days of test period ---
N_7D = 24 * 7
fig, axes = plt.subplots(2, 1, figsize=(18, 9), sharex=True)

for ax, (pred, label, color) in zip(axes, [
    (y_rf_pred,  "Random Forest", "#2C5F2D"),
    (y_xgb_pred, "XGBoost",       "#065A82"),
]):
    ax.plot(test_index[:N_7D], y_test[:N_7D], "o-", color="grey",
            markersize=3, linewidth=0.8, alpha=0.6, label="Observed")
    ax.plot(test_index[:N_7D], pred[:N_7D], "s-", color=color,
            markersize=3, linewidth=0.8, alpha=0.8, label=f"{label} Predicted")
    ax.set_ylabel("Global Active Power (normalised)")
    ax.set_title(f"{label} — First 7 Days of Test")
    ax.legend(loc="upper right", fontsize=9)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
    ax.xaxis.set_major_locator(mdates.DayLocator())

plt.tight_layout()
fig.savefig(os.path.join(OUT, "rf_xgb_7days.png"))
plt.close()
print("   → rf_xgb_7days.png")

# --- 5c  Scatter: Predicted vs Observed ---
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, (pred, label, color) in zip(axes, [
    (y_rf_pred,  "Random Forest", "#2C5F2D"),
    (y_xgb_pred, "XGBoost",       "#065A82"),
]):
    m = metrics(y_test, pred)
    ax.scatter(y_test, pred, alpha=0.3, s=6, color=color, edgecolors="none")
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    ax.set_xlabel("Observed"); ax.set_ylabel("Predicted")
    ax.set_title(f"{label}  |  R²={m['R²']:.4f}, MAPE={m['MAPE(%)']:.2f}%")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("equal")

plt.tight_layout()
fig.savefig(os.path.join(OUT, "rf_xgb_scatter.png"))
plt.close()
print("   → rf_xgb_scatter.png")

# --- 5d  Residual distribution ---
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

for ax, (pred, label, color) in zip(axes, [
    (y_rf_pred,  "Random Forest", "#2C5F2D"),
    (y_xgb_pred, "XGBoost",       "#065A82"),
]):
    residuals = y_test - pred
    ax.hist(residuals, bins=80, color=color, edgecolor="white", alpha=0.85)
    ax.axvline(0, color="grey", linestyle="--", linewidth=1)
    ax.set_xlabel("Residual (Observed − Predicted)")
    ax.set_ylabel("Frequency")
    ax.set_title(f"{label} Residual Distribution")

plt.tight_layout()
fig.savefig(os.path.join(OUT, "rf_xgb_residuals.png"))
plt.close()
print("   → rf_xgb_residuals.png")

# ===================== 6. Save Models =====================
print("\n" + "=" * 60)
print("6. Saving models …")

with open(os.path.join(MODELS, "rf.pkl"), "wb") as f:
    pickle.dump(rf_final, f)
with open(os.path.join(MODELS, "xgb.pkl"), "wb") as f:
    pickle.dump(xgb_final, f)

# Save predictions for later ensemble comparison
pred_df = pd.DataFrame({
    "observed":     y_test,
    "rf_predicted": y_rf_pred,
    "xgb_predicted": y_xgb_pred,
}, index=test_index)
pred_df.to_pickle(os.path.join(OUT, "rf_xgb_predictions.pkl"))

print("   rf.pkl, xgb.pkl, rf_xgb_predictions.pkl saved")

print("\n" + "=" * 60)
print("RF & XGBoost baseline complete.")
print("=" * 60)
