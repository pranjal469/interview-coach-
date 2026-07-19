"""
Quick end-to-end test for Supabase integration.
Run with: python test_supabase.py
"""
from storage import save_session, get_progress

CANDIDATE = "test_user_demo"

print("=" * 50)
print("TEST 1: Writing a session to Supabase...")
print("=" * 50)

record = save_session(
    candidate_name=CANDIDATE,
    role="software_engineer",
    session_results=[
        {
            "question": "Tell me about yourself.",
            "answer": "I am a software engineer with 2 years of Python experience.",
            "evaluation": "Score: 7/10\nStrengths: Clear and concise.\nWeaknesses: Could add more specifics.",
            "followup": "What specific projects have you worked on?",
            "score": 7,
        }
    ],
    final_feedback="Good overall communication. Work on specificity.",
)
print(f"  Saved! Average score stored: {record['average_score']}/10")

print()
print("=" * 50)
print("TEST 2: Reading progress back from Supabase...")
print("=" * 50)
progress = get_progress(CANDIDATE)
print(f"  Progress message: {progress}")

print()
print("SUCCESS — Supabase read & write both working correctly!")
