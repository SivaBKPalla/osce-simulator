from __future__ import annotations

from copy import deepcopy

from app.models import HiddenSheet, PatientCase, Vitals, new_id

PRESET_CASES: list[PatientCase] = [
    PatientCase(
        id="acs-chest-pain",
        title="Crushing substernal chest pain",
        presenting_complaint="Chest pain for 45 minutes",
        age=58,
        gender="Male",
        setting="Emergency department",
        vitals=Vitals(
            temperature_c=36.8,
            heart_rate=102,
            blood_pressure="148/92",
            respiratory_rate=20,
            spo2=96,
            pain_score=8,
        ),
        brief_history=(
            "A 58-year-old man is brought in by his partner after sudden heavy chest pressure "
            "while shoveling snow. He looks diaphoretic and anxious."
        ),
        hidden_sheet=HiddenSheet(
            hidden_diagnosis="Non-ST elevation acute coronary syndrome (NSTE-ACS)",
            acceptable_differentials=[
                "Unstable angina / NSTEMI",
                "STEMI",
                "Aortic dissection",
                "Pulmonary embolism",
                "Esophageal spasm / GERD",
                "Anxiety / panic attack",
            ],
            recommended_next_steps=[
                "12-lead ECG now and serial troponins",
                "Aspirin 325 mg chewed if no contraindication",
                "IV access, continuous telemetry, oxygen if hypoxic",
                "Chest X-ray and basic labs including lipids and CBC",
                "Cardiology consult / ACS pathway",
            ],
            history_of_present_illness=(
                "Pain started 45 minutes ago while shoveling. It is a heavy pressure in the center "
                "of the chest, 8/10, radiating to the left arm and jaw. Associated with sweating, "
                "nausea, and mild shortness of breath. Not pleuritic, not worse with movement. "
                "He has had similar milder episodes walking uphill over the last 3 weeks that "
                "resolved with rest."
            ),
            associated_symptoms=["Diaphoresis", "Nausea", "Mild dyspnea", "Left arm and jaw radiation"],
            pertinent_negatives=[
                "No tearing back pain",
                "No syncope",
                "No fever or cough",
                "No calf swelling",
                "Pain not reproduced by palpation",
            ],
            past_medical_history=["Hypertension", "Hyperlipidemia", "Type 2 diabetes"],
            medications=["Lisinopril 20 mg daily", "Atorvastatin 40 mg nightly", "Metformin 1000 mg BID"],
            allergies=["Penicillin — rash"],
            social_history=(
                "Smokes half a pack per day for 30 years. Occasional beer on weekends. "
                "Works as a contractor. Lives with partner."
            ),
            family_history="Father had an MI at age 54.",
            review_of_systems="No recent illness. No GI bleeding. Occasional ankle swelling at night.",
            personality_notes="Anxious but cooperative. Speaks in short sentences. Minimizes smoking.",
            teaching_points=[
                "Ask about radiation, exertional pattern, and associated autonomic symptoms.",
                "Distinguish ischemic pain from dissection and PE risk factors.",
                "Immediate ECG and aspirin are first-line next steps, not a CT first.",
            ],
        ),
    ),
    PatientCase(
        id="pe-dyspnea",
        title="Pleuritic pain after a long flight",
        presenting_complaint="Sudden shortness of breath",
        age=24,
        gender="Female",
        setting="Urgent care, transferred to ED",
        vitals=Vitals(
            temperature_c=37.1,
            heart_rate=118,
            blood_pressure="108/70",
            respiratory_rate=24,
            spo2=91,
            pain_score=6,
        ),
        brief_history=(
            "A 24-year-old woman develops sudden right-sided chest pain and dyspnea two days "
            "after a 14-hour flight home from a conference."
        ),
        hidden_sheet=HiddenSheet(
            hidden_diagnosis="Acute pulmonary embolism",
            acceptable_differentials=[
                "Pulmonary embolism",
                "Pneumothorax",
                "Pneumonia",
                "Pericarditis",
                "Anxiety attack",
                "Musculoskeletal chest pain",
            ],
            recommended_next_steps=[
                "Oxygen to keep SpO2 ≥ 94%",
                "Wells / YEARS assessment and D-dimer if low probability, otherwise CT PA",
                "ECG looking for sinus tachycardia or right heart strain",
                "Pregnancy test before imaging",
                "Anticoagulation if PE confirmed or high suspicion and low bleed risk",
            ],
            history_of_present_illness=(
                "Sudden sharp right-sided pain two hours ago while walking to class. Worse with "
                "deep breath and cough. Feels like she cannot get a full breath. No trauma. "
                "Returned from a 14-hour flight 2 days ago. Takes combined oral contraceptive pills."
            ),
            associated_symptoms=["Pleuritic pain", "Dyspnea", "Mild dry cough", "Lightheadedness"],
            pertinent_negatives=["No fever", "No hemoptysis", "No calf pain she noticed", "No wheeze or asthma history"],
            past_medical_history=["Migraines"],
            medications=["Ethinyl estradiol / norethindrone OCP daily", "Sumatriptan as needed"],
            allergies=["NKDA"],
            social_history="Does not smoke. Drinks socially. No illicit drugs. College student.",
            family_history="Aunt had a blood clot after surgery; no known thrombophilia testing.",
            review_of_systems="Last menstrual period 1 week ago. No leg swelling she noticed.",
            personality_notes="Frightened, talks quickly, asks if she is having a heart attack.",
            teaching_points=[
                "Combine sudden hypoxia + tachycardia + OCP + recent flight.",
                "Students should ask about estrogen, immobility, pregnancy, and prior clots.",
                "Do not treat this as simple anxiety without considering PE.",
            ],
        ),
    ),
    PatientCase(
        id="appy-rlq",
        title="Migrating abdominal pain",
        presenting_complaint="Stomach pain since last night",
        age=22,
        gender="Male",
        setting="Emergency department",
        vitals=Vitals(
            temperature_c=38.1,
            heart_rate=96,
            blood_pressure="124/78",
            respiratory_rate=18,
            spo2=99,
            pain_score=7,
        ),
        brief_history=(
            "A 22-year-old man presents with abdominal pain that began around the umbilicus "
            "last night and is now worse on the right side. He has not eaten today."
        ),
        hidden_sheet=HiddenSheet(
            hidden_diagnosis="Acute appendicitis",
            acceptable_differentials=[
                "Appendicitis",
                "Mesenteric adenitis",
                "Gastroenteritis",
                "Nephrolithiasis",
                "Testicular torsion / epididymitis",
                "IBD flare",
            ],
            recommended_next_steps=[
                "NPO, IV fluids, analgesia",
                "CBC, CRP, BMP, urinalysis",
                "Pregnancy test if applicable; here, consider testicular exam",
                "Ultrasound or CT abdomen/pelvis with contrast",
                "Surgical consult",
            ],
            history_of_present_illness=(
                "Pain started 18 hours ago as a dull ache around the belly button. Over the last "
                "6 hours it moved to the right lower quadrant and became sharper. Anorexia, one "
                "episode of vomiting, low-grade fever. Pain worse with walking and coughing. "
                "No diarrhea. Last bowel movement yesterday, normal."
            ),
            associated_symptoms=["Anorexia", "Nausea", "One episode of vomiting", "Low-grade fever"],
            pertinent_negatives=[
                "No diarrhea",
                "No dysuria or hematuria",
                "No testicular pain",
                "No prior abdominal surgeries",
            ],
            past_medical_history=["None"],
            medications=["Ibuprofen 400 mg this morning"],
            allergies=["NKDA"],
            social_history="College athlete. No tobacco. Occasional alcohol. Sexually active, uses condoms.",
            family_history="Non-contributory.",
            review_of_systems="No rash. No joint pain. No recent travel.",
            personality_notes="Stoic, embarrassed about vomiting. Holds his right side when he walks.",
            teaching_points=[
                "Classic migratory pain plus anorexia is high-yield.",
                "Ask GU symptoms so torsion and stone are not missed.",
                "Imaging and surgical consult, not empiric antibiotics alone.",
            ],
        ),
    ),
    PatientCase(
        id="meningitis-ha",
        title="Worst headache with photophobia",
        presenting_complaint="Severe headache and fever",
        age=19,
        gender="Female",
        setting="College health, sent to ED",
        vitals=Vitals(
            temperature_c=39.2,
            heart_rate=112,
            blood_pressure="118/68",
            respiratory_rate=22,
            spo2=98,
            pain_score=9,
        ),
        brief_history=(
            "A 19-year-old first-year student is brought in by roommates for a rapidly worsening "
            "headache, fever, and sensitivity to light."
        ),
        hidden_sheet=HiddenSheet(
            hidden_diagnosis="Acute bacterial meningitis",
            acceptable_differentials=[
                "Bacterial meningitis",
                "Viral meningitis",
                "Influenza / viral syndrome",
                "Migraine",
                "Subarachnoid hemorrhage",
                "Intracranial mass with fever",
            ],
            recommended_next_steps=[
                "Airway and sepsis ABCs; isolation precautions",
                "Blood cultures and immediate empiric IV antibiotics plus dexamethasone",
                "Lumbar puncture unless contraindicated; CT first only if focal neuro signs",
                "CBC, BMP, lactate, glucose",
                "Droplet precautions and public-health notification if confirmed",
            ],
            history_of_present_illness=(
                "Headache started last night and is now the worst of her life, diffuse, 9/10. "
                "Fever, neck stiffness, photophobia, one episode of vomiting. Roommate says she "
                "was confused this morning and called her mother by the wrong name. Lives in a "
                "dorm. Not sure about meningococcal vaccination."
            ),
            associated_symptoms=["Fever", "Photophobia", "Neck stiffness", "Vomiting", "Confusion"],
            pertinent_negatives=["No head trauma", "No seizure witnessed", "No rash noticed by her", "No prior migraine diagnosis"],
            past_medical_history=["Mild asthma"],
            medications=["Albuterol inhaler as needed"],
            allergies=["Sulfa — hives"],
            social_history="Dormitory living. Does not smoke. Recent campus flu-like illness in hall.",
            family_history="Non-contributory.",
            review_of_systems="No cough she remembers. No urinary symptoms. Last period 2 weeks ago.",
            personality_notes="Lethargic, irritable when lights are on, answers slowly but can follow commands.",
            teaching_points=[
                "Fever + headache + neck stiffness + altered mental status is an emergency.",
                "Do not delay antibiotics for imaging if suspicion is high.",
                "Ask about dorms, vaccines, rash, and immunocompromise.",
            ],
        ),
    ),
    PatientCase(
        id="chf-dyspnea",
        title="Orthopnea and ankle swelling",
        presenting_complaint="Getting more short of breath this week",
        age=72,
        gender="Female",
        setting="Outpatient clinic same-day slot",
        vitals=Vitals(
            temperature_c=36.6,
            heart_rate=88,
            blood_pressure="162/94",
            respiratory_rate=22,
            spo2=90,
            pain_score=0,
        ),
        brief_history=(
            "A 72-year-old woman reports progressive dyspnea on exertion, needing two pillows "
            "to sleep, and new lower-leg swelling."
        ),
        hidden_sheet=HiddenSheet(
            hidden_diagnosis="Acute decompensated heart failure (HFrEF exacerbation)",
            acceptable_differentials=[
                "Acute decompensated heart failure",
                "COPD exacerbation",
                "Community-acquired pneumonia",
                "Anemia",
                "Pulmonary embolism",
                "Nephrotic syndrome / CKD volume overload",
            ],
            recommended_next_steps=[
                "ECG, chest X-ray, BNP or NT-proBNP, troponin",
                "CBC, BMP including creatinine and electrolytes",
                "Supplemental oxygen as needed",
                "Diuretic therapy if congestion confirmed",
                "Echo if no recent assessment of EF",
            ],
            history_of_present_illness=(
                "Over 10 days she has become short of breath walking across a room. Sleeps on "
                "two pillows; last night she woke gasping and went to the window. Weight up 6 "
                "pounds. Swelling in both ankles. Missed two days of furosemide last week while "
                "traveling. No chest pain today. Chronic dry cough, no fever."
            ),
            associated_symptoms=["Orthopnea", "PND", "Bilateral edema", "Weight gain", "Fatigue"],
            pertinent_negatives=["No fever", "No pleuritic pain", "No calf asymmetry", "No new neurologic symptoms"],
            past_medical_history=["HFrEF EF 35% after NSTEMI 4 years ago", "Hypertension", "CKD stage 3"],
            medications=[
                "Lisinopril 10 mg daily",
                "Metoprolol succinate 50 mg daily",
                "Furosemide 40 mg daily (missed 2 doses)",
                "Aspirin 81 mg",
                "Atorvastatin 40 mg",
            ],
            allergies=["Iodine contrast — itching"],
            social_history="Former smoker, quit 15 years ago, 20 pack-years. Lives alone. Daughter nearby.",
            family_history="Mother had heart failure in her 80s.",
            review_of_systems="No black stools. Occasional palpitations. Dietary salt higher while traveling.",
            personality_notes="Polite, slightly embarrassed about missed pills, minimizes how bad nights have been.",
            teaching_points=[
                "Orthopnea, PND, weight gain, and missed diuretic point to congestion.",
                "Ask medication adherence and dietary salt.",
                "BNP, CXR, and diuresis are more appropriate than PE-first workup here.",
            ],
        ),
    ),
    PatientCase(
        id="pancreatitis-epigastric",
        title="Epigastric pain radiating to the back",
        presenting_complaint="Severe upper stomach pain",
        age=47,
        gender="Male",
        setting="Emergency department",
        vitals=Vitals(
            temperature_c=37.8,
            heart_rate=110,
            blood_pressure="138/86",
            respiratory_rate=20,
            spo2=97,
            pain_score=9,
        ),
        brief_history=(
            "A 47-year-old man has severe epigastric pain radiating straight through to the back "
            "after a weekend of heavy drinking."
        ),
        hidden_sheet=HiddenSheet(
            hidden_diagnosis="Acute pancreatitis, likely alcohol-related",
            acceptable_differentials=[
                "Acute pancreatitis",
                "Peptic ulcer disease / perforation",
                "Cholecystitis / choledocholithiasis",
                "Inferior MI",
                "Gastritis",
                "AAA (less likely given age)",
            ],
            recommended_next_steps=[
                "NPO, aggressive IV fluids, analgesia",
                "Lipase, CMP, CBC, triglycerides, alcohol level as indicated",
                "ECG to exclude ACS",
                "Right-upper-quadrant ultrasound if gallstone etiology possible",
                "Assess severity (SIRS, organ failure) and admit",
            ],
            history_of_present_illness=(
                "Pain began 12 hours ago, constant, boring through to the back, 9/10. Worse lying "
                "flat, a bit better sitting forward. Repeated vomiting. Drank a fifth of whiskey "
                "over Saturday and Sunday. No coffee-ground emesis. No fatty food trigger he recalls."
            ),
            associated_symptoms=["Vomiting", "Anorexia", "Low-grade fever", "Pain better leaning forward"],
            pertinent_negatives=["No diarrhea", "No jaundice he has noticed", "No chest pressure", "No hematemesis"],
            past_medical_history=["Alcohol use disorder", "Prior similar milder episode last year, did not seek care"],
            medications=["None regularly", "Took 3 extra-strength acetaminophen last night"],
            allergies=["NKDA"],
            social_history="Drinks daily, more on weekends. Smokes 1 pack/day. Unemployed. Lives with brother.",
            family_history="Brother has gallstones.",
            review_of_systems="No dark urine. No pale stools. Some recent poor appetite.",
            personality_notes="In severe pain, irritable, downplays drinking until asked twice.",
            teaching_points=[
                "Boring pain to the back plus alcohol binge is classic.",
                "Still exclude ACS and perforation.",
                "Ask honestly about alcohol, gallstones, and triglycerides.",
            ],
        ),
    ),
    PatientCase(
        id="palpitations-thyrotoxic",
        title="Racing heart and weight loss",
        presenting_complaint="Palpitations for two weeks",
        age=28,
        gender="Female",
        setting="Outpatient clinic",
        vitals=Vitals(
            temperature_c=37.4,
            heart_rate=118,
            blood_pressure="142/78",
            respiratory_rate=18,
            spo2=99,
            pain_score=0,
        ),
        brief_history=(
            "A 28-year-old woman comes to clinic because her heart has been racing and she feels "
            "jittery. She has lost weight without trying."
        ),
        hidden_sheet=HiddenSheet(
            hidden_diagnosis="Overt hyperthyroidism (likely Graves disease)",
            acceptable_differentials=[
                "Hyperthyroidism / Graves disease",
                "Anxiety / panic disorder",
                "SVT / atrial fibrillation with RVR",
                "Anemia",
                "Pheochromocytoma (less likely)",
                "Caffeine or stimulant use",
            ],
            recommended_next_steps=[
                "ECG now",
                "TSH with free T4",
                "CBC and pregnancy test",
                "Avoid empiric beta-blocker only workup; treat rate if symptomatic after ECG",
                "Endocrine referral if thyrotoxicosis confirmed",
            ],
            history_of_present_illness=(
                "For two weeks she feels her heart pounding, especially at rest. Heat intolerance, "
                "sweating, loose stools, and tremor in her hands. Down 8 pounds despite a bigger "
                "appetite. Sleep is poor. No chest pain. Occasional extra coffee, no energy drinks "
                "or diet pills."
            ),
            associated_symptoms=["Heat intolerance", "Tremor", "Weight loss", "Diarrhea", "Insomnia"],
            pertinent_negatives=["No syncope", "No chest pain", "No true panic episodes with fear of dying", "No recent pregnancy"],
            past_medical_history=["None"],
            medications=["Occasional ibuprofen"],
            allergies=["NKDA"],
            social_history="Two cups of coffee daily. Does not smoke. Rare alcohol. Graduate student.",
            family_history="Mother has Hashimoto thyroiditis.",
            review_of_systems="Irregular lighter periods lately. No neck pain. Friends say her eyes look a bit more open.",
            personality_notes="Restless, talks quickly, laughs at how much she is eating.",
            teaching_points=[
                "Pair palpitations with systemic thyrotoxic features, not anxiety alone.",
                "Always get an ECG before assuming sinus tachycardia.",
                "Ask about stimulants, blood loss, and pregnancy.",
            ],
        ),
    ),
]


def all_cases() -> list[PatientCase]:
    return [deepcopy(case) for case in PRESET_CASES]


def get_case(case_id: str) -> PatientCase | None:
    for case in PRESET_CASES:
        if case.id == case_id:
            return deepcopy(case)
    return None


def clone_as_generated(case: PatientCase) -> PatientCase:
    clone = deepcopy(case)
    clone.id = new_id()
    clone.generated = True
    return clone
