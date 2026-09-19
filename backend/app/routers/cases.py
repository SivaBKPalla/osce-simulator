from fastapi import APIRouter, HTTPException

from app import store
from app.llm import generate_case, generate_circuit
from app.models import GenerateCaseRequest, VisibleCase, to_visible

router = APIRouter(prefix="/api/cases", tags=["cases"])
CIRCUIT_SIZE = 6


@router.get("", response_model=list[VisibleCase])
async def list_cases() -> list[VisibleCase]:
    return [to_visible(case) for case in store.current_circuit()]


@router.post("/circuit", response_model=list[VisibleCase])
async def new_circuit(force: bool = False) -> list[VisibleCase]:
    if not force and store.should_reuse_circuit():
        return [to_visible(case) for case in store.current_circuit()]
    cases = await generate_circuit(CIRCUIT_SIZE, store.recent_fingerprints())
    store.save_circuit(cases)
    return [to_visible(case) for case in cases]


@router.get("/{case_id}", response_model=VisibleCase)
def get_case(case_id: str) -> VisibleCase:
    case = store.find_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return to_visible(case)


@router.post("/generate", response_model=VisibleCase)
async def create_case(payload: GenerateCaseRequest) -> VisibleCase:
    case = await generate_case(payload.presenting_complaint, payload.age, payload.gender)
    store.add_case(case)
    return to_visible(case)
