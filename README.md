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
3. If a first sync failed, push this update (Python 3.12 pin) and click **Manual Sync** on the Blueprint page.
4. After the API is live, confirm `API_PROXY_TARGET` on the web service is the public API URL (Render sets this from `RENDER_EXTERNAL_URL`).
5. Optional: add `OPENAI_API_KEY` on the API service for live AI patients and circuits.

A GitHub Action pings the live API and site every 10 minutes so the free Render services stay awake. The website also retries and waits if a request still hits a cold start.

## Features

1. **Fresh circuit on reload** — six diverse stations, different every visit
2. **Interview** — history questions; the patient only answers from the hidden case sheet
3. **Evaluation** — top 3 differentials and next steps, then a structured rubric
