import unicodedata
import emoji
import re
from typing import List

def normalize_unicode(text: str) -> str:
    """Normalize unicode characters to NFC form."""
    return unicodedata.normalize('NFC', text)

def extract_emojis(text: str) -> List[str]:
    """Extract all emojis from the text."""
    return [c for c in text if c in emoji.EMOJI_DATA]

def annotate_emojis(text: str) -> str:
    """Replace emojis with their textual description in the text."""
    return emoji.demojize(text, delimiters=("<", ">"))

def extract_math_symbols(text: str) -> List[str]:
    """Extract common math symbols from the text."""
    math_symbols = re.findall(r"[\u2200-\u22FF\u2190-\u21FF\u25A0-\u25FF\u2070-\u209F\u00B1\u2212\u00D7\u00F7\u03C0\u03A0\u03A3\u03B1-\u03C9]", text)
    return math_symbols

def annotate_math_symbols(text: str) -> str:
    """Optionally replace math symbols with their unicode name (for LLM context)."""
    def repl(match):
        char = match.group(0)
        try:
            return f"<{unicodedata.name(char)}>",
        except ValueError:
            return char
    return re.sub(r"[\u2200-\u22FF\u2190-\u21FF\u25A0-\u25FF\u2070-\u209F\u00B1\u2212\u00D7\u00F7\u03C0\u03A0\u03A3\u03B1-\u03C9]", repl, text)
