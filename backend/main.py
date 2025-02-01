from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
import yt_dlp
import os
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure downloads folder exists
os.makedirs("downloads", exist_ok=True)

# Store active WebSocket connections
active_connections = set()

class VideoRequest(BaseModel):
    url: str
    format: str  # "mp3" or "mp4"

async def send_progress(progress_data):
    """Broadcast progress updates to all connected WebSocket clients."""
    message = {"progress": progress_data["downloaded_bytes"] / progress_data["total_bytes"] * 100}
    
    # Send progress to all active clients
    for websocket in active_connections:
        try:
            await websocket.send_json(message)
        except:
            active_connections.remove(websocket)  # Remove broken connections

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except:
        pass
    finally:
        active_connections.remove(websocket)

@app.post("/download")
async def download_video(request: VideoRequest):
    """Start downloading a YouTube video asynchronously and send progress updates."""
    output_path = f"downloads/%(title)s.{'mp3' if request.format == 'mp3' else 'mp4'}"
    
    def progress_hook(d):
        """Hook to send real-time progress updates via WebSocket."""
        if d["status"] == "downloading":
            asyncio.run(send_progress(d))  # Ensures WebSocket updates

    ydl_opts = {
        "format": "bestaudio/best" if request.format == "mp3" else "best",
        "outtmpl": output_path,
        "progress_hooks": [progress_hook],
    }

    # Run yt_dlp in a non-blocking thread
    await asyncio.to_thread(lambda: yt_dlp.YoutubeDL(ydl_opts).download([request.url]))

    return {"message": "Download started"}
