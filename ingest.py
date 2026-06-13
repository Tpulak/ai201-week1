"""
Load RMP review documents, clean them, and split into one-review-per-chunk.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import asdict, dataclass
from pathlib import Path

DOCUMENTS_DIR = Path(__file__).parent / "documents"
CHUNKS_PATH = Path(__file__).parent / "chunks.json"

REVIEW_SPLIT_PATTERN = re.compile(r"(?=^Review \d+\s*$)", re.MULTILINE)
SEPARATOR_LINE_PATTERN = re.compile(r"^=+$|^-+$")
HEADER_FIELD_PATTERN = re.compile(r"^(Source|Professor|Department|Collected):\s*(.*)$")
SOURCE_DOCUMENT_PATTERN = re.compile(
    r"^Source Document:\s*Rate My Professors reviews for\s+(.*)$", re.IGNORECASE
)


def professor_from_filename(filename: str) -> str:
    stem = Path(filename).stem
    if stem.startswith("rmp_"):
        stem = stem[4:]
    return " ".join(word.capitalize() for word in stem.split("_"))


@dataclass
class DocumentMeta:
    source_file: str
    source_url: str
    professor: str
    department: str
    collected: str


@dataclass
class Chunk:
    text: str
    source_file: str
    source_url: str
    professor: str
    department: str
    class_name: str
    quality: str
    difficulty: str
    date: str
    review_number: int
    chunk_index: int

    def to_dict(self) -> dict:
        return asdict(self)


def load_document(path: Path) -> tuple[DocumentMeta, str]:
    raw = path.read_text(encoding="utf-8")
    meta = DocumentMeta(
        source_file=path.name,
        source_url="",
        professor=professor_from_filename(path.name),
        department="Computer Science",
        collected="",
    )

    review_match = re.search(r"(?m)^Review \d+\s*$", raw)
    if not review_match:
        raise ValueError(f"No reviews found in {path.name}")

    header_text = raw[: review_match.start()]
    body = raw[review_match.start() :]

    for line in header_text.splitlines():
        stripped = line.strip()
        if not stripped or SEPARATOR_LINE_PATTERN.match(stripped):
            continue

        match = HEADER_FIELD_PATTERN.match(stripped)
        if match:
            field, value = match.group(1), match.group(2).strip()
            if field == "Source":
                meta.source_url = value
            elif field == "Professor":
                meta.professor = value
            elif field == "Department":
                meta.department = value
            elif field == "Collected":
                meta.collected = value
            continue

        source_doc_match = SOURCE_DOCUMENT_PATTERN.match(stripped)
        if source_doc_match:
            meta.professor = source_doc_match.group(1).strip()

    return meta, body


def clean_body(text: str) -> str:
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        if stripped.startswith("Likes:") or stripped.startswith("Dislikes:"):
            continue
        if SEPARATOR_LINE_PATTERN.match(stripped):
            continue
        if stripped == "Rate My Professors Reviews" or stripped == "Reviews":
            continue
        cleaned_lines.append(stripped)

    text = "\n".join(cleaned_lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_review_block(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    review_lines: list[str] = []
    in_review = False

    for line in block.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("Likes:") or stripped.startswith("Dislikes:"):
            break

        if stripped.startswith("Review:"):
            in_review = True
            same_line = stripped[len("Review:") :].strip()
            if same_line:
                review_lines.append(same_line)
            continue

        if in_review:
            review_lines.append(stripped)
            continue

        match = re.match(r"^([^:]+):\s*(.*)$", stripped)
        if match:
            key = match.group(1).strip().lower().replace(" ", "_")
            fields[key] = match.group(2).strip()

    fields["review"] = " ".join(review_lines)
    return fields


def build_chunk_text(meta: DocumentMeta, fields: dict[str, str]) -> str:
    quality = fields.get("quality") or fields.get("quality_score") or "N/A"
    difficulty = fields.get("difficulty") or "N/A"
    date = fields.get("date") or fields.get("date_of_review") or "N/A"
    class_name = fields.get("class") or "N/A"
    tags = fields.get("tags")
    review = fields.get("review", "")

    lines = [
        f"Professor: {meta.professor}",
        f"Source: {meta.source_file}",
        f"Class: {class_name}",
        f"Quality: {quality} | Difficulty: {difficulty}",
        f"Date: {date}",
    ]
    if tags:
        lines.append(f"Tags: {tags}")
    lines.append(f"Review: {review}")
    return "\n".join(lines)


def chunk_document(meta: DocumentMeta, body: str, start_index: int) -> list[Chunk]:
    cleaned = clean_body(body)
    blocks = REVIEW_SPLIT_PATTERN.split(cleaned)
    chunks: list[Chunk] = []
    chunk_index = start_index

    for block in blocks:
        block = block.strip()
        if not block.startswith("Review "):
            continue

        header_line, _, remainder = block.partition("\n")
        review_number_match = re.match(r"Review (\d+)", header_line.strip())
        if not review_number_match:
            continue

        fields = parse_review_block(remainder)
        review_text = fields.get("review", "").strip()
        if len(review_text) < 10:
            continue

        chunk_index += 1
        chunks.append(
            Chunk(
                text=build_chunk_text(meta, fields),
                source_file=meta.source_file,
                source_url=meta.source_url,
                professor=meta.professor,
                department=meta.department,
                class_name=fields.get("class") or "N/A",
                quality=fields.get("quality") or fields.get("quality_score") or "N/A",
                difficulty=fields.get("difficulty") or "N/A",
                date=fields.get("date") or fields.get("date_of_review") or "N/A",
                review_number=int(review_number_match.group(1)),
                chunk_index=chunk_index,
            )
        )

    return chunks


def load_and_chunk(documents_dir: Path = DOCUMENTS_DIR) -> list[Chunk]:
    all_chunks: list[Chunk] = []
    chunk_index = 0

    for path in sorted(documents_dir.glob("*.txt")):
        meta, body = load_document(path)
        doc_chunks = chunk_document(meta, body, chunk_index)
        all_chunks.extend(doc_chunks)
        chunk_index = len(all_chunks)

    return all_chunks


def save_chunks(chunks: list[Chunk], path: Path = CHUNKS_PATH) -> None:
    path.write_text(
        json.dumps([chunk.to_dict() for chunk in chunks], indent=2),
        encoding="utf-8",
    )


def print_sample_chunks(chunks: list[Chunk], count: int = 5) -> None:
    samples = random.sample(chunks, min(count, len(chunks)))
    for index, chunk in enumerate(samples, start=1):
        print(f"\n{'=' * 72}")
        print(f"SAMPLE CHUNK {index} (chunk_index={chunk.chunk_index})")
        print(f"{'=' * 72}")
        print(chunk.text)


def print_summary(chunks: list[Chunk]) -> None:
    by_file: dict[str, int] = {}
    for chunk in chunks:
        by_file[chunk.source_file] = by_file.get(chunk.source_file, 0) + 1

    print(f"\nTotal chunks: {len(chunks)}")
    print("\nChunks per document:")
    for source_file, count in sorted(by_file.items()):
        print(f"  {source_file}: {count}")


def main() -> None:
    random.seed(42)
    chunks = load_and_chunk()
    save_chunks(chunks)

    print_sample_chunks(chunks, count=5)
    print_summary(chunks)
    print(f"\nSaved {len(chunks)} chunks to {CHUNKS_PATH}")


if __name__ == "__main__":
    main()
