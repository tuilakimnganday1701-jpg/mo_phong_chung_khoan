import os
import shutil
import uuid
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

# BẮT BUỘC PHẢI CÓ name="static" ĐỂ url_for NHẬN DIỆN ĐƯỢC
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Thư mục lưu trữ tệp CSV tải lên
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """API nhận tệp CSV, kiểm tra định dạng và trả về video tương ứng với tên tệp"""
    try:
        # Kiểm tra phần mở rộng tệp có phải là .csv không
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension != ".csv":
            return JSONResponse(
                status_code=400, 
                content={"success": False, "error": "Chỉ chấp nhận tệp có định dạng .csv!"}
            )
        
        # Tạo tên tệp độc nhất để tránh bị trùng lặp trong thư mục uploads
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Lấy tên gốc của tệp CSV (không bao gồm phần mở rộng .csv)
        # Ví dụ: người dùng tải lên "abc-21.csv" thì base_name sẽ là "abc-21"
        base_name = os.path.splitext(file.filename)[0]
        
        # Đường dẫn tới video tương ứng trong thư mục static/video/
        target_video_path = os.path.join("static", "video", f"{base_name}.mp4")
        
        # Kiểm tra xem trong thư mục static/video/ đã có video ứng với tên tệp này chưa
        if os.path.exists(target_video_path):
            video_url = f"/static/video/{base_name}.mp4"
        else:
            # Nếu chưa có video riêng tương ứng, fallback về video mặc định
            video_url = f"/static/video/mo_phong_chung_khoan.mp4"
            
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "video_url": video_url
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
