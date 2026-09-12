"""语料解析与结构校验器测试。"""

from pathlib import Path

import pytest

from app.ingest import corpus_check
from app.ingest.corpus_check import check_corpus, validate_file
from app.rag.corpus import load_corpus_document

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DIR = REPOSITORY_ROOT / "data" / "raw_md"


def copy_sample(tmp_path: Path, filename: str = "qingjing_mosque.md") -> tuple[Path, str]:
    """复制一篇真实样例到临时目录并返回路径与原文。"""

    source = SAMPLE_DIR / filename
    original = source.read_text(encoding="utf-8")
    target = tmp_path / filename
    target.write_text(original, encoding="utf-8")
    return target, original


def test_three_samples_pass_structural_validation() -> None:
    """D11 三篇样例应全部通过结构校验。"""

    results = check_corpus(SAMPLE_DIR)

    assert len(results) == 3
    assert all(result.ok for result in results)


def test_parser_returns_frontmatter_and_body() -> None:
    """解析器应把 frontmatter 和正文交给同一个文档模型。"""

    document = load_corpus_document(SAMPLE_DIR / "qingjing_mosque.md")

    assert document.site_key == "qingjing_mosque"
    assert document.metadata["name"] == "清净寺"
    assert document.content.startswith("## 概述")


def test_malformed_yaml_returns_structured_failure(tmp_path: Path) -> None:
    """YAML 语法错误应转为失败结果，而不是向上抛异常。"""

    path = tmp_path / "broken_yaml.md"
    path.write_text("---\nname: [未闭合\n---\n", encoding="utf-8")

    result = validate_file(path)

    assert not result.ok
    assert result.errors


def test_check_corpus_continues_after_malformed_file(tmp_path: Path) -> None:
    """目录中存在坏文件时，批量校验仍应返回结构化失败结果。"""

    path = tmp_path / "broken_yaml.md"
    path.write_text("---\nname: [未闭合\n---\n", encoding="utf-8")

    results = check_corpus(tmp_path)

    assert len(results) == 1
    assert not results[0].ok
    assert results[0].errors


def test_missing_required_field_fails(tmp_path: Path) -> None:
    """缺少必填字段不能通过。"""

    path, original = copy_sample(tmp_path)
    path.write_text(original.replace("name: 清净寺", "name_removed: 清净寺"), encoding="utf-8")

    result = validate_file(path)

    assert not result.ok
    assert any("缺少必填字段: name" in error for error in result.errors)


def test_site_key_must_match_filename(tmp_path: Path) -> None:
    """站点标识和文件名不一致时应失败。"""

    path, original = copy_sample(tmp_path)
    path.write_text(
        original.replace("site_key: qingjing_mosque", "site_key: another_site"),
        encoding="utf-8",
    )

    result = validate_file(path)

    assert not result.ok
    assert any("site_key 必须与文件名" in error for error in result.errors)


def test_controlled_vocab_and_types_are_checked(tmp_path: Path) -> None:
    """受控词表、列表和数值字段应被校验。"""

    path, original = copy_sample(tmp_path)
    corrupted = original.replace("category: 宗教建筑", "category: 不明类别")
    corrupted = corrupted.replace("key_element: 多元社群", "key_element: [多元社群]")
    corrupted = corrupted.replace("alias: [圣友寺, 艾苏哈卜大寺]", "alias: 圣友寺")
    corrupted = corrupted.replace("lat: null", "lat: true")
    corrupted = corrupted.replace("visit_duration_min: null", "visit_duration_min: 0")
    path.write_text(corrupted, encoding="utf-8")

    result = validate_file(path)

    assert not result.ok
    assert any("category 不在受控词表" in error for error in result.errors)
    assert any("key_element 不在受控词表" in error for error in result.errors)
    assert any("字段必须是列表: alias" in error for error in result.errors)
    assert any("lat 必须是数字或 null" in error for error in result.errors)
    assert any("visit_duration_min 必须是正整数或 null" in error for error in result.errors)


def test_source_and_pending_fields_must_be_consistent(tmp_path: Path) -> None:
    """来源结构和 pending_fields 规则不能被绕过。"""

    path, original = copy_sample(tmp_path)
    corrupted = original.replace("    accessed: 2026-09-12", "    accessed: 2026/09/12")
    corrupted = corrupted.replace("lat: null", "lat: 24.9")
    path.write_text(corrupted, encoding="utf-8")

    result = validate_file(path)

    assert not result.ok
    assert any("accessed 必须是 YYYY-MM-DD" in error for error in result.errors)
    assert any("pending_fields 字段值必须为 null/待校对: lat" in error for error in result.errors)


def test_datetime_is_not_accepted_as_date_string(tmp_path: Path) -> None:
    """带时间的 datetime 值不应冒充合同要求的 YYYY-MM-DD。"""

    path, original = copy_sample(tmp_path)
    corrupted = original.replace(
        "    accessed: 2026-09-12",
        "    accessed: 2026-09-12 10:00:00",
        1,
    )
    path.write_text(corrupted, encoding="utf-8")

    result = validate_file(path)

    assert not result.ok
    assert any("accessed 必须是 YYYY-MM-DD" in error for error in result.errors)


def test_fact_status_and_sections_are_checked(tmp_path: Path) -> None:
    """已核对状态和正文六节顺序必须与合同一致。"""

    path, original = copy_sample(tmp_path)
    corrupted = original.replace("fact_status: 待校对", "fact_status: 已核对")
    corrupted = corrupted.replace("## 常见问答", "## 其他内容")
    path.write_text(corrupted, encoding="utf-8")

    result = validate_file(path)

    assert not result.ok
    assert any("fact_status 为已核对时 pending_fields 必须为空" in error for error in result.errors)
    assert any("正文一级标题必须按固定六节出现" in error for error in result.errors)


def test_corrupt_then_restore_proves_cli_failure_and_recovery(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """故意破坏时 CLI 返回 1，恢复后返回 0。"""

    path, original = copy_sample(tmp_path)
    monkeypatch.setattr(corpus_check, "DEFAULT_CORPUS_DIR", tmp_path)
    path.write_text(original.replace("fact_status: 待校对", "fact_status: 随便"), encoding="utf-8")

    assert corpus_check.main() == 1
    assert "FAIL" in capsys.readouterr().out

    path.write_text(original, encoding="utf-8")

    assert corpus_check.main() == 0
    assert "PASS" in capsys.readouterr().out
