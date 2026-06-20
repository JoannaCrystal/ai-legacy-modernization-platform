from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "docs" / "knowledge_base"

CATEGORY_MAP = {
    "soap-modernization": "Integration",
    "spring-modernization": "Framework",
    "monolith-modernization": "Architecture",
}

DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100


class DocumentLoader:
    def load_documents(self) -> list[dict[str, str]]:
        if not KNOWLEDGE_BASE_DIR.exists():
            raise FileNotFoundError(
                f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}"
            )

        documents: list[dict[str, str]] = []

        for file_path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
            content = file_path.read_text(encoding="utf-8").strip()
            if not content:
                continue

            stem = file_path.stem
            documents.append(
                {
                    "title": self._extract_title(content, stem),
                    "content": content,
                    "category": CATEGORY_MAP.get(
                        stem,
                        "General",
                    ),
                }
            )

        return documents

    def chunk_document(
        self,
        content: str,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_CHUNK_OVERLAP,
    ) -> list[str]:
        paragraphs = [part.strip() for part in content.split("\n\n") if part.strip()]
        if not paragraphs:
            return []

        chunks: list[str] = []
        current_chunk = ""

        for paragraph in paragraphs:
            candidate = (
                f"{current_chunk}\n\n{paragraph}".strip()
                if current_chunk
                else paragraph
            )

            if len(candidate) <= chunk_size:
                current_chunk = candidate
                continue

            if current_chunk:
                chunks.extend(
                    self._split_large_text(current_chunk, chunk_size, overlap)
                )

            if len(paragraph) <= chunk_size:
                current_chunk = paragraph
            else:
                chunks.extend(
                    self._split_large_text(paragraph, chunk_size, overlap)
                )
                current_chunk = ""

        if current_chunk:
            chunks.extend(
                self._split_large_text(current_chunk, chunk_size, overlap)
            )

        return chunks

    def _extract_title(self, content: str, stem: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return stem.replace("-", " ").title()

    def _split_large_text(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> list[str]:
        chunks: list[str] = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(text):
                break
            start = max(end - overlap, start + 1)

        return chunks
