1. Clone the repo
2. docker build -t ats-api . [Make sure you're inside folder]
3. docker run --name ats-api-container -p 8000:8000 --env-file .env ats-api
- Build using docker for better understanding make sure you have .env file.

Code have Two different methods for calculating ATS score.
---
1. OLD METHOD(sry for aribitry naming)
- Uses spacy, nltk, and small embedding model for calculating ATS score or aka NLP based approch.
- I have added all the model weights and other dependencies while dockerising this will prevent downloading of weights every single run.
- FastAPI endpoint: /old/ats
- Input: Resume and JD(TXT FORMAT) -> JSON


2. NEW METHOD
- Uses GEMINI model for calculating ATS
- FastAPI endpoint: /new/ats
- Input: Resume and JD(TXT FORMAT) -> JSON

