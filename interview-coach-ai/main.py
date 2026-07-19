from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import re
import io
from pypdf import PdfReader

from agents import get_questions, generate_resume_based_questions, interviewer_agent, evaluator_agent, coach_agent
from storage import save_session, get_progress

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions = {}


class StartRequest(BaseModel):
    candidate_name: str
    role: str
    difficulty: str = "entry"
    background: str = ""


class AnswerRequest(BaseModel):
    session_id: str
    answer: str


def extract_score(evaluation_text):
    match = re.search(r"Score:\s*(\d+)\s*/\s*10", evaluation_text)
    if match:
        return int(match.group(1))
    return None


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Accepts a PDF file upload and extracts all text from its pages."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        contents = await file.read()
        reader = PdfReader(io.BytesIO(contents))
        extracted_text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text += page_text + "\n"
        extracted_text = extracted_text.strip()

        if not extracted_text:
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from this PDF. It may be image-based (scanned). Please paste your background manually."
            )

        return {"text": extracted_text}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")


@app.post("/start-interview")
def start_interview(req: StartRequest):
    if req.background.strip():
        questions = generate_resume_based_questions(req.background, req.role)
    else:
        questions = get_questions(req.role)

    session_id = str(uuid.uuid4())

    sessions[session_id] = {
        "candidate_name": req.candidate_name,
        "role": req.role,
        "difficulty": req.difficulty,
        "questions": questions,
        "current_index": 0,
        "session_results": []
    }

    first = questions[0]

    return {
        "session_id": session_id,
        "total_questions": len(questions),
        "first_question": first["text"],
        "first_question_type": first["type"]
    }


@app.post("/submit-answer")
def submit_answer(req: AnswerRequest):
    session = sessions[req.session_id]
    idx = session["current_index"]
    question_obj = session["questions"][idx]
    question = question_obj["text"]
    difficulty = session["difficulty"]

    evaluation = evaluator_agent(question, req.answer, difficulty)
    followup = interviewer_agent(question, req.answer, difficulty)
    score = extract_score(evaluation)

    result = {
        "question": question,
        "answer": req.answer,
        "evaluation": evaluation,
        "followup": followup,
        "score": score
    }
    session["session_results"].append(result)
    session["current_index"] += 1

    is_last = session["current_index"] >= len(session["questions"])
    next_question = None
    next_question_type = None
    if not is_last:
        next_obj = session["questions"][session["current_index"]]
        next_question = next_obj["text"]
        next_question_type = next_obj["type"]

    return {
        "evaluation": evaluation,
        "followup": followup,
        "score": score,
        "is_last_question": is_last,
        "next_question": next_question,
        "next_question_type": next_question_type
    }


@app.post("/end-session/{session_id}")
def end_session(session_id: str):
    session = sessions[session_id]
    feedback = coach_agent(session["session_results"])

    saved = save_session(
        session["candidate_name"],
        session["role"],
        session["session_results"],
        feedback
    )

    progress = get_progress(session["candidate_name"])

    return {
        "final_feedback": feedback,
        "average_score": saved["average_score"],
        "progress": progress,
        "full_results": session["session_results"],
        "candidate_name": session["candidate_name"],
        "role": session["role"]
    }