from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class FixtureCase:
    fixture_id: str
    scene_family: str
    source_paths: tuple[str, ...]
    expected_concern: str
    false_positive_risk: str


@dataclass(frozen=True)
class PreviewVerdict:
    fixture_id: str
    scene_family: str
    input_summary: str
    expected_concern: str
    preview_only_recommendation: str
    severity: str
    action: str
    evidence_phrase: str
    false_positive_risk: str
    mutation: str = "none"


FIXTURES = [
    FixtureCase(
        fixture_id="demo_electives_synthesis_stub",
        scene_family="project-synthesis",
        source_paths=("content/projects/demo-electives.md",),
        expected_concern="thin project stub should not be promoted into synthesis narrative",
        false_positive_risk="low",
    ),
    FixtureCase(
        fixture_id="seminar_cards_anti_washing",
        scene_family="anti_washing",
        source_paths=("content/projects/example-seminar-cards.md",),
        expected_concern="bounded agentivity claim still needs stronger outcome evidence",
        false_positive_risk="medium",
    ),
    FixtureCase(
        fixture_id="seminar_cards_stakeholder_attack_rector",
        scene_family="stakeholder_attack",
        source_paths=(
            "content/projects/example-seminar-cards.md",
            "content/stakeholders/rector.md",
        ),
        expected_concern="strategic, budget, and accountability answers are only partial",
        false_positive_risk="medium",
    ),
    FixtureCase(
        fixture_id="seminar_cards_export_rpd_gap",
        scene_family="export_rpd",
        source_paths=(
            "content/projects/example-seminar-cards.md",
            "content/stakeholders/fgos-expert.md",
            "prompts/docs/rpd.md",
        ),
        expected_concern="export readiness is weaker than the narrative suggests",
        false_positive_risk="low",
    ),
    FixtureCase(
        fixture_id="seminar_cards_rough_valid_control",
        scene_family="rough_valid_control",
        source_paths=("content/projects/example-seminar-cards.md",),
        expected_concern="rough draft should receive advice without being blocked",
        false_positive_risk="high",
    ),
]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def load_fixture_text(case: FixtureCase) -> str:
    return "\n\n".join(read(path) for path in case.source_paths)


def has_all(text: str, *needles: str) -> bool:
    lowered = text.lower()
    return all(needle.lower() in lowered for needle in needles)


def evaluate_quality_gate_preview(case: FixtureCase) -> PreviewVerdict:
    text = load_fixture_text(case)
    lowered = text.lower()

    if case.fixture_id == "demo_electives_synthesis_stub":
        assert "agentivity: 2" in lowered
        assert "workspace" in lowered
        assert "problem_situation:" not in lowered
        return PreviewVerdict(
            fixture_id=case.fixture_id,
            scene_family=case.scene_family,
            input_summary="Minimal project stub with signature context and a one-line intent only.",
            expected_concern=case.expected_concern,
            preview_only_recommendation="Do not synthesize beyond stub level; request missing problem, mechanism, risks, and evaluation fields first.",
            severity="high",
            action="request_revision",
            evidence_phrase="Only signature context and one-line intent are present; operational project sections are missing.",
            false_positive_risk=case.false_positive_risk,
        )

    if case.fixture_id == "seminar_cards_anti_washing":
        assert has_all(
            lowered,
            "agentivity: 2",
            "logs: true",
            "prompts_versioned: true",
            "quality gate",
            "has_metrics: false",
        )
        return PreviewVerdict(
            fixture_id=case.fixture_id,
            scene_family=case.scene_family,
            input_summary="Richer seminar project with bounded agentivity, logs, prompt versioning, and explicit AI roles.",
            expected_concern=case.expected_concern,
            preview_only_recommendation="Keep the agentivity claim modest and add stronger outcome evidence before any stronger branding.",
            severity="low",
            action="advise",
            evidence_phrase="The project already declares low agentivity and keeps audit hints, but outcome evidence is still thin.",
            false_positive_risk=case.false_positive_risk,
        )

    if case.fixture_id == "seminar_cards_stakeholder_attack_rector":
        assert has_all(
            lowered,
            "quality gate",
            "institutional_loop:",
            "attack_style: strategic / risk-averse",
        )
        return PreviewVerdict(
            fixture_id=case.fixture_id,
            scene_family=case.scene_family,
            input_summary="Seminar project reviewed against rector-level pressure around budget, brand, strategy, and accountability.",
            expected_concern=case.expected_concern,
            preview_only_recommendation="Escalate to human review before positioning this as an institution-level initiative.",
            severity="medium",
            action="escalate_review",
            evidence_phrase="Methodical approval is mentioned, but budget, institutional strategy, and named accountability remain only partial.",
            false_positive_risk=case.false_positive_risk,
        )

    if case.fixture_id == "seminar_cards_export_rpd_gap":
        assert has_all(lowered, "рпд", "fgos", "competencies", "learning_outcomes")
        assert "competencies:" not in read("content/projects/example-seminar-cards.md").lower()
        return PreviewVerdict(
            fixture_id=case.fixture_id,
            scene_family=case.scene_family,
            input_summary="Seminar project checked against RPD/FGOS export expectations and the methodist pressure surface.",
            expected_concern=case.expected_concern,
            preview_only_recommendation="Keep export in preview-only mode until competency mapping, learning outcomes, and responsibility are explicit.",
            severity="medium",
            action="request_revision",
            evidence_phrase="The project names institutional intent, but the project draft does not yet expose an explicit competency map or export-grade responsibility chain.",
            false_positive_risk=case.false_positive_risk,
        )

    if case.fixture_id == "seminar_cards_rough_valid_control":
        assert has_all(
            lowered,
            "problem_situation:",
            "effect_hypothesis:",
            "team_roles:",
            "metrics_evidence:",
            "risks:",
        )
        return PreviewVerdict(
            fixture_id=case.fixture_id,
            scene_family=case.scene_family,
            input_summary="Rough but operational seminar draft with problem, hypothesis, roles, metrics, and explicit risks.",
            expected_concern=case.expected_concern,
            preview_only_recommendation="Allow the draft to proceed with advice; do not block a living draft that already names risks and evidence targets.",
            severity="low",
            action="allow",
            evidence_phrase="The draft is incomplete, but it is operational: problem, hypothesis, roles, metrics, and risks are visible.",
            false_positive_risk=case.false_positive_risk,
        )

    raise AssertionError(case.fixture_id)


def test_selected_fixture_sources_exist() -> None:
    for case in FIXTURES:
        for relative_path in case.source_paths:
            assert (ROOT / relative_path).is_file(), relative_path


def test_preview_quality_gate_results_match_expected_boundaries() -> None:
    results = {case.fixture_id: evaluate_quality_gate_preview(case) for case in FIXTURES}

    assert results["demo_electives_synthesis_stub"].action == "request_revision"
    assert results["demo_electives_synthesis_stub"].severity == "high"

    assert results["seminar_cards_anti_washing"].action == "advise"
    assert results["seminar_cards_anti_washing"].severity == "low"

    assert results["seminar_cards_stakeholder_attack_rector"].action == "escalate_review"
    assert results["seminar_cards_stakeholder_attack_rector"].severity == "medium"

    assert results["seminar_cards_export_rpd_gap"].action == "request_revision"
    assert results["seminar_cards_export_rpd_gap"].severity == "medium"

    assert results["seminar_cards_rough_valid_control"].action == "allow"
    assert results["seminar_cards_rough_valid_control"].severity == "low"

    for result in results.values():
        assert result.mutation == "none"


def test_preview_fixture_report_records_results_and_limits() -> None:
    report = read("docs/agent/PAIDEIA_QUALITY_GATE_PREVIEW_FIXTURE_RUN_2026-06-15.md")

    for expected in [
        "PAIDEIA_QUALITY_GATE_PREVIEW_FIXTURE_RUN_2026-06-15",
        "no runtime auto-blocking was enabled",
        "ALLOW_PREVIEW_ONLY_FOR_SELECTED_SCENES",
        "rough but valid",
        "mutation = none",
    ]:
        assert expected in report

    for case in FIXTURES:
        result = evaluate_quality_gate_preview(case)
        for expected in [
            case.fixture_id,
            case.scene_family,
            result.severity,
            result.action,
            result.evidence_phrase,
            result.false_positive_risk,
        ]:
            assert expected in report
