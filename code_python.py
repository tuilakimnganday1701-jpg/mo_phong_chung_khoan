import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection, PatchCollection

def generate_stock_video(csv_path: str, output_video_path: str):
    
    # 1. NẠP VÀ TIỀN XỬ LÝ DỮ LIỆU TỪ TỆP ĐƯỢC TẢI LÊN
    df_raw = pd.read_csv(csv_path, header=None)
    n_days = len(df_raw)
    n_candles = n_days
    n_total_days = n_days
    x_positions = np.arange(n_days)

    open_prices = df_raw.iloc[:, 0].values
    close_prices = df_raw.iloc[:, -1].values
    high_prices = df_raw.max(axis=1).values
    low_prices = df_raw.min(axis=1).values

    ref_prices = np.roll(close_prices, 1)
    ref_prices[0] = open_prices[0]

    floor_prices = ref_prices * 0.90
    ceiling_prices = ref_prices * 1.10

    # 2. THIẾT LẬP GIAO DIỆN CHO VIDEO 
    plt.style.use('dark_background')
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), facecolor='black')
    fig.subplots_adjust(left=0.08, right=0.95, top=0.95, bottom=0.15, hspace=0.25)
    y_max_limit = max(high_prices) * 1.1

    # --- ĐỒ THỊ 1 ---
    ax1.set_facecolor('black')
    ax1.set_ylabel('VND', color='white', fontsize=8)
    ax1.set_xlim(-2, n_total_days + 5)
    ax1.set_ylim(0, y_max_limit)
    ax1.set_xticks(range(0, n_total_days + 1, 30))
    ax1.tick_params(colors='white', labelsize=8)
    ax1.grid(True, linestyle='--', alpha=0.3)

    line_coll = LineCollection([], linewidths=1.2)
    patch_coll = PatchCollection([], match_original=False)
    ax1.add_collection(line_coll)
    ax1.add_collection(patch_coll)

    # --- ĐỒ THỊ 2 ---
    ax2.set_facecolor('black')
    ax2.set_xlabel('Ngày (0 - 365)', color='white', fontsize=8, fontweight='bold')
    ax2.set_ylabel('VND', color='white', fontsize=8, fontweight='bold')
    ax2.set_xlim(-2, n_total_days + 5)
    ax2.set_ylim(0, y_max_limit)
    ax2.set_xticks(range(0, n_total_days + 1, 30))
    ax2.tick_params(colors='#888888', labelsize=8)
    ax2.grid(True, linestyle=':', alpha=0.2, color='#FFFFFF')

    line_full, = ax2.plot([],[], color='yellowgreen', linewidth=1.5, label='Giá Đóng cửa')
    line_max, = ax2.plot([], [], color='green', linestyle='--', linewidth=1, alpha=0.7, label='Giá Max')
    line_min, = ax2.plot([], [], color='red', linestyle='--', linewidth=1, alpha=0.7, label='Giá Min')

    fill_poly = ax2.fill_between([], [], [], alpha=0.12, zorder=1)

    dot_max, = ax2.plot([], [], 'o', color='green', markersize=6, zorder=5) 
    dot_min, = ax2.plot([], [], 'o', color='red', markersize=6, zorder=5) 

    text_max_point = ax2.text(0, 0, '', color='green', fontsize=8, fontweight='bold', ha='center', va='bottom')
    text_min_point = ax2.text(0, 0, '', color='red', fontsize=8, fontweight='bold', ha='center', va='top')

    ref_line     = ax2.axhline(0, color='#FFD700', linestyle='--', linewidth=1, alpha=0)
    ceiling_line = ax2.axhline(0, color='#AB47BC', linestyle='--', linewidth=1, alpha=0)
    floor_line   = ax2.axhline(0, color="#0066FF", linestyle='--', linewidth=1, alpha=0)

    legend_elements = [
        line_max,
        line_min,
        Line2D([0], [0], color='#FFD700', lw=1.5, ls='--', label='Giá Tham chiếu '),
        Line2D([0], [0], color='#AB47BC', lw=1.5, ls='--', label
