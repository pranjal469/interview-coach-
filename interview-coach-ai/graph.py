from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from agents import get_questions, interviewer_agent, evaluator_agent, coach_agent


class InterviewState(TypedDict):
    role: str
    questions: List[str]
    current_index: int
    answers: List[str]
    session_results: List[dict]
    final_feedback: str


def start_node(state: InterviewState):
    questions = get_questions(state["role"])
    return {"questions": questions, "current_index": 0, "session_results": []}


def ask_and_evaluate_node(state: InterviewState):
    idx = state["current_index"]
    question = state["questions"][idx]
    answer = state["answers"][idx]  # in the real app, this comes from user input

    evaluation = evaluator_agent(question, answer)
    followup = interviewer_agent(question, answer)

    result = {
        "question": question,
        "answer": answer,
        "evaluation": evaluation,
        "followup": followup
    }

    updated_results = state["session_results"] + [result]
    return {"session_results": updated_results, "current_index": idx + 1}


def should_continue(state: InterviewState):
    if state["current_index"] < len(state["questions"]):
        return "continue"
    return "done"


def coach_node(state: InterviewState):
    feedback = coach_agent(state["session_results"])
    return {"final_feedback": feedback}


# Build the graph
graph = StateGraph(InterviewState)
graph.add_node("start", start_node)
graph.add_node("ask_and_evaluate", ask_and_evaluate_node)
graph.add_node("coach", coach_node)

graph.set_entry_point("start")
graph.add_edge("start", "ask_and_evaluate")
graph.add_conditional_edges(
    "ask_and_evaluate",
    should_continue,
    {"continue": "ask_and_evaluate", "done": "coach"}
)
graph.add_edge("coach", END)

app = graph.compile()