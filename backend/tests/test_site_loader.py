"""验证语料主数据 loader 的短引文和完整率输出契约。"""

from pathlib import Path

import pytest

from app.ingest.site_loader import _print_completeness, _source_short
from app.rag.corpus import CorpusDocument, iter_corpus_documents

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
CORPUS_DIR = REPOSITORY_ROOT / "data" / "raw_md"


def test_source_short_preserves_paired_book_title_marks() -> None:
    """MySQL 短引文必须保留首项书名号，避免来源展示被静默破坏。"""

    document = CorpusDocument(
        path=Path("anping_bridge.md"),
        metadata={
            "source": [
                {
                    "publisher": "泉州市人民政府",
                    "title": "安平桥-全国重点文物保护单位简介",
                }
            ]
        },
        content="",
    )

    short_source = _source_short(document)

    assert short_source is not None
    assert short_source.endswith("》")
    assert short_source.count("《") == short_source.count("》") == 1


def test_source_short_keeps_closing_mark_when_truncated() -> None:
    """短引文达到数据库长度上限时，也不能丢失右书名号。"""

    document = CorpusDocument(
        path=Path("long_source.md"),
        metadata={
            "source": [{"publisher": "泉州市人民政府", "title": "资料" * 200}],
        },
        content="",
    )

    short_source = _source_short(document)

    assert short_source is not None
    assert len(short_source) == 255
    assert short_source.endswith("》")
    assert short_source.count("《") == short_source.count("》") == 1


def test_completeness_report_is_written_to_stdout(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """完整率表应能通过 stdout 重定向单独收集。"""

    _print_completeness(iter_corpus_documents(CORPUS_DIR))

    captured = capsys.readouterr()
    assert "完整率 v1" in captured.out
    assert "字段 | 可得数 | 待校对数 | 可得率" in captured.out
    assert captured.err == ""
