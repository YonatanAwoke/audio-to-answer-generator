import json
from typing import List, Dict
from tools.llm_interface import invoke_llm

def answer_generator_agent(state: dict) -> dict:
    """
    Generates answers for the extracted questions.
    """
    questions = state["questions"]
    answers = []
    for question in questions:
        answer_raw = invoke_llm(
            prompt_path="prompts/answer_generator.md",
            llm_input={"question": json.dumps(question)}
        )
        answers.append({
            "qid": question["id"],
            "answer": answer_raw.strip()
        })
    return {"answers": answers}
