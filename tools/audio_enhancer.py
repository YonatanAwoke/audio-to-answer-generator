import os
import subprocess
import shutil

def enhance_audio(input_path: str) -> str:
    """
    Enhances an audio file using ffmpeg to reduce noise and normalize volume.
    Returns the path to the enhanced audio file.
    """
    if not shutil.which("ffmpeg"):
        print("ffmpeg not found. Please install ffmpeg and ensure it's in your PATH.")
        return input_path

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    
    filename, ext = os.path.splitext(os.path.basename(input_path))
    output_path = os.path.join(output_dir, f"{filename}_enhanced{ext}")

    # ffmpeg command with filters for noise reduction and normalization
    command = [
        "ffmpeg",
        "-i", input_path,
        "-af", "highpass=f=200,lowpass=f=3000,acompressor",
        "-y",
        output_path,
    ]

    print(f"Running ffmpeg to enhance audio: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error enhancing audio: {result.stderr}")
        # If enhancement fails, return the original path
        return input_path

    return output_path
