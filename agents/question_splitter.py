import json
import re
from tools.llm_interface import invoke_llm
from tools.nlp_utils import split_into_sentences, is_potential_question, QUESTION_WORDS

def question_splitter_agent(state: dict) -> dict:
    """
    Extracts questions from the transcript using a language-aware hybrid approach.
    """
    transcript = state["transcript"]
    language = state.get("language", "en")

    import spacy
    nlp = spacy.load("en_core_web_sm")

    # Remove filler words for cleaner processing
    cleaned = re.sub(r"\b(uh|um|like|and then|so|the final one|and|uh,)\b", "", transcript, flags=re.IGNORECASE)
    # Use spaCy for robust sentence segmentation
    doc = nlp(cleaned)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    # Try to find a question and its answer choices
    question_idx = -1
    for i, sent in enumerate(sentences):
        if is_potential_question(sent, language):
            question_idx = i
            break

    questions = []
    if question_idx != -1:
        # Collect answer choices from subsequent sentences
        choices = []
        choice_pattern = re.compile(r"([A-Da-d])[.,)]?\s*(\d+)")
        for sent in sentences[question_idx+1:]:
            found = choice_pattern.findall(sent)
            if found:
                choices.extend(found)
            # Also handle sentences like "the final one, 51"
            final_match = re.search(r"final one[,:]?\s*(\d+)", sent, re.IGNORECASE)
            if final_match:
                choices.append((chr(65+len(choices)), final_match.group(1)))
        # If choices found, merge into a single question
        if choices:
            options = ", ".join([f"{label.upper()}. {value}" for label, value in choices])
            merged_question = f"{sentences[question_idx]} {options}"
            # Use LLM to robustly rephrase the question if needed
            llm_rephrased = invoke_llm(
                prompt_path="prompts/question_splitter.md",
                llm_input={"transcript": merged_question}
            )
            try:
                start_index = llm_rephrased.index('[')
                end_index = llm_rephrased.rindex(']') + 1
                questions_str = llm_rephrased[start_index:end_index]
                questions = json.loads(questions_str)
            except (ValueError, json.JSONDecodeError):
                # Fallback: use merged_question directly
                questions = [{"id": "1", "question": merged_question}]
        else:
            # Fallback to LLM for question extraction from all sentences
            potential_questions_str = "\n".join(sentences)
            questions_raw = invoke_llm(
                prompt_path="prompts/question_splitter.md",
                llm_input={"transcript": potential_questions_str}
            )
            try:
                start_index = questions_raw.index('[')
                end_index = questions_raw.rindex(']') + 1
                questions_str = questions_raw[start_index:end_index]
                questions = json.loads(questions_str)
            except (ValueError, json.JSONDecodeError):
                questions = []
    else:
        # Fallback to LLM for question extraction from all sentences
        potential_questions_str = "\n".join(sentences)
        questions_raw = invoke_llm(
            prompt_path="prompts/question_splitter.md",
            llm_input={"transcript": potential_questions_str}
        )
        try:
            start_index = questions_raw.index('[')
            end_index = questions_raw.rindex(']') + 1
            questions_str = questions_raw[start_index:end_index]
            questions = json.loads(questions_str)
        except (ValueError, json.JSONDecodeError):
            questions = []

    return {"questions": questions}
