"""
FastAPI backend for resParser.

Exposes POST /api/analyze which accepts a job description (text) and
one or more resume files, runs them through parser.analyze_resumes,
and returns ranked JSON results. Also serves the static frontend
(static/index.html) at "/".
"""

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from parser import analyze_resumes

app = FastAPI(title="resParser API")

# Loosen for local dev / same-origin static hosting. Tighten allow_origins
# to your actual frontend domain once deployed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze")
async def analyze(
    job_description: str = Form(...),
    resumes: list[UploadFile] = File(...),
):
    files = []
    for resume in resumes:
        content = await resume.read()
        files.append((resume.filename, content))

    try:
        job, results = analyze_resumes(job_description, files)
    except Exception as exc:
        # Most likely cause: the LLM provider (Groq) call failed, e.g.
        # bad/missing API key, rate limit, or network issue. This covers
        # the job-description extraction call, which isn't wrapped
        # per-resume like the parse/score calls are.
        raise HTTPException(
            status_code=502,
            detail=f"Failed to analyze job description: {exc}",
        )

    return {
        "job": job.model_dump(),
        "results": results,
    }


@app.get("/api/health")
async def health():
    return {"status": "ok"}


# Serve the frontend. Must be mounted after the API routes above so
# /api/* is matched first.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
