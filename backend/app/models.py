from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Vitals(BaseModel):
    temperature_c: float
    heart_rate: int
    blood_pressure: str
    respiratory_rate: int
    spo2: int
    pain_score: int | None = None


class HiddenSheet(BaseModel):
    """Information the standardized patient knows but the student cannot see."""

    hidden_diagnosis: str
    acceptable_differentials: list[str]
    recommended_next_steps: list[str]
    history_of_present_illness: str
    associated_symptoms: list[str]
    pertinent_negatives: list[str]
    past_medical_history: list[str]
    medications: list[str]
    allergies: list[str]
    social_history: str
    family_history: str
    review_of_systems: str
    personality_notes: str
    teaching_points: list[str]


class PatientCase(BaseModel):
    id: str
    title: str
    presenting_complaint: str
    age: int
    gender: str
    setting: str
    vitals: Vitals
    brief_history: str
    hidden_sheet: HiddenSheet
    generated: bool = False


class VisibleCase(BaseModel):
    id: str
    title: str
    presenting_complaint: str
    age: int
    gender: str
    setting: str
    vitals: Vitals
    brief_history: str
    generated: bool = False


class ChatMessage(BaseModel):
    role: Literal["student", "patient"]
    content: str
    created_at: datetime = Field(default_factory=utc_now)


class Session(BaseModel):
    id: str
    case_id: str
    messages: list[ChatMessage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)
    submitted: bool = False


class RubricScore(BaseModel):
    criterion: str
    score: int
    max_score: int
    comments: str


class EvaluationResult(BaseModel):
    overall_score: int
    max_score: int
    summary: str
    hidden_diagnosis: str
    rubric: list[RubricScore]
    missed_questions: list[str]
    strengths: list[str]
    next_study_focus: list[str]


class GenerateCaseRequest(BaseModel):
    presenting_complaint: str | None = None
    age: int | None = None
    gender: str | None = None


class ChatRequest(BaseModel):
    message: str


class EvaluationRequest(BaseModel):
    differential_1: str
    differential_2: str
    differential_3: str
    next_steps: str


def new_id() -> str:
    return uuid4().hex[:12]


def to_visible(case: PatientCase) -> VisibleCase:
    return VisibleCase(
        id=case.id,
        title=case.title,
        presenting_complaint=case.presenting_complaint,
        age=case.age,
        gender=case.gender,
        setting=case.setting,
        vitals=case.vitals,
        brief_history=case.brief_history,
        generated=case.generated,
    )
