import argparse
import os
import subprocess
import sys
from langgraph.graph import StateGraph, END
from utils.exceptions import LargeFileError, UnsupportedAudioFormatError, UnsupportedAudioCodecError, CorruptAudioError

# Constants for audio validation
MAX_AUDIO_FILE_SIZE_MB = 500  # 500 MB
SUPPORTED_AUDIO_FORMATS = ['mp3', 'wav', 'flac', 'm4a', 'ogg']
SUPPORTED_AUDIO_CODECS = ['mp3', 'pcm_s16le', 'flac', 'aac', 'opus']
from typing import TypedDict, List, Optional

def validate_audio_file(audio_file_path: str):
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    if not os.path.isfile(audio_file_path):
        raise ValueError(f"Path is not a file: {audio_file_path}")

    # Validate file size
    file_size_mb = os.path.getsize(audio_file_path) / (1024 * 1024)
    if file_size_mb > MAX_AUDIO_FILE_SIZE_MB:
        raise LargeFileError(f"Audio file size ({file_size_mb:.2f} MB) exceeds the maximum allowed size of {MAX_AUDIO_FILE_SIZE_MB} MB.")

    # Validate format and codec using ffprobe
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name:format=format_name",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout.strip().split('\n')
        
        if len(output) < 2:
            raise CorruptAudioError(f"Could not get audio stream information from {audio_file_path}. It might be corrupt or not an audio file.")

        codec_name = output[0]
        format_name = output[1]

        if format_name not in SUPPORTED_AUDIO_FORMATS:
            raise UnsupportedAudioFormatError(f"Unsupported audio format: {format_name}. Supported formats are: {', '.join(SUPPORTED_AUDIO_FORMATS)}")
        
        if codec_name not in SUPPORTED_AUDIO_CODECS:
            raise UnsupportedAudioCodecError(f"Unsupported audio codec: {codec_name}. Supported codecs are: {', '.join(SUPPORTED_AUDIO_CODECS)}")

    except subprocess.CalledProcessError as e:
        raise CorruptAudioError(f"ffprobe failed to analyze audio file: {e.stderr.strip()}")
    except Exception as e:
        raise CorruptAudioError(f"An unexpected error occurred during audio file analysis: {e}")


from agents.profanity_agent import profanity_agent
from agents.audio_enhancer_agent import audio_enhancer_agent
from agents.diarization_agent import diarization_agent
from agents.audio_transcriber import audio_transcriber_agent
from agents.question_splitter import question_splitter_agent
from agents.answer_generator import answer_generator_agent
from .output_utils import save_as_json, save_as_text, save_as_pdf

class AppState(TypedDict):
    audio_file: str
    enhanced_audio_file: Optional[str]
    transcript: str
    questions: List[dict]
    answers: List[dict]
    language: Optional[str]
    enhance_audio: bool
    speaker_timestamps: List[dict]
    speaker_transcripts: List[dict]
    profanity_detected: bool

# Build the graph
workflow = StateGraph(AppState)

workflow.add_node("enhancer", audio_enhancer_agent)
workflow.add_node("diarizer", diarization_agent)
workflow.add_node("transcriber", audio_transcriber_agent)
workflow.add_node("profanity_checker", profanity_agent)
workflow.add_node("splitter", question_splitter_agent)
workflow.add_node("generator", answer_generator_agent)

workflow.add_edge("enhancer", "diarizer")
workflow.add_edge("diarizer", "transcriber")
workflow.add_edge("transcriber", "profanity_checker")


def check_profanity(state: AppState):
    if state.get("profanity_detected"):
        return END
    return "splitter"

workflow.add_conditional_edges(
    "profanity_checker",
    check_profanity,
    {END: END, "splitter": "splitter"}
)

workflow.add_conditional_edges(
    "splitter",
    lambda state: "generator" if state.get("questions") else END,
    {"generator": "generator", END: END}
)
workflow.add_edge("generator", END)

def should_enhance(state: AppState):
    return "enhancer" if state.get("enhance_audio") else "diarizer"

workflow.set_conditional_entry_point(should_enhance)

app = workflow.compile()

def main():
    from huggingface_hub import login
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        login(token=hf_token)
    else:
        print("Warning: HF_TOKEN environment variable not set. Diarization might fail if the model requires authentication.")
    parser = argparse.ArgumentParser(description="Audio-to-Answer Pipeline")
    parser.add_argument("audio_file", help="Path to the audio file to process.")
    parser.add_argument("--output_format", choices=["json", "text", "pdf"], default="json", help="Desired output format.")
    parser.add_argument("--language", help="Language of the audio file (e.g., 'en', 'es'). If not provided, language will be auto-detected.")
    parser.add_argument("--enhance-audio", action="store_true", help="Enhance the audio before transcription to improve quality.")
    args = parser.parse_args()

    try:
        validate_audio_file(args.audio_file)

        # Prepare initial state and output path
        initial_state = {
            "audio_file": args.audio_file,
            "language": args.language,
            "enhance_audio": args.enhance_audio
        }
        output_filename = os.path.splitext(os.path.basename(args.audio_file))[0]
        output_path = f"outputs/{output_filename}.{args.output_format}"

        # Run the pipeline
        final_state = app.invoke(initial_state)

        if final_state.get("profanity_detected"):
            print("Offensive language detected in the audio. Please revise the audio.")
            return

        if not final_state.get("questions"):
            print("No valid questions found in the audio.")
            return

        # Save the output
        if args.output_format == "json":
            save_as_json(final_state, output_path)
        elif args.output_format == "text":
            save_as_text(final_state, output_path)
        elif args.output_format == "pdf":
            save_as_pdf(final_state, output_path)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except (LargeFileError, UnsupportedAudioFormatError, UnsupportedAudioCodecError, CorruptAudioError) as e:
        print(f"Audio Validation Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
