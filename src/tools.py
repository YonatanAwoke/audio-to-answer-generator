
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes an audio file using the Gemini API.
    """
    print(f"Uploading audio file: {audio_path}")
    audio_file = genai.upload_file(path=audio_path)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    print("Transcribing audio file with Gemini...")
    response = model.generate_content([
        "Please transcribe this audio file accurately.",
        audio_file
    ])
    
    # Clean up the uploaded file
    genai.delete_file(audio_file.name)

    return response.text

def invoke_llm(prompt_path: str, llm_input: dict) -> str:
    """
    Invokes the Gemini API with a prompt and input.
    """
    print(f"Invoking LLM with prompt: {prompt_path}")
    with open(prompt_path, "r") as f:
        prompt_template = f.read()
    
    prompt = prompt_template.format(**llm_input)
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text
