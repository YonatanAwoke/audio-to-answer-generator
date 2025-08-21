import json
import re
from tools.llm_interface import invoke_llm
from tools.nlp_utils import split_into_sentences, is_potential_question, QUESTION_WORDS

def question_splitter_agent(state: dict) -> dict:
    from tools.sensitive_topic_utils import detect_sensitive_topics
    """
    Extracts questions from the transcript using a language-aware hybrid approach.
    """
    transcript = state["transcript"]
    language = state.get("language", "en")

    import spacy
    from tools.preprocess_utils import normalize_unicode, annotate_emojis, annotate_math_symbols
    from tools.math_utils import normalize_math_phrases
    nlp = spacy.load("en_core_web_sm")

    # Step 1: Unicode normalization
    norm_transcript = normalize_unicode(transcript)
    # Step 2: Annotate emojis and math symbols for LLM/context
    norm_transcript = annotate_emojis(norm_transcript)
    norm_transcript = annotate_math_symbols(norm_transcript)
    # Step 3: Normalize math phrases
    norm_transcript, math_found = normalize_math_phrases(norm_transcript)
    # Step 4: Remove filler words for cleaner processing
    cleaned = re.sub(r"\b(uh|um|like|and then|so|the final one|and|uh,)\b", "", norm_transcript, flags=re.IGNORECASE)
    # Step 5: Use spaCy for robust sentence segmentation
    doc = nlp(cleaned)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]

    # Group context sentences with each question for context-aware extraction
    questions = []
    context_buffer = []
    for i, sent in enumerate(sentences):
        if is_potential_question(sent, language):
            # Group all previous context sentences with this question
            context = " ".join(context_buffer + [sent])
            # Use LLM to robustly rephrase the context+question if needed
            llm_rephrased = invoke_llm(
                prompt_path="prompts/question_splitter.md",
                llm_input={"transcript": context}
            )
            try:
                start_index = llm_rephrased.index('[')
                end_index = llm_rephrased.rindex(']') + 1
                questions_str = llm_rephrased[start_index:end_index]
                qs = json.loads(questions_str)
                for q in qs:
                    sensitive = detect_sensitive_topics(q["question"])
                    if sensitive:
                        q["sensitive_topics"] = sensitive
                    if math_found:
                        q["is_math"] = True
                questions.extend(qs)
            except (ValueError, json.JSONDecodeError):
                sensitive = detect_sensitive_topics(context)
                q = {"id": str(len(questions)+1), "question": context}
                if sensitive:
                    q["sensitive_topics"] = sensitive
                if math_found:
                    q["is_math"] = True
                questions.append(q)
            context_buffer = []  # Reset buffer after a question
        else:
            # Add to context buffer if not a question
            context_buffer.append(sent)
    # If no questions found, fallback to LLM for all sentences
    if not questions:
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
            for q in questions:
                sensitive = detect_sensitive_topics(q["question"])
                if sensitive:
                    q["sensitive_topics"] = sensitive
                if math_found:
                    q["is_math"] = True
        except (ValueError, json.JSONDecodeError):
            questions = []
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
                # Sensitive topic detection for each question
                for q in questions:
                    sensitive = detect_sensitive_topics(q["question"])
                    if sensitive:
                        q["sensitive_topics"] = sensitive
                    if math_found:
                        q["is_math"] = True
            except (ValueError, json.JSONDecodeError):
                # Fallback: use merged_question directly
                sensitive = detect_sensitive_topics(merged_question)
                q = {"id": "1", "question": merged_question}
                if sensitive:
                    q["sensitive_topics"] = sensitive
                if math_found:
                    q["is_math"] = True
                questions = [q]
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
                for q in questions:
                    sensitive = detect_sensitive_topics(q["question"])
                    if sensitive:
                        q["sensitive_topics"] = sensitive
                    if math_found:
                        q["is_math"] = True
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
            for q in questions:
                sensitive = detect_sensitive_topics(q["question"])
                if sensitive:
                    q["sensitive_topics"] = sensitive
                if math_found:
                    q["is_math"] = True
        except (ValueError, json.JSONDecodeError):
            questions = []

    return {"questions": questions}
