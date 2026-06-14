"""
Grounded question answering: retrieve review chunks, then answer with Groq.
"""

from __future__ import annotations

import os

from dotenv import load_dotenv
from groq import Groq

from retrieve import DEFAULT_TOP_K, build_index, retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are a helpful assistant for Hunter College CS students researching professor reviews.

Answer the user's question using ONLY the information in the provided document excerpts.

Rules:
- Do not use outside knowledge, assumptions, or information not present in the excerpts.
- If the excerpts do not contain enough information to answer the question, respond with exactly: "I don't have enough information on that."
- When you use information from an excerpt, name the source file (for example, rmp_tong_yi.txt) in your answer.
- If reviews disagree, summarize what students say without treating one opinion as the only truth.
- Keep answers concise and directly tied to the excerpts."""


def format_context(chunks: list[dict]) -> str:
    parts: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        parts.append(
            f"--- Excerpt {index} "
            f"(source: {chunk['source_file']}, professor: {chunk['professor']}) ---\n"
            f"{chunk['text']}"
        )
    return "\n\n".join(parts)


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise ValueError(
            "GROQ_API_KEY is missing. Copy .env.example to .env and add your Groq API key."
        )
    return Groq(api_key=api_key)


def ask(question: str, k: int = DEFAULT_TOP_K) -> dict:
    chunks = retrieve(question, k=k)

    sources: list[str] = []
    seen: set[str] = set()
    for chunk in chunks:
        source_file = chunk["source_file"]
        if source_file and source_file not in seen:
            seen.add(source_file)
            sources.append(source_file)

    context = format_context(chunks)
    user_message = f"""Document excerpts:

{context}

Question: {question}"""

    client = get_groq_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content or ""
    answer = answer.strip()

    return {
        "answer": answer,
        "sources": sources,
        "chunks": chunks,
    }


def print_result(question: str, result: dict) -> None:
    print(f"\nQUESTION: {question}")
    print("-" * 72)
    print(f"ANSWER:\n{result['answer']}")
    print("\nSOURCES:")
    for source in result["sources"]:
        print(f"  • {source}")


def main() -> None:
    build_index()

    test_questions = [
        "How is Eric Schweitzer's grade broken down according to student reviews?",
        "What do students say about going to Pavel Shostak's office hours?",
        "What is the best dining hall at Hunter College?",
    ]

    print("=" * 72)
    print("GROUNDED GENERATION TESTS (Milestone 5)")
    print("=" * 72)

    for question in test_questions:
        print_result(question, ask(question))


if __name__ == "__main__":
    main()
