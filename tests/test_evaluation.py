
import os
import sys
import json
import time
import subprocess

# Add project root to the Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

from jiwer import wer
from sentence_transformers import SentenceTransformer, util

# --- 1. Configuration ---
EVAL_DATA_DIR = os.path.join(PROJECT_ROOT, "evaluation_data")
PIPELINE_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "outputs")
# Load the sentence transformer model for semantic similarity
print("Loading sentence transformer model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded.")


def get_ground_truth(audio_filename):
    """Loads the ground truth transcript and answers for a given audio file."""
    base_name = os.path.splitext(audio_filename)[0]
    transcript_path = os.path.join(EVAL_DATA_DIR, f"{base_name}.txt")
    answers_path = os.path.join(EVAL_DATA_DIR, f"{base_name}.json")

    try:
        with open(transcript_path, 'r') as f:
            transcript = f.read()
        with open(answers_path, 'r') as f:
            answers = json.load(f)
        return transcript, answers
    except FileNotFoundError as e:
        print(f"Error: Ground truth file not found for {audio_filename}. {e}")
        return None, None

def evaluate_pipeline_run(audio_filename):
    """
    Evaluates a single run of the pipeline for a given audio file.
    """
    print(f"--- Evaluating: {audio_filename} ---")
    
    # --- 2. Load Ground Truth ---
    gt_transcript, gt_answers = get_ground_truth(audio_filename)
    if gt_transcript is None:
        return

    # --- 3. Run the Pipeline ---
    # The pipeline's main() function is designed to be called from the command line.
    # We will use subprocess to execute it.
    print("Running pipeline via subprocess...")
    pipeline_start_time = time.time()
    
    try:
        # Construct the command to run the pipeline script
        command = [
            sys.executable, # Use the same python interpreter that is running this script
            os.path.join(PROJECT_ROOT, 'orchestration', 'pipeline.py'),
            os.path.join(EVAL_DATA_DIR, audio_filename)
        ]
        
        # We need to set the environment variables for the subprocess, including PYTHONPATH
        process_env = os.environ.copy()
        base_name = os.path.splitext(audio_filename)[0]
        process_env["JOB_ID"] = f"eval_{base_name}"
        process_env["AUDIO_HASH"] = "testhash"
        process_env["PYTHONPATH"] = PROJECT_ROOT + os.pathsep + process_env.get('PYTHONPATH', '')

        result = subprocess.run(command, capture_output=True, text=True, check=True, env=process_env)
        
        # The pipeline saves output to a file, so we don't get it directly.
        # We will load the generated output file in the next step.
        print("--- Pipeline STDOUT ---")
        print(result.stdout)
        print("--- Pipeline STDERR ---")
        print(result.stderr)
        print("-----------------------")

    except subprocess.CalledProcessError as e:
        print(f"ERROR: Pipeline execution failed for {audio_filename}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return

    total_latency = time.time() - pipeline_start_time
    
    # The output filename is now determined by the JOB_ID and AUDIO_HASH env vars
    output_filename = f"eval_{base_name}_testhash"
    output_filepath = os.path.join(PIPELINE_OUTPUT_DIR, f"{output_filename}.json")
    
    try:
        with open(output_filepath, 'r') as f:
            generated_output = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Output file not found at {output_filepath}. Did the pipeline run?")
        return

    # --- 4. Calculate Metrics ---
    metrics = {}

    # Latency and Cost (from pipeline instrumentation)
    metrics['total_latency'] = total_latency
    # metrics['agent_timings'] = timings
    # metrics['total_tokens'] = token_counts

    # Transcription Quality (WER)
    generated_transcript = generated_output.get('transcript', '')
    metrics['wer'] = wer(gt_transcript, generated_transcript)

    # Answer Quality (Semantic Similarity)
    generated_qna = generated_output.get('answers', [])
    gt_qna = gt_answers.get('answers', [])
    if generated_qna and gt_qna:
        # For simplicity, comparing the first answer. A real implementation would loop through all.
        gen_answer = generated_qna[0]['answer']
        gt_answer = gt_qna[0]['answer']
        embedding1 = model.encode(gen_answer, convert_to_tensor=True)
        embedding2 = model.encode(gt_answer, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(embedding1, embedding2).item()
        metrics['answer_similarity'] = similarity

    # --- 5. Report Results ---
    print("\n--- Results ---")
    print(f"Transcription WER: {metrics.get('wer', 'N/A'):.2f}")
    print(f"Answer Similarity: {metrics.get('answer_similarity', 'N/A'):.2f}")
    print(f"Total Latency: {metrics.get('total_latency', 'N/A'):.2f}s")
    print(f"Total Tokens Used: {metrics.get('total_tokens', 'N/A')}")
    print("NOTE: Metrics are placeholders. Uncomment code to enable real calculations.")
    print("-----------------")


if __name__ == "__main__":
    # Find all audio files in the evaluation directory
    audio_files = [f for f in os.listdir(EVAL_DATA_DIR) if f.endswith(('.wav', '.mp3'))]
    
    if not audio_files:
        print(f"No audio files found in {EVAL_DATA_DIR}. Please add audio and ground truth files to begin.")
    else:
        for audio_file in audio_files:
            evaluate_pipeline_run(audio_file)
