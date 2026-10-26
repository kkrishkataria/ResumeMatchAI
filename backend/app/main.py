import os
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .database import delete_analysis, get_history, save_analysis
from .matcher import build_explanation, calculate_similarity, calculate_skill_similarity
from .resume_parser import MAX_FILE_SIZE, extract_pdf_text, validate_pdf
from .schemas import AnalysisResponse, HistoryResponse
from .skill_extractor import analyze_skill_gap

load_dotenv()
app = FastAPI(title="ResumeMatch AI", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "ResumeMatch AI API is running."}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(resume: UploadFile = File(...), job_description: str = Form(...)):
    if not job_description or not job_description.strip():
        raise HTTPException(status_code=422, detail="Please enter a job description.")

    file_data = await resume.read()
    max_size = int(os.getenv("MAX_UPLOAD_SIZE", MAX_FILE_SIZE))
    try:
        validate_pdf(resume.filename, resume.content_type, file_data, max_size)
        resume_text = extract_pdf_text(file_data)
        # Keep this explainable text measure calculated for future extensions,
        # while the user-facing score is based on recognizable skill coverage.
        calculate_similarity(resume_text, job_description)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    skills = analyze_skill_gap(resume_text, job_description)
    score = calculate_skill_similarity(skills["matched_skills"], skills["job_skills"])
    saved, history_message = save_analysis(score, skills["matched_skills"], skills["missing_skills"], job_description)
    return AnalysisResponse(
        score=score,
        **skills,
        explanation=build_explanation(score, len(skills["matched_skills"]), len(skills["missing_skills"])),
        history_saved=saved,
        history_message=history_message,
    )


@app.get("/history", response_model=HistoryResponse)
def history():
    items, available, message = get_history()
    return HistoryResponse(items=items, available=available, message=message)


@app.delete("/history/{analysis_id}")
def remove_history_item(analysis_id: str):
    deleted, message = delete_analysis(analysis_id)
    if not deleted:
        if message and "invalid" in message:
            status_code = 422
        elif message and "no longer exists" in message:
            status_code = 404
        else:
            status_code = 503
        raise HTTPException(status_code=status_code, detail=message)
    return {"message": "Analysis history item deleted."}

