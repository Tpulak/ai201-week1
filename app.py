"""
Gradio web UI for The Unofficial Guide RAG system.
"""

from __future__ import annotations

import gradio as gr

from query import ask
from retrieve import build_index

build_index()


def handle_query(question: str) -> tuple[str, str]:
    question = question.strip()
    if not question:
        return "Please enter a question.", ""

    try:
        result = ask(question)
    except ValueError as error:
        return str(error), ""
    except RuntimeError as error:
        return str(error), ""

    sources = "\n".join(f"• {source}" for source in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown(
        "# The Unofficial Guide\n"
        "Ask questions about Hunter College CS professors using student reviews "
        "from Rate My Professors."
    )

    question_input = gr.Textbox(
        label="Your question",
        placeholder="e.g. How is Eric Schweitzer's grade broken down?",
        lines=2,
    )
    ask_button = gr.Button("Ask", variant="primary")

    answer_output = gr.Textbox(label="Answer", lines=10)
    sources_output = gr.Textbox(label="Retrieved from", lines=4)

    ask_button.click(
        handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output],
    )
    question_input.submit(
        handle_query,
        inputs=question_input,
        outputs=[answer_output, sources_output],
    )


if __name__ == "__main__":
    demo.launch()
