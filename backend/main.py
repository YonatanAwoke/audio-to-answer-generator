
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import shutil
import os
import uuid
import threading
import time
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import SessionLocal, init_db
from models import User, AudioJob, Transcript, Question, Answer

# Import your pipeline as a function
from orchestration.pipeline import main as pipeline_main

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/register/")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter_by(username=username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=username, password_hash=password)  # Hash in production!
    db.add(user)
    db.commit()
    return {"msg": "Registered"}

@app.post("/api/login/")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(username=username, password_hash=password).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"msg": "Login successful", "user_id": user.id}

def run_pipeline_and_store(job_id, audio_path, user_id, db):
    try:
        # Directly call the pipeline and get the result as a dict
        from orchestration.pipeline import main as pipeline_main
        # pipeline_main should be refactored to accept arguments and return a result dict
        # We'll simulate command-line args using argparse.Namespace
        import types
        args = types.SimpleNamespace(
            audio_file=audio_path,
            output_format='json',
            language=None,
            enhance_audio=False
        )
        # Patch sys.argv for pipeline_main if needed
        import sys
        sys.argv = ["pipeline.py", audio_path, "--output_format", "json"]
        # pipeline_main will save the output to outputs/{job_id}.json
        pipeline_main()
        import os, json
        output_filename = os.path.splitext(os.path.basename(audio_path))[0]
        output_path = f"outputs/{output_filename}.json"
        with open(output_path, "r") as f:
            result = json.load(f)
        job = db.query(AudioJob).get(job_id)
        job.status = 'done'
        job.completed_at = time.strftime('%Y-%m-%d %H:%M:%S')
        # Store transcript
        transcript = Transcript(job_id=job_id, transcript_text=result.get('transcript', ''))
        db.add(transcript)
        # Store questions and answers
        for q in result.get('questions', []):
            question = Question(job_id=job_id, question_text=q['question'])
            db.add(question)
            db.flush()  # get question.id
            for a in result.get('answers', []):
                if a['qid'] == q['id']:
                    answer = Answer(question_id=question.id, answer_text=a['answer'], math_results=result.get('math_results'))
                    db.add(answer)
        db.commit()
    except Exception as e:
        job = db.query(AudioJob).get(job_id)
        job.status = 'error'
        db.commit()

@app.post("/api/upload-audio/")
async def upload_audio(background_tasks: BackgroundTasks, file: UploadFile = File(...), user_id: int = 1, db: Session = Depends(get_db)):
    job_id = str(uuid.uuid4())
    audio_path = os.path.join(UPLOAD_DIR, f"{job_id}_{file.filename}")
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    job = AudioJob(id=job_id, user_id=user_id, filename=file.filename, status='processing')
    db.add(job)
    db.commit()
    background_tasks.add_task(run_pipeline_and_store, job_id, audio_path, user_id, db)
    return {"job_id": job_id}

@app.get("/api/result/{job_id}")
def get_result(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AudioJob).get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status == 'done':
        transcript = db.query(Transcript).filter_by(job_id=job_id).first()
        questions = db.query(Question).filter_by(job_id=job_id).all()
        answers = db.query(Answer).join(Question).filter(Question.job_id==job_id).all()
        return {
            "status": "done",
            "transcript": transcript.transcript_text if transcript else '',
            "questions": [{"id": str(q.id), "question": q.question_text} for q in questions],
            "answers": [{"qid": str(a.question_id), "answer": a.answer_text} for a in answers],
        }
    elif job.status == 'error':
        return {"status": "error"}
    else:
        return {"status": job.status}

@app.get("/api/history/")
def get_history(user_id: int = 1, db: Session = Depends(get_db)):
    jobs = db.query(AudioJob).filter_by(user_id=user_id).order_by(AudioJob.created_at.desc()).all()
    return [{
        "job_id": job.id,
        "filename": job.filename,
        "status": job.status,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    } for job in jobs]
