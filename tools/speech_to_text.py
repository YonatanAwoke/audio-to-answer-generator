import os
import google.generativeai as genai
from dotenv import load_dotenv
import subprocess
from utils.exceptions import CorruptAudioError
import uuid
import tempfile
import shutil

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def transcribe_audio(audio_path: str, language: str = None, start_time: float = None, end_time: float = None) -> str:
    """
    Transcribes an audio file or a segment of an audio file using the Gemini API.
    """
    temp_dir = None
    try:
        if start_time is not None and end_time is not None:
            temp_dir = tempfile.mkdtemp()
            temp_audio_file = os.path.join(temp_dir, f"{uuid.uuid4()}.wav")
            temp_audio_file = os.path.normpath(temp_audio_file).replace("\\", "/")
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

        return response.text
    finally:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
