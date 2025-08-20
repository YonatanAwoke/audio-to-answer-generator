import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def invoke_llm(prompt_path: str, llm_input: dict) -> str:
    """
    Invokes the Gemini API with a prompt and input.
    """
    print(f"Invoking LLM with prompt: {prompt_path}")
    with open(prompt_path, "r") as f:
        prompt_template = f.read()
    
    prompt = prompt_template.format(**llm_input)
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        return response.text
    except Exception as e:
        print(f"Error invoking LLM: {e}")
        return "[]"
