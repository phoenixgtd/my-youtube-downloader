from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import yt_dlp
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.post("/info")
async def get_info(request: Request):
    data = await request.json()
    url = data.get("video_url")
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "resolutions": ['144p', '480p', '720p', '1080p']
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/download")
async def download(url: str, resolution: str):
    # إعدادات التحميل
    output_path = f"video.mp4"
    ydl_opts = {
        'format': f'bestvideo[height<={resolution.replace("p", "")}]+bestaudio/best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return FileResponse(output_path, media_type='video/mp4', filename='video.mp4')
    except Exception as e:
        return {"error": str(e)}
