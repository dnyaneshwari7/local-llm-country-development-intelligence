from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class TextChunk:
    chunk_id: int
    page_start: int
    page_end: int
    text: str


def extract_pdf_pages(pdf_path: Path) -> list[dict]:
    reader = PdfReader(str(pdf_path))
    pages: list[dict] = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append({"page": index, "text": clean_text(text)})
    return pages


def clean_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def pages_to_text(pages: list[dict]) -> str:
    return "\n\n".join(f"[Page {page['page']}]\n{page['text']}" for page in pages if page["text"])


def chunk_pages(pages: list[dict], max_words: int = 900, overlap_words: int = 120) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    buffer: list[str] = []
    page_start = 1
    page_end = 1
    chunk_id = 1

    for page in pages:
        words = page["text"].split()
        if not words:
            continue
        if not buffer:
            page_start = page["page"]
        buffer.extend(words)
        page_end = page["page"]

        while len(buffer) >= max_words:
            chunk_words = buffer[:max_words]
            chunks.append(TextChunk(chunk_id, page_start, page_end, " ".join(chunk_words)))
            chunk_id += 1
            buffer = buffer[max_words - overlap_words :]
            page_start = page["page"]

    if buffer:
        chunks.append(TextChunk(chunk_id, page_start, page_end, " ".join(buffer)))

    return chunks


def split_chapters(full_text: str) -> list[dict]:
    pattern = re.compile(r"(?i)(chapter\s+\d+[:.\s-]+[^\[]+)")
    matches = list(pattern.finditer(full_text))
    if not matches:
        return [{"chapter_title": "Full report", "text": full_text}]

    chapters: list[dict] = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(full_text)
        title = clean_text(match.group(1))[:160]
        body = full_text[start:end].strip()
        if len(body.split()) > 80:
            chapters.append({"chapter_title": title, "text": body})
    return chapters


def save_text_artifacts(pdf_path: Path, output_dir: Path, max_words: int, overlap_words: int) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    pages = extract_pdf_pages(pdf_path)
    full_text = pages_to_text(pages)
    chunks = chunk_pages(pages, max_words=max_words, overlap_words=overlap_words)
    chapters = split_chapters(full_text)

    (output_dir / "report_text.txt").write_text(full_text, encoding="utf-8")
    (output_dir / "pages.json").write_text(json.dumps(pages, indent=2), encoding="utf-8")
    (output_dir / "chunks.json").write_text(
        json.dumps([asdict(chunk) for chunk in chunks], indent=2),
        encoding="utf-8",
    )
    (output_dir / "chapters.json").write_text(json.dumps(chapters, indent=2), encoding="utf-8")
    return {"pages": pages, "text": full_text, "chunks": chunks, "chapters": chapters}

