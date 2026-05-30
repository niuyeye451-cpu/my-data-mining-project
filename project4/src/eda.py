"""
Exploratory Data Analysis — UCI Household Electric Power Consumption
==========================================================================
Covers: missing values, resampling, statistical summary, seasonal decomposition,
correlation heatmap, and power variation heatmap (dates × hours).
"""

import os, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

warnings.filterwarnings("ignore")
sns.set_style("whitegrid")
plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150,
    "font.size": 11, "axes.titlesize": 14, "axes.labelsize": 12
})

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
OUT_DIR  = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUT_DIR, exist_ok=True)

# ===================== 1. Load & inspect =====================
print("=" * 60)
print("1. Loading data …")

data_path = os.path.join(DATA_DIR, "household_power_consumption.txt")
df = pd.read_csv(
    data_path, sep=";",
    low_memory=False, na_values="?"
)
df["datetime"] = pd.to_datetime(df["Date"] + " " + df["Time"], dayfirst=True)
df.drop(columns=["Date", "Time"], inplace=True)
df.set_index("datetime", inplace=True)
df = df.astype(float)

print(f"   Shape: {df.shape}")
print(f"   Date range: {df.index.min()}  →  {df.index.max()}")
print(f"   Columns: {list(df.columns)}")

# ===================== 2. Missing value analysis =====================
print("\n" + "=" * 60)
print("2. Missing value analysis")

missing = df.isnull().sum()
missing_pct = (missing / len(df) * 100).round(4)
miss_df = pd.DataFrame({"missing_count": missing, "missing_%": missing_pct})
print(miss_df[miss_df["missing_count"] > 0])

# Fill or drop missing values
before = len(df)
df.dropna(inplace=True)
print(f"   Rows after dropna: {len(df)}  (removed {before - len(df)}, "
      f"{(before - len(df)) / before * 100:.2f}%)")

# ===================== 3. Statistical summary =====================
print("\n" + "=" * 60)
print("3. Statistical summary")
print(df.describe().round(4).to_string())

# ===================== 4. Resample to hourly =====================
print("\n" + "=" * 60)
print("4. Resampling to 1-hour mean …")
df_hourly = df.resample("1h").mean()
print(f"   Hourly shape: {df_hourly.shape}")

# ===================== 5. Distribution of key variable =====================
print("\n" + "=" * 60)
print("5. Plotting distributions & time series …")

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
for ax, col in zip(axes.flat, df.columns):
    ax.hist(df[col].values, bins=120, color="steelblue", edgecolor="none", alpha=0.85)
    ax.set_title(f"Distribution of {col}", fontsize=10)
    ax.set_xlabel(col)
    ax.set_ylabel("Frequency")
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eda_distributions.png"))
plt.close()
print("   → eda_distributions.png")

# ===================== 6. Time series of daily Global_active_power =====================
fig, axes = plt.subplots(3, 1, figsize=(18, 10))

# Full period (daily mean)
daily = df["Global_active_power"].resample("1D").mean()
axes[0].plot(daily.index, daily.values, color="steelblue", linewidth=0.5)
axes[0].set_title("Daily Mean Global Active Power (full period)")
axes[0].set_ylabel("kW")

# Zoom: first 3 months
start = daily.index[0]
axes[1].plot(daily.index, daily.values, color="steelblue", linewidth=0.6)
axes[1].set_xlim(start, start + pd.DateOffset(months=3))
axes[1].set_title("First 3 Months")
axes[1].set_ylabel("kW")

# Zoom: last 2 weeks (Nov 2010)
axes[2].plot(daily.index, daily.values, color="firebrick", linewidth=0.8)
axes[2].set_xlim(daily.index[-1] - pd.DateOffset(days=14), daily.index[-1])
axes[2].set_title("Last 14 Days (Nov 2010)")
axes[2].set_xlabel("Date")
axes[2].set_ylabel("kW")

plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eda_timeseries.png"))
plt.close()
print("   → eda_timeseries.png")

# ===================== 7. Seasonal Decomposition =====================
print("\n" + "=" * 60)
print("7. Seasonal decomposition (daily data, period=7) …")

try:
    decomp = seasonal_decompose(daily.dropna(), model="additive", period=7)
    fig, axes = plt.subplots(4, 1, figsize=(18, 10), sharex=True)
    for ax, (name, series) in zip(axes, [
        ("Observed", decomp.observed),
        ("Trend", decomp.trend),
        ("Seasonal", decomp.seasonal),
        ("Residual", decomp.resid),
    ]):
        ax.plot(series.index, series.values, linewidth=0.6, color="steelblue")
        ax.set_ylabel(name)
        ax.set_title(name)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "eda_seasonal_decompose.png"))
    plt.close()
    print("   → eda_seasonal_decompose.png")
except Exception as e:
    print(f"   Skipped: {e}")

# ===================== 8. Correlation Heatmap =====================
print("\n" + "=" * 60)
print("8. Correlation heatmap …")

corr = df.corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
fig, ax = plt.subplots(figsize=(11, 9))
sns.heatmap(corr, mask=mask, annot=True, fmt=".3f",
            cmap="RdBu_r", center=0, square=True,
            linewidths=0.5, cbar_kws={"shrink": 0.8},
            vmin=-1, vmax=1)
ax.set_title("Correlation Matrix of Household Power Variables", fontsize=14, pad=16)
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eda_correlation_heatmap.png"))
plt.close()
print("   → eda_correlation_heatmap.png")

# ===================== 9. Power variation heatmap (dates × hours) =====================
print("\n" + "=" * 60)
print("9. Power variation heatmap (last 60 days × 24 hours) …")

# Use last 60 days of hourly data
df_last60 = df_hourly.loc[df_hourly.index[-1] - pd.DateOffset(days=60):]
pivot = df_last60.pivot_table(
    values="Global_active_power",
    index=df_last60.index.date,
    columns=df_last60.index.hour,
    aggfunc="mean"
)
# Sort by date descending (most recent at top)
pivot = pivot.sort_index(ascending=False)

fig, ax = plt.subplots(figsize=(16, 10))
sns.heatmap(pivot, cmap="YlOrRd", ax=ax,
            cbar_kws={"label": "Global Active Power (kW)", "shrink": 0.8},
            xticklabels=1)
ax.set_title("Power Variation Heatmap — Last 60 Days × 24 Hours", fontsize=14, pad=12)
ax.set_xlabel("Hour of Day")
ax.set_ylabel("Date")
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eda_power_heatmap.png"))
plt.close()
print("   → eda_power_heatmap.png")

# ===================== 10. Hour-of-day / day-of-week boxplots =====================
print("\n" + "=" * 60)
print("10. Hour-of-day & day-of-week patterns …")

df_h = df_hourly.copy()
df_h["hour"] = df_h.index.hour
df_h["dayofweek"] = df_h.index.dayofweek

fig, axes = plt.subplots(1, 2, figsize=(16, 6))
# Hour-of-day
sns.boxplot(x="hour", y="Global_active_power", data=df_h,
            color="steelblue", fliersize=1, ax=axes[0])
axes[0].set_title("Global Active Power by Hour of Day")
axes[0].set_xlabel("Hour")
axes[0].set_ylabel("kW")

# Day-of-week (0=Mon, 6=Sun)
sns.boxplot(x="dayofweek", y="Global_active_power", data=df_h,
            color="firebrick", fliersize=1, ax=axes[1])
axes[1].set_xticklabels(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
axes[1].set_title("Global Active Power by Day of Week")
axes[1].set_xlabel("")
axes[1].set_ylabel("kW")
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eda_time_patterns.png"))
plt.close()
print("   → eda_time_patterns.png")

# ===================== 11. ACF & PACF =====================
print("\n" + "=" * 60)
print("11. ACF / PACF plots (daily data) …")

fig, axes = plt.subplots(1, 2, figsize=(16, 5))
plot_acf(daily.dropna(), lags=60, ax=axes[0])
axes[0].set_title("Autocorrelation (ACF) — Daily Power")
plot_pacf(daily.dropna(), lags=60, ax=axes[1], method="ywm")
axes[1].set_title("Partial Autocorrelation (PACF) — Daily Power")
plt.tight_layout()
fig.savefig(os.path.join(OUT_DIR, "eda_acf_pacf.png"))
plt.close()
print("   → eda_acf_pacf.png")

print("\n" + "=" * 60)
print(f"EDA complete. All figures saved to {OUT_DIR}/")
print("=" * 60)
