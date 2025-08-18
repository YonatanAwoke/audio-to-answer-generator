import json
from tools.llm_interface import invoke_llm
from tools.nlp_utils import split_into_sentences, is_potential_question

def question_splitter_agent(state: dict) -> dict:
    """
    Extracts questions from the transcript using a hybrid approach.
    """
    transcript = state["transcript"]
    sentences = split_into_sentences(transcript)
    potential_questions = [s for s in sentences if is_potential_question(s)]

    if not potential_questions:
        return {"questions": []}

    # Join potential questions to send to LLM in one go
    potential_questions_str = "\n".join(potential_questions)

    questions_raw = invoke_llm(
        prompt_path="prompts/question_splitter.md",
        llm_input={"transcript": potential_questions_str} # The prompt uses {transcript}
    )
    # Clean the LLM output to be valid JSON
    questions_str = questions_raw.strip().replace("\n", "").replace("```json", "").replace("```", "")
    try:
        questions = json.loads(questions_str)
    except json.JSONDecodeError:
        questions = [] # or handle error appropriately
        
    return {"questions": questions}