# resParser

AI-powered resume screening tool. Paste a job description, upload candidate resumes (PDF/DOCX), and get an instant AI-ranked shortlist with match scores, matched/missing skills, and a short verdict per candidate.

Built with [Groq](https://groq.com) (`openai/gpt-oss-120b`) for structured extraction and scoring, FastAPI for the backend, and a single-page vanilla HTML/JS frontend.

## Features

- Paste any job description — no hardcoding required.
- Drag-and-drop upload for multiple resumes (`.pdf`, `.docx`).
- Each resume is parsed into structured fields (skills, experience, education, projects, certifications) regardless of section-heading wording.
- Candidates are scored against the job description and ranked by match percentage.
- Results UI shows a stat summary, color-coded score badges, and an expandable detail view per candidate (matched skills, missing skills, verdict).
- Failed/unreadable files are reported individually instead of breaking the whole batch.

## Tech stack

- **Backend:** FastAPI, Pydantic, Groq SDK, `pypdf`, `python-docx`
- **Frontend:** Static HTML/CSS/JS (no build step), served directly by FastAPI
- **Package management:** [uv](https://docs.astral.sh/uv/)

## Setup

1. Clone the repo and install dependencies:

   ```bash
   git clone https://github.com/ShivankSubanshi/resparser.git
   cd resparser
   uv sync
   ```

2. Create a `.env` file in the project root (copy `.env.example`) and add your Groq API key:

   ```
   GROQ_API_KEY=your_groq_api_key_here
   ```

   Get a key from [console.groq.com](https://console.groq.com).

## Running locally

```bash
uv run uvicorn app:app --reload
```

Open `http://127.0.0.1:8000/` in your browser. Paste a job description, upload one or more resumes, and click **Analyze Candidates**.

## API

### `POST /api/analyze`

Multipart form request.

| Field | Type | Description |
|---|---|---|
| `job_description` | text | Full job description text |
| `resumes` | file(s) | One or more `.pdf`/`.docx` resume files |

Returns:

```json
{
  "job": { "role": "...", "required_skills": [...], "...": "..." },
  "results": [
    {
      "name": "Candidate Name",
      "score": 82,
      "details": { "matching_skills": [...], "missing_skills": [...], "verdict": "..." }
    }
  ]
}
```

Results are sorted by score descending. Candidates that fail to parse are included with `score: null` and an `error` key in `details`.

### `GET /api/health`

Simple liveness check, returns `{"status": "ok"}`.

## Project structure

```
resparser/
├── app.py              # FastAPI app: /api/analyze, /api/health, serves static/
├── parser.py           # Groq calls, Pydantic schemas, PDF/DOCX text extraction
├── static/
│   └── index.html      # Frontend (HTML/CSS/JS, single file)
├── pyproject.toml
├── uv.lock
└── .env.example
```

## Notes

- Each resume costs two LLM calls (parse + score) with a short delay between calls to stay under Groq rate limits — expect a batch of resumes to take roughly 10-15 seconds per file.
- `GROQ_API_KEY` must stay server-side only; it is never exposed to the frontend.
- This tool is meant to assist screening, not replace it — always have a human review the final shortlist.
