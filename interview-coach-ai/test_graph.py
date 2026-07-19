from graph import app

sample_answers = [
    "Once my teammate wanted to use a library I thought was overkill. I explained my concerns, we discussed tradeoffs, and eventually agreed on a simpler approach that worked well.",
    "I had to learn React in about a week for a project deadline. I focused on official docs and built a small practice app before touching the real codebase.",
    "I'd use a hash function to convert the long URL into a short code, store the mapping in a database, and redirect using that code when accessed.",
    "SQL databases are structured with fixed schemas, good for relational data. NoSQL is more flexible, better for unstructured or rapidly changing data like logs."
]

initial_state = {
    "role": "software_engineer",
    "answers": sample_answers
}

result = app.invoke(initial_state)

print("\n===== SESSION RESULTS =====")
for i, r in enumerate(result["session_results"], 1):
    print(f"\nQ{i}: {r['question']}")
    print(f"Answer: {r['answer']}")
    print(f"Evaluation:\n{r['evaluation']}")
    print(f"Follow-up: {r['followup']}")

print("\n===== COACH FEEDBACK =====")
print(result["final_feedback"])

from storage import save_session, get_progress

saved = save_session("Pranjal", result["role"], result["session_results"], result["final_feedback"])
print("\n===== SESSION SAVED =====")
print(f"Average score: {saved['average_score']}/10")

print("\n===== PROGRESS =====")
print(get_progress("Pranjal"))