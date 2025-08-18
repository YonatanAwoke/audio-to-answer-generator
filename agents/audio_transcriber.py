import json
from typing import List, Dict
from tools.whisper_wrapper import transcribe_audio

def audio_transcriber_agent(state: dict) -> dict:
    """
    Transcribes the audio file and adds the transcript to the state.
    """
    audio_file = state["audio_file"]
    transcript = transcribe_audio(audio_file)
    return {"transcript": transcript}
