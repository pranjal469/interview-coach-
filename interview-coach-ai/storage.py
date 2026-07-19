import os
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE = "interview_sessions"


def save_session(candidate_name: str, role: str, session_results: list, final_feedback: str) -> dict:
    """
    Inserts a completed interview session into Supabase and returns
    a record dict that matches the shape main.py expects:
    { timestamp, role, average_score, session_results, final_feedback }
    """
    # ── Calculate average score from evaluation text ──────────────
    scores = []
    for r in session_results:
        for line in r["evaluation"].split("\n"):
            if line.startswith("Score:"):
                try:
                    score = int(line.split(":")[1].strip().split("/")[0])
                    scores.append(score)
                except Exception:
                    pass
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Insert into Supabase ──────────────────────────────────────
    row = {
        "candidate_name": candidate_name,
        "role": role,
        "average_score": avg_score,
        "final_feedback": final_feedback,
        "session_results": session_results,   # stored as JSONB
    }
    supabase.table(TABLE).insert(row).execute()

    # Return the local record so main.py can read average_score
    return {
        "timestamp": timestamp,
        "role": role,
        "average_score": avg_score,
        "session_results": session_results,
        "final_feedback": final_feedback,
    }


def get_progress(candidate_name: str) -> str:
    """
    Queries all sessions for this candidate (oldest first) and
    returns a human-readable score trend message.
    """
    response = (
        supabase.table(TABLE)
        .select("average_score, created_at")
        .eq("candidate_name", candidate_name)
        .order("created_at", desc=False)
        .execute()
    )

    rows = response.data  # list of dicts

    if len(rows) < 2:
        return "This is your first tracked session — keep practicing to see progress over time!"

    scores = [row["average_score"] for row in rows]
    first_score = scores[0]
    latest_score = scores[-1]
    change = round(latest_score - first_score, 1)

    if change > 0:
        return (
            f"Your average score improved by {change} points since your first session "
            f"({first_score} → {latest_score}). Great progress!"
        )
    elif change < 0:
        return (
            f"Your average score dropped by {abs(change)} points since your first session "
            f"({first_score} → {latest_score}). Let's work on consistency."
        )
    else:
        return f"Your average score has stayed steady at {latest_score} across sessions. Keep it up!"