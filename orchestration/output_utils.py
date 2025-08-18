import json
from fpdf import FPDF

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
            f.write(f"Type: {q['type']}\n")
            f.write(f"Question: {q['text']}\n")
            if 'options' in q:
                f.write(f"Options: {', '.join(q['options'])}\n")
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
        question_text = f"ID: {q['id']}\nType: {q['type']}\nQuestion: {q['text']}"
        pdf.multi_cell(page_width, 10, txt=write_to_pdf(question_text))
        if 'options' in q and q['options']:
            options_text = f"Options: {', '.join(q['options'])}"
            pdf.multi_cell(page_width, 10, txt=write_to_pdf(options_text))
        pdf.ln()

    pdf.add_page()
    pdf.cell(page_width, 10, txt="Answers", ln=True, align='C')
    for a in data["answers"]:
        answer_text = f"QID: {a['qid']}\nAnswer: {a['answer']}"
        pdf.multi_cell(page_width, 10, txt=write_to_pdf(answer_text))
        pdf.ln()
        
    pdf.output(output_path)
    print(f"Saved PDF output to {output_path}")
