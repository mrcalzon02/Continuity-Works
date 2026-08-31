from __future__ import annotations

import hashlib
import json
import random

from .facility_library import FacilityLibrary
from .seeded_facility_primitives import SeededFacilityGenerationError
from .seeded_facility_retail_grammars import RetailFacilityGrammars
from .seeded_facility_industrial_grammars import IndustrialFacilityGrammars


class SeededFacilityGenerator(RetailFacilityGrammars, IndustrialFacilityGrammars):
    """Deterministic vanilla facility generator for semantic facility archetypes."""

    CONTRACT = "continuityworks:seeded_facility/v1"
    M = {
        "canopy": "continuityworks:module/fuel_canopy_13x5x9",
        "pump": "continuityworks:module/pump_island_3x3x5",
        "pylon": "continuityworks:module/roadside_pylon_3x9x3",
        "room": "continuityworks:module/standard_room_9x5x9",
        "utility": "continuityworks:module/utility_service_9x5x9",
        "pumpjack": "continuityworks:module/pumpjack_9x8x9",
        "tank": "continuityworks:module/storage_tank_9x7x9",
        "pipe": "continuityworks:module/pipe_rack_5x5x13",
        "column": "continuityworks:module/process_column_5x16x5",
        "flare": "continuityworks:module/flare_stack_3x20x3",
        "gantry": "continuityworks:module/loading_gantry_9x6x7",
    }

    def __init__(self, facility_library=None):
        self.facilities = facility_library or FacilityLibrary()

    @classmethod
    def _rng(cls, seed, archetype_id):
        if isinstance(seed, bool) or not isinstance(seed, (int, str)) or not str(seed):
            raise SeededFacilityGenerationError("Seed must be a non-empty integer or string")
        text = str(seed)
        digest = hashlib.sha256(f"{cls.CONTRACT}|{archetype_id}|{text}".encode()).hexdigest()
        return text, digest, random.Random(int(digest[:32], 16))

    def generate(self, archetype_id, seed, corporate_language_id=None, scale=None):
        if self.facilities.entry(archetype_id).get("kind") != "archetype":
            raise SeededFacilityGenerationError(f"Not an archetype: {archetype_id}")
        archetype = self.facilities.load(archetype_id)
        seed_text, seed_digest, rng = self._rng(seed, archetype_id)
        allowed = list(archetype.get("allowed_corporate_languages", []))
        corporate = corporate_language_id or rng.choice(allowed)
        if corporate not in allowed:
            raise SeededFacilityGenerationError(f"{corporate} not allowed for {archetype_id}")
        tiers = list(archetype.get("scale_tiers", []))
        chosen_scale = scale or rng.choice(tiers)
        if chosen_scale not in tiers:
            raise SeededFacilityGenerationError(f"{chosen_scale} not allowed for {archetype_id}")
        slug = archetype_id.rsplit("/", 1)[-1]
        method = getattr(self, f"_g_{slug}", None)
        if method is None:
            raise SeededFacilityGenerationError(f"No seeded grammar for {archetype_id}")
        built = method(rng, self.facilities.corporate_palette(corporate), corporate, chosen_scale)
        structure = built["plan"].structure()
        required = list(archetype.get("recognition", {}).get("required_signatures", []))
        present = sorted(set(built["signatures"]))
        missing = [x for x in required if x not in present]
        minimum = float(archetype.get("recognition", {}).get("minimum_required_fraction", 1.0))
        fraction = 1.0 if not required else (len(required) - len(missing)) / len(required)
        fingerprint = self.structure_fingerprint(structure)
        report = {
            "gate": "SEEDED_FACILITY_GENERATION",
            "status": "PASS" if fraction >= minimum else "FAIL",
            "generation_contract": self.CONTRACT,
            "seed": seed_text,
            "seed_digest": seed_digest,
            "archetype_id": archetype_id,
            "corporate_language_id": corporate,
            "scale": chosen_scale,
            "size": structure["size"],
            "block_count": len(structure["blocks"]),
            "structure_fingerprint": fingerprint,
            "variant": built["variant"],
            "module_counts": built["modules"],
            "required_signatures": required,
            "present_signatures": present,
            "missing_signatures": missing,
            "recognition_fraction": fraction,
            "minimum_required_fraction": minimum,
        }
        structure["metadata"] = {
            **{k: report[k] for k in ("generation_contract", "seed", "seed_digest", "archetype_id", "corporate_language_id", "scale", "variant", "module_counts", "present_signatures", "structure_fingerprint")},
            "recognition_status": report["status"],
            "architectural_reference": True,
            "engineering_specification": False,
        }
        return {"structure": structure, "report": report}

    def generate_run_record(self, run_id, archetype_id, seed, corporate_language_id=None, scale=None):
        result = self.generate(archetype_id, seed, corporate_language_id, scale)
        return {
            "run_id": run_id,
            "request": {
                "archetype_id": archetype_id,
                "seed": str(seed),
                "corporate_language_id": corporate_language_id,
                "scale": scale,
            },
            "result": result["report"],
        }

    @staticmethod
    def structure_fingerprint(structure):
        data = {"size": structure.get("size"), "blocks": structure.get("blocks")}
        return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
