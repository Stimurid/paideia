"""Валидация yaml-фронтматтера всех content/*.md по pydantic-схемам.

Запуск: pytest tests/test_frontmatter.py

Цель — гарантировать, что любые поля кейсов/типов/гипотез/противоречий из
content/ соответствуют taxonomy/. Если кто-то правит карточку руками и
ставит agentivity=42 или pattern=Z — тест падает.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter
import pytest

from api.schemas import (
    CaseFrontmatter,
    CounterSignalFrontmatter,
    HypothesisFrontmatter,
    ModeFrontmatter,
    ProjectFrontmatter,
    TensionFrontmatter,
    TypeFrontmatter,
)

CONTENT = Path(__file__).resolve().parent.parent / "content"

_SCHEMAS = {
    "cases": CaseFrontmatter,
    "projects": ProjectFrontmatter,
    "types": TypeFrontmatter,
    "hypotheses": HypothesisFrontmatter,
    "tensions": TensionFrontmatter,
    "modes": ModeFrontmatter,
    "counter-signals": CounterSignalFrontmatter,
}


def _all_files() -> list[tuple[str, Path]]:
    out: list[tuple[str, Path]] = []
    for kind in _SCHEMAS:
        for path in (CONTENT / kind).glob("*.md"):
            out.append((kind, path))
    return out


@pytest.mark.parametrize("kind,path", _all_files(), ids=lambda v: str(v))
def test_frontmatter_parses(kind: str, path: Path) -> None:
    post = frontmatter.load(path)
    schema = _SCHEMAS[kind]
    schema.model_validate(post.metadata)


def test_corpus_not_empty() -> None:
    assert _all_files(), "content/ должен содержать хотя бы по одной карточке на сущность"


def test_unique_ids_per_kind() -> None:
    seen: dict[str, set[str]] = {k: set() for k in _SCHEMAS}
    for kind, path in _all_files():
        post = frontmatter.load(path)
        eid = post.metadata.get("id")
        assert eid, f"{path}: missing id"
        assert eid not in seen[kind], f"duplicate id '{eid}' in {kind}"
        seen[kind].add(eid)
