from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
form nltk import data, download
import os
from app.methods.old import calculate_enhanced_ats_score, generate_improvement_suggestions
from app.methods.new import LLMATSCalculator

from dotenv import load_dotenv
load_dotenv()
header = os.getenv('API_HEADER')

@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        data.find('corpora/wordnet')
    except LookupError:
        download('wordnet')

    try:
        data.find('corpora/omw-1.4')
    except LookupError:
        download('omw-1.4')
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
async def calculate_ats(resume: UploadFile = File(...), jd: UploadFile = File(...), x_api_header: str = Header(...)):
    if x_api_header != header:
        raise HTTPException(status_code=403, detail="Unauthorized access")
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

@app.post("/new/ats")
async def calculate_ats(resume: UploadFile = File(...), jd: UploadFile = File(...)x_api_header: str = Header(...)):
    if x_api_header != header:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    # Validate file extensions
    if not resume.filename.endswith(".txt") or not jd.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported")
    
    resume_text = (await resume.read()).decode("utf-8", errors="ignore")
    jd_text = (await jd.read()).decode("utf-8", errors="ignore")
    cal_ats = LLMATSCalculator()
    out = cal_ats.run_analysis(jd_text, resume_text)

    return JSONResponse({
        "output_data": out
    })