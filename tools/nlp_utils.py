import re
import google.generativeai as genai

# Language-specific question words
QUESTION_WORDS = {
    "en": ['what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should'],
    "es": ['qué', 'quién', 'dónde', 'cuándo', 'por qué', 'cómo', 'es', 'está', 'hace', 'haces', 'hizo', 'puede', 'podría', 'hará', 'haría', 'debería'],
    "fr": ['que', 'qui', 'où', 'quand', 'pourquoi', 'comment', 'est-ce que', 'est', 'sont', 'fait', 'font', 'a fait', 'peut', 'pourrait', 'fera', 'ferait', 'devrait'],
    "de": ['was', 'wer', 'wo', 'wann', 'warum', 'wie', 'ist', 'sind', 'tut', 'tun', 'tat', 'kann', 'könnte', 'wird', 'würde', 'sollte']
}

def detect_language(text: str) -> str:
    """
    Detects the language of a text using the Gemini API.
    Returns the language code (e.g., 'en', 'es').
    """
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"Detect the language of the following text. Respond with only the two-letter ISO 639-1 language code. Text: {text}")
    return response.text.strip().lower()

def split_into_sentences(text: str) -> list[str]:
    """
    Splits a text into sentences using regex.
    """
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def is_potential_question(sentence: str, language: str = 'en') -> bool:
    """
    Checks if a sentence is a potential question based on heuristics for a given language.
    """
    sentence = sentence.lower().strip()
    if not sentence:
        return False

    # Check for question mark
    if sentence.endswith('?'):
        return True

    # Check for question words at the beginning
    question_words = QUESTION_WORDS.get(language, [])
    for word in question_words:
        if sentence.startswith(word + ' '):
            return True

    return False
