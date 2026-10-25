import os
import shutil
import uuid
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Import hàm xử lý video từ tệp code_python.py
from code_python import generate_stock_video

app = FastAPI(title="Stock Video Simulation API", version="1.0.0")

# Cấu hình đường dẫn tệp tĩnh (CSS, JS, Video, Uploads)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Cấu hình giao diện HTML templates
templates = Jinja2Templates(directory="templates")

# Khởi tạo thư mục lưu trữ nếu chưa tồn tại
UPLOAD_DIR = "static/uploads"
VIDEO_DIR = "static/video"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Trang chủ hiển thị giao diện web (index.html)"""
    return templates.TemplateResponse(request, "index.html", {})

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    API nhận tệp CSV từ giao diện:
    1. Kiểm tra định dạng tệp.
    2. Lưu tệp CSV vào thư mục uploads với tên định danh độc nhất.
    3. Kiểm tra xem video tương ứng đã tồn tại chưa; nếu chưa, gọi code Python để render.
    4. Trả về đường dẫn video URL cho giao diện hiển thị.
    """
    try:
        # Kiểm tra phần mở rộng tệp
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension != ".csv":
            return JSONResponse(
                status_code=400, 
                content={"success": False, "error": "Chỉ chấp nhận tệp có định dạng .csv!"}
            )
        
        # Lưu tệp CSV tải lên với UUID để tránh trùng lặp tên
        base_name = os.path.splitext(file.filename)[0]
        csv_save_path = os.path.join(UPLOAD_DIR, f"{base_name}_{uuid.uuid4()}{file_extension}")
        
        with open(csv_save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Đường dẫn tệp video đầu ra tương ứng
        output_video_filename = f"{base_name}.mp4"
        output_video_path = os.path.join(VIDEO_DIR, output_video_filename)
        
        # Gọi hàm render video từ code_python.py nếu chưa có sẵn
        if not os.path.exists(output_video_path):
            generate_stock_video(csv_save_path, output_video_path)

        video_url = f"/static/video/{output_video_filename}"
            
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "video_url": video_url
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"success": False, "error": f"Lỗi hệ thống: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
