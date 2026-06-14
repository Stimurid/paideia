from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_protected_layer_entrypoints_exist() -> None:
    required = [
        "AGENTS.md",
        "CLAUDE.md",
        "docs/agent/NO_TOUCH_SURFACES.md",
        "docs/agent/PROMPT_AND_OVERLAY_GOVERNANCE.md",
        "docs/agent/BYOK_AND_SECRET_SAFETY.md",
        "docs/agent/KAIRON_KAIYONA_TRIZ_BOUNDARIES.md",
        "docs/agent/PAIDEIA_AGENT_COMMANDS.md",
        "docs/agent/PROTECTED_LAYER_STATUS.md",
    ]

    for relative_path in required:
        assert (ROOT / relative_path).is_file(), relative_path


def test_agents_names_core_protected_surfaces() -> None:
    text = read("AGENTS.md")

    for expected in [
        "docs/agent/NO_TOUCH_SURFACES.md",
        "docs/agent/PROMPT_AND_OVERLAY_GOVERNANCE.md",
        "docs/agent/BYOK_AND_SECRET_SAFETY.md",
        "api/**",
        "prompts/**",
        "raw/**",
        ".env",
        "Quinta",
        "Kairon",
        "Kaiyona",
    ]:
        assert expected in text


def test_protected_status_does_not_claim_hard_enforcement() -> None:
    text = read("docs/agent/PROTECTED_LAYER_STATUS.md")

    assert "protected: partial / strong-context" in text
    assert "hooks" in text
    assert "permission deny rules" in text
    assert "runtime blockers" in text
    assert "Docs-level presence is not behavior proof" in text
