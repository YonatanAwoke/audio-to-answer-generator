from tools.audio_enhancer import enhance_audio

def audio_enhancer_agent(state: dict) -> dict:
    """
    Enhances the audio file if the enhance_audio flag is set.
    """
    audio_file = state["audio_file"]
    enhanced_audio_file = enhance_audio(audio_file)
    return {"enhanced_audio_file": enhanced_audio_file}
