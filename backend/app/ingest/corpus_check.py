"""对 Markdown 语料执行 frontmatter、词表、溯源和正文结构校验。"""

import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from app.rag.corpus import CorpusDocument, iter_corpus_documents, load_corpus_document

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CORPUS_DIR = REPOSITORY_ROOT / "data" / "raw_md"

REQUIRED_FIELDS = (
    "site_key",
    "name",
    "alias",
    "category",
    "key_element",
    "unesco_group",
    "area",
    "lat",
    "lng",
    "address",
    "open_hours",
    "tags",
    "intro_short",
    "visit_duration_min",
    "theme",
    "notice",
    "source",
    "pending_fields",
    "fact_status",
    "updated",
)
FACT_FIELDS = {
    "name",
    "alias",
    "category",
    "key_element",
    "area",
    "lat",
    "lng",
    "address",
    "open_hours",
    "visit_duration_min",
    "notice",
}
CONTROLLED_CATEGORIES = {
    "港口码头",
    "桥梁",
    "航标塔",
    "城市遗址",
    "管理机构",
    "文教建筑",
    "宗教建筑",
    "墓葬",
    "石刻",
    "窑址",
    "冶铁遗址",
}
CONTROLLED_KEY_ELEMENTS = {
    "机构保障",
    "多元社群",
    "城市结构",
    "生产基地",
    "交通网络",
    "整体格局",
}
CONTROLLED_THEMES = {
    "海丝溯源",
    "宗教多元",
    "古建桥梁",
    "非遗体验",
    "城市漫步",
    "亲子研学",
}
FACT_STATUSES = {"已核对", "待校对"}
SECTION_TITLES = (
    "概述",
    "历史沿革",
    "遗产价值",
    "看点与细节",
    "实用信息",
    "常见问答",
)
SITE_KEY_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


@dataclass(frozen=True)
class ValidationResult:
    """记录一篇语料的校验结果。"""

    path: Path
    errors: tuple[str, ...]

    @property
    def ok(self) -> bool:
        """返回语料是否通过全部结构校验。"""

        return not self.errors


def _is_blank(value: Any) -> bool:
    """判断值是否为空或待校对标记。"""

    return value is None or value == "" or value == "待校对"


def _is_number(value: Any) -> bool:
    """判断坐标值是否为数字而不是布尔值。"""

    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_iso_date(value: Any) -> bool:
    """判断日期字段是否符合 YYYY-MM-DD。"""

    if isinstance(value, date):
        return True
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate_metadata(document: CorpusDocument) -> list[str]:
    """校验 frontmatter 字段及字段间约束。"""

    metadata = document.metadata
    errors: list[str] = []

    missing_fields = [field for field in REQUIRED_FIELDS if field not in metadata]
    errors.extend(f"缺少必填字段: {field}" for field in missing_fields)

    for field in ("site_key", "name", "category", "area", "fact_status", "updated"):
        if field in metadata and metadata[field] in (None, ""):
            errors.append(f"字段不能为空: {field}")

    site_key = metadata.get("site_key")
    if not isinstance(site_key, str) or not SITE_KEY_PATTERN.fullmatch(site_key):
        errors.append("site_key 必须是小写英文蛇形标识")
    elif document.path.name != "<memory>" and site_key != document.path.stem:
        errors.append("site_key 必须与文件名（去 .md）一致")

    for field in ("alias", "tags", "theme", "pending_fields"):
        if field in metadata and not isinstance(metadata[field], list):
            errors.append(f"字段必须是列表: {field}")

    category = metadata.get("category")
    if not isinstance(category, str) or category not in CONTROLLED_CATEGORIES:
        errors.append(f"category 不在受控词表: {category}")

    key_element = metadata.get("key_element")
    if not isinstance(key_element, str) or key_element not in CONTROLLED_KEY_ELEMENTS:
        errors.append(f"key_element 不在受控词表: {key_element}")

    themes = metadata.get("theme")
    if isinstance(themes, list):
        errors.extend(
            f"theme 不在受控词表: {theme}"
            for theme in themes
            if not isinstance(theme, str) or theme not in CONTROLLED_THEMES
        )

    fact_status = metadata.get("fact_status")
    if fact_status not in FACT_STATUSES:
        errors.append(f"fact_status 不在受控词表: {fact_status}")

    for field in ("lat", "lng"):
        if field in metadata and metadata[field] is not None and not _is_number(metadata[field]):
            errors.append(f"{field} 必须是数字或 null")

    visit_duration = metadata.get("visit_duration_min")
    if visit_duration is not None and (
        not isinstance(visit_duration, int)
        or isinstance(visit_duration, bool)
        or visit_duration <= 0
    ):
        errors.append("visit_duration_min 必须是正整数或 null")

    sources = metadata.get("source")
    if not isinstance(sources, list) or not sources:
        errors.append("source 必须是非空列表")
    else:
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                errors.append(f"source[{index}] 必须是对象")
                continue
            for field in ("title", "url", "accessed"):
                if _is_blank(source.get(field)):
                    errors.append(f"source[{index}] 缺少字段或值为空: {field}")
            if "accessed" in source and not _is_iso_date(source["accessed"]):
                errors.append(f"source[{index}].accessed 必须是 YYYY-MM-DD")

    pending_fields = metadata.get("pending_fields")
    if isinstance(pending_fields, list):
        for field in pending_fields:
            if not isinstance(field, str) or field not in FACT_FIELDS:
                errors.append(f"pending_fields 包含未知事实字段: {field}")
                continue
            value = metadata.get(field)
            # 样例中的 key_element 是老师给出的暂定归类，必须保留值并标记待核对。
            if not _is_blank(value) and field != "key_element":
                errors.append(f"pending_fields 字段值必须为 null/待校对: {field}")

        for field in FACT_FIELDS:
            if field in metadata and _is_blank(metadata[field]) and field not in pending_fields:
                errors.append(f"待校对字段必须列入 pending_fields: {field}")

        if fact_status == "已核对" and pending_fields:
            errors.append("fact_status 为已核对时 pending_fields 必须为空")
        if fact_status == "待校对" and not pending_fields:
            errors.append("fact_status 为待校对时 pending_fields 不能为空")

    updated = metadata.get("updated")
    if updated is not None and not _is_iso_date(updated):
        errors.append("updated 必须是 YYYY-MM-DD")

    return errors


def _validate_sections(document: CorpusDocument) -> list[str]:
    """校验正文六个一级标题及其固定顺序。"""

    headings = [
        line[3:].strip()
        for line in document.content.splitlines()
        if line.startswith("## ")
    ]
    if tuple(headings) != SECTION_TITLES:
        return [f"正文一级标题必须按固定六节出现: {list(SECTION_TITLES)}"]
    return []


def validate_document(document: CorpusDocument) -> list[str]:
    """返回单篇语料的全部结构校验错误。"""

    return _validate_metadata(document) + _validate_sections(document)


def validate_file(path: Path) -> ValidationResult:
    """读取并校验一篇语料，解析失败也转换为结构化结果。"""

    try:
        document = load_corpus_document(path)
    except (OSError, ValueError) as exc:
        return ValidationResult(path=path, errors=(str(exc),))
    return ValidationResult(path=path, errors=tuple(validate_document(document)))


def check_corpus(corpus_dir: Path = DEFAULT_CORPUS_DIR) -> list[ValidationResult]:
    """校验目录内全部 Markdown 语料并按文件名排序返回结果。"""

    results: list[ValidationResult] = []
    for document in iter_corpus_documents(corpus_dir):
        results.append(ValidationResult(document.path, tuple(validate_document(document))))
    return results


def main() -> int:
    """运行命令行校验并按结果返回进程退出码。"""

    results = check_corpus(DEFAULT_CORPUS_DIR)
    for result in results:
        if result.ok:
            sys.stdout.write(f"PASS {result.path}\n")
            continue
        sys.stdout.write(f"FAIL {result.path}\n")
        for error in result.errors:
            sys.stdout.write(f"  - {error}\n")

    failed_count = sum(not result.ok for result in results)
    sys.stdout.write(
        f"总计: {len(results)}，通过: {len(results) - failed_count}，失败: {failed_count}\n"
    )
    return 1 if failed_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
