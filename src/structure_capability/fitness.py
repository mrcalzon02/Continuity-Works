FITNESS_DIMENSIONS = (
    "mechanical_validity",
    "accessibility",
    "circulation",
    "functional_readability",
    "purpose_fit",
    "geospatial_fit",
    "cultural_consistency",
    "structural_plausibility",
    "site_infrastructure",
    "progression_safety",
    "worldgen_suitability",
    "performance_budget",
    "visual_quality",
)

def evaluate_plan(request, audit):
    scores = {k: 1.0 for k in FITNESS_DIMENSIONS}
    notes = []
    if any(f["severity"] == "error" for f in audit.get("findings", [])):
        scores["mechanical_validity"] = 0.0
    if not request.purpose.required_zones:
        scores["purpose_fit"] = 0.5
        scores["functional_readability"] = 0.5
        notes.append("Define required functional zones before a major rebuild.")
    if not request.theme.palette_roles and request.theme.name != "neutral":
        scores["cultural_consistency"] = 0.5
        notes.append("Named theme has no palette-role contract.")
    if request.context.terrain == "unknown":
        scores["geospatial_fit"] = 0.5
        notes.append("Terrain class is unknown.")
    # Visual quality is never self-approved.
    scores["visual_quality"] = None
    return {"scores": scores, "notes": notes, "visual_gate": "REVIEW_NEEDED"}
