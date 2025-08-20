from tools.profanity_filter import contains_profanity

def profanity_agent(state: dict) -> dict:
    """
    Checks for profanity in the transcript.
    """
    transcript = state["transcript"]
    if contains_profanity(transcript):
        return {"profanity_detected": True}
    return {"profanity_detected": False}
