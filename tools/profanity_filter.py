from better_profanity import profanity

def contains_profanity(text: str) -> bool:
    """
    Checks if a text contains profanity.
    """
    return profanity.contains_profanity(text)