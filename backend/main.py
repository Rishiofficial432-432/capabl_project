import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

@app.get("/")
async def root():
    return {"status": "CareerBot API is live", "market": "India"}

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        executor = get_agent()
        # Enforce the same 'build_query' logic from app.py here if needed, 
        # or handle it in the frontend. We'll pass the message directly for now.
        response = ask_agent(executor, request.message)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/saved")
async def get_saved_jobs():
    return db.get_saved_jobs()

@app.post("/jobs/save")
async def save_job(request: SaveJobRequest):
    ok = db.save_job(request.job)
    return {"success": ok}

@app.delete("/jobs/saved/{job_id}")
async def delete_job(job_id: int):
    db.delete_saved_job(job_id)
    return {"success": True}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
