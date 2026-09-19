from __future__ import annotations

import json
import re
from app.catalog import mock_circuit, mock_single_case
from app.config import settings
from app.models import (
    AnalysisTab,
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
recommended_next_steps must match OSCE-level acuity: a simple cold or viral URI gets advice, supportive care, and safety-netting — not CT, blood cultures, or admission. Unstable or high-risk diagnoses get urgent, realistic first steps.
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
- Next steps must match acuity. Minor viral illness is advice and safety-netting, not an emergency workup.

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
    prompt = f"""Grade this OSCE history-taking station. The hidden case sheet is the only source of truth — including user-generated cases.

{_sheet_block(case)}
Generated case: {case.generated}

Transcript:
{transcript}

Student submission:
1. {submission.differential_1}
2. {submission.differential_2}
3. {submission.differential_3}
Next steps: {submission.next_steps}

Mark like a real OSCE examiner:
- Judge what the candidate actually asked and wrote. Do not invent transcript questions.
- History (30): introduction/open question, focused HPI (SOCRATES/OPQRST if pain), ICE if relevant, PMH, drugs, allergies, FH, SH, and the red-flag screen this stem needed.
- Differentials (40): rank and clinical relatedness, not exact string match. "Exact" = working diagnosis or a standard synonym. "Related" = same family/syndrome but wrong entity or severity (example: "a cold" or "viral URI" when the case is pneumonia) — about half credit for that slot. Unrelated = no credit.
- Next steps (30): must be realistic for THIS diagnosis, setting, and vitals. Simple viral cold / uncomplicated URI: advice, supportive care, safety-netting; do not reward CXR, bloods, IV antibiotics, or admission. Unstable or high-risk disease: ABC, urgent tests, treatment, and the right referral. Penalize both over-investigation of minor illness and under-treatment of emergencies.
- Follow ordinary OSCE practice if any other instruction conflicts with it.
- Model-answer tabs are the best candidate performance for this station, written in prose, grounded in this case.

Return JSON only:
{{
  "overall_score": int,
  "max_score": 100,
  "summary": str,
  "diagnosis_correct": bool,
  "diagnosis_match": "exact" | "related" | "miss",
  "diagnosis_explanation": str,
  "rubric": [
    {{
      "criterion": "History taking" | "Differential diagnosis" | "Next steps",
      "score": int,
      "max_score": 30 or 40,
      "comments": str,
      "tabs": [
        {{"id": "yours", "label": "Your version", "body": str, "bullets": [str]}},
        {{"id": "model", "label": "Model answer", "body": str, "bullets": [str]}},
        {{"id": "why", "label": "Why this is better", "body": str, "bullets": [str]}}
      ]
    }}
  ],
  "missed_questions": [str],
  "strengths": [str],
  "next_study_focus": [str]
}}
diagnosis_correct is true only when diagnosis_match is exact.
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
    result = EvaluationResult(
        overall_score=int(raw.get("overall_score", 0)),
        max_score=int(raw.get("max_score", 100)),
        summary=raw.get("summary", ""),
        hidden_diagnosis=case.hidden_sheet.hidden_diagnosis,
        diagnosis_correct=bool(raw.get("diagnosis_correct", False)),
        diagnosis_match=str(raw.get("diagnosis_match", "miss")),
        diagnosis_explanation=raw.get("diagnosis_explanation", ""),
        rubric=[RubricScore(**item) for item in raw.get("rubric", [])],
        missed_questions=list(raw.get("missed_questions", [])),
        strengths=list(raw.get("strengths", [])),
        next_study_focus=list(raw.get("next_study_focus", [])),
    )
    if result.diagnosis_match not in {"exact", "related", "miss"}:
        result.diagnosis_match = "exact" if result.diagnosis_correct else "miss"
    if not any(row.tabs for row in result.rubric):
        fallback = _mock_evaluate(case, messages, submission)
        result.diagnosis_correct = fallback.diagnosis_correct
        result.diagnosis_match = fallback.diagnosis_match
        result.diagnosis_explanation = fallback.diagnosis_explanation
        result.rubric = fallback.rubric
    return result


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


def _token_set(text: str) -> set[str]:
    return {token for token in _normalize(text).split() if len(token) > 2}


def _jaccard(a: str, b: str) -> float:
    left, right = _token_set(a), _token_set(b)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _mentions(text: str, term: str) -> bool:
    hay = _normalize(text)
    if " " in term or len(term) > 3:
        return term in hay
    return term in _token_set(text)


def _same_family(student: str, target: str) -> bool:
    families = [
        {"cold", "uri", "urti", "rhino", "viral", "flu", "influenza", "covid", "bronchitis", "pneumonia", "chest infection", "congestion", "pharyngitis", "sinus"},
        {"mi", "nstemi", "stemi", "acs", "angina", "infarct", "coronary", "heart attack"},
        {"pe", "embolus", "dvt", "clot", "thrombus"},
        {"appendicitis", "appy", "rlq"},
        {"meningitis", "encephalitis", "meningococcal"},
        {"stroke", "tia", "cva", "aphasia"},
        {"asthma", "wheeze", "bronchospasm"},
        {"uti", "pyelo", "cystitis", "dysuria"},
        {"stone", "ureteric", "renal colic", "nephrolith"},
        {"ectopic", "pregnancy", "miscarriage"},
        {"dissection", "tearing", "aortic"},
        {"pancreatitis", "epigastric", "lipase"},
        {"seizure", "epilep", "convuls"},
        {"anaphylaxis", "allergic", "angioedema"},
        {"heart failure", "chf", "orthopnea", "pnd", "decompensat"},
    ]
    return any(
        any(_mentions(student, term) for term in family) and any(_mentions(target, term) for term in family)
        for family in families
    )


def _item_credit(student: str, targets: list[str]) -> float:
    if not student.strip():
        return 0.0
    best = 0.0
    for target in targets:
        if _normalize(target) in _normalize(student) or _normalize(student) in _normalize(target):
            return 1.0
        if _jaccard(student, target) >= 0.45:
            best = max(best, 1.0)
        elif _same_family(student, target) or _jaccard(student, target) >= 0.2:
            best = max(best, 0.5)
    return best


def _diagnosis_match(submitted: list[str], case: PatientCase) -> tuple[str, float]:
    diagnosis = case.hidden_sheet.hidden_diagnosis
    accept = case.hidden_sheet.acceptable_differentials
    best_exact = 0.0
    best_related = 0.0
    for item in submitted:
        diag_credit = _item_credit(item, [diagnosis])
        syn_credit = _item_credit(item, accept)
        if diag_credit >= 1.0 or (syn_credit >= 1.0 and _same_family(item, diagnosis)):
            best_exact = 1.0
        best_related = max(best_related, diag_credit, syn_credit if _same_family(item, diagnosis) else 0.0)
    if best_exact >= 1.0:
        return "exact", 1.0
    if best_related >= 0.5:
        return "related", 0.5
    return "miss", 0.0


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


def _plan_acuity(text: str) -> str:
    blob = _normalize(text)
    high = ["admit", "icu", "intub", "thrombol", "blood culture", "iv antibiotic", "ct chest", "ct pa", "ctpa"]
    low = ["safety net", "safety-net", "reassure", "supportive", "return if", "no routine", "self limited", "self-limited"]
    if any(term in blob for term in high) and "no routine" not in blob:
        return "high"
    if any(term in blob for term in low):
        return "low"
    return "mid"


def _next_step_score(student: str, case: PatientCase) -> int:
    gold = " ".join(case.hidden_sheet.recommended_next_steps)
    alignment = max((_item_credit(student, [step]) for step in case.hidden_sheet.recommended_next_steps), default=0.0)
    if _jaccard(student, gold) >= 0.2:
        alignment = max(alignment, 0.65)
    gold_acuity, student_acuity = _plan_acuity(gold), _plan_acuity(student)
    if gold_acuity == student_acuity == "low":
        alignment = max(alignment, 0.6)
    score = int(8 + alignment * 22)
    if gold_acuity == "low" and student_acuity == "high":
        score = min(score, 12)
    if gold_acuity == "high" and student_acuity == "low":
        score = min(score, 12)
    return min(30, score)


def _mock_evaluate(case: PatientCase, messages: list[ChatMessage], submission: EvaluationRequest) -> EvaluationResult:
    submitted = [submission.differential_1, submission.differential_2, submission.differential_3]
    match, credit = _diagnosis_match(submitted, case)
    extra = sum(
        _item_credit(item, case.hidden_sheet.acceptable_differentials)
        for item in submitted
    )
    ddx_score = min(40, int(credit * 24 + min(16, extra * 6)))

    history_score, strengths_hist, missed = _history_coverage(messages, case)
    next_score = _next_step_score(submission.next_steps, case)
    overall = history_score + ddx_score + next_score

    diagnosis = case.hidden_sheet.hidden_diagnosis
    asked = [m.content for m in messages if m.role == "student"]
    diagnosis_hit = match == "exact"
    if match == "exact":
        diagnosis_explanation = f"You named the working diagnosis for this station: {diagnosis}."
    elif match == "related":
        diagnosis_explanation = (
            f"Half credit: you were in the right family, but the working diagnosis is {diagnosis}. "
            "Related labels (for example calling pneumonia a cold) show the right system without the correct severity or entity."
        )
    else:
        diagnosis_explanation = (
            f"The correct diagnosis is {diagnosis}. It was not in your top 3. "
            "An OSCE differential is ranked: most likely, next plausible, then must-not-miss if the stem is dangerous."
        )
    summary = (
        f"This station's working diagnosis is {diagnosis}. "
        + { "exact": "You matched it. ", "related": "You were close enough for partial credit. ", "miss": "You missed the working diagnosis. " }[match]
        + f"History covered {len(strengths_hist)} of 8 OSCE domains."
    )

    return EvaluationResult(
        overall_score=overall,
        max_score=100,
        summary=summary,
        hidden_diagnosis=diagnosis,
        diagnosis_correct=diagnosis_hit,
        diagnosis_match=match,
        diagnosis_explanation=diagnosis_explanation,
        rubric=[
            RubricScore(
                criterion="History taking",
                score=history_score,
                max_score=30,
                comments="You asked about " + (", ".join(strengths_hist) or "very little of the HPI") + ".",
                tabs=_history_tabs(asked, strengths_hist, missed, case),
            ),
            RubricScore(
                criterion="Differential diagnosis",
                score=ddx_score,
                max_score=40,
                comments=(
                    "Working diagnosis matched."
                    if diagnosis_hit
                    else "Related diagnosis — half credit."
                    if match == "related"
                    else "The working diagnosis was missing from your ranking."
                ),
                tabs=_ddx_tabs(submitted, match, case),
            ),
            RubricScore(
                criterion="Next steps",
                score=next_score,
                max_score=30,
                comments="Next steps were judged against what this specific case and acuity required.",
                tabs=_next_step_tabs(submission.next_steps, case),
            ),
        ],
        missed_questions=missed[:5],
        strengths=strengths_hist or ["You completed the station and committed to a differential."],
        next_study_focus=case.hidden_sheet.teaching_points,
    )


def _tabs(yours_body: str, yours_bullets: list[str], model_body: str, model_bullets: list[str], why_body: str, why_bullets: list[str]) -> list[AnalysisTab]:
    return [
        AnalysisTab(id="yours", label="Your version", body=yours_body, bullets=yours_bullets),
        AnalysisTab(id="model", label="Model answer", body=model_body, bullets=model_bullets),
        AnalysisTab(id="why", label="Why this is better", body=why_body, bullets=why_bullets),
    ]


def _history_tabs(asked: list[str], covered: list[str], missed: list[str], case: PatientCase) -> list[AnalysisTab]:
    sheet = case.hidden_sheet
    return _tabs(
        yours_body="Questions you asked during the interview." if asked else "You submitted without taking a history.",
        yours_bullets=asked[:12] or ["No history questions were recorded."],
        model_body=(
            "A high-scoring OSCE history covers onset, character, associated symptoms, "
            "past history, medications, allergies, social context, and family risk, "
            "then checks the pertinent positives on this stem."
        ),
        model_bullets=[
            f"HPI to elicit: {sheet.history_of_present_illness}",
            "Associated symptoms: " + ", ".join(sheet.associated_symptoms),
            "Pertinent negatives: " + ", ".join(sheet.pertinent_negatives),
            "PMH / meds / allergies: "
            + "; ".join([", ".join(sheet.past_medical_history), ", ".join(sheet.medications), ", ".join(sheet.allergies)]),
            f"Social and family: {sheet.social_history} {sheet.family_history}",
        ],
        why_body=(
            f"You covered {len(covered)} of 8 core domains. "
            "The model script is built so the hidden diagnosis becomes the most coherent story."
        ),
        why_bullets=missed[:6] or ["You already covered the core history domains."],
    )


def _ddx_tabs(submitted: list[str], match: str, case: PatientCase) -> list[AnalysisTab]:
    sheet = case.hidden_sheet
    ranked = [sheet.hidden_diagnosis] + [
        item for item in sheet.acceptable_differentials if item.lower() not in sheet.hidden_diagnosis.lower()
    ]
    if match == "exact":
        model_body = f"You reached the working diagnosis: {sheet.hidden_diagnosis}."
        why_body = "An OSCE differential is ranked. Keep the leading diagnosis first so the examiner can see your judgment, not just a brainstorm."
    elif match == "related":
        model_body = (
            f"You were in the right family, but the working diagnosis is {sheet.hidden_diagnosis}. "
            "Related labels get partial credit; they are not a full mark."
        )
        why_body = (
            "Near-miss answers such as calling pneumonia a cold show you recognized an infectious respiratory process "
            "but missed focality, severity, and the investigation that follows."
        )
    else:
        model_body = f"The working diagnosis on this case sheet is {sheet.hidden_diagnosis}."
        why_body = "Name the single best fit first, then a close alternative, then a must-not-miss if the stem is dangerous."
    return _tabs(
        yours_body="What you committed to, in your order.",
        yours_bullets=[item for item in submitted if item.strip()] or ["No differentials submitted."],
        model_body=model_body,
        model_bullets=[
            f"Most likely: {ranked[0]}",
            f"Next plausible: {ranked[1] if len(ranked) > 1 else ranked[0]}",
            f"Must-not-miss if needed: {ranked[2] if len(ranked) > 2 else ranked[-1]}",
        ],
        why_body=why_body,
        why_bullets=sheet.teaching_points[:3],
    )


def _next_step_tabs(student_steps: str, case: PatientCase) -> list[AnalysisTab]:
    sheet = case.hidden_sheet
    return _tabs(
        yours_body="The investigations and management you proposed.",
        yours_bullets=[line.strip() for line in student_steps.replace(";", "\n").split("\n") if line.strip()]
        or [student_steps.strip() or "No next steps submitted."],
        model_body=(
            f"For {sheet.hidden_diagnosis} in this setting, the model plan matches ordinary OSCE acuity: "
            "do what changes management now, and do not over-investigate a minor illness."
        ),
        model_bullets=list(sheet.recommended_next_steps),
        why_body=(
            "Examiners mark a plan that is safe and proportionate. "
            "A viral cold is safety-netted; pneumonia or ACS is investigated and treated the same day."
        ),
        why_bullets=sheet.teaching_points[:3],
    )

