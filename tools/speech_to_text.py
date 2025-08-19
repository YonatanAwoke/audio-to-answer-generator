import os
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
from utils.exceptions import CorruptAudioError
import uuid

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def transcribe_audio(audio_path: str, language: str = None, start_time: float = None, end_time: float = None) -> str:
    """
    Transcribes an audio file or a segment of an audio file using the Gemini API.
    """
    temp_audio_file = None
    if start_time is not None and end_time is not None:
        # Create a temporary audio segment
        temp_audio_file = f"/tmp/{uuid.uuid4()}.wav"
        try:
            cmd = [
                "ffmpeg",
                "-i", audio_path,
                "-ss", str(start_time),
                "-to", str(end_time),
                "-c", "copy",
                temp_audio_file
            ]
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            audio_path_to_upload = temp_audio_file
        except subprocess.CalledProcessError as e:
            if temp_audio_file and os.path.exists(temp_audio_file):
                os.remove(temp_audio_file)
            raise CorruptAudioError(f"ffmpeg failed to extract audio segment: {e.stderr.strip()}")
    else:
        audio_path_to_upload = audio_path

    # First, perform a corruption check using ffmpeg
    try:
        cmd = [
            "ffmpeg",
            "-v", "error",
            "-i", audio_path_to_upload,
            "-f", "null",
            "-"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if result.stderr:
            raise CorruptAudioError(f"Audio file appears corrupt or unreadable: {result.stderr.strip()}")
    except subprocess.CalledProcessError as e:
        raise CorruptAudioError(f"ffmpeg failed to analyze audio file for corruption: {e.stderr.strip()}")
    except Exception as e:
        raise CorruptAudioError(f"An unexpected error occurred during audio corruption check: {e}")

    print(f"Uploading audio file: {audio_path_to_upload}")
    audio_file = genai.upload_file(path=audio_path_to_upload)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = "Please transcribe this audio file accurately."
    if language:
        prompt = f"{prompt} The language of the audio is {language}."

    print("Transcribing audio file with Gemini...")
    response = model.generate_content([
        prompt,
        audio_file
    ])
    
    # Clean up the uploaded file
    genai.delete_file(audio_file.name)
    if temp_audio_file and os.path.exists(temp_audio_file):
        os.remove(temp_audio_file)

    return response.text