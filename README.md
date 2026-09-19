# OSCE Clinical Reasoning Simulator

A full-stack web app for pre-med students to practice history-taking and differential diagnosis with a virtual standardized patient.

**Live path:** push this repo, then deploy with the included Render blueprint (`render.yaml`). The site URL will look like `https://osce-simulator-web.onrender.com`.

## Stack

- **Backend:** Python, FastAPI
- **Frontend:** Next.js (TypeScript), Tailwind CSS
- **AI:** OpenAI API when `OPENAI_API_KEY` is set; otherwise a diverse mock patient and case circuit

## Run locally

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Deploy as a website

1. Put this project on GitHub (public repo).
2. Open [Render Blueprint](https://dashboard.render.com/blueprints) and connect the repo. Render reads `render.yaml` and starts two free web services: the API and the Next.js UI.
3. After the API is live, confirm `API_PROXY_TARGET` on the web service is the API URL (for example `https://osce-simulator-api.onrender.com`).
4. Optional: add `OPENAI_API_KEY` on the API service for live AI patients and circuits.

Free Render services sleep after idle time; the first visit after a nap can take about a minute.

## Features

1. **Fresh circuit on reload** — six diverse stations, different every visit
2. **Interview** — history questions; the patient only answers from the hidden case sheet
3. **Evaluation** — top 3 differentials and next steps, then a structured rubric
