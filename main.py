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

@app.get("/GemGenerated_Image_1q3821q3821q3821.png")
async def get_image():
    return FileResponse(os.path.join(BASE_DIR, "GemGenerated_Image_1q3821q3821q3821.png"))

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
                "resolutions": ['144p', '480p', '720p', '1080p', '1440p']
            }
    except Exception as e:
        return {"error": str(e)}

@app.get("/download")
async def download(url: str, resolution: str):