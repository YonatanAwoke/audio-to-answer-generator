import re

LATEX_UNICODE_MAP = [
    (r'\\frac\{([^}]+)\}\{([^}]+)\}', lambda m: f"{m.group(1)}/{m.group(2)}"),
    (r'\\sqrt\{([^}]+)\}', lambda m: f"√{m.group(1)}"),
    (r'\\int', lambda m: "∫"),
    (r'\\sum', lambda m: "∑"),
    (r'\\pi', lambda m: "π"),
    (r'\\theta', lambda m: "θ"),
    (r'\\alpha', lambda m: "α"),
    (r'\\beta', lambda m: "β"),
    (r'\\gamma', lambda m: "γ"),
    (r'\\delta', lambda m: "δ"),
    (r'\\leq', lambda m: "≤"),
    (r'\\geq', lambda m: "≥"),
    (r'\\neq', lambda m: "≠"),
    (r'\\times', lambda m: "×"),
    (r'\\div', lambda m: "÷"),
    (r'\\cdot', lambda m: "·"),
    (r'\\pm', lambda m: "±"),
    (r'\\rightarrow', lambda m: "→"),
    (r'\\leftarrow', lambda m: "←"),
    (r'\\infty', lambda m: "∞"),
    (r'\^\{2\}', lambda m: "²"),
    (r'\^\{3\}', lambda m: "³"),
    (r'\^\{([0-9]+)\}', lambda m: f"^{m.group(1)}"),
]

def latex_to_unicode(text: str) -> str:
    """Convert common LaTeX math expressions to Unicode for PDF/plaintext output."""
    for pattern, repl in LATEX_UNICODE_MAP:
        text = re.sub(pattern, repl, text)
    # Remove $ and $$
    text = re.sub(r'\${1,2}', '', text)
    return text
