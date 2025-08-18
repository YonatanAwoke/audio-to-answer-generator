import os
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
from utils.exceptions import CorruptAudioError

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def transcribe_audio(audio_path: str, language: str = None) -> str:
    """
    Transcribes an audio file using the Gemini API.
    """
    # First, perform a corruption check using ffmpeg
    try:
        cmd = [
            "ffmpeg",
            "-v", "error",
            "-i", audio_path,
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

    print(f"Uploading audio file: {audio_path}")
    audio_file = genai.upload_file(path=audio_path)
    
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

    return response.text