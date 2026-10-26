# ResumeMatch AI

An approachable full-stack project that compares a PDF resume to a job description using **TF-IDF** and **cosine similarity**. It offers a keyword-based skill gap view and optional MongoDB history without storing resume text.

## How it works

1. The FastAPI backend reads text from the uploaded PDF in memory with PyMuPDF.
2. `TfidfVectorizer` gives important terms more weight and removes common English stop words as a supporting text-comparison signal.
3. The headline score is **skill similarity**: recognized job skills found in the resume ÷ all recognized job skills in the job description.
4. `skill_extractor.py` looks for a small, editable list of skill terms with word-boundary rules. It is intentionally limited; this is not a hiring predictor or a full NLP understanding of either document.

## Run locally

Prerequisites: Python 3.10+ and Node.js 18+.

```bash
cp .env.example .env
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The API docs are at `http://localhost:8000/docs`.

## Optional history

Set `MONGODB_URI` (and optionally `MONGODB_DATABASE`) in `.env`. If MongoDB is not configured or unreachable, matching continues normally and the UI explains that history is unavailable.

## Tests

```bash
cd backend
pytest
```

## Project layout

```text
backend/app/       FastAPI routes, PDF parser, matcher, skills, database
backend/tests/     Essential unit tests
frontend/src/      React interface
```

## Good next improvements

- Add terms relevant to your target roles in `backend/app/skill_extractor.py`.
- Test with several real text-based resume PDFs and job descriptions.
- Add OCR only if scanned-resume support becomes a requirement; it is purposely outside this lightweight project.

