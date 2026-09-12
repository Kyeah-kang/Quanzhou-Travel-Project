"""解析带 YAML frontmatter 的 Markdown 语料，供后续切分与索引复用。"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

FRONTMATTER_DELIMITER = "---"


@dataclass(frozen=True)
class CorpusDocument:
    """一篇语料的路径、结构化元数据和 Markdown 正文。"""

    path: Path
    metadata: dict[str, Any]
    content: str

    @property
    def site_key(self) -> str:
        """返回语料的站点或主题标识。"""

        return str(self.metadata.get("site_key", ""))


def parse_markdown(text: str, source_path: Path | None = None) -> CorpusDocument:
    """解析单篇 Markdown 的 frontmatter 和正文。"""

    lines = text.splitlines()
    if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
        location = f" in {source_path}" if source_path else ""
        raise ValueError(f"frontmatter must start with ---{location}")

    try:
        end_index = next(
            index
            for index, line in enumerate(lines[1:], start=1)
            if line.strip() == FRONTMATTER_DELIMITER
        )
    except StopIteration as exc:
        location = f" in {source_path}" if source_path else ""
        raise ValueError(f"frontmatter closing --- not found{location}") from exc

    raw_frontmatter = "\n".join(lines[1:end_index])
    metadata = yaml.safe_load(raw_frontmatter)
    if not isinstance(metadata, dict):
        location = f" in {source_path}" if source_path else ""
        raise ValueError(f"frontmatter must be a mapping{location}")

    content = "\n".join(lines[end_index + 1 :]).lstrip("\n")
    return CorpusDocument(
        path=source_path or Path("<memory>"),
        metadata=dict(metadata),
        content=content,
    )


def load_corpus_document(path: Path) -> CorpusDocument:
    """从磁盘读取并解析一篇 UTF-8 Markdown 语料。"""

    return parse_markdown(path.read_text(encoding="utf-8"), source_path=path)


def iter_corpus_documents(corpus_dir: Path) -> list[CorpusDocument]:
    """按文件名排序读取语料目录中的 Markdown 文件。"""

    return [
        load_corpus_document(path)
        for path in sorted(corpus_dir.glob("*.md"))
        if not path.name.startswith("_")
    ]
