import json
from typing import List, Dict
from tools.llm_interface import invoke_llm

def question_splitter_agent(state: dict) -> dict:
    """
    Extracts questions from the transcript.
    """
    transcript = state["transcript"]
    questions_raw = invoke_llm(
        prompt_path="prompts/question_splitter.md",
        llm_input={"transcript": transcript}
    )
    # Clean the LLM output to be valid JSON
    questions_str = questions_raw.strip().replace("\n", "").replace("```json", "").replace("```", "")
    questions = json.loads(questions_str)
    return {"questions": questions}

