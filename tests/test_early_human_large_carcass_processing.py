import pytest

from structure_capability.early_human_large_carcass_processing import (
    LargeCarcassProcessingSiteGenerationError,
    LargeCarcassProcessingSiteGenerator,
)


def test_deterministic_replay_and_seed_variation():
    generator = LargeCarcassProcessingSiteGenerator()
    a = generator.generate(seed=130013, scale="medium")
    b = generator.generate(seed=130013, scale="medium")
    c = generator.generate(seed=130014, scale="medium")
    assert a["metadata"]["fingerprint"] == b["metadata"]["fingerprint"]
    assert a["metadata"]["fingerprint"] != c["metadata"]["fingerprint"]


@pytest.mark.parametrize(
    ("scale", "size", "minimum_bays"),
    [
        ("small", [43, 8, 35], 3),
        ("medium", [57, 9, 47], 4),
        ("large", [73, 10, 61], 6),
    ],
)
def test_scale_envelopes_and_large_carcass_identity(scale, size, minimum_bays):
    site = LargeCarcassProcessingSiteGenerator().generate(seed=7713, scale=scale)
    metadata = site["metadata"]
    assert site["size"] == size
    assert len(metadata["task_bays"]) >= minimum_bays
    assert len(metadata["heavy_bone_points"]) >= 6
    assert metadata["carcass_axis_length"] >= 15
    assert all(metadata["qualification"].values())
    assert size[0] > 39 and size[2] > 33


def test_processing_topology_has_dirty_and_clean_sides_with_clear_haul_route():
    site = LargeCarcassProcessingSiteGenerator().generate(seed="megafauna-topology", scale="large")
    metadata = site["metadata"]
    assert metadata["discard_cell_count"] >= 12
    assert len(metadata["staging_points"]) >= 5
    assert len(metadata["haul_corridor"]) >= 2
    assert metadata["qualification"]["directional_dirty_discard"]
    assert metadata["qualification"]["clean_staging_present"]
    assert metadata["qualification"]["haul_corridor_clear"]


@pytest.mark.parametrize(
    "culture",
    ["cooperative_disarticulation", "marrow_intensive", "transport_priority", "hide_retention"],
)
def test_culture_variants_preserve_archetype(culture):
    site = LargeCarcassProcessingSiteGenerator().generate(
        seed=f"culture-{culture}",
        scale="medium",
        culture_profile=culture,
    )
    assert site["metadata"]["culture_profile"] == culture
    assert all(site["metadata"]["qualification"].values())


def test_marrow_intensive_variant_increases_heavy_bone_evidence():
    generator = LargeCarcassProcessingSiteGenerator()
    baseline = generator.generate(seed=91, scale="medium", culture_profile="cooperative_disarticulation")
    marrow = generator.generate(seed=91, scale="medium", culture_profile="marrow_intensive")
    assert len(marrow["metadata"]["heavy_bone_points"]) > len(baseline["metadata"]["heavy_bone_points"])


def test_transport_priority_increases_staging():
    generator = LargeCarcassProcessingSiteGenerator()
    baseline = generator.generate(seed=92, scale="medium")
    transport = generator.generate(seed=92, scale="medium", culture_profile="transport_priority")
    assert len(transport["metadata"]["staging_points"]) > len(baseline["metadata"]["staging_points"])


def test_hide_retention_increases_hide_handling_without_domination():
    generator = LargeCarcassProcessingSiteGenerator()
    baseline = generator.generate(seed=93, scale="large")
    hide = generator.generate(seed=93, scale="large", culture_profile="hide_retention")
    assert len(hide["metadata"]["hide_offcut_points"]) > len(baseline["metadata"]["hide_offcut_points"])
    assert hide["metadata"]["qualification"]["hide_handling_subordinate"]


@pytest.mark.parametrize(
    "condition",
    ["active", "recent", "repeated", "abandoned", "weathered", "scavenger_reworked", "sediment_reworked", "repurposed"],
)
def test_condition_variants_remain_qualified(condition):
    site = LargeCarcassProcessingSiteGenerator().generate(
        seed=f"condition-{condition}",
        scale="medium",
        condition=condition,
    )
    assert all(site["metadata"]["qualification"].values())


def test_arid_weathering_does_not_add_moss():
    site = LargeCarcassProcessingSiteGenerator().generate(
        seed="dry-weathering",
        scale="medium",
        biome_family="arid",
        condition="weathered",
    )
    assert all(block["block"] != "minecraft:moss_carpet" for block in site["blocks"])


def test_all_blocks_stay_inside_declared_bounds():
    site = LargeCarcassProcessingSiteGenerator().generate(seed=13013, scale="large")
    width, height, depth = site["size"]
    for block in site["blocks"]:
        x, y, z = block["pos"]
        assert 0 <= x < width
        assert 0 <= y < height
        assert 0 <= z < depth


def test_invalid_inputs_rejected():
    generator = LargeCarcassProcessingSiteGenerator()
    with pytest.raises(LargeCarcassProcessingSiteGenerationError):
        generator.generate(seed=1, scale="gigantic")
    with pytest.raises(LargeCarcassProcessingSiteGenerationError):
        generator.generate(seed=1, condition="museum")
    with pytest.raises(LargeCarcassProcessingSiteGenerationError):
        generator.generate(seed=1, culture_profile="industrial_butchery")


def test_worldgen_is_additive_and_protected_at_minimum_radius():
    bundle = LargeCarcassProcessingSiteGenerator().worldgen_bundle()
    protection = bundle["protection_profile"]
    assert bundle["structure_id"] == "continuityworks:e01_013_large_carcass_processing_site"
    assert bundle["family_id"] == "continuityworks:early_human_carcass_processing"
    assert bundle["replace_policy"] == "bounded_additive_non_destructive"
    assert bundle["compatible_family_policy"] == "same_parent_reservation_only"
    assert protection["exclusion_radius"] >= 500
    assert protection["jigsaw_piece_exclusion_radius"] >= 500
    assert protection["protect_jigsaw_pieces"] is True


def test_worldgen_random_spread_spacing_is_valid():
    bundle = LargeCarcassProcessingSiteGenerator().worldgen_bundle()
    placement = bundle["structure_set"]["placement"]
    assert placement["spacing"] > placement["separation"]
    assert bundle["validation_findings"] == []
