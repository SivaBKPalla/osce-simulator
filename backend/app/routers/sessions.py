from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app import store
from app.llm import evaluate_session, patient_reply
from app.models import (
    ChatMessage,
    ChatRequest,
    EvaluationRequest,
    EvaluationResult,
    Session,
    VisibleCase,
    new_id,
    to_visible,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


class StartSessionRequest(BaseModel):
    case_id: str


class SessionResponse(BaseModel):
    session: Session
    case: VisibleCase


@router.post("", response_model=SessionResponse)
def start_session(payload: StartSessionRequest) -> SessionResponse:
    case = store.find_case(payload.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    session = store.add_session(Session(id=new_id(), case_id=case.id))
    return SessionResponse(session=session, case=to_visible(case))


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str) -> SessionResponse:
    session = store.find_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    case = store.find_case(session.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return SessionResponse(session=session, case=to_visible(case))


@router.post("/{session_id}/chat", response_model=ChatMessage)
async def chat(session_id: str, payload: ChatRequest) -> ChatMessage:
    session = store.find_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.submitted:
        raise HTTPException(status_code=400, detail="This station has already been submitted")
    if not payload.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    case = store.find_case(session.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    student_msg = ChatMessage(role="student", content=payload.message.strip())
    session.messages.append(student_msg)
    reply_text = await patient_reply(case, session.messages[:-1], student_msg.content)
    patient_msg = ChatMessage(role="patient", content=reply_text)
    session.messages.append(patient_msg)
    store.save_session(session)
    return patient_msg


@router.post("/{session_id}/evaluate", response_model=EvaluationResult)
async def evaluate(session_id: str, payload: EvaluationRequest) -> EvaluationResult:
    session = store.find_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    case = store.find_case(session.case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    result = await evaluate_session(case, session.messages, payload)
    session.submitted = True
    store.save_session(session)
    return result
