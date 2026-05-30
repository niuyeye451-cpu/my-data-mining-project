"""
Feature Engineering — UCI Household Electric Power Consumption
==============================================================================
Builds two feature sets:
  (A) Tabular features → RF / XGBoost  (time features, lags, rolling statistics)
  (B) Sequence  features → LSTM        (sliding-window 3D arrays)

Memory-optimised: loads only needed columns, uses float32 throughout.
"""

import os, gc, warnings, pickle
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

warnings.filterwarnings("ignore")

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
RAW  = os.path.join(BASE_DIR, "data", "household_power_consumption.txt")
OUT  = os.path.join(BASE_DIR, "data", "processed")
os.makedirs(OUT, exist_ok=True)

TARGET = "Global_active_power"

# =============================================================================
# 1.  MEMORY-EFFICIENT LOAD & RESAMPLE
# =============================================================================
print("=" * 60)
print("1. Loading raw data (memory-efficient) …")

# Only load columns we actually need
USECOLS = [
    "Date", "Time",
    "Global_active_power", "Global_reactive_power", "Voltage",
    "Global_intensity", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3",
]
DTYPES = {
    "Global_active_power":   "float32",
    "Global_reactive_power": "float32",
    "Voltage":               "float32",
    "Global_intensity":      "float32",
    "Sub_metering_1":        "float32",
    "Sub_metering_2":        "float32",
    "Sub_metering_3":        "float32",
}

df = pd.read_csv(
    RAW, sep=";", usecols=USECOLS, dtype=DTYPES,
    low_memory=False, na_values="?"
)

# Build datetime index and drop string columns immediately
df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], dayfirst=True)
df.drop(columns=["Date", "Time"], inplace=True)
df.set_index("datetime", inplace=True)

print(f"   Loaded sparse: {df.shape}  (mem: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB)")

# Resample to hourly — this dramatically reduces memory
print("   Resampling to hourly mean …")
df = df.resample("1h").mean()           # 2M → 35K rows
df.dropna(inplace=True)
gc.collect()

print(f"   Hourly: {df.shape},  dtype={df.dtypes.iloc[0]}")
print(f"   Memory: {df.memory_usage(deep=True).sum() / 1e6:.1f} MB")

# =============================================================================
# 2.  TIME-BASED FEATURES
# =============================================================================
print("\n" + "=" * 60)
print("2. Time-based features …")

h = df.index
df["hour"]       = h.hour.astype("int16")
df["dayofweek"]  = h.dayofweek.astype("int16")
df["month"]      = h.month.astype("int16")
df["is_weekend"] = (df["dayofweek"] >= 5).astype("int16")
df["hour_sin"]   = np.sin(2 * np.pi * df["hour"] / 24).astype("float32")
df["hour_cos"]   = np.cos(2 * np.pi * df["hour"] / 24).astype("float32")
df["month_sin"]  = np.sin(2 * np.pi * df["month"] / 12).astype("float32")
df["month_cos"]  = np.cos(2 * np.pi * df["month"] / 12).astype("float32")

print(f"   Total cols: {df.shape[1]}")

# =============================================================================
# 3.  LAG + ROLLING FEATURES
# =============================================================================
print("\n" + "=" * 60)
print("3. Lag + rolling features …")

for lag in [1, 2, 3, 6, 12, 24]:
    df[f"lag{lag}h"] = df[TARGET].shift(lag)

for w in [6, 12, 24]:
    shifted = df[TARGET].shift(1)
    df[f"roll_mean_{w}h"] = shifted.rolling(w).mean()
    df[f"roll_std_{w}h"]  = shifted.rolling(w).std()
    df[f"roll_min_{w}h"]  = shifted.rolling(w).min()
    df[f"roll_max_{w}h"]  = shifted.rolling(w).max()

before = len(df)
df.dropna(inplace=True)
gc.collect()
print(f"   Rows (after NaN drop): {len(df)}  (removed {before - len(df)})")

# =============================================================================
# 4.  CHRONOLOGICAL SPLIT  (70 / 15 / 15)
# =============================================================================
print("\n" + "=" * 60)
print("4. Train / val / test split …")

n = len(df)
train_df = df.iloc[:int(n * 0.7)]
val_df   = df.iloc[int(n * 0.7):int(n * 0.85)]
test_df  = df.iloc[int(n * 0.85):]

# Free the full df now that we have splits
del df; gc.collect()

for name, d in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
    print(f"   {name}: {d.shape[0]} rows  ({d.index[0]} → {d.index[-1]})")

# =============================================================================
# 5.  NORMALIZATION  (Min-Max only, saves memory)
# =============================================================================
print("\n" + "=" * 60)
print("5. Min-Max normalization …")

all_cols = train_df.columns.tolist()
feature_cols = [c for c in all_cols if c != TARGET]

scaler = MinMaxScaler()
scaler.fit(train_df[all_cols].values.astype("float32"))

def normalise(d):
    arr = scaler.transform(d[all_cols].values.astype("float32"))
    return pd.DataFrame(arr, index=d.index, columns=all_cols, dtype="float32")

train = normalise(train_df)
val   = normalise(val_df)
test  = normalise(test_df)

print(f"   Features: {len(feature_cols)},  memory OK")

# =============================================================================
# 6.  SLIDING-WINDOW SEQUENCES  (LSTM)
# =============================================================================
print("\n" + "=" * 60)
print("6. Sliding-window sequences for LSTM (seq_len=24) …")

SEQ_LEN = 24
SEQ_FEATURES = [
    TARGET,                    # autoregressive component
    "hour_sin", "hour_cos",   # daily cycle
    "month_sin", "month_cos", # annual cycle
    "is_weekend",              # weekend vs weekday
    "Sub_metering_1",          # kitchen
    "Sub_metering_2",          # laundry
    "Sub_metering_3",          # AC / water heater
    "Voltage",                 # grid voltage
]

def build_sequences(data, feat_list, tgt, seq_len):
    feats = data[feat_list].values.astype("float32")
    target = data[tgt].values.astype("float32")
    n_samples = len(data) - seq_len
    X = np.lib.stride_tricks.sliding_window_view(feats, seq_len, axis=0)
    X = X[:n_samples]                    # (samples, seq_len, n_feats)
    y = target[seq_len:]                 # (samples,)
    # Copy to make contiguous (sliding_window_view returns a view)
    return np.ascontiguousarray(X, dtype="float32"), y.copy()

X_train, y_train = build_sequences(train, SEQ_FEATURES, TARGET, SEQ_LEN)
X_val,   y_val   = build_sequences(val,   SEQ_FEATURES, TARGET, SEQ_LEN)
X_test,  y_test  = build_sequences(test,  SEQ_FEATURES, TARGET, SEQ_LEN)

print(f"   X_train: {X_train.shape},  y_train: {y_train.shape}")
print(f"   X_val:   {X_val.shape},    y_val:   {y_val.shape}")
print(f"   X_test:  {X_test.shape},   y_test:  {y_test.shape}")

# =============================================================================
# 7.  SAVE
# =============================================================================
print("\n" + "=" * 60)
print("7. Saving …")

train.to_pickle(os.path.join(OUT, "train_tabular.pkl"))
val.to_pickle(  os.path.join(OUT, "val_tabular.pkl"))
test.to_pickle( os.path.join(OUT, "test_tabular.pkl"))

np.save(os.path.join(OUT, "lstm_X_train.npy"), X_train)
np.save(os.path.join(OUT, "lstm_y_train.npy"), y_train)
np.save(os.path.join(OUT, "lstm_X_val.npy"),   X_val)
np.save(os.path.join(OUT, "lstm_y_val.npy"),   y_val)
np.save(os.path.join(OUT, "lstm_X_test.npy"),  X_test)
np.save(os.path.join(OUT, "lstm_y_test.npy"),  y_test)

with open(os.path.join(OUT, "scaler.pkl"), "wb") as f:
    pickle.dump(scaler, f)

meta = {
    "feature_cols": feature_cols,
    "target": TARGET,
    "seq_features": SEQ_FEATURES,
    "seq_len": SEQ_LEN,
    "train_period": (str(train_df.index[0]), str(train_df.index[-1])),
    "val_period":   (str(val_df.index[0]),   str(val_df.index[-1])),
    "test_period":  (str(test_df.index[0]),  str(test_df.index[-1])),
}
with open(os.path.join(OUT, "metadata.pkl"), "wb") as f:
    pickle.dump(meta, f)

print(f"   Files: {sorted(os.listdir(OUT))}")
print("\n" + "=" * 60)
print("Feature engineering complete.")
print("=" * 60)
