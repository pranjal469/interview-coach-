from agents import get_questions, interviewer_agent, evaluator_agent

# Test 1: pull questions for a role
questions = get_questions("software_engineer")
print("Questions for Software Engineer:")
for q in questions:
    print("-", q)

print("\n" + "="*50 + "\n")

# Test 2: simulate one Q&A round
sample_question = questions[0]
sample_answer = "Once my teammate wanted to use a library I thought was overkill. I explained my concerns, we discussed tradeoffs, and eventually agreed on a simpler approach that worked well."

print("Question:", sample_question)
print("Candidate answer:", sample_answer)

print("\n--- Evaluator Agent ---")
evaluation = evaluator_agent(sample_question, sample_answer)
print(evaluation)

print("\n--- Interviewer Agent (follow-up) ---")
followup = interviewer_agent(sample_question, sample_answer)
print(followup)