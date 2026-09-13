"""把语料 frontmatter 幂等写入 MySQL 世遗点主数据表。"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.heritage_site import HeritageSite
from app.rag.corpus import CorpusDocument, iter_corpus_documents

logger = logging.getLogger(__name__)
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
CORPUS_DIR = REPOSITORY_ROOT / "data" / "raw_md"


@dataclass
class LoadSummary:
    """记录一次主数据装载的结果。"""

    inserted: int = 0
    updated: int = 0
    skipped: int = 0


def _source_short(document: CorpusDocument) -> str | None:
    """将完整来源列表压缩为 MySQL 使用的首项短引文。"""

    sources = document.metadata.get("source")
    if not isinstance(sources, list) or not sources:
        return None
    first = sources[0]
    if not isinstance(first, dict):
        return None
    publisher = str(first.get("publisher", "")).strip()
    title = str(first.get("title", "")).strip()
    short_source = f"{publisher}《{title}》".strip("《》")
    return short_source[:255] or None


def _model_values(document: CorpusDocument) -> dict[str, Any]:
    """提取 ORM 模型需要的 frontmatter 字段。"""

    metadata = document.metadata
    return {
        "site_key": metadata["site_key"],
        "name": metadata["name"],
        "alias": metadata.get("alias"),
        "area": metadata["area"],
        "category": metadata["category"],
        "unesco_group": metadata.get("unesco_group"),
        "key_element": metadata.get("key_element"),
        "lat": metadata.get("lat"),
        "lng": metadata.get("lng"),
        "address": metadata.get("address"),
        "open_hours": metadata.get("open_hours"),
        "tags": metadata.get("tags"),
        "intro_short": metadata.get("intro_short"),
        "visit_duration_min": metadata.get("visit_duration_min"),
        "theme": metadata.get("theme"),
        "notice": metadata.get("notice"),
        "fact_status": metadata.get("fact_status"),
        "pending_fields": metadata.get("pending_fields"),
        "source": _source_short(document),
    }


def _load_document(db: Any, document: CorpusDocument, summary: LoadSummary) -> None:
    """插入或按字段更新单个站点，确保重复运行不产生重复行。"""

    values = _model_values(document)
    site = db.scalar(select(HeritageSite).where(HeritageSite.site_key == values["site_key"]))
    if site is None:
        db.add(HeritageSite(**values))
        summary.inserted += 1
        return

    changed = False
    for field, value in values.items():
        if getattr(site, field) != value:
            setattr(site, field, value)
            changed = True
    if changed:
        summary.updated += 1
    else:
        summary.skipped += 1


def _print_completeness(documents: list[CorpusDocument]) -> None:
    """输出可得率与待校对率分开的字段完整率。"""

    fields = ("lat", "lng", "open_hours", "visit_duration_min", "theme", "notice")
    total = len(documents)
    logger.info("完整率 v1（总数=%s）", total)
    logger.info("字段 | 可得数 | 待校对数 | 可得率")
    for field in fields:
        available = sum(
            not _is_pending(document.metadata.get(field)) for document in documents
        )
        pending = total - available
        rate = f"{available / total:.1%}" if total else "0.0%"
        logger.info("%s | %s | %s | %s", field, available, pending, rate)


def _is_pending(value: Any) -> bool:
    """判断字段是否仍为空或待校对。"""

    return value is None or value == "待校对" or value == []


def load_sites(corpus_dir: Path = CORPUS_DIR) -> LoadSummary:
    """读取全量站点语料并执行一次事务内幂等装载。"""

    documents = iter_corpus_documents(corpus_dir)
    summary = LoadSummary()
    with SessionLocal() as db:
        for document in documents:
            _load_document(db, document, summary)
        db.commit()
    _print_completeness(documents)
    return summary


def main() -> int:
    """运行主数据装载并输出计数摘要。"""

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    summary = load_sites()
    logger.info(
        "装载完成: inserted=%s updated=%s skipped=%s",
        summary.inserted,
        summary.updated,
        summary.skipped,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
