import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter
from matplotlib.widgets import Slider
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection, PatchCollection

# ==============================================================================
#  1. NẠP VÀ TIỀN XỬ LÝ DỮ LIỆU
# ==============================================================================
file_path = 'abc-20.csv'

df_raw = pd.read_csv(file_path, header=None)
n_days = len(df_raw)
n_candles = n_days
n_total_days = n_days
x_positions = np.arange(n_days)

dates = pd.date_range(start='2025-01-01', periods=n_days, freq='D')

open_prices = df_raw.iloc[:, 0].values
close_prices = df_raw.iloc[:, -1].values
high_prices = df_raw.max(axis=1).values
low_prices = df_raw.min(axis=1).values

ref_prices = np.roll(close_prices, 1)
ref_prices[0] = open_prices[0]

floor_prices = ref_prices * 0.90
ceiling_prices = ref_prices * 1.10

# ==============================================================================
#  2. THIẾT LẬP GIAO DIỆN CHO VIDEO 
# ==============================================================================
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

line_full, = ax2.plot([],[],
                       color='yellowgreen',
                       linewidth=1.5,
                       label='Giá Đóng cửa')
line_max, = ax2.plot([], [], 
                     color='green', 
                     linestyle='--', 
                     linewidth=1, 
                     alpha=0.7, 
                     label='Giá Max')
line_min, = ax2.plot([], [], 
                    color='red',
                    linestyle='--',
                    linewidth=1,
                    alpha=0.7,
                    label='Giá Min')

fill_poly = ax2.fill_between([], [], [], alpha=0.12, zorder=1)

# TẠO ĐIỂM CHẤM VÀ TEXT ĐÁNH DẤU ĐỈNH/ĐÁY (MAX/MIN)
dot_max, = ax2.plot([], [], 'o', color='green', markersize=6, zorder=5) 
dot_min, = ax2.plot([], [], 'o', color='red', markersize=6, zorder=5) 

text_max_point = ax2.text(0, 0, '',
                          color='green',
                          fontsize=8,
                          fontweight='bold',
                          ha='center',
                          va='bottom')
text_min_point = ax2.text(0, 0, '',
                          color='red',
                          fontsize=8,
                          fontweight='bold',
                          ha='center',
                          va='top')


# KHAI BÁO CÁC ĐƯỜNG MỐC GIÁ
ref_line     = ax2.axhline(0, color='#FFD700', linestyle='--', linewidth=1, alpha=0)
ceiling_line = ax2.axhline(0, color='#AB47BC', linestyle='--', linewidth=1, alpha=0)
floor_line   = ax2.axhline(0, color="#0066FF", linestyle='--', linewidth=1, alpha=0)

legend_elements = [
    line_max,
    line_min,
    Line2D([0], [0], color='#FFD700', lw=1.5, ls='--', label='Giá Tham chiếu '),
    Line2D([0], [0], color='#AB47BC', lw=1.5, ls='--', label='Giá Trần'),
    Line2D([0], [0], color='#0066FF', lw=1.5, ls='--', label='Giá Sàn')
]

legend_box = ax2.legend(
    handles=legend_elements,
    loc='upper right',
    fontsize=8,
    facecolor='#111111',
    edgecolor='#555555',
    labelcolor='white',
    framealpha=0.85
)

text_x_pos = n_total_days - 10
text_ref   = ax2.text(text_x_pos, 0, '', color='#FFD700', fontsize=8, fontweight='bold', va='center') 
text_ceil  = ax2.text(text_x_pos, 0, '', color='#AB47BC', fontsize=8, va='center')                    
text_floor = ax2.text(text_x_pos, 0, '', color='#0066FF', fontsize=8, va='center')  

# ==============================================================================
#  3. HÀM CẬP NHẬT HOẠT HÌNH (UPDATE)
# ==============================================================================
def update(frame):
    i = frame
    
    # --- ĐỒ THỊ 1 ---
    segments = []
    patches = []
    colors = []

    for idx in range(0, i + 1):
        x_pos = x_positions[idx]
        o, c = open_prices[idx], close_prices[idx]
        h, l = high_prices[idx], low_prices[idx]
        ref = ref_prices[idx]
        
        color = "green" if c >= ref else "red"
        colors.append(color) 

        segments.append([(x_pos, l), (x_pos, h)])
        
        body_bottom = min(o, c)
        min_height = o * 0.001 if o != 0 else 0.01
        body_height = max(abs(c - o), min_height)
        
        rect = Rectangle((x_pos - 0.9, body_bottom), 1.8, body_height)
        patches.append(rect)

    line_coll.set_segments(segments)
    line_coll.set_color(colors)
    
    patch_coll.set_paths(patches)
    patch_coll.set_facecolor(colors)
    patch_coll.set_edgecolor(colors)

    # --- ĐỒ THỊ 2 ---
    x_data = x_positions[:i + 1]
    y_close = close_prices[:i + 1]
    y_min_data = low_prices[:i + 1]
    y_max_data = high_prices[:i + 1]
    
    line_full.set_data(x_data, y_close)
    line_min.set_data(x_data, y_min_data)
    line_max.set_data(x_data, y_max_data)

    # TÍNH VÀ CẬP NHẬT CHẤM TRÒN TẠI ĐỈNH CAO NHẤT / THẤP NHẤT
    idx_max = np.argmax(y_max_data)
    idx_min = np.argmin(y_min_data)

    x_max, val_max = x_data[idx_max], y_max_data[idx_max]
    x_min, val_min = x_data[idx_min], y_min_data[idx_min]

    dot_max.set_data([x_max], [val_max])
    text_max_point.set_position((x_max, val_max + (y_max_limit * 0.02)))
    text_max_point.set_text(f"{val_max:,.0f}")

    dot_min.set_data([x_min], [val_min])
    text_min_point.set_position((x_min, val_min - (y_max_limit * 0.02)))
    text_min_point.set_text(f" {val_min:,.0f}")

    cur_close = close_prices[i]
    cur_ref   = ref_prices[i]
    cur_ceil  = ceiling_prices[i]
    cur_floor = floor_prices[i]

    fill_color = "green" if cur_close >= cur_ref else "red"
    
    if i > 0:
        pts_x = np.concatenate([x_data, x_data[::-1]])
        pts_y = np.concatenate([y_max_data, y_min_data[::-1]])
        fill_poly.set_verts([np.column_stack([pts_x, pts_y])])
        fill_poly.set_facecolor(fill_color)
    else:
        fill_poly.set_verts([])
        
    ref_line.set_ydata([cur_ref, cur_ref])
    ref_line.set_alpha(0.8)

    ceiling_line.set_ydata([cur_ceil, cur_ceil])
    ceiling_line.set_alpha(0.8)

    floor_line.set_ydata([cur_floor, cur_floor])
    floor_line.set_alpha(0.8)
    
    text_ref.set_position((text_x_pos, cur_ref))
    text_ref.set_text(f"{cur_ref:,.0f}")
    
    text_ceil.set_position((text_x_pos, cur_ceil))
    text_ceil.set_text(f"{cur_ceil:,.0f}")
    
    text_floor.set_position((text_x_pos, cur_floor))
    text_floor.set_text(f"{cur_floor:,.0f}")

    slider_time.eventson = False  
    slider_time.set_val(i)      
    slider_time.eventson = True   

    return (
        line_coll, patch_coll, line_full, line_min, line_max, 
        fill_poly, dot_max, dot_min, text_max_point, text_min_point,
        ref_line, ceiling_line, floor_line, 
        text_ref, text_ceil, text_floor
    )

# Tạo giao diện cho thanh điều khiển (Slider)
ax_slider = plt.axes([0.15, 0.03, 0.75, 0.03])

slider_time = Slider(
    ax_slider, 'Khung hình', 0, n_candles - 1,
    valinit=0, valstep=1, color='#26A69A'
)

def on_slider_change(val):
    frame = int(val)
    update(frame)
    fig.canvas.draw_idle() 

slider_time.on_changed(on_slider_change)

# ==============================================================================
#  4. XUẤT VIDEO
# ==============================================================================
ani = animation.FuncAnimation(
    fig, 
    update, 
    frames=n_candles, 
    interval=500, 
    repeat=False, 
    blit=False
)

ffmpeg_path = "ffmpeg"

writer = FFMpegWriter(
    fps=max(5, int(n_candles / 10)), 
    metadata=dict(artist='Kim Ngan'), 
    bitrate=1800, 
    codec='libx264',
    extra_args=['-pix_fmt', 'yuv420p']
)
writer.executable = ffmpeg_path

print(">>> Đang tiến hành xuất video MP4, vui lòng đợi trong giây lát...")
#ani.save("mo_phong_chung_khoan.mp4", writer=writer, dpi=200)
print("Đã xuất file video thành công: mo_phong_chung_khoan.mp4")

plt.show()