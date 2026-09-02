from enum import IntEnum

class RebuildGrade(IntEnum):
    AUDIT_ONLY = 0
    TOUCH_UP = 1
    REFIT = 2
    DETAIL_PASS = 3
    FUNCTIONAL_REBUILD = 4
    HEAVY_REBUILD = 5
    FULL_RECONTEXTUALIZATION = 6

    @classmethod
    def parse(cls, value):
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            return cls(value)
        normalized = str(value).strip().upper().replace("-", "_").replace(" ", "_")
        aliases = {
            "FULL_REBUILD": "FULL_RECONTEXTUALIZATION",
            "REBUILD": "FUNCTIONAL_REBUILD",
            "DETAIL": "DETAIL_PASS",
        }
        return cls[aliases.get(normalized, normalized)]

GRADE_CONTRACTS = {
    RebuildGrade.AUDIT_ONLY: {
        "geometry": "immutable",
        "purpose_reprogramming": False,
        "massing_change": False,
    },
    RebuildGrade.TOUCH_UP: {
        "geometry": "minimal",
        "purpose_reprogramming": False,
        "massing_change": False,
    },
    RebuildGrade.REFIT: {
        "geometry": "local",
        "purpose_reprogramming": False,
        "massing_change": False,
    },
    RebuildGrade.DETAIL_PASS: {
        "geometry": "local_to_moderate",
        "purpose_reprogramming": False,
        "massing_change": False,
    },
    RebuildGrade.FUNCTIONAL_REBUILD: {
        "geometry": "substantial_internal",
        "purpose_reprogramming": True,
        "massing_change": "limited",
    },
    RebuildGrade.HEAVY_REBUILD: {
        "geometry": "substantial",
        "purpose_reprogramming": True,
        "massing_change": True,
    },
    RebuildGrade.FULL_RECONTEXTUALIZATION: {
        "geometry": "authoritative_rebuild",
        "purpose_reprogramming": True,
        "massing_change": True,
    },
}
