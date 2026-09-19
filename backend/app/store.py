from __future__ import annotations

import time
from threading import Lock

from app.cases import get_case
from app.catalog import fingerprint
from app.models import PatientCase, Session

_lock = Lock()
_cases: dict[str, PatientCase] = {}
_sessions: dict[str, Session] = {}
_recent: list[str] = []
_current_circuit: list[str] = []
_last_circuit_at = 0.0
CIRCUIT_DEBOUNCE_SEC = 2.5
RECENT_LIMIT = 48


def add_case(case: PatientCase) -> PatientCase:
    with _lock:
        _cases[case.id] = case
        return case


def find_case(case_id: str) -> PatientCase | None:
    with _lock:
        if case_id in _cases:
            return _cases[case_id]
        return get_case(case_id)


def recent_fingerprints() -> list[str]:
    with _lock:
        return list(_recent)


def current_circuit() -> list[PatientCase]:
    with _lock:
        return [_cases[case_id] for case_id in _current_circuit if case_id in _cases]


def should_reuse_circuit() -> bool:
    with _lock:
        return bool(_current_circuit) and (time.time() - _last_circuit_at) < CIRCUIT_DEBOUNCE_SEC


def save_circuit(cases: list[PatientCase]) -> list[PatientCase]:
    global _last_circuit_at, _current_circuit
    with _lock:
        ids: list[str] = []
        for case in cases:
            _cases[case.id] = case
            ids.append(case.id)
            _recent.append(fingerprint(case))
        _recent[:] = _recent[-RECENT_LIMIT:]
        _current_circuit = ids
        _last_circuit_at = time.time()
        return cases


def add_session(session: Session) -> Session:
    with _lock:
        _sessions[session.id] = session
        return session


def find_session(session_id: str) -> Session | None:
    with _lock:
        return _sessions.get(session_id)


def save_session(session: Session) -> Session:
    with _lock:
        _sessions[session.id] = session
        return session
