import os
import google.generativeai as genai
import tempfile
import whisper

# ASR: Automatic Speech Recognition using OpenAI Whisper

def transcribe_audio_whisper(audio_path: str, model_size: str = "base") -> str:
    """
    Transcribe audio to text using OpenAI Whisper.
    """
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result["text"]

# Math Normalizer using Gemini LLM

def normalize_math_llm(text: str, api_key: str = None) -> str:
    """
    Use Gemini LLM to convert spoken math to formal math notation.
    """
    if api_key:
        genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = (
        "You are a math-aware assistant. Convert the following spoken math text into a formal mathematical expression. "
        "Use standard math notation, parentheses, exponents, and symbols as appropriate. "
        "If the text is not mathematical, return it unchanged.\n\nText: " + text
    )
    response = model.generate_content(prompt)
    return response.text.strip()

# SymPy integration is in tools/math_utils.py
# Use: parse_equation, solve_equation, compute_derivative, compute_integral
