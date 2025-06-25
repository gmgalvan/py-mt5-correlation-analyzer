# 📈 High-Frequency Forex Tick Analysis - Currency Correlation Discovery
# 🚀 Real-time EUR/USD vs USD/JPY relationship analyzer
# 📅 Sampling Date: Tuesday, June 24, 2025

import MetaTrader5 as mt5
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timezone

# 🔧 ---------- CONFIG ---------- 🔧
symbols       = ["EURUSD", "USDJPY"]  # 💱 Major currency pairs to analyze
resample_freq = "1s"                  # ⏰ 1-second high-frequency sampling
sampling_date = "June 24, 2025"       # 📅 Today's trading session
# -------------------------------- 🎯

def download_ticks(symbol, utc_from, utc_to):
    """
    📥 Download tick data from MetaTrader 5
    """
    if not mt5.symbol_select(symbol, True):
        raise RuntimeError(f"❌ Cannot select {symbol}")
    
    ticks = mt5.copy_ticks_range(symbol, utc_from, utc_to, mt5.COPY_TICKS_ALL)
    
    if ticks is None or ticks.size == 0:
        raise RuntimeError(f"❌ No ticks for {symbol}: {mt5.last_error()}")
    
    # 🔄 Convert to DataFrame and process timestamps  
    df = pd.DataFrame(ticks)
    df["time"] = pd.to_datetime(df["time"], unit="s", utc=True)
    df.sort_values("time", inplace=True)
    
    # 💾 Save raw data
    filename = f"ticks_{symbol}_{sampling_date.replace(' ', '_').replace(',', '')}.csv"
    df.to_csv(filename, index=False)
    print(f"✅ {symbol}: {len(df):,} ticks")
    
    return df

def main():
    """
    🎯 Main analysis pipeline
    """
    print("🚀 Forex Tick Analysis")
    print(f"📅 {sampling_date}")
    
    # 🔌 Initialize MT5
    if not mt5.initialize():
        print(f"❌ MT5 failed: {mt5.last_error()}")
        return
    print("✅ MT5 connected")

    # ⏰ Set timeframe
    utc_from = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    utc_to   = datetime.now(timezone.utc)

    # 📥 Download data
    data = {}
    try:
        for sym in symbols:
            data[sym] = download_ticks(sym, utc_from, utc_to)
    finally:
        mt5.shutdown()

    # 🔄 Process and align data
    resampled = {
        sym: (df.set_index("time")["bid"]
                .resample(resample_freq).last().ffill())
        for sym, df in data.items()
    }
    
    idx = set.intersection(*(set(s.index) for s in resampled.values()))
    idx = sorted(idx)
    aligned = pd.DataFrame({sym: s.loc[idx] for sym, s in resampled.items()})
    
    print(f"📊 Aligned: {len(aligned):,} intervals")

    # 🧮 Calculate statistics
    diff_ret = aligned.diff().dropna()
    pct_ret  = aligned.pct_change().dropna()

    print("\n📈 === Correlation ===")
    correlation_matrix = pct_ret.corr()
    print(correlation_matrix)
    
    correlation_value = correlation_matrix.iloc[0, 1]
    print(f"\n🔍 {symbols[0]} vs {symbols[1]}: {correlation_value:.6f}")
    
    if correlation_value < -0.3:
        print("📉 Strong negative correlation")
    elif correlation_value > 0.3:
        print("📈 Strong positive correlation")
    else:
        print("⚖️ Moderate correlation")

    # 📈 Create charts
    print("\n🎨 Generating charts...")
    
    # Price chart
    plt.figure(figsize=(12, 6))
    colors = ['#2E86C1', '#E74C3C']
    
    for i, sym in enumerate(symbols):
        plt.plot(aligned.index, aligned[sym], label=f"{sym}", 
                color=colors[i], linewidth=1.2)
    
    plt.title(f"Bid Prices (1-second intervals) - {sampling_date}", 
              fontsize=14, fontweight='bold')
    plt.xlabel("UTC Time", fontsize=12)
    plt.ylabel("Price", fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Scatter plot
    plt.figure(figsize=(10, 8))
    
    plt.scatter(pct_ret[symbols[0]], pct_ret[symbols[1]], 
               s=8, alpha=0.8, color='#3498DB', edgecolors='none')
    
    plt.title(f"Correlation Scatter: 1-second % Returns\n"
              f"{sampling_date} | Correlation: {correlation_value:.3f}", 
              fontsize=14, fontweight='bold')
    plt.xlabel(f"{symbols[0]} % Return", fontsize=12)
    plt.ylabel(f"{symbols[1]} % Return", fontsize=12)
    
    # Info box
    textstr = f'Correlation: {correlation_value:.6f}\nSample Size: {len(pct_ret):,}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    plt.text(0.02, 0.98, textstr, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=props)
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    print("✅ Analysis complete!")

if __name__ == "__main__":
    main()