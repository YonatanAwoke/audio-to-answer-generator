import re
from typing import List
from transformers import pipeline

# Load a zero-shot classification pipeline for sensitive topic detection
# (You may want to load this once and reuse in production)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

SENSITIVE_TOPICS = [
    "self-harm", "suicide", "violence", "abuse", "harassment", "hate speech", "sexual content", "drugs", "addiction"
]

def detect_sensitive_topics(text: str, threshold: float = 0.7) -> List[str]:
    """Detect sensitive topics in the text using zero-shot classification."""
    result = classifier(text, SENSITIVE_TOPICS)
    detected = [label for label, score in zip(result['labels'], result['scores']) if score >= threshold]
    return detected
