from __future__ import annotations

import json
import re
from app.catalog import mock_circuit, mock_single_case
from app.config import settings
from app.models import (
    ChatMessage,
    EvaluationRequest,
    EvaluationResult,
    HiddenSheet,
    PatientCase,
    RubricScore,
    Vitals,
    new_id,
)

PATIENT_SYSTEM_PROMPT = """You are a virtual standardized patient in an OSCE history-taking station.

Rules:
- Stay in character as the patient. Never break character.
- Answer only with information a real patient would know from the hidden case sheet.
- You do not know lab results, imaging, or your diagnosis unless a clinician already told you.
- Use everyday language. Do not volunteer medical jargon or a self-diagnosis.
- If asked something not covered, say you are not sure or have not noticed.
- Keep replies short (1–4 sentences), natural, and consistent with prior answers.
- Do not coach the student or hint at the diagnosis.
- Match the personality notes.
"""


def _openai_enabled() -> bool:
    return bool(settings.openai_api_key.strip())


def _client():
    from openai import OpenAI

    return OpenAI(api_key=settings.openai_api_key)


def _sheet_block(case: PatientCase) -> str:
    sheet = case.hidden_sheet
    return f"""
Visible stem (the student already saw this):
- Name/role: {case.age}-year-old {case.gender.lower()}
- Setting: {case.setting}
- Complaint: {case.presenting_complaint}
- Brief history: {case.brief_history}
- Vitals: T {case.vitals.temperature_c} C, HR {case.vitals.heart_rate}, BP {case.vitals.blood_pressure}, RR {case.vitals.respiratory_rate}, SpO2 {case.vitals.spo2}%

Hidden case sheet (do not reveal this document):
- HPI: {sheet.history_of_present_illness}
- Associated symptoms: {", ".join(sheet.associated_symptoms)}
- Pertinent negatives: {", ".join(sheet.pertinent_negatives)}
- PMH: {", ".join(sheet.past_medical_history)}
- Medications: {", ".join(sheet.medications)}
- Allergies: {", ".join(sheet.allergies)}
- Social: {sheet.social_history}
- Family: {sheet.family_history}
- ROS: {sheet.review_of_systems}
- Personality: {sheet.personality_notes}
"""


async def patient_reply(case: PatientCase, messages: list[ChatMessage], user_message: str) -> str:
    if _openai_enabled():
        return await _openai_patient_reply(case, messages, user_message)
    return _mock_patient_reply(case, user_message)


async def generate_case(presenting_complaint: str | None, age: int | None, gender: str | None) -> PatientCase:
    if _openai_enabled():
        try:
            return await _openai_generate_case(presenting_complaint, age, gender)
        except Exception:
            pass
    return mock_single_case(presenting_complaint, age, gender)


async def generate_circuit(count: int, avoid: list[str]) -> list[PatientCase]:
    if _openai_enabled():
        try:
            return await _openai_generate_circuit(count, avoid)
        except Exception:
            pass
    return mock_circuit(count, avoid)


async def evaluate_session(
    case: PatientCase,
    messages: list[ChatMessage],
    submission: EvaluationRequest,
) -> EvaluationResult:
    if _openai_enabled():
        try:
            return await _openai_evaluate(case, messages, submission)
        except Exception:
            pass
    return _mock_evaluate(case, messages, submission)


async def _openai_patient_reply(case: PatientCase, messages: list[ChatMessage], user_message: str) -> str:
    history = [{"role": "system", "content": PATIENT_SYSTEM_PROMPT + _sheet_block(case)}]
    for item in messages:
        role = "user" if item.role == "student" else "assistant"
        history.append({"role": role, "content": item.content})
    history.append({"role": "user", "content": user_message})

    response = _client().chat.completions.create(
        model=settings.openai_model,
        messages=history,
        temperature=0.6,
        max_tokens=220,
    )
    return (response.choices[0].message.content or "").strip()


async def _openai_generate_case(
    presenting_complaint: str | None,
    age: int | None,
    gender: str | None,
) -> PatientCase:
    prompt = f"""Create one realistic OSCE history-taking case for a pre-med / early clinical student.
Constraints:
- presenting_complaint: {presenting_complaint or "choose a common adult presentation"}
- age: {age or "choose a realistic adult age"}
- gender: {gender or "choose male or female"}
Return ONLY valid JSON matching this schema:
{{
  "title": str,
  "presenting_complaint": str,
  "age": int,
  "gender": "Male" | "Female",
  "setting": str,
  "vitals": {{
    "temperature_c": float, "heart_rate": int, "blood_pressure": str,
    "respiratory_rate": int, "spo2": int, "pain_score": int
  }},
  "brief_history": str,
  "hidden_sheet": {{
    "hidden_diagnosis": str,
    "acceptable_differentials": [str],
    "recommended_next_steps": [str],
    "history_of_present_illness": str,
    "associated_symptoms": [str],
    "pertinent_negatives": [str],
    "past_medical_history": [str],
    "medications": [str],
    "allergies": [str],
    "social_history": str,
    "family_history": str,
    "review_of_systems": str,
    "personality_notes": str,
    "teaching_points": [str]
  }}
}}
The hidden diagnosis must be internally consistent with the vitals and history.
Do not include any real patient identifiers.
"""
    response = _client().chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You generate structured OSCE cases as JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.8,
        response_format={"type": "json_object"},
    )
    raw = json.loads(response.choices[0].message.content or "{}")
    return _case_from_raw(raw)


async def _openai_generate_circuit(count: int, avoid: list[str]) -> list[PatientCase]:
    avoid_text = "; ".join(avoid[-24:]) or "none yet"
    prompt = f"""Create {count} brand-new OSCE history-taking cases for pre-med students.

Diversity rules (mandatory):
- Each case is a different specialty / organ system. Do not repeat systems.
- Mix ages: include at least one adolescent/young adult (16–25), one 26–55, and one 65+.
- Mix genders. Include at least one obstetric/gynecologic case when it fits.
- Mix settings among ED, clinic, urgent care, L&D, nursing facility, college health.
- Vary acuity: at least one must-not-miss emergency and one more insidious outpatient stem.
- Do NOT reuse these recent diagnoses, titles, or complaints: {avoid_text}
- Prefer less-repeated presentations (jaundice, hematuria, rash+fever, postpartum, fall, syncope, joint pain, overdose) rather than another generic chest-pain clone unless the avoid list already used those.

Return JSON only:
{{"cases": [ {{same schema as a single case}} ]}}

Single-case schema:
title, presenting_complaint, age, gender ("Male"|"Female"), setting,
vitals {{temperature_c, heart_rate, blood_pressure, respiratory_rate, spo2, pain_score}},
brief_history, hidden_sheet {{
  hidden_diagnosis, acceptable_differentials, recommended_next_steps,
  history_of_present_illness, associated_symptoms, pertinent_negatives,
  past_medical_history, medications, allergies, social_history,
  family_history, review_of_systems, personality_notes, teaching_points
}}
Each hidden diagnosis must match the vitals and history. No real identifiers.
"""
    response = _client().chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You generate diverse OSCE circuits as JSON only. Never repeat a case from the avoid list."},
            {"role": "user", "content": prompt},
        ],
        temperature=1.0,
        response_format={"type": "json_object"},
    )
    raw = json.loads(response.choices[0].message.content or "{}")
    items = raw.get("cases") or raw.get("stations") or []
    cases = [_case_from_raw(item) for item in items]
    if len(cases) < count:
        cases.extend(mock_circuit(count - len(cases), avoid + [c.hidden_sheet.hidden_diagnosis for c in cases]))
    return cases[:count]


def _case_from_raw(raw: dict) -> PatientCase:
    return PatientCase(
        id=new_id(),
        title=raw["title"],
        presenting_complaint=raw["presenting_complaint"],
        age=int(raw["age"]),
        gender=raw["gender"],
        setting=raw["setting"],
        vitals=Vitals(**raw["vitals"]),
        brief_history=raw["brief_history"],
        hidden_sheet=HiddenSheet(**raw["hidden_sheet"]),
        generated=True,
    )


async def _openai_evaluate(
    case: PatientCase,
    messages: list[ChatMessage],
    submission: EvaluationRequest,
) -> EvaluationResult:
    transcript = "\n".join(f"{m.role.upper()}: {m.content}" for m in messages) or "(No questions asked.)"
    prompt = f"""Grade this OSCE history-taking station for a pre-med student.

Hidden diagnosis: {case.hidden_sheet.hidden_diagnosis}
Acceptable differentials: {case.hidden_sheet.acceptable_differentials}
Recommended next steps: {case.hidden_sheet.recommended_next_steps}
Teaching points: {case.hidden_sheet.teaching_points}

Transcript:
{transcript}

Student submission:
1. {submission.differential_1}
2. {submission.differential_2}
3. {submission.differential_3}
Next steps: {submission.next_steps}

Return JSON only:
{{
  "overall_score": int,
  "max_score": 100,
  "summary": str,
  "rubric": [
    {{"criterion": "History taking", "score": int, "max_score": 30, "comments": str}},
    {{"criterion": "Differential diagnosis", "score": int, "max_score": 40, "comments": str}},
    {{"criterion": "Next steps", "score": int, "max_score": 30, "comments": str}}
  ],
  "missed_questions": [str],
  "strengths": [str],
  "next_study_focus": [str]
}}
Be specific and educational. Do not invent transcript questions the student never asked.
"""
    response = _client().chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You are a fair OSCE examiner. Return JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    raw = json.loads(response.choices[0].message.content or "{}")
    return EvaluationResult(
        overall_score=int(raw.get("overall_score", 0)),
        max_score=int(raw.get("max_score", 100)),
        summary=raw.get("summary", ""),
        hidden_diagnosis=case.hidden_sheet.hidden_diagnosis,
        rubric=[RubricScore(**item) for item in raw.get("rubric", [])],
        missed_questions=list(raw.get("missed_questions", [])),
        strengths=list(raw.get("strengths", [])),
        next_study_focus=list(raw.get("next_study_focus", [])),
    )


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", " ", text.lower())


def _contains_any(text: str, keywords: list[str]) -> bool:
    haystack = _normalize(text)
    return any(keyword in haystack for keyword in keywords)


def _mock_patient_reply(case: PatientCase, user_message: str) -> str:
    sheet = case.hidden_sheet
    q = user_message.strip()
    if not q:
        return "Sorry — could you say that again?"

    rules: list[tuple[list[str], str]] = [
        (["pain start", "when did", "how long", "started", "onset", "duration"], sheet.history_of_present_illness.split(".")[0] + "."),
        (["where", "location", "radiat", "move"], _first_matching_sentence(sheet.history_of_present_illness, ["radiat", "left", "right", "back", "jaw", "arm", "side"]) or sheet.history_of_present_illness),
        (["feel like", "character", "sharp", "pressure", "crush", "quality", "describe the pain"], _first_matching_sentence(sheet.history_of_present_illness, ["pressure", "sharp", "heavy", "dull", "boring", "ache"]) or "It's pretty intense. Hard to ignore."),
        (["worse", "better", "aggrav", "reliev", "position"], _first_matching_sentence(sheet.history_of_present_illness, ["worse", "better", "walking", "breath", "rest", "flat", "forward"]) or "It just stays about the same unless I stay still."),
        (["associated", "other symptom", "else going on", "nausea", "sweat", "fever", "vomit", "cough", "short of breath", "dizzy"], "Also: " + ", ".join(sheet.associated_symptoms).lower() + "."),
        (["medication", "medicine", "pill", "drug"], "I take " + ", ".join(sheet.medications) + "."),
        (["allerg"], "Allergies: " + ", ".join(sheet.allergies) + "."),
        (["past medical", "pmh", "medical history", "diagnos", "condition", "diabetes", "hypertens", "asthma"], "I've been told I have " + ", ".join(sheet.past_medical_history) + "."),
        (["smok", "drink", "alcohol", "drug use", "social", "live", "work", "job"], sheet.social_history),
        (["family", "mother", "father", "parent"], sheet.family_history),
        (["allerg to contrast", "iodine"], "Allergies: " + ", ".join(sheet.allergies) + "."),
        (["travel", "flight", "plane"], sheet.social_history if "flight" in sheet.history_of_present_illness.lower() else "I have not traveled anywhere unusual lately, I don't think."),
        (["period", "pregnant", "lmp", "sexual"], sheet.review_of_systems),
        (["what do you think", "diagnos", "what is wrong"], "I was hoping you could tell me. I'm just scared and want this to stop."),
        (["lab", "ct", "x-ray", "troponin", "ecg result"], "Nobody has told me any test results yet."),
    ]

    for keywords, answer in rules:
        if _contains_any(q, keywords):
            return answer

    if _contains_any(q, ["yes", "no"]) and len(q.split()) <= 3:
        return "I'm not sure I followed — can you ask that as a full question?"

    # Pertinent negative if the student asked about a denied symptom.
    for negative in sheet.pertinent_negatives:
        tokens = [token for token in _normalize(negative).split() if len(token) > 3]
        if tokens and any(token in _normalize(q) for token in tokens[:3]):
            return negative + "."

    if "?" in q or q.lower().startswith(("do you", "have you", "are you", "did you", "can you", "is the")):
        return "I don't think so — or at least I have not noticed that."

    return "I'm not sure how to answer that. Could you ask it in a simpler way?"


def _first_matching_sentence(text: str, keywords: list[str]) -> str | None:
    for sentence in text.split("."):
        if _contains_any(sentence, keywords):
            return sentence.strip() + "."
    return None


def _score_overlap(submitted: list[str], acceptable: list[str]) -> int:
    hits = 0
    for item in submitted:
        if any(_contains_any(item, _normalize(acc).split()[:3]) or _contains_any(acc, _normalize(item).split()[:3]) for acc in acceptable):
            hits += 1
    return hits


def _history_coverage(messages: list[ChatMessage], case: PatientCase) -> tuple[int, list[str], list[str]]:
    asked = " ".join(m.content for m in messages if m.role == "student")
    domains: list[tuple[str, list[str]]] = [
        ("onset and timeline", ["when", "start", "long", "onset", "duration"]),
        ("pain character or quality", ["feel", "sharp", "pressure", "describe", "quality"]),
        ("associated symptoms", ["else", "nausea", "fever", "sweat", "associated", "vomit"]),
        ("past medical history", ["history", "medical", "diabetes", "condition"]),
        ("medications", ["medication", "pill", "medicine"]),
        ("allergies", ["allerg"]),
        ("social history", ["smok", "drink", "alcohol", "live", "work"]),
        ("family history", ["family", "mother", "father"]),
    ]
    covered: list[str] = []
    missed: list[str] = []
    for label, keys in domains:
        if _contains_any(asked, keys):
            covered.append(label)
        else:
            missed.append(f"Ask about {label}")
    score = round(30 * (len(covered) / len(domains)))
    if not messages:
        score = 4
        missed = [item[0] for item in domains]
        missed = [f"Ask about {item}" for item in missed]
    return score, covered, missed


def _mock_evaluate(case: PatientCase, messages: list[ChatMessage], submission: EvaluationRequest) -> EvaluationResult:
    submitted = [submission.differential_1, submission.differential_2, submission.differential_3]
    hits = _score_overlap(submitted, case.hidden_sheet.acceptable_differentials)
    diagnosis_hit = _contains_any(
        " ".join(submitted),
        _normalize(case.hidden_sheet.hidden_diagnosis).split()[:4],
    )
    ddx_score = min(40, hits * 12 + (8 if diagnosis_hit else 0))

    step_hits = sum(
        1
        for step in case.hidden_sheet.recommended_next_steps
        if _contains_any(submission.next_steps, _normalize(step).split()[:4])
    )
    next_score = min(30, 6 + step_hits * 6)

    history_score, strengths_hist, missed = _history_coverage(messages, case)
    overall = history_score + ddx_score + next_score

    summary = (
        f"The working diagnosis on the case sheet is {case.hidden_sheet.hidden_diagnosis}. "
        + (
            "Your differentials included a close match. "
            if diagnosis_hit
            else "The true diagnosis was not clearly listed. "
        )
        + f"You covered {len(strengths_hist)} of 8 core history domains."
    )

    return EvaluationResult(
        overall_score=overall,
        max_score=100,
        summary=summary,
        hidden_diagnosis=case.hidden_sheet.hidden_diagnosis,
        rubric=[
            RubricScore(
                criterion="History taking",
                score=history_score,
                max_score=30,
                comments="You asked about " + (", ".join(strengths_hist) or "very little of the HPI") + ".",
            ),
            RubricScore(
                criterion="Differential diagnosis",
                score=ddx_score,
                max_score=40,
                comments=(
                    f"{hits} of your three differentials overlap the expected list. "
                    + ("The hidden diagnosis is represented." if diagnosis_hit else "Add the leading diagnosis more explicitly.")
                ),
            ),
            RubricScore(
                criterion="Next steps",
                score=next_score,
                max_score=30,
                comments="Expected actions include: " + "; ".join(case.hidden_sheet.recommended_next_steps[:3]) + ".",
            ),
        ],
        missed_questions=missed[:5],
        strengths=strengths_hist or ["You completed the station and committed to a differential."],
        next_study_focus=case.hidden_sheet.teaching_points,
    )

