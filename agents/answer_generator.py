import json
from typing import List, Dict
from tools.llm_interface import invoke_llm


def answer_generator_agent(state: dict) -> dict:
    """
    Generates answers for all questions in the transcript, using full context.
    """
    transcript = state["transcript"]
    # Use a full-context prompt
    llm_output = invoke_llm(
        prompt_path="prompts/answer_generator_fullcontext.md",
        llm_input={"transcript": transcript}
    )
    # Try to extract a JSON array of question/answer pairs from the LLM output
    try:
        start_index = llm_output.index('[')
        end_index = llm_output.rindex(']') + 1
        qa_str = llm_output[start_index:end_index]
        qa_pairs = json.loads(qa_str)
    except (ValueError, json.JSONDecodeError):
        # Fallback: treat the whole output as a single answer
        qa_pairs = [{"id": "1", "question": "(full transcript)", "answer": llm_output.strip()}]
    # Map to output format (qid, question, answer)
    answers = []
    for qa in qa_pairs:
        answers.append({
            "qid": qa.get("id", str(len(answers)+1)),
            "question": qa.get("question", ""),
            "answer": qa.get("answer", "")
        })
    return {"answers": answers}
