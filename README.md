# Audio-to-Answer Generator

## Introduction

This project is a powerful pipeline that takes an audio file as input and generates answers to questions found within the audio. It leverages a combination of speech-to-text, natural language processing, and large language models to provide a seamless experience from audio to answers.

## Project Description

The Audio-to-Answer Generator is designed to process audio files, transcribe them, identify questions within the transcript, and generate corresponding answers. The pipeline is built to be robust, with features like audio enhancement, profanity detection, and speaker diarization. It also has the capability to recognize and solve mathematical equations present in the audio.

## Project Structure

The project is organized into the following directories:

- **agents**: Contains the different agents responsible for specific tasks in the pipeline, such as answering generation, audio enhancement, audio transcription, diarization, profanity checking, and question splitting.
- **cache**: Caches intermediate results like transcripts and answers to speed up subsequent runs with the same audio file.
- **orchestration**: Contains the main pipeline logic that orchestrates the different agents and tools.
- **outputs**: Stores the final output files in the specified format (JSON, text, or PDF).
- **prompts**: Contains the prompts used to interact with the large language models.
- **schemas**: Contains the JSON schema for the output.
- **tests**: Contains tests for the pipeline.
- **tools**: Contains various utility functions and tools used by the pipeline, such as ASR, math equation solvers, and profanity filters.
- **utils**: Contains utility functions for the project.

- ## Features

*   **Audio Transcription:** Transcribes audio files using Whisper.
*   **Question & Answer Generation:** Generates answers to questions found in the transcript using a Large Language Model.
*   **Math Problem Solving:** Can solve mathematical equations found in the transcript.
*   **Performance Evaluation:** Evaluates the performance of the question-answering system.
*   **Human-in-the-Loop Feedback:** Allows users to provide feedback on the generated answers to improve the system's accuracy.

## System Scope and Limitation

### Scope

-   Transcribe audio files (MP3, WAV, FLAC, M4A, OGG).
-   Detect and answer questions from the transcribed text.
-   Enhance audio quality for better transcription.
-   Detect and handle profanity.
-   Identify different speakers in the audio.
-   Recognize and solve mathematical equations.
-   Output results in JSON, text, or PDF format.
-   Evaluate performance of the expected output and the original output
-   Feedback on generated answers which can be fine-tune the model for better accuracy

### Limitations

-   The maximum allowed audio file size is 500 MB.
-   The system relies on external APIs (like Google Gemini and Hugging Face), so it requires an internet connection and API keys.
-   The accuracy of the transcription and answers depends on the quality of the audio and the performance of the underlying models.

## Usage

To use the Audio-to-Answer Generator, run the following command:

```bash
python main.py <audio_file_path> [--output_format <format>] [--language <lang>] [--enhance-audio]
```

To run the evaluation, use the following command:

```bash
pytest tests/test_evaluation.py
```

To use the feedback mechanism, run the pipeline with the `--feedback` flag:

```bash
python -m orchestration.pipeline <audio_file_path> --feedback
```

For each generated answer, you will be prompted to provide feedback:

*   Enter `c` if the answer is correct.
*   Enter `r` if the answer needs revision.

If you choose to revise the answer, you will be prompted to enter the corrected answer.

The feedback will be saved to a JSON file in the `feedback` directory.

### Arguments

-   `audio_file_path`: Path to the audio file to process.
-   `--output_format`: Desired output format (`json`, `text`, or `pdf`). Defaults to `json`.
-   `--language`: Language of the audio file (e.g., 'en', 'es'). If not provided, the language will be auto-detected.
-   `--enhance-audio`: Enhance the audio before transcription to improve quality.
-   * `--feedback`: Enable the human-in-the-loop feedback mechanism.

## Project Components

The pipeline consists of the following main components:

-   **Audio Validator**: Validates the audio file format, size, and codec.
-   **Audio Enhancer**: Enhances the audio quality.
-   **Diarizer**: Identifies the different speakers in the audio.
-   **Audio Transcriber**: Transcribes the audio file to text using Whisper.
-   **Profanity Checker**: Detects profanity in the transcribed text.
-   **Answer Generator**: Generates answers to the questions found in the transcript using a large language model.
-   **Math Pipeline**: A specialized pipeline to handle mathematical equations found in the audio.

## Model Input and Output

### Input

-   An audio file (MP3, WAV, FLAC, M4A, OGG).

### Output

The output is a JSON, text, or PDF file containing the following information:

-   Transcript of the audio.
-   A list of questions and their corresponding answers.
-   Speaker timestamps and transcripts (if diarization is enabled).
-   Math results (if any math equations are found).

## Requirements

The project requires the following Python packages:

-   `google-generativeai`
-   `langchain-google-genai`
-   `langgraph`
-   `python-dotenv`
-   `fpdf`
-   `langchain`
-   `ffmpeg`
-   `jsonschema`
-   `pyannote.audio`
-   `torch`
-   `torchaudio`
-   `better_profanity`
-   `demjson`
-   `spacy`

You will also need to have `ffprobe` installed and available in your system's PATH.

## License

This project is licensed under the MIT License.

## Contact

For any questions or feedback, please contact Yonatan Awoke at yonatanawoke@gmail.com.
