from datetime import datetime
from pydantic import BaseModel, Field


class AnalysisResponse(BaseModel):
    # Headline score: matched recognized job skills / recognized job skills.
    score: float = Field(ge=0, le=100)
    resume_skills: list[str]
    job_skills: list[str]
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str
    history_saved: bool
    history_message: str | None = None


class HistoryItem(BaseModel):
    id: str
    timestamp: datetime
    score: float
    score_type: str = "text"  # Older saved records used TF-IDF text similarity.
    matched_skills: list[str]
    missing_skills: list[str]
    job_summary: str | None = None


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    available: bool
    message: str | None = None

