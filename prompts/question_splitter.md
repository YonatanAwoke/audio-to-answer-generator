You are an expert at analyzing transcripts and extracting questions. Your task is to identify all questions in the provided transcript and format them into a JSON list.

For each question, provide the following information:
- "id": A unique identifier for the question (e.g., "q1", "q2").
- "type": The type of question. Choose from: "multiple-choice", "true/false", "short-answer", or "open-ended".
- "text": The full text of the question.
- "options": A list of options, only for "multiple-choice" questions.

Transcript:
---
{transcript}
---

Respond ONLY with the JSON object.
