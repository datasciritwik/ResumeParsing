from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, JSONResponse
from contextlib import asynccontextmanager
import nltk

from app.methods.old import calculate_enhanced_ats_score, generate_improvement_suggestions

@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet')

    try:
        nltk.data.find('corpora/omw-1.4')
    except LookupError:
        nltk.download('omw-1.4')
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/old/ats")
async def calculate_ats(resume: UploadFile = File(...), jd: UploadFile = File(...)):
    # Validate file extensions
    if not resume.filename.endswith(".txt") or not jd.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    
    resume_text = (await resume.read()).decode("utf-8", errors="ignore")
    jd_text = (await jd.read()).decode("utf-8", errors="ignore")

    # Calculate ATS score using your old function
    results = calculate_enhanced_ats_score(resume_text, jd_text)  # your old function

    # Generate suggestions
    suggestions = generate_improvement_suggestions(results)  # your old function

    return JSONResponse({
        "ats_results": results,
        "suggestions": suggestions
    })
