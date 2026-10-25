import os
import shutil
import uuid
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# IMPORT HÀM TỪ TỆP CODE RIÊNG CỦA BẠN
from code_python import generate_stock_video

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "static/uploads"
VIDEO_DIR = "static/video"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """API nhận tệp CSV, gọi code Python riêng để tạo video và trả về kết quả"""
    try:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension != ".csv":
            return JSONResponse(
                status_code=400, 
                content={"success": False, "error": "Chỉ chấp nhận tệp có định dạng .csv!"}
            )
        
        # Lưu tệp CSV tải lên
        base_name = os.path.splitext(file.filename)[0]
        csv_save_path = os.path.join(UPLOAD_DIR, f"{base_name}_{uuid.uuid4()}{file_extension}")
        
        with open(csv_save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Đường dẫn tệp video đầu ra tương ứng (ví dụ: static/video/abc-21.mp4)
        output_video_filename = f"{base_name}.mp4"
        output_video_path = os.path.join(VIDEO_DIR, output_video_filename)
        
        # GỌI HÀM TỪ TỆP code_python.py ĐỂ TỰ ĐỘNG TẠO VIDEO NẾU CHƯA CÓ
        if not os.path.exists(output_video_path):
            generate_stock_video(csv_save_path, output_video_path)

        video_url = f"/static/video/{output_video_filename}"
            
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
