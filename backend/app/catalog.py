from __future__ import annotations

import random
from copy import deepcopy
from dataclasses import dataclass, field

from app.models import HiddenSheet, PatientCase, Vitals, new_id


def v(temp: float, hr: int, bp: str, rr: int, spo2: int, pain: int | None) -> Vitals:
    return Vitals(
        temperature_c=temp,
        heart_rate=hr,
        blood_pressure=bp,
        respiratory_rate=rr,
        spo2=spo2,
        pain_score=pain,
    )

JOBS = [
    "teacher",
    "night-shift nurse",
    "warehouse picker",
    "rideshare driver",
    "retired postal worker",
    "college student",
    "line cook",
    "software engineer",
    "farm worker",
    "home health aide",
]
HOMES = [
    "lives with a partner",
    "lives alone",
    "lives in a dorm",
    "lives with an adult child",
    "stays in a shelter some nights",
    "lives in a skilled-nursing facility",
]
HABITS = [
    "does not smoke",
    "smokes half a pack a day",
    "vapes most evenings",
    "quit smoking 4 years ago",
    "drinks two beers on weekends",
    "has been drinking daily this month",
]
PERSONAS = [
    "Minimizes symptoms and wants to go back to work.",
    "Anxious, asks if this could be cancer.",
    "Stoic, answers in short phrases.",
    "Chatty and a little embarrassed.",
    "Confused about dates but trying to help.",
    "Irritable from pain, still cooperative.",
]


@dataclass
class CaseSeed:
    domain: str
    titles: list[str]
    complaints: list[str]
    age_range: tuple[int, int]
    genders: list[str]
    settings: list[str]
    diagnoses: list[str]
    differentials: list[str]
    next_steps: list[str]
    hpi: list[str]
    associated: list[str]
    negatives: list[str]
    pmh: list[str]
    meds: list[str]
    allergies: list[str]
    family: list[str]
    ros: list[str]
    teaching: list[str]
    vitals_base: Vitals
    extra_social: list[str] = field(default_factory=list)


SEEDS: list[CaseSeed] = [
    CaseSeed(
        domain="acs",
        titles=["Pressure in the chest after shoveling", "Heaviness while climbing stairs", "Jaw pain with sweating"],
        complaints=["Chest pressure for 40 minutes", "Heavy chest pain after exertion", "Chest and jaw discomfort"],
        age_range=(49, 78),
        genders=["Male", "Female"],
        settings=["Emergency department", "Urgent care, sent to ED"],
        diagnoses=["NSTE-ACS", "Unstable angina", "Inferior-wall NSTEMI"],
        differentials=["NSTEMI / unstable angina", "STEMI", "Aortic dissection", "PE", "GERD", "Panic attack"],
        next_steps=["ECG now", "Serial troponins", "Aspirin if safe", "Telemetry", "Cardiology pathway"],
        hpi=[
            "Pain started during exertion, heavy and central, radiating to the arm, with sweating and nausea.",
            "Pressure began at rest after several days of walking-related tightness that used to ease with sitting.",
        ],
        associated=["Diaphoresis", "Nausea", "Mild dyspnea"],
        negatives=["No tearing back pain", "No fever", "No calf swelling"],
        pmh=["Hypertension", "Diabetes", "High cholesterol"],
        meds=["Lisinopril", "Metformin", "Atorvastatin"],
        allergies=["Penicillin — rash", "NKDA"],
        family=["Father had an MI in his 50s.", "Sister had a stent at 61."],
        ros=["Occasional ankle swelling.", "No black stools."],
        teaching=["Ask radiation, exertion, and autonomic symptoms.", "ECG and aspirin before CT."],
        vitals_base=v(36.8, 104, "152/90", 20, 95, 8),
    ),
    CaseSeed(
        domain="dissection",
        titles=["Sudden tearing pain to the back", "Chest ripping while lifting", "Worst-ever chest-back pain"],
        complaints=["Tearing chest pain", "Sudden chest and back pain", "Ripping pain between the shoulders"],
        age_range=(52, 76),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["Acute aortic dissection", "Type A aortic dissection", "Type B aortic dissection"],
        differentials=["Aortic dissection", "ACS", "PE", "Pneumothorax", "Esophageal rupture"],
        next_steps=["Two large-bore IVs", "Blood pressure in both arms", "ECG", "CT aortogram", "Immediate surgical consult"],
        hpi=[
            "Pain began instantly, 10/10, tearing from chest into the back, still severe.",
            "While lifting a box the chest ripped and the right arm felt strangely cool.",
        ],
        associated=["Diaphoresis", "A sense of doom", "One near-syncope"],
        negatives=["No cough", "No calf pain"],
        pmh=["Long-standing hypertension", "Bicuspid aortic valve"],
        meds=["Amlodipine", "Sometimes skips blood-pressure pills"],
        allergies=["NKDA", "Iodine — itch"],
        family=["Uncle died suddenly at 48.", "No known connective-tissue disease."],
        ros=["No fever.", "No neurologic weakness they are sure of."],
        teaching=["Sudden tearing plus pulse or BP asymmetry is dissection until proven otherwise."],
        vitals_base=v(36.6, 98, "188/64", 22, 97, 10),
    ),
    CaseSeed(
        domain="heart-failure",
        titles=["Two pillows and swollen ankles", "Waking up gasping", "Weight up and short of breath"],
        complaints=["Worsening dyspnea this week", "Cannot lie flat", "Swelling and breathlessness"],
        age_range=(64, 86),
        genders=["Female", "Male"],
        settings=["Clinic same-day slot", "Emergency department"],
        diagnoses=["Acute decompensated heart failure", "HFrEF exacerbation", "Flash pulmonary edema"],
        differentials=["Heart failure", "COPD flare", "Pneumonia", "PE", "Anemia", "CKD volume overload"],
        next_steps=["Oxygen as needed", "CXR", "BNP", "ECG", "Diuretic if congested"],
        hpi=[
            "Ten days of worse dyspnea, orthopnea, a 6-pound gain, and missed diuretic doses while traveling.",
            "Woke from sleep last night gasping and sat at the window until dawn.",
        ],
        associated=["Orthopnea", "PND", "Bilateral edema"],
        negatives=["No fever", "No pleuritic pain"],
        pmh=["HFrEF", "CKD", "Prior MI"],
        meds=["Furosemide", "Metoprolol", "Lisinopril"],
        allergies=["NKDA"],
        family=["Mother had heart failure."],
        ros=["Salt-heavier diet last week.", "No chest pain today."],
        teaching=["Ask adherence, salt, orthopnea, and weight change."],
        vitals_base=v(36.5, 92, "166/94", 24, 89, 0),
    ),
    CaseSeed(
        domain="pe",
        titles=["Pleuritic pain after a long trip", "Sudden hypoxia on a walk", "Sharp chest pain postpartum"],
        complaints=["Sudden shortness of breath", "Pleuritic right chest pain", "Cannot catch a full breath"],
        age_range=(19, 54),
        genders=["Female", "Male"],
        settings=["Urgent care to ED", "Emergency department"],
        diagnoses=["Acute pulmonary embolism", "Submassive PE", "Unprovoked PE"],
        differentials=["PE", "Pneumothorax", "Pneumonia", "Pericarditis", "Anxiety"],
        next_steps=["Oxygen", "Wells / YEARS", "Pregnancy test if needed", "CT PA or D-dimer pathway", "Anticoagulate if high suspicion"],
        hpi=[
            "Sudden sharp pain and dyspnea hours after a long flight; takes estrogen.",
            "Pain worse with a deep breath two days after knee immobilization.",
        ],
        associated=["Pleuritic pain", "Tachypnea", "Lightheadedness"],
        negatives=["No fever at home", "No wheeze"],
        pmh=["Migraines", "None"],
        meds=["Combined OCP", "None"],
        allergies=["NKDA"],
        family=["Aunt had a clot after surgery."],
        ros=["Last period recently.", "No hemoptysis."],
        extra_social=["just flew home", "desk job after an ankle sprain"],
        teaching=["Immobility, estrogen, sudden hypoxia."],
        vitals_base=v(37.0, 116, "106/70", 26, 90, 6),
    ),
    CaseSeed(
        domain="pneumothorax",
        titles=["Sudden one-sided chest pain in a tall teen", "Sharp pain after a coughing fit", "Dyspnea and absent breath sounds"],
        complaints=["Sudden left chest pain", "Sharp chest pain and dyspnea", "Pain after coughing"],
        age_range=(16, 34),
        genders=["Male", "Female"],
        settings=["Emergency department", "College health to ED"],
        diagnoses=["Primary spontaneous pneumothorax", "Secondary pneumothorax", "Small apical pneumothorax"],
        differentials=["Pneumothorax", "PE", "Pleuritis", "Musculoskeletal pain", "Pericarditis"],
        next_steps=["Oxygen", "Upright CXR", "Needle or tube if unstable", "Observe if tiny and stable"],
        hpi=[
            "Sudden one-sided pain while sitting in class, worse with inspiration, no trauma.",
            "Tall thin patient felt a pop then became short of breath.",
        ],
        associated=["Dyspnea", "Pleuritic pain"],
        negatives=["No fever", "No leg swelling"],
        pmh=["None", "Mild asthma"],
        meds=["None", "Albuterol PRN"],
        allergies=["NKDA"],
        family=["A cousin had a collapsed lung."],
        ros=["Smokes socially.", "No recent diving."],
        teaching=["Tall thin young adult plus sudden unilateral pain."],
        vitals_base=v(36.7, 108, "118/72", 24, 93, 6),
    ),
    CaseSeed(
        domain="pneumonia",
        titles=["Fever, cough, and one-sided pain", "Rigors after a week of cough", "Confusion and fever in a grandparent"],
        complaints=["Cough and fever", "Chest pain when I cough", "Fever and feeling awful"],
        age_range=(22, 88),
        genders=["Female", "Male"],
        settings=["Emergency department", "Walk-in clinic"],
        diagnoses=["Community-acquired pneumonia", "Lobar pneumonia", "Influenza with bacterial pneumonia"],
        differentials=["Pneumonia", "COVID / viral illness", "PE", "COPD flare", "Pyelo"],
        next_steps=["CXR", "CBC, lactate", "Cultures if septic", "Empiric antibiotics", "Oxygen"],
        hpi=[
            "Five days of cough, rust-colored sputum, fever, and right-sided pleuritic pain.",
            "Family says the patient is newly confused with fever and a productive cough.",
        ],
        associated=["Fever", "Cough", "Malaise"],
        negatives=["No calf pain", "No rash"],
        pmh=["Diabetes", "COPD", "None"],
        meds=["Metformin", "Inhalers", "None"],
        allergies=["NKDA", "Sulfa — hives"],
        family=["Non-contributory."],
        ros=["Decreased oral intake.", "No dysuria."],
        teaching=["Fever plus focal chest findings is pneumonia until imaged."],
        vitals_base=v(38.8, 110, "128/74", 24, 91, 4),
    ),
    CaseSeed(
        domain="asthma",
        titles=["Nighttime wheeze after a viral week", "Cannot speak full sentences", "Rescue inhaler empty"],
        complaints=["Wheezing and tight chest", "Asthma attack", "Cannot catch my breath"],
        age_range=(16, 45),
        genders=["Female", "Male"],
        settings=["Emergency department", "Urgent care"],
        diagnoses=["Acute asthma exacerbation", "Viral-triggered asthma", "Near-fatal asthma risk"],
        differentials=["Asthma flare", "Anaphylaxis", "Foreign body", "Heart failure", "PE"],
        next_steps=["Oxygen / bronchodilators", "Steroids", "Peak flow if able", "Reassess work of breathing"],
        hpi=[
            "Three days of a cold then tonight progressive wheeze; used the inhaler eight times.",
            "Exposed to a cat, then tight chest and audible wheeze.",
        ],
        associated=["Wheeze", "Cough", "Chest tightness"],
        negatives=["No hives", "No leg swelling"],
        pmh=["Asthma", "Allergic rhinitis"],
        meds=["Albuterol", "Forgotten controller inhaler"],
        allergies=["Cats", "NKDA"],
        family=["Parent has asthma."],
        ros=["No fever now.", "Can still speak short phrases."],
        teaching=["Ask controllers, triggers, and prior intubations."],
        vitals_base=v(36.9, 122, "132/80", 28, 92, 3),
    ),
    CaseSeed(
        domain="appendicitis",
        titles=["Pain that migrated to the right", "Anorexia and RLQ pain", "Walks bent to the right"],
        complaints=["Stomach pain since last night", "Right lower abdominal pain", "Belly pain and vomiting"],
        age_range=(16, 38),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["Acute appendicitis", "Perforated appendicitis", "Early appendicitis"],
        differentials=["Appendicitis", "Mesenteric adenitis", "Ectopic / ovarian torsion", "Stone", "Gastroenteritis"],
        next_steps=["NPO, IV fluids", "CBC, CRP, pregnancy test if needed", "US or CT", "Surgery consult"],
        hpi=[
            "Periumbilical ache that moved to the RLQ with anorexia and one vomit.",
            "Pain worse over speed bumps on the way in; has not wanted food all day.",
        ],
        associated=["Anorexia", "Nausea", "Low-grade fever"],
        negatives=["No diarrhea", "No dysuria"],
        pmh=["None"],
        meds=["Ibuprofen this morning"],
        allergies=["NKDA"],
        family=["Non-contributory."],
        ros=["Last stool yesterday.", "No vaginal bleeding."],
        teaching=["Migratory pain plus anorexia is classic; still exclude GU causes."],
        vitals_base=v(38.0, 98, "122/76", 18, 99, 7),
    ),
    CaseSeed(
        domain="gi-bleed",
        titles=["Black stools and lightheadedness", "Coffee-ground emesis", "Passing maroon stool"],
        complaints=["Dizziness and dark stool", "Vomiting blood", "Black sticky stools"],
        age_range=(42, 82),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["Upper GI bleed from peptic ulcer", "Variceal bleed", "Lower GI bleed from diverticula"],
        differentials=["PUD bleed", "Varices", "Diverticular bleed", "Ischemic colitis", "Malignancy"],
        next_steps=["ABCs, two IVs", "Type and screen", "CBC, INR, BUN", "PPI", "GI consult"],
        hpi=[
            "Three black tarry stools today, then stood up and nearly fainted. Takes daily NSAIDs.",
            "Vomited coffee-ground material after a binge and has known liver disease.",
        ],
        associated=["Melena", "Lightheadedness", "Fatigue"],
        negatives=["No chest pain", "No fever"],
        pmh=["Osteoarthritis", "Alcohol use disorder", "Prior ulcer"],
        meds=["Ibuprofen", "Aspirin 81 mg"],
        allergies=["NKDA"],
        family=["Father had colon cancer at 70."],
        ros=["No weight loss they noticed.", "Some epigastric burn for weeks."],
        teaching=["Ask NSAIDs, alcohol, liver disease, and volume symptoms."],
        vitals_base=v(36.4, 118, "92/58", 20, 97, 2),
    ),
    CaseSeed(
        domain="cholecystitis",
        titles=["Fatty-meal pain under the ribs", "RUQ pain into the scapula", "Fever after biliary colic"],
        complaints=["Right upper abdominal pain", "Pain after fried food", "Stomach pain and fever"],
        age_range=(28, 68),
        genders=["Female", "Male"],
        settings=["Emergency department", "Urgent care to ED"],
        diagnoses=["Acute cholecystitis", "Choledocholithiasis", "Biliary colic"],
        differentials=["Cholecystitis", "Cholangitis", "Hepatitis", "PUD", "Inferior MI"],
        next_steps=["LFTs, lipase, CBC", "RUQ ultrasound", "NPO, fluids, analgesia", "Surgery if cholecystitis"],
        hpi=[
            "Steady RUQ pain after pizza, radiating to the scapula, with nausea and low fever.",
            "Prior episodic post-prandial pain; this episode has lasted 8 hours and they look ill.",
        ],
        associated=["Nausea", "Fever", "RUQ pain"],
        negatives=["No diarrhea", "No chest pressure"],
        pmh=["Obesity", "Known gallstones"],
        meds=["OCPs", "None"],
        allergies=["NKDA"],
        family=["Mother had a cholecystectomy."],
        ros=["Urine not dark.", "Stools still brown."],
        teaching=["Fatty meal, scapular radiation, and duration >6 hours."],
        vitals_base=v(38.2, 102, "136/82", 18, 98, 8),
    ),
    CaseSeed(
        domain="pancreatitis",
        titles=["Boring pain through to the back", "Pain after a heavy drinking weekend", "Leaning forward to get comfortable"],
        complaints=["Severe upper stomach pain", "Pain straight through my back", "Vomiting and belly pain"],
        age_range=(28, 62),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["Acute pancreatitis", "Alcoholic pancreatitis", "Gallstone pancreatitis"],
        differentials=["Pancreatitis", "PUD perforation", "Cholecystitis", "Inferior MI", "SBO"],
        next_steps=["NPO, IV fluids", "Lipase, CMP, triglycerides", "ECG", "Ultrasound if gallstone likely"],
        hpi=[
            "Constant boring epigastric pain to the back after a whiskey binge, better leaning forward.",
            "Pain and vomiting after a fatty meal in a patient with known stones.",
        ],
        associated=["Vomiting", "Anorexia"],
        negatives=["No diarrhea", "No hematemesis"],
        pmh=["Alcohol use disorder", "Gallstones"],
        meds=["None", "Acetaminophen last night"],
        allergies=["NKDA"],
        family=["Sibling has gallstones."],
        ros=["No jaundice noticed.", "No chest pressure."],
        teaching=["Back-boring pain plus alcohol or gallstones; still exclude ACS."],
        vitals_base=v(37.7, 112, "140/86", 20, 97, 9),
    ),
    CaseSeed(
        domain="sbo",
        titles=["Bilious vomiting and no flatus", "Colicky pain with prior surgery", "Distended and obstipated"],
        complaints=["Vomiting and bloating", "Crampy belly pain", "Cannot pass gas"],
        age_range=(36, 80),
        genders=["Female", "Male"],
        settings=["Emergency department"],
        diagnoses=["Small-bowel obstruction", "Adhesive SBO", "Incarcerated hernia with SBO"],
        differentials=["SBO", "Ileus", "Gastroenteritis", "Large-bowel obstruction", "Mesenteric ischemia"],
        next_steps=["NPO, NG if needed", "IV fluids", "CBC, lactate", "CT abdomen/pelvis", "Surgery consult"],
        hpi=[
            "Colicky pain, bilious vomiting, no stool or flatus for a day; prior appendectomy.",
            "A bulge in the groin became painful and they started vomiting.",
        ],
        associated=["Vomiting", "Distension", "Obstipation"],
        negatives=["No bloody stool", "No fever at first"],
        pmh=["Prior abdominal surgery", "Ventral hernia"],
        meds=["Oxycodone after a fall last week", "None"],
        allergies=["NKDA"],
        family=["Non-contributory."],
        ros=["No chest pain.", "Last flatus yesterday morning."],
        teaching=["Prior surgery plus obstipation is SBO until imaged."],
        vitals_base=v(37.2, 108, "128/78", 20, 98, 8),
    ),
    CaseSeed(
        domain="stroke",
        titles=["Face droop at breakfast", "Arm weakness that will not lift", "Sudden slurred speech"],
        complaints=["Right-sided weakness", "Cannot speak clearly", "Face looks uneven"],
        age_range=(58, 88),
        genders=["Female", "Male"],
        settings=["Emergency department", "Brought from a diner"],
        diagnoses=["Acute ischemic stroke", "Left MCA syndrome", "TIA that has not fully resolved"],
        differentials=["Ischemic stroke", "TIA", "Hypoglycemia", "Seizure with Todd paresis", "Migraine"],
        next_steps=["Last-known-well time", "Glucose", "Stroke code, noncontrast CT", "NIHSS", "Thrombolysis window check"],
        hpi=[
            "Partner saw facial droop and arm drift 50 minutes ago; last seen well at breakfast.",
            "Sudden aphasia while on the phone; still cannot find words.",
        ],
        associated=["Dysarthria", "Arm drift", "Facial droop"],
        negatives=["No seizure witnessed", "No trauma"],
        pmh=["Atrial fibrillation off anticoagulation", "Hypertension"],
        meds=["Missed apixaban", "Amlodipine"],
        allergies=["NKDA"],
        family=["Brother had a stroke."],
        ros=["No chest pain.", "No fever."],
        teaching=["Time of onset is the first question."],
        vitals_base=v(36.7, 88, "176/96", 16, 98, 0),
    ),
    CaseSeed(
        domain="meningitis",
        titles=["Worst headache with photophobia", "Fever and a stiff neck", "Dorm roommate who is confused"],
        complaints=["Severe headache and fever", "Neck pain and light hurts", "Fever and confusion"],
        age_range=(17, 34),
        genders=["Female", "Male"],
        settings=["College health to ED", "Emergency department"],
        diagnoses=["Acute bacterial meningitis", "Meningococcal meningitis", "Viral meningitis"],
        differentials=["Bacterial meningitis", "Viral meningitis", "SAH", "Influenza", "Migraine"],
        next_steps=["Isolation", "Blood cultures", "Empiric antibiotics + dexamethasone", "LP unless contraindicated"],
        hpi=[
            "Rapidly worsening headache, fever, photophobia, and this morning they called a roommate by the wrong name.",
            "Neck stiffness and vomiting after 12 hours of the worst headache of their life.",
        ],
        associated=["Fever", "Photophobia", "Neck stiffness"],
        negatives=["No trauma", "No known prior migraine"],
        pmh=["None", "Asplenia"],
        meds=["None"],
        allergies=["Sulfa — hives", "NKDA"],
        family=["Non-contributory."],
        extra_social=["lives in a dorm"],
        ros=["Unsure about meningococcal vaccine.", "No rash they have seen."],
        teaching=["Do not delay antibiotics for imaging if suspicion is high."],
        vitals_base=v(39.1, 114, "108/64", 22, 98, 9),
    ),
    CaseSeed(
        domain="sah",
        titles=["Thunderclap while lifting", "Worst headache of my life", "Sudden headache then vomiting"],
        complaints=["Sudden worst headache", "Thunderclap headache", "Headache after straining"],
        age_range=(28, 62),
        genders=["Female", "Male"],
        settings=["Emergency department"],
        diagnoses=["Subarachnoid hemorrhage", "Aneurysmal SAH", "Sentinel-bleed SAH"],
        differentials=["SAH", "Migraine", "Meningitis", "Dissection", "Pituitary apoplexy"],
        next_steps=["Noncontrast CT now", "LP if CT negative and suspicion high", "BP control", "Neurosurgery"],
        hpi=[
            "Instant 10/10 occipital headache at peak exertion, then vomiting and a stiff neck.",
            "Worst headache of life, peaked in seconds, unlike any migraine.",
        ],
        associated=["Vomiting", "Photophobia", "Neck stiffness"],
        negatives=["No fever at onset", "No trauma"],
        pmh=["Hypertension", "Polycystic kidney disease"],
        meds=["None", "Oral contraceptive"],
        allergies=["NKDA"],
        family=["Cousin had a brain aneurysm."],
        ros=["No seizure they know of.", "Brief loss of consciousness for a few seconds."],
        teaching=["Thunderclap peaking in seconds is SAH until cleared."],
        vitals_base=v(36.9, 96, "168/98", 18, 99, 10),
    ),
    CaseSeed(
        domain="seizure",
        titles=["First witnessed shaking spell", "Tongue bite and a long sleep", "Confused after a collapse"],
        complaints=["I blacked out and woke up sore", "People say I shook", "First seizure"],
        age_range=(18, 55),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["First unprovoked seizure", "Alcohol-withdrawal seizure", "Focal seizure with secondary generalization"],
        differentials=["Seizure", "Syncope", "Psychogenic nonepileptic spell", "Hypoglycemia", "Arrhythmia"],
        next_steps=["Glucose", "Protect airway if still post-ictal", "Labs, ECG", "CT if first or focal", "Neuro follow-up"],
        hpi=[
            "Witnessed 90 seconds of tonic-clonic activity, tongue bite, then sleepy and sore.",
            "Stopped drinking two days ago, then a convulsion; still confused.",
        ],
        associated=["Tongue bite", "Incontinence", "Post-ictal confusion"],
        negatives=["No chest pain before", "No prodromal tunnel vision they recall"],
        pmh=["None", "Alcohol use disorder"],
        meds=["None"],
        allergies=["NKDA"],
        family=["Uncle has epilepsy."],
        ros=["No pregnancy known.", "No fever."],
        teaching=["Witness description and tongue bite help separate seizure from syncope."],
        vitals_base=v(37.3, 108, "132/80", 18, 98, 3),
    ),
    CaseSeed(
        domain="dka",
        titles=["Thirst, vomiting, and deep breathing", "New polyuria in a thin teen", "Fruity breath and confusion"],
        complaints=["Vomiting and very thirsty", "Breathing fast and tired", "Confusion and frequent urination"],
        age_range=(16, 44),
        genders=["Female", "Male"],
        settings=["Emergency department"],
        diagnoses=["Diabetic ketoacidosis", "New-onset type 1 diabetes with DKA", "DKA from missed insulin"],
        differentials=["DKA", "HHS", "Gastroenteritis", "Sepsis", "Toxic alcohol"],
        next_steps=["Fingerstick glucose", "VBG, ketones, BMP", "IV fluids", "Insulin drip protocol", "Potassium repletion plan"],
        hpi=[
            "Two weeks of thirst and weight loss, then a day of vomiting and Kussmaul breathing.",
            "Ran out of insulin, now nauseated, sleepy, and urinating constantly.",
        ],
        associated=["Polyuria", "Polydipsia", "Vomiting"],
        negatives=["No stiff neck", "No focal weakness"],
        pmh=["Type 1 diabetes", "None"],
        meds=["Missed insulin", "None"],
        allergies=["NKDA"],
        family=["Cousin has type 1 diabetes."],
        ros=["No chest pain.", "Possible mild viral illness last week."],
        teaching=["Always check glucose in vomiting plus tachypnea."],
        vitals_base=v(37.4, 124, "102/64", 28, 99, 3),
    ),
    CaseSeed(
        domain="thyroid",
        titles=["Racing heart and heat intolerance", "Weight loss with a tremor", "Palpitations and stare"],
        complaints=["Palpitations for two weeks", "Heart racing and sweating", "Shaky and losing weight"],
        age_range=(18, 46),
        genders=["Female", "Male"],
        settings=["Outpatient clinic", "Urgent care"],
        diagnoses=["Overt hyperthyroidism (Graves)", "Thyrotoxicosis", "Thyroid-storm risk"],
        differentials=["Graves / hyperthyroidism", "Panic", "SVT", "Anemia", "Stimulant use"],
        next_steps=["ECG", "TSH and free T4", "CBC, pregnancy test", "Beta-blocker if needed", "Endocrine follow-up"],
        hpi=[
            "Two weeks of pounding heart, heat intolerance, diarrhea, and an 8-pound loss with a bigger appetite.",
            "Tremor and insomnia; friends say the eyes look more open.",
        ],
        associated=["Heat intolerance", "Tremor", "Weight loss"],
        negatives=["No syncope", "No chest pain"],
        pmh=["None"],
        meds=["Occasional ibuprofen"],
        allergies=["NKDA"],
        family=["Mother has Hashimoto thyroiditis."],
        ros=["Lighter periods.", "Two cups of coffee only."],
        teaching=["Pair palpitations with systemic thyrotoxic features."],
        vitals_base=v(37.3, 118, "142/76", 18, 99, 0),
    ),
    CaseSeed(
        domain="pyelo",
        titles=["Fever and flank pain", "Dysuria that became shaking chills", "CVA tenderness after a UTI"],
        complaints=["Back pain and fever", "Painful urination and chills", "Flank pain"],
        age_range=(18, 55),
        genders=["Female", "Male"],
        settings=["Emergency department", "Urgent care"],
        diagnoses=["Acute pyelonephritis", "Complicated UTI", "Pyelo in pregnancy"],
        differentials=["Pyelonephritis", "Nephrolithiasis", "Appendicitis", "PID", "Musculoskeletal strain"],
        next_steps=["UA and culture", "Pregnancy test", "CBC", "IV fluids and antibiotics", "Imaging if obstructed or septic"],
        hpi=[
            "Dysuria for three days, then fever, shaking chills, and right flank pain.",
            "Costovertebral pain and vomiting; cannot keep down oral antibiotics.",
        ],
        associated=["Fever", "Dysuria", "Flank pain"],
        negatives=["No vaginal bleeding", "No diarrhea"],
        pmh=["Recurrent UTIs", "None"],
        meds=["None"],
        allergies=["NKDA", "Cipro — tendon pain"],
        family=["Non-contributory."],
        ros=["Last period two weeks ago.", "No stone history."],
        teaching=["Lower UTI plus fever and flank pain is pyelo."],
        vitals_base=v(39.0, 112, "118/70", 20, 98, 6),
    ),
    CaseSeed(
        domain="stone",
        titles=["Colicky flank pain that will not sit still", "Pain to the groin with blood in urine", "Writhing with a normal belly exam"],
        complaints=["Severe side pain", "Pain from back to groin", "Blood in my urine and pain"],
        age_range=(22, 60),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["Ureterolithiasis", "Obstructing kidney stone", "Distal ureteral stone"],
        differentials=["Nephrolithiasis", "Pyelo", "AAA if older", "Appendicitis", "Ovarian torsion"],
        next_steps=["UA", "Pain control", "Noncontrast CT or US", "Strain urine", "Urology if infected or obstructed"],
        hpi=[
            "Sudden 9/10 flank pain radiating to the groin; cannot find a comfortable position; pink urine.",
            "Colicky waves of pain with nausea; similar milder episode last year.",
        ],
        associated=["Nausea", "Hematuria", "Restlessness"],
        negatives=["No fever", "No diarrhea"],
        pmh=["Prior kidney stone", "None"],
        meds=["None"],
        allergies=["NKDA"],
        family=["Father had stones."],
        ros=["No chest pain.", "Still making urine."],
        teaching=["Writhing pain plus hematuria; image if first stone or older adult."],
        vitals_base=v(36.8, 102, "148/88", 18, 99, 9),
    ),
    CaseSeed(
        domain="ectopic",
        titles=["Unilateral pain and spotting", "Shoulder pain with a late period", "Syncope and pelvic pain"],
        complaints=["Pelvic pain and spotting", "One-sided lower pain", "Passed out with belly pain"],
        age_range=(18, 40),
        genders=["Female"],
        settings=["Emergency department", "Urgent care to ED"],
        diagnoses=["Ruptured ectopic pregnancy", "Unruptured ectopic pregnancy", "Pregnancy of unknown location"],
        differentials=["Ectopic", "Threatened miscarriage", "Ovarian torsion", "PID", "Appendicitis"],
        next_steps=["Urine and serum hCG", "CBC", "TVUS", "RhoGAM if indicated", "GYN / surgery if unstable"],
        hpi=[
            "Six weeks from LMP, unilateral pelvic pain, brown spotting, then lightheaded in the bathroom.",
            "Sharp left pain and referred shoulder pain; IUD in place.",
        ],
        associated=["Spotting", "Shoulder pain", "Lightheadedness"],
        negatives=["No fever", "No dysuria"],
        pmh=["Prior PID", "IUD", "None"],
        meds=["IUD", "None"],
        allergies=["NKDA"],
        family=["Non-contributory."],
        ros=["Sexually active.", "No heavy soaking."],
        teaching=["Any woman of childbearing age with pain or syncope needs a pregnancy test."],
        vitals_base=v(36.7, 118, "96/60", 20, 98, 7),
    ),
    CaseSeed(
        domain="preeclampsia",
        titles=["Headache and swelling at 34 weeks", "Lights flashing in late pregnancy", "High blood pressure after 20 weeks"],
        complaints=["Headache while pregnant", "Swelling and seeing spots", "Severe headache at 34 weeks"],
        age_range=(18, 42),
        genders=["Female"],
        settings=["L&D triage", "Emergency department"],
        diagnoses=["Preeclampsia with severe features", "Preeclampsia", "HELLP syndrome"],
        differentials=["Preeclampsia", "Migraine", "SAH", "TTP", "Dehydration"],
        next_steps=["OB emergency", "BP, CBC, LFTs, creatinine, urine protein", "Fetal monitoring", "Magnesium if indicated"],
        hpi=[
            "G1 at 34 weeks with frontal headache, photopsia, and sudden hand and face swelling.",
            "RUQ pain and headache; home BP cuff has been 160s.",
        ],
        associated=["Visual scotomata", "Edema", "RUQ discomfort"],
        negatives=["No trauma", "No fever"],
        pmh=["First pregnancy", "Chronic hypertension"],
        meds=["Prenatal vitamin", "Labetalol"],
        allergies=["NKDA"],
        family=["Sister had preeclampsia."],
        ros=["Baby still moving.", "No vaginal bleeding."],
        teaching=["Headache plus visual change after 20 weeks is preeclampsia until proven otherwise."],
        vitals_base=v(36.8, 98, "172/108", 18, 98, 5),
    ),
    CaseSeed(
        domain="dvt-cellulitis",
        titles=["Unilateral swollen painful calf", "Red hot leg after a flight", "One leg bigger than the other"],
        complaints=["Swollen left leg", "Painful red calf", "Leg swelling after travel"],
        age_range=(26, 74),
        genders=["Female", "Male"],
        settings=["Urgent care", "Emergency department"],
        diagnoses=["Lower-extremity DVT", "DVT with cellulitis mimic", "Provoked DVT"],
        differentials=["DVT", "Cellulitis", "Baker cyst rupture", "Chronic venous insufficiency", "Superficial thrombophlebitis"],
        next_steps=["Wells score", "Duplex US", "D-dimer if low probability", "Anticoagulate if confirmed"],
        hpi=[
            "Three days of unilateral calf swelling and tightness after a long drive; no fever.",
            "Red painful shin but also a lot of swelling and a recent hospitalization.",
        ],
        associated=["Unilateral edema", "Calf tightness"],
        negatives=["No trauma they recall", "No chest pain yet"],
        pmh=["Cancer on treatment", "Prior clot", "None"],
        meds=["OCPs", "Tamoxifen", "None"],
        allergies=["NKDA"],
        family=["Parent had a DVT."],
        ros=["No fever.", "No dyspnea now."],
        teaching=["Unilateral swelling after stasis is DVT until duplexed."],
        vitals_base=v(37.0, 92, "128/78", 16, 98, 5),
    ),
    CaseSeed(
        domain="septic-joint",
        titles=["Hot swollen knee that will not flex", "Fever and a single angry joint", "Cannot bear weight on one hip"],
        complaints=["Painful swollen knee", "Fever and joint pain", "Cannot walk on my hip"],
        age_range=(19, 78),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["Septic arthritis", "Gonococcal septic arthritis", "Prosthetic-joint infection"],
        differentials=["Septic joint", "Gout", "Lyme", "Trauma", "Rheumatoid flare"],
        next_steps=["Do not wait on oral antibiotics alone", "Arthrocentesis before antibiotics if stable", "CBC, CRP, cultures", "Ortho consult"],
        hpi=[
            "One knee became hot, swollen, and impossible to bend over 24 hours, now febrile.",
            "Sexually active young adult with migratory arthralgias then a locked wrist.",
        ],
        associated=["Fever", "Refusal to range the joint"],
        negatives=["No trauma", "No tick they remember"],
        pmh=["Gout", "Knee replacement", "None"],
        meds=["Allopurinol", "None"],
        allergies=["NKDA"],
        family=["Non-contributory."],
        ros=["Possible urethral discharge.", "No other joints as bad."],
        teaching=["A single hot joint is infection until fluid is sampled."],
        vitals_base=v(38.6, 108, "122/74", 18, 98, 9),
    ),
    CaseSeed(
        domain="cauda-equina",
        titles=["Back pain plus saddle numbness", "Cannot void after a disc flare", "Bilateral sciatica and incontinence"],
        complaints=["Back pain and numb groin", "Cannot pee and my legs feel weak", "Sciatica in both legs"],
        age_range=(28, 64),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["Cauda equina syndrome", "Acute lumbar disc herniation with CES", "Epidural compression"],
        differentials=["Cauda equina", "Simple sciatica", "Epidural abscess", "AAA", "Guillain-Barré"],
        next_steps=["Urgent MRI", "Foley if in retention", "Dexamethasone if tumor suspected", "Spine surgery consult"],
        hpi=[
            "Chronic back pain exploded last night; now saddle numbness and overflow incontinence.",
            "Bilateral sciatica and they have not voided in 12 hours.",
        ],
        associated=["Saddle anesthesia", "Urinary retention", "Bilateral leg symptoms"],
        negatives=["No fever unless abscess", "No abdominal pain"],
        pmh=["Known disc disease", "IV drug use", "None"],
        meds=["NSAIDs", "None"],
        allergies=["NKDA"],
        family=["Non-contributory."],
        ros=["No chest pain.", "Legs feel heavy."],
        teaching=["Saddle anesthesia or new incontinence is an emergency MRI, not next-week PT."],
        vitals_base=v(36.8, 96, "138/82", 16, 99, 8),
    ),
    CaseSeed(
        domain="anaphylaxis",
        titles=["Hives and throat tightness after peanuts", "Wheeze after a bee sting", "Lip swelling from a new antibiotic"],
        complaints=["Throat closing and hives", "Allergic reaction", "Cannot breathe after a sting"],
        age_range=(16, 55),
        genders=["Female", "Male"],
        settings=["Emergency department", "Ambulance bay"],
        diagnoses=["Anaphylaxis", "Food-triggered anaphylaxis", "Drug-induced anaphylaxis"],
        differentials=["Anaphylaxis", "Asthma", "Panic", "ACE-inhibitor angioedema", "Foreign body"],
        next_steps=["IM epinephrine now", "Airway support", "IV fluids", "Antihistamine and steroid adjuncts", "Observe for biphasic reaction"],
        hpi=[
            "Peanut cookie 10 minutes ago, then hives, wheeze, and a feeling the throat is closing.",
            "First dose of amoxicillin, then facial swelling and dizziness.",
        ],
        associated=["Urticaria", "Wheeze", "Lightheadedness"],
        negatives=["No fever", "No gradual days-long course"],
        pmh=["Known peanut allergy", "None"],
        meds=["Forgot epinephrine autoinjector", "Lisinopril"],
        allergies=["Peanuts", "Amoxicillin"],
        family=["Sibling has food allergy."],
        ros=["No chest pain first.", "Voice feels hoarse."],
        teaching=["Epinephrine first, not an antihistamine trial."],
        vitals_base=v(36.6, 128, "86/50", 26, 91, 4),
    ),
    CaseSeed(
        domain="overdose",
        titles=["Acetaminophen after an argument", "Sleepy after extra pills", "Nausea hours after a handful of tablets"],
        complaints=["I took too many pills", "Nauseated after an overdose", "Drowsy and I took something"],
        age_range=(16, 48),
        genders=["Female", "Male"],
        settings=["Emergency department"],
        diagnoses=["Acetaminophen overdose", "Mixed ingestion with acetaminophen", "Intentional overdose"],
        differentials=["Acetaminophen toxicity", "Opioid overdose", "Anticholinergic toxidrome", "Psychiatric crisis without toxin"],
        next_steps=["ABCs", "Fingerstick glucose", "APAP level, ECG, ASA, etOH", "N-acetylcysteine if indicated", "Psychiatry once stable"],
        hpi=[
            "Took a bottle of extra-strength acetaminophen 6 hours ago after a fight; now nauseated.",
            "Found with empty pill bottles; time of ingestion unclear; a little sleepy.",
        ],
        associated=["Nausea", "Abdominal pain", "Somnolence"],
        negatives=["No trauma", "No fever"],
        pmh=["Depression", "None"],
        meds=["Sertraline", "None prescribed"],
        allergies=["NKDA"],
        family=["Aunt has bipolar disorder."],
        ros=["Suicidal intent earlier, now regretful.", "No chest pain."],
        teaching=["Always get a timed acetaminophen level and involve psych after medical clearance."],
        vitals_base=v(36.5, 100, "118/72", 16, 98, 3),
    ),
    CaseSeed(
        domain="delirium",
        titles=["Night confusion in a nursing-home resident", "Suddenly not acting like themself", "Fever and picking at the sheets"],
        complaints=["Confusion since last night", "Family says they are not themselves", "Agitation and fever"],
        age_range=(72, 92),
        genders=["Female", "Male"],
        settings=["Emergency department", "Brought from a facility"],
        diagnoses=["Delirium from UTI", "Sepsis-related delirium", "Medication-related delirium"],
        differentials=["Delirium", "Dementia unmasking", "Stroke", "Hypoglycemia", "Withdrawal"],
        next_steps=["Glucose, pulse ox", "UA, CBC, BMP, CXR", "Med rec including anticholinergics", "Treat cause, reorient"],
        hpi=[
            "Usually pleasant resident became agitated overnight, picking at the air; Foley recently removed.",
            "Daughter says they are inattentive and the story changes minute to minute after a new sleeping pill.",
        ],
        associated=["Inattention", "Sleep-wake reversal", "Possible dysuria"],
        negatives=["No obvious focal weakness", "No head strike seen"],
        pmh=["Mild cognitive impairment", "BPH", "Diabetes"],
        meds=["New diphenhydramine", "Donepezil", "Metformin"],
        allergies=["NKDA"],
        family=["Daughter is historian."],
        ros=["Fewer wet briefs.", "No chest pain they report."],
        teaching=["Acute inattention is delirium; hunt infection, meds, and metabolic causes."],
        vitals_base=v(38.4, 104, "148/82", 20, 94, 0),
    ),
    CaseSeed(
        domain="syncope",
        titles=["Passed out while shaving", "Collapse without warning", "Faint after a long stand"],
        complaints=["I passed out", "Fainting spell", "Woke up on the floor"],
        age_range=(19, 82),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["Reflex syncope", "Arrhythmic syncope", "Orthostatic syncope"],
        differentials=["Vasovagal syncope", "Arrhythmia", "Aortic stenosis", "Seizure", "PE", "GI bleed"],
        next_steps=["ECG", "Orthostatics", "Glucose", "CBC if bleed suspected", "Admit if high-risk cardiac features"],
        hpi=[
            "Prodrome of warmth and tunnel vision after standing in church, brief loss, no confusion afterward.",
            "No warning, palpitations, hit the floor; a bystander says they were pale.",
        ],
        associated=["Diaphoresis", "Nausea", "or no prodrome"],
        negatives=["No tongue bite", "No prolonged confusion"],
        pmh=["Aortic stenosis", "None", "Anemia"],
        meds=["None", "Tamsulosin"],
        allergies=["NKDA"],
        family=["Uncle died suddenly."],
        ros=["Black stools? they are not sure.", "No chest pain after."],
        teaching=["Prodrome versus sudden collapse changes the cardiac risk."],
        vitals_base=v(36.6, 48, "102/70", 14, 98, 1),
    ),
    CaseSeed(
        domain="sickle-crisis",
        titles=["Bone pain like prior crises", "Chest pain in a patient with sickle cell", "Cannot get comfortable, bones ache"],
        complaints=["Sickle cell pain crisis", "Whole-body bone pain", "Chest pain with sickle cell"],
        age_range=(16, 38),
        genders=["Male", "Female"],
        settings=["Emergency department"],
        diagnoses=["Vaso-occlusive crisis", "Acute chest syndrome until proven otherwise", "Uncomplicated VOC"],
        differentials=["VOC", "Acute chest", "Osteomyelitis", "ACS", "Dehydration"],
        next_steps=["Oxygen if hypoxic", "Analgesia, fluids", "CXR if chest symptoms", "CBC, retic", "Incentive spirometry"],
        hpi=[
            "Typical long-bone pain after a viral illness, 8/10, no fever at home.",
            "Pain plus new cough and chest tightness — worse than a usual crisis.",
        ],
        associated=["Bone pain", "Possible cough"],
        negatives=["No focal neurologic change", "No priapism this time"],
        pmh=["HbSS", "Prior acute chest"],
        meds=["Hydroxyurea", "Folic acid"],
        allergies=["NKDA"],
        family=["Sibling also has sickle cell."],
        ros=["No new weakness.", "Using incentive spirometer poorly."],
        teaching=["Chest symptoms in sickle cell are acute chest until a CXR is clear."],
        vitals_base=v(37.6, 110, "124/76", 22, 93, 8),
    ),
]


def fingerprint(case: PatientCase) -> str:
    return " | ".join(
        [
            case.hidden_sheet.hidden_diagnosis.lower(),
            case.presenting_complaint.lower(),
            case.title.lower(),
        ]
    )


def _jitter_vitals(base: Vitals) -> Vitals:
    sys, dia = (int(part) for part in base.blood_pressure.split("/"))
    return Vitals(
        temperature_c=round(base.temperature_c + random.uniform(-0.3, 0.4), 1),
        heart_rate=max(42, base.heart_rate + random.randint(-8, 10)),
        blood_pressure=f"{sys + random.randint(-8, 10)}/{max(40, dia + random.randint(-6, 8))}",
        respiratory_rate=max(10, base.respiratory_rate + random.randint(-2, 3)),
        spo2=min(100, max(82, base.spo2 + random.randint(-2, 2))),
        pain_score=None if base.pain_score is None else min(10, max(0, base.pain_score + random.randint(-1, 1))),
    )


def realize_seed(seed: CaseSeed, age: int | None = None, gender: str | None = None) -> PatientCase:
    picked_gender = gender.title() if gender else random.choice(seed.genders)
    if picked_gender not in seed.genders:
        picked_gender = seed.genders[0]
    picked_age = age if age else random.randint(*seed.age_range)
    diagnosis = random.choice(seed.diagnoses)
    title = random.choice(seed.titles)
    complaint = random.choice(seed.complaints)
    setting = random.choice(seed.settings)
    brief = (
        f"A {picked_age}-year-old {picked_gender.lower()} presents with {complaint.lower()}. "
        + random.choice(seed.hpi)
    )
    social = (
        f"{random.choice(JOBS).capitalize()}. {random.choice(HOMES).capitalize()}. "
        f"{random.choice(HABITS).capitalize()}."
    )
    if seed.extra_social:
        social += " " + random.choice(seed.extra_social).capitalize() + "."
    return PatientCase(
        id=new_id(),
        title=title,
        presenting_complaint=complaint,
        age=picked_age,
        gender=picked_gender,
        setting=setting,
        vitals=_jitter_vitals(seed.vitals_base),
        brief_history=brief,
        generated=True,
        hidden_sheet=HiddenSheet(
            hidden_diagnosis=diagnosis,
            acceptable_differentials=list(seed.differentials),
            recommended_next_steps=list(seed.next_steps),
            history_of_present_illness=random.choice(seed.hpi),
            associated_symptoms=list(seed.associated),
            pertinent_negatives=list(seed.negatives),
            past_medical_history=list(seed.pmh),
            medications=list(seed.meds),
            allergies=[random.choice(seed.allergies)],
            social_history=social,
            family_history=random.choice(seed.family),
            review_of_systems=random.choice(seed.ros),
            personality_notes=random.choice(PERSONAS),
            teaching_points=list(seed.teaching),
        ),
    )


def mock_circuit(count: int, avoid: list[str]) -> list[PatientCase]:
    avoid_blob = " ".join(avoid).lower()
    available = [seed for seed in SEEDS if seed.domain not in avoid_blob and not any(d.lower() in avoid_blob for d in seed.diagnoses)]
    if len(available) < count:
        available = list(SEEDS)
        random.shuffle(available)
    random.shuffle(available)

    picked: list[CaseSeed] = []
    used_domains: set[str] = set()
    for seed in available:
        if seed.domain in used_domains:
            continue
        picked.append(seed)
        used_domains.add(seed.domain)
        if len(picked) >= count:
            break
    if len(picked) < count:
        extras = [seed for seed in SEEDS if seed not in picked]
        random.shuffle(extras)
        picked.extend(extras[: count - len(picked)])

    return [realize_seed(seed) for seed in picked[:count]]


def mock_single_case(presenting_complaint: str | None, age: int | None, gender: str | None) -> PatientCase:
    pool = list(SEEDS)
    if presenting_complaint:
        needle = presenting_complaint.lower()
        filtered = [
            seed
            for seed in pool
            if needle in seed.domain
            or any(needle in item.lower() for item in seed.complaints + seed.titles + seed.diagnoses)
        ]
        if filtered:
            pool = filtered
    seed = deepcopy(random.choice(pool))
    return realize_seed(seed, age=age, gender=gender)
