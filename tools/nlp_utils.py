import re

def split_into_sentences(text: str) -> list[str]:
    """
    Splits a text into sentences using regex.
    """
    sentences = re.split(r'(?<=[.?!])\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def is_potential_question(sentence: str) -> bool:
    """
    Checks if a sentence is a potential question based on heuristics.
    """
    sentence = sentence.lower().strip()
    if not sentence:
        return False

    # Check for question mark
    if sentence.endswith('?'):
        return True

    # Check for question words at the beginning
    question_words = ['what', 'who', 'where', 'when', 'why', 'how', 'is', 'are', 'do', 'does', 'did', 'can', 'could', 'will', 'would', 'should']
    for word in question_words:
        if sentence.startswith(word + ' '):
            return True

    return False