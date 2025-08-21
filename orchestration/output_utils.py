import json
import os
from fpdf import FPDF
import jsonschema
from utils.exceptions import InvalidOutputFormatError
from tools.latex_utils import latex_to_unicode

# Load the output schema
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), '..', 'schemas', 'output_schema.json')
with open(SCHEMA_PATH, 'r') as f:
    OUTPUT_SCHEMA = json.load(f)

def validate_output_data(data: dict):
    """
    This function no longer performs schema validation as per user request.
    It now only includes a fallback for missing 'question' fields.
    """
    if "questions" in data and isinstance(data["questions"], list):
        for i, q in enumerate(data["questions"]):
            if "question" not in q:
                print(f"Warning: 'question' field missing in question {i}. Adding placeholder.")
                q["question"] = "Placeholder Question" # Add a default value
    # No schema validation performed as per user request.
    pass

def save_as_json(data: dict, output_path: str):
    """
    Saves the data as a JSON file.
    """
    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Saved JSON output to {output_path}")

def save_as_text(data: dict, output_path: str):
    """
    Saves the data as a plain text file.
    """
    with open(output_path, "w") as f:
        f.write("--- Transcript ---\n")
        f.write(data["transcript"] + "\n\n")
        f.write("--- Questions ---\n")
        for q in data["questions"]:
            f.write(f"ID: {q['id']}\n")
            f.write(f"Question: {q['question']}\n")
            f.write("\n")
        f.write("--- Answers ---\n")
        for a in data["answers"]:
            f.write(f"QID: {a['qid']}\n")
            f.write(f"Answer: {a['answer']}\n\n")
    print(f"Saved text output to {output_path}")

def save_as_pdf(data: dict, output_path: str):
    """
    Saves the data as a PDF file.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Calculate effective page width
    page_width = pdf.w - 2 * pdf.l_margin

    def write_to_pdf(text):
        # Encode text to latin-1, replacing characters that can't be encoded
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf.cell(page_width, 10, txt="Transcript", ln=True, align='C')
    pdf.multi_cell(page_width, 10, txt=write_to_pdf(data["transcript"]))
    pdf.ln()

    pdf.add_page()
    pdf.cell(page_width, 10, txt="Questions", ln=True, align='C')
    for q in data["questions"]:
        # Convert LaTeX to Unicode for PDF output
        question_text = f"ID: {q['id']}\nQuestion: {latex_to_unicode(q['question'])}"
        pdf.multi_cell(page_width, 10, txt=write_to_pdf(question_text))
        pdf.ln()

    pdf.add_page()
    pdf.cell(page_width, 10, txt="Answers", ln=True, align='C')
    for a in data["answers"]:
        # Convert LaTeX to Unicode for PDF output
        answer_text = f"QID: {a['qid']}\nAnswer: {latex_to_unicode(a['answer'])}"
        pdf.multi_cell(page_width, 10, txt=write_to_pdf(answer_text))
        pdf.ln()
    
    pdf.output(output_path)
    print(f"Saved PDF output to {output_path}")
