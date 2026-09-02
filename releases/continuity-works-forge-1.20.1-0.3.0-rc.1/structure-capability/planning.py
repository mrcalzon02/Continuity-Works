from __future__ import annotations
from .grading import RebuildGrade, GRADE_CONTRACTS

PASS_SEQUENCE = [
    "baseline_inventory",
    "purpose_program",
    "precedent_and_context",
    "massing",
    "circulation_and_clearance",
    "functional_zones",
    "structural_system",
    "facade_and_silhouette",
    "utilities_and_operational_systems",
    "interior_fitout",
    "site_infrastructure",
    "cultural_theme",
    "narrative_history",
    "damage_condition",
    "encounters_loot_or_evidence",
    "detail_and_cleanup",
    "mechanical_validation",
    "fixed_camera_visual_review",
    "promotion",
]

def recommended_grade(audit, requested):
    requested = RebuildGrade.parse(requested)
    metrics = audit.get("metrics", {})
    errors = [x for x in audit.get("findings", []) if x["severity"] == "error"]
    if errors:
        return min(requested, RebuildGrade.FUNCTIONAL_REBUILD) if requested > RebuildGrade.AUDIT_ONLY else RebuildGrade.AUDIT_ONLY
    # Do not auto-escalate beyond caller permission.
    return requested

def build_plan(request, audit):
    grade = recommended_grade(audit, request.grade)
    contract = GRADE_CONTRACTS[grade]
    preserve = sorted(set(request.preserve) | set(request.integration_contracts.get("preserve", [])))
    frozen = [
        "registry_id",
        "quest_or_external_references",
        "loot/evidence contracts unless explicitly mutable",
        "geospatial selector ownership unless explicitly mutable",
    ]
    if grade <= RebuildGrade.REFIT:
        frozen += ["major footprint", "major massing", "primary purpose"]
    steps = []
    for i, name in enumerate(PASS_SEQUENCE):
        eligibility = "required"
        if grade == RebuildGrade.AUDIT_ONLY and name not in {"baseline_inventory", "mechanical_validation", "fixed_camera_visual_review"}:
            eligibility = "skip"
        steps.append({"sequence": i, "pass": name, "eligibility": eligibility})
    return {
        "structure_id": request.structure_id,
        "requested_grade": int(request.grade),
        "effective_grade": int(grade),
        "grade_name": grade.name,
        "mutation_contract": contract,
        "preserve": preserve,
        "frozen_by_default": frozen,
        "passes": steps,
        "review_policy": {
            "author_may_self_approve_visual_gate": False,
            "mechanical_and_visual_status_are_separate": True,
            "fixed_camera_comparison_preferred": True,
        },
    }
