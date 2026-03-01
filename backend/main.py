import os
import json
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List

# Local imports
try:
    from agent import build_agent, ask_agent
    import database as db
except ImportError:
    # Handle imports when running from different locations
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from agent import build_agent, ask_agent
    import database as db

app = FastAPI(title="CareerBot AI Backend")

# Enable CORS for React frontend (Vite defaults to 5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Agent State
agent_executor = None
agent_memory = None

def get_agent():
    global agent_executor, agent_memory
    if agent_executor is None:
        executor, memory = build_agent()
        agent_executor = executor
        agent_memory = memory
    return agent_executor

class ChatRequest(BaseModel):
    message: str
    filters: Optional[dict] = None

class SaveJobRequest(BaseModel):
    job: dict

@app.get("/api")
async def root():
    return {"status": "CareerBot API is live", "market": "India"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        executor = get_agent()
        response = ask_agent(executor, request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/saved")
async def get_saved_jobs():
    return db.get_saved_jobs()

@app.post("/api/jobs/save")
async def save_job(request: SaveJobRequest):
    ok = db.save_job(request.job)
    return {"success": ok}

@app.delete("/api/jobs/saved/{job_id}")
async def delete_job(job_id: int):
    db.delete_saved_job(job_id)
    return {"success": True}

# Serve React Frontend
# In Docker, the built files will be in /app/frontend/dist
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if not os.path.exists(frontend_path):
    # Fallback if running directly from backend folder
    frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")

if os.path.exists(frontend_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    # Catch-all route to serve index.html for SPA rendering
    @app.get("/{full_path:path}")
    async def serve_react_app(request: Request, full_path: str):
        # Don't intercept /api/ calls if somehow they reach here
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        
        # Check if the requested file exists in the dist root (like vite.svg, favicon, etc)
        file_path = os.path.join(frontend_path, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Default to index.html for all other routes
        return FileResponse(os.path.join(frontend_path, "index.html"))
else:
    print(f"Warning: Frontend build folder not found at {frontend_path}. Frontend will not be served.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
