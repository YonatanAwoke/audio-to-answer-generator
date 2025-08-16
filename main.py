import argparse
import os
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

from src.agents import audio_transcriber_agent, question_splitter_agent, answer_generator_agent
from src.utils import save_as_json, save_as_text, save_as_pdf

class AppState(TypedDict):
    audio_file: str
    transcript: str
    questions: List[dict]
    answers: List[dict]

# Build the graph
workflow = StateGraph(AppState)

workflow.add_node("transcriber", audio_transcriber_agent)
workflow.add_node("splitter", question_splitter_agent)
workflow.add_node("generator", answer_generator_agent)

workflow.set_entry_point("transcriber")
workflow.add_edge("transcriber", "splitter")
workflow.add_edge("splitter", "generator")
workflow.add_edge("generator", END)

app = workflow.compile()

def main():
    parser = argparse.ArgumentParser(description="Audio-to-Answer Pipeline")
    parser.add_argument("audio_file", help="Path to the audio file to process.")
    parser.add_argument("--output_format", choices=["json", "text", "pdf"], default="json", help="Desired output format.")
    args = parser.parse_args()

    # Prepare initial state and output path
    initial_state = {"audio_file": args.audio_file}
    output_filename = os.path.splitext(os.path.basename(args.audio_file))[0]
    output_path = f"outputs/{output_filename}.{args.output_format}"

    # Run the pipeline
    final_state = app.invoke(initial_state)

    # Save the output
    if args.output_format == "json":
        save_as_json(final_state, output_path)
    elif args.output_format == "text":
        save_as_text(final_state, output_path)
    elif args.output_format == "pdf":
        save_as_pdf(final_state, output_path)

if __name__ == "__main__":
    main()
