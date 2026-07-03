from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import yt_dlp
import os
import uuid

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_PATH = os.path.join(BASE_DIR, "cookies.txt")
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/info")
async def get_info(request: Request):
    data = await request.json()
    url = data.get("video_url")
    try:
        ydl_opts = {
            'quiet': True,
            'user_agent': USER_AGENT,
            'cookiefile': COOKIES_PATH,
            'noplaylist': True,
            'sleep_interval': 3,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "resolutions": ['144p', '480p', '720p', '1080p']
            }
    except Exception as e:
        return {"error": f"Info extraction failed: {str(e)}"}

@app.get("/download")
async def download(url: str, resolution: str):
    # إنشاء اسم ملف فريد لكل مستخدم
    file_id = str(uuid.uuid4())
    output_path = f"video_{file_id}.mp4"
    
    # التعديل هنا: استخدام [height<=...] ليكون الاختيار مرناً
    # إذا لم يجد 1080p سيختار تلقائياً 720p أو أقل المتاح
    ydl_opts = {
        'format': f'bestvideo[height<={resolution.replace("p", "")}]+bestaudio/best[height<={resolution.replace("p", "")}]/best[height<={resolution.replace("p", "")}]',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
        'user_agent': USER_AGENT,
        'cookiefile': COOKIES_PATH,
        'noplaylist': True,
        'nocheckcertificate': True,
        'extractor_args': {'youtube': {'player_client': 'web'}},
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # التأكد من أن الملف قد تم إنشاؤه وليس فارغاً
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return FileResponse(path=output_path, media_type='video/mp4', filename='video.mp4')
        else:
            return {"error": "Download failed: The file was not created or is empty."}
            
    except Exception as e:
        return {"error": f"Download failed: {str(e)}"}
