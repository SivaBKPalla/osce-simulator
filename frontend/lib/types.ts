export type Vitals = {
  temperature_c: number;
  heart_rate: number;
  blood_pressure: string;
  respiratory_rate: number;
  spo2: number;
  pain_score: number | null;
};

export type VisibleCase = {
  id: string;
  title: string;
  presenting_complaint: string;
  age: number;
  gender: string;
  setting: string;
  vitals: Vitals;
  brief_history: string;
  generated: boolean;
};

export type ChatMessage = {
  role: "student" | "patient";
  content: string;
  created_at: string;
};

export type Session = {
  id: string;
  case_id: string;
  messages: ChatMessage[];
  created_at: string;
  submitted: boolean;
};

export type SessionResponse = {
  session: Session;
  case: VisibleCase;
};

export type RubricScore = {
  criterion: string;
  score: number;
  max_score: number;
  comments: string;
};

export type EvaluationResult = {
  overall_score: number;
  max_score: number;
  summary: string;
  hidden_diagnosis: string;
  rubric: RubricScore[];
  missed_questions: string[];
  strengths: string[];
  next_study_focus: string[];
};

export type GenerateCasePayload = {
  presenting_complaint?: string;
  age?: number;
  gender?: string;
};
