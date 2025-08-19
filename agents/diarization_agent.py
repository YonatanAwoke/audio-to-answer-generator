from pyannote.audio import Pipeline
import torch
import os

def diarization_agent(state: dict) -> dict:
    """
    Performs speaker diarization on the audio file.
    """
    audio_file = state.get("enhanced_audio_file") or state["audio_file"]
    
    # Initialize the diarization pipeline
    # You need to provide a Hugging Face token to use pyannote.audio models.
    # 1. Visit hf.co/pyannote/speaker-diarization and accept the user agreement.
    # 2. Generate a User Access Token: hf.co/settings/tokens
    # 3. Log in using the Hugging Face CLI: `huggingface-cli login`
    #    Alternatively, set the HF_HOME environment variable to a directory
    #    where your token can be stored, or pass the token directly.
    try:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization",
            use_auth_token=os.getenv("HF_TOKEN")
        )
    except Exception as e:
        raise Exception(f"Failed to load diarization pipeline. Please ensure you have accepted the user agreement for pyannote/speaker-diarization and are logged in to Hugging Face CLI or have set your HF_HOME environment variable. Error: {e}")
    
    # Perform diarization
    diarization = pipeline(audio_file)
    
    # Process the diarization output
    speaker_timestamps = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        speaker_timestamps.append({
            "speaker": speaker,
            "start": turn.start,
            "end": turn.end
        })
        
    return {"speaker_timestamps": speaker_timestamps}
