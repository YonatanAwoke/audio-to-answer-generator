import json
from typing import List, Dict
from src.tools import transcribe_audio, invoke_llm

def audio_transcriber_agent(state: dict) -> dict:
    """
    Transcribes the audio file and adds the transcript to the state.
    """
    audio_file = state["audio_file"]
    transcript = transcribe_audio(audio_file)
    return {"transcript": transcript}

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
