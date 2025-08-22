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
from tools.asr_math_pipeline import transcribe_audio_whisper, normalize_math_llm
from tools.math_utils import normalize_math_phrases, parse_equation, solve_equation, compute_derivative, compute_integral, to_latex
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

workflow.add_node("generator", answer_generator_agent)
workflow.add_edge("enhancer", "diarizer")
workflow.add_edge("diarizer", "transcriber")
workflow.add_edge("transcriber", "profanity_checker")

def check_profanity(state: AppState):
    if state.get("profanity_detected"):
        return END
    return "generator"

workflow.add_conditional_edges(
    "profanity_checker",
    check_profanity,
    {END: END, "generator": "generator"}
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

    import time
    import pickle
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    transcript = None
    math_normalized = None
    math_found = False
    math_results = {}
    output_filename = os.path.splitext(os.path.basename(args.audio_file))[0]
    output_path = f"outputs/{output_filename}.{args.output_format}"
    transcript_cache_path = f"cache/{output_filename}.transcript.pkl"
    answer_cache_path = f"cache/{output_filename}.answers.pkl"
    try:
        validate_audio_file(args.audio_file)

        # --- ASR: Transcribe audio to text using Whisper ---
        if os.path.exists(transcript_cache_path):
            with open(transcript_cache_path, 'rb') as f:
                transcript = pickle.load(f)
            print("Loaded cached transcript.")
        else:
            for attempt in range(MAX_RETRIES):
                try:
                    transcript = transcribe_audio_whisper(args.audio_file)
                    with open(transcript_cache_path, 'wb') as f:
                        pickle.dump(transcript, f)
                    break
                except Exception as e:
                    print(f"Transcription failed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                    if attempt == MAX_RETRIES-1:
                        print("Transcription failed after retries. Exiting.")
                        sys.exit(1)
                    time.sleep(RETRY_DELAY)

        # --- Math Normalization: Use Gemini LLM and regex/rules ---
        for attempt in range(MAX_RETRIES):
            try:
                math_normalized = normalize_math_llm(transcript)
                math_normalized, math_found = normalize_math_phrases(math_normalized)
                break
            except Exception as e:
                if 'quota' in str(e).lower() or 'rate limit' in str(e).lower():
                    print("LLM API quota exceeded. Please try again later or check your API limits.")
                    sys.exit(1)
                print(f"Math normalization failed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                if attempt == MAX_RETRIES-1:
                    print("Math normalization failed after retries. Exiting.")
                    sys.exit(1)
                time.sleep(RETRY_DELAY)

        # --- (Optional) Math Parsing/Solving: Use SymPy if math detected ---
        if math_found:
            eq = parse_equation(math_normalized)
            if eq is not None:
                for var in ['t', 'x']:
                    sol = solve_equation(eq, var)
                    if sol:
                        math_results['solution'] = sol
                        break
                if hasattr(eq, 'lhs') and hasattr(eq, 'rhs'):
                    expr = eq.lhs - eq.rhs
                else:
                    expr = eq
                deriv = compute_derivative(str(expr))
                integ = compute_integral(str(expr))
                if deriv is not None:
                    math_results['derivative'] = to_latex(deriv)
                if integ is not None:
                    math_results['integral'] = to_latex(integ)

        # Prepare initial state and output path
        initial_state = {
            "audio_file": args.audio_file,
            "language": args.language,
            "enhance_audio": args.enhance_audio,
            "transcript": math_normalized,
        }

        # Run the pipeline (diarization, profanity, then generator/LLM full-context answer)
        final_state = None
        if os.path.exists(answer_cache_path):
            with open(answer_cache_path, 'rb') as f:
                final_state = pickle.load(f)
            print("Loaded cached answers.")
        else:
            for attempt in range(MAX_RETRIES):
                try:
                    final_state = app.invoke(initial_state)
                    with open(answer_cache_path, 'wb') as f:
                        pickle.dump(final_state, f)
                    break
                except Exception as e:
                    if 'quota' in str(e).lower() or 'rate limit' in str(e).lower():
                        print("LLM API quota exceeded. Please try again later or check your API limits.")
                        sys.exit(1)
                    print(f"Answer generation failed (attempt {attempt+1}/{MAX_RETRIES}): {e}")
                    if attempt == MAX_RETRIES-1:
                        print("Answer generation failed after retries. Exiting.")
                        sys.exit(1)
                    time.sleep(RETRY_DELAY)

        # Attach math results if available
        if math_results:
            final_state['math_results'] = math_results

        # Extract questions from the LLM's output (answers)
        if "answers" in final_state and final_state["answers"]:
            final_state["questions"] = [
                {"id": a["qid"], "question": a.get("question", "")}
                for a in final_state["answers"] if a.get("question")
            ]

        if final_state.get("profanity_detected"):
            print("Offensive language detected in the audio. Please revise the audio.")
            return

        if not final_state.get("answers"):
            print("No valid answers found in the audio.")
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
