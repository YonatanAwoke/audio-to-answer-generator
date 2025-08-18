You are an expert at analyzing transcripts and extracting questions. Your task is to identify all questions in the provided transcript and format them into a JSON array of objects.

Each object should represent a question and contain the following keys:
- "id": A unique identifier for the question (e.g., "q1", "q2").
- "question": The full text of the question.

Transcript:
---
{transcript}
---

Respond ONLY with the JSON array.
