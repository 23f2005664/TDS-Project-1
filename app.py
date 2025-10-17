from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
import os
import json
import time
import requests
from models import Request, Notification
from generator import generate_app
from github_handler import create_or_update_repo

app = FastAPI()

MY_SECRET = os.getenv("MY_SECRET", "default-secret")

@app.post("/api")
async def handle_request(request_data: dict):
    try:
        req = Request(**request_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if req.secret != MY_SECRET:
        raise HTTPException(status_code=401, detail="Invalid secret")

    files = generate_app(req.brief, req.attachments, req.task, req.round, req.checks)

    repo_info = create_or_update_repo(req.task, req.round, files, os.getenv("GITHUB_TOKEN"))

    notification = Notification(
        email=req.email,
        task=req.task,
        round=req.round,
        nonce=req.nonce,
        repo_url=repo_info['repo_url'],
        commit_sha=repo_info['commit_sha'],
        pages_url=repo_info['pages_url']
    )
    notify_evaluation(req.evaluation_url, notification)

    return {"status": "success"}

def notify_evaluation(url: str, notification: Notification):
    data = notification.dict()
    try:
        resp = requests.post(url, json=data, timeout=10)
        if resp.status_code != 200:
            for delay in [1, 2, 4, 8]:
                time.sleep(delay)
                resp = requests.post(url, json=data, timeout=10)
                if resp.status_code == 200:
                    break
    except Exception as e:
        print(f"Notification failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
