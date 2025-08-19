from tools.speech_to_text import transcribe_audio
from tools.nlp_utils import detect_language

def audio_transcriber_agent(state: dict) -> dict:
    """
    Transcribes the audio file, detects the language if not provided,
    and adds the transcript and language to the state.
    """
    audio_file_to_transcribe = state.get("enhanced_audio_file") or state["audio_file"]
    language = state.get("language")
    speaker_timestamps = state.get("speaker_timestamps", [])

    full_transcript_text = []
    speaker_transcripts = []

    if speaker_timestamps:
        for entry in speaker_timestamps:
            speaker = entry["speaker"]
            start = entry["start"]
            end = entry["end"]
            
            segment_transcript = transcribe_audio(
                audio_file_to_transcribe,
                language=language,
                start_time=start,
                end_time=end
            )
            full_transcript_text.append(f"[{speaker}]: {segment_transcript}")
            speaker_transcripts.append({
                "speaker": speaker,
                "start": start,
                "end": end,
                "transcript": segment_transcript
            })
    else:
        # Fallback to transcribing the whole audio if no speaker timestamps
        transcript = transcribe_audio(audio_file_to_transcribe, language=language)
        full_transcript_text.append(transcript)
        speaker_transcripts.append({
            "speaker": "UNKNOWN",
            "start": 0,
            "end": -1, # Indicate full audio
            "transcript": transcript
        })

    final_transcript = "\n".join(full_transcript_text)

    if not language:
        language = detect_language(final_transcript)

    return {"transcript": final_transcript, "language": language, "speaker_transcripts": speaker_transcripts}
