import json
import random
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
llm = ChatGroq(model="llama-3.3-70b-versatile")

with open("questions.json", "r") as f:
    question_bank = json.load(f)


def get_questions(role, num_behavioral=2, num_technical=2):
    """Pick a RANDOM set of questions for a given role, so each session varies.
    Returns list of dicts: {text, type}."""
    available_behavioral = question_bank[role]["behavioral"]
    available_technical = question_bank[role]["technical"]

    num_behavioral = min(num_behavioral, len(available_behavioral))
    num_technical = min(num_technical, len(available_technical))

    behavioral = random.sample(available_behavioral, num_behavioral)
    technical = random.sample(available_technical, num_technical)

    questions = []
    for q in behavioral:
        questions.append({"text": q, "type": "behavioral"})
    for q in technical:
        questions.append({"text": q, "type": "technical"})

    random.shuffle(questions)
    return questions


def tailored_question_agent(background, role):
    """Generates ONE question tailored to the candidate's actual background/resume."""
    prompt = f"""You are an interviewer preparing for a {role.replace('_', ' ')} interview.
The candidate shared this background about themselves:
"{background}"

Write ONE specific interview question that references something concrete from their
background (a technology, project, or experience they mentioned). Make it feel personal,
not generic.

Respond ONLY in this exact format, nothing else:
TYPE: <behavioral or technical>
QUESTION: <the question>"""

    response = llm.invoke(prompt).content.strip()
    q_type = "technical"
    q_text = response

    for line in response.split("\n"):
        if line.startswith("TYPE:"):
            q_type = line.split(":", 1)[1].strip().lower()
        if line.startswith("QUESTION:"):
            q_text = line.split(":", 1)[1].strip()

    if q_type not in ["behavioral", "technical"]:
        q_type = "technical"

    return {"text": q_text, "type": q_type}


def generate_resume_based_questions(background, role, num_behavioral=2, num_technical=2):
    """Generates a FULL set of questions derived from the candidate's background,
    instead of pulling from the fixed question bank. Falls back gracefully if
    the LLM output can't be parsed."""
    total = num_behavioral + num_technical

    prompt = f"""You are an experienced interviewer preparing for a {role.replace('_', ' ')} interview.
The candidate shared this background about themselves:
"{background}"

Write {total} interview questions ({num_behavioral} behavioral, {num_technical} technical)
that reference SPECIFIC things from their background wherever possible (a named technology,
project, team situation, or metric they mentioned). If their background is too short for a
fully specific question, write a strong general {role.replace('_', ' ')} question instead of
inventing false details.

Respond ONLY as a JSON array, nothing else, in this exact format:
[
  {{"type": "behavioral", "question": "..."}},
  {{"type": "technical", "question": "..."}}
]"""

    response = llm.invoke(prompt).content.strip()

    # strip markdown code fences if the model adds them
    if response.startswith("```"):
        response = response.strip("`")
        if response.lower().startswith("json"):
            response = response[4:].strip()

    try:
        parsed = json.loads(response)
        questions = []
        for item in parsed:
            q_type = item.get("type", "technical").lower()
            if q_type not in ["behavioral", "technical"]:
                q_type = "technical"
            questions.append({"text": item["question"], "type": q_type})
        if len(questions) >= 2:
            random.shuffle(questions)
            return questions
    except (json.JSONDecodeError, KeyError, TypeError):
        pass

    # fallback: fixed bank, if generation failed or returned too little
    return get_questions(role, num_behavioral, num_technical)


def interviewer_agent(question, candidate_answer, difficulty="entry"):
    """Generates ONE natural follow-up question based on the candidate's answer."""
    depth_instruction = (
        "Keep the follow-up simple and encouraging, appropriate for an entry-level candidate."
        if difficulty == "entry"
        else "Push harder — ask a follow-up that probes deeper technical or strategic reasoning, appropriate for an experienced candidate."
    )

    prompt = f"""You are a professional job interviewer. You just asked this question:
"{question}"

The candidate answered:
"{candidate_answer}"

{depth_instruction}

Ask ONE short, natural follow-up question to probe deeper into their answer.
Only output the follow-up question, nothing else."""

    response = llm.invoke(prompt)
    return response.content.strip()


def evaluator_agent(question, candidate_answer, difficulty="entry"):
    """Scores the candidate's answer against a rubric, adjusted for difficulty level."""
    bar_instruction = (
        "The candidate is entry-level. Be encouraging but honest — don't expect deep expertise, focus on clarity of thought and basic understanding."
        if difficulty == "entry"
        else "The candidate claims to be experienced. Hold them to a higher bar — expect depth, specific examples, and strong technical or strategic reasoning."
    )

    prompt = f"""You are a strict, objective interview evaluator. Evaluate this answer.

Question: "{question}"
Candidate's answer: "{candidate_answer}"

{bar_instruction}

Score the answer from 1-10 on these criteria:
- Structure and clarity
- Relevance to the question
- Depth/specificity (concrete examples vs vague statements)

Respond ONLY in this exact format:
Score: <number>/10
Strengths: <one short sentence>
Weaknesses: <one short sentence>"""

    response = llm.invoke(prompt)
    return response.content.strip()


def coach_agent(session_results):
    """
    session_results: list of dicts, each with question, answer, and evaluation
    Produces overall session feedback across all answers.
    """
    summary_text = ""
    for i, r in enumerate(session_results, 1):
        summary_text += f"\nQ{i}: {r['question']}\nAnswer: {r['answer']}\nEvaluation: {r['evaluation']}\n"

    prompt = f"""You are a supportive, constructive interview coach. Below are a candidate's
full mock interview results across several questions.

{summary_text}

Based on ALL the answers together, give the candidate:
1. Two overall strengths you noticed (patterns across multiple answers, not just one)
2. Two overall areas to improve (patterns across multiple answers)
3. One specific, actionable tip for their next practice session

Keep it encouraging but honest. Format as short bullet points."""

    response = llm.invoke(prompt)
    return response.content.strip()