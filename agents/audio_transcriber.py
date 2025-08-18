from tools.speech_to_text import transcribe_audio
from tools.nlp_utils import detect_language

def audio_transcriber_agent(state: dict) -> dict:
    """
    Transcribes the audio file, detects the language if not provided,
    and adds the transcript and language to the state.
    """
    audio_file_to_transcribe = state.get("enhanced_audio_file") or state["audio_file"]
    language = state.get("language")

    transcript = transcribe_audio(audio_file_to_transcribe, language=language)

    if not language:
        language = detect_language(transcript)

    return {"transcript": transcript, "language": language}
