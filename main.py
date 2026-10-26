import os
import shutil
import uuid
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Cấu hình matplotlib chạy ngầm trên server
matplotlib.use('Agg')

app = FastAPI(title='OHLC Chart API', version='1.0.0')

# Cấu hình đường dẫn tệp tĩnh và template
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

UPLOAD_DIR = 'static/uploads'
IMAGE_DIR = 'static/images'
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)


@app.get('/', response_class=HTMLResponse)
async def read_root(request: Request):
  return templates.TemplateResponse(request, 'index.html', {})


@app.post('/api/upload-csv')
async def upload_csv(file: UploadFile = File(...)):
  try:
    if not file.filename.endswith('.csv'):
      return JSONResponse(
          status_code=400,
          content={
              'success': False,
              'error': 'Chỉ chấp nhận tệp có định dạng .csv!',
          },
      )

    base_name = os.path.splitext(file.filename)[0]
    csv_save_path = os.path.join(
        UPLOAD_DIR, f'{base_name}_{uuid.uuid4()}.csv'
    )

    with open(csv_save_path, 'wb') as buffer:
      shutil.copyfileobj(file.file, buffer)

    # 1. Đọc dữ liệu từ tệp CSV không có tiêu đề
    df_raw = pd.read_csv(csv_save_path, header=None)
    n_total_days = len(df_raw)
    dates = pd.date_range(start='2025-01-01', periods=n_total_days, freq='D')

    df = pd.DataFrame({
        'Date': dates,
        'Open': df_raw.iloc[:, 0].values,
        'High': df_raw.max(axis=1).values,
        'Low': df_raw.min(axis=1).values,
        'Close': df_raw.iloc[:, -1].values,
    })
    df.set_index('Date', inplace=True)

    # 2. Xác định mốc thời gian và giá trị của điểm Max và Min (dựa trên giá Close)
    max_idx = df['Close'].idxmax()
    max_val = df['Close'].loc[max_idx]

    min_idx = df['Close'].idxmin()
    min_val = df['Close'].loc[min_idx]

    # 3. Thiết lập biểu đồ
    fig, ax = plt.subplots(figsize=(12, 6))

    # Vẽ đường giá Đóng cửa (Close)
    ax.plot(
        df.index,
        df['Close'],
        label='Close Price',
        color='blue',
        linewidth=1.5,
        alpha=0.7,
    )

    # Đánh dấu điểm Max bằng màu xanh lá (Green) kèm chú thích giá trị
    ax.scatter(
        max_idx,
        max_val,
        color='green',
        s=120,
        zorder=5,
        label=f'Max: {max_val}',
    )
    ax.annotate(
        f'Max: {max_val}',
        xy=(max_idx, max_val),
        xytext=(0, 10),
        textcoords='offset points',
        ha='center',
        color='green',
        fontweight='bold',
    )

    # Đánh dấu điểm Min bằng màu đỏ (Red) kèm chú thích giá trị
    ax.scatter(
        min_idx,
        min_val,
        color='red',
        s=120,
        zorder=5,
        label=f'Min: {min_val}',
    )
    ax.annotate(
        f'Min: {min_val}',
        xy=(min_idx, min_val),
        xytext=(0, -15),
        textcoords='offset points',
        ha='center',
        color='red',
        fontweight='bold',
    )

    # 4. Tùy chỉnh trục thời gian cách nhau 30 ngày
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=30))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    # 5. Định dạng tổng thể biểu đồ
    ax.set_title('Biểu đồ giá Close với điểm Max (Xanh) và Min (Đỏ)', fontsize=14)
    ax.set_xlabel('Thời gian', fontsize=12)
    ax.set_ylabel('Giá trị', fontsize=12)
    ax.legend()
    ax.grid(True)
    plt.tight_layout()

    # 6. Lưu hình ảnh vào thư mục static/images
    output_image_filename = f'{base_name}_{uuid.uuid4().hex[:8]}.png'
    output_image_path = os.path.join('static/images', output_image_filename)
    plt.savefig(output_image_path, format='png', bbox_inches='tight')
    plt.close(fig)

    image_url = f'/static/images/{output_image_filename}'

    return JSONResponse(
        content={'success': True, 'filename': file.filename, 'image_url': image_url}
    )

  except Exception as e:
    return JSONResponse(
        status_code=500,
        content={'success': False, 'error': f'Lỗi hệ thống: {str(e)}'},
    )


if __name__ == '__main__':
  import uvicorn

  uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
