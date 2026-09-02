from __future__ import annotations

from typing import Any

from ..compatibility import validate_compatibility_request
from .infrastructure import (
    InfrastructureGenerator as _BaseInfrastructureGenerator,
    InfrastructureLayoutRequest,
)


class InfrastructureGenerator(_BaseInfrastructureGenerator):
    """Public infrastructure generator with the global additive compatibility gate."""

    def generate(self, request: dict[str, Any] | InfrastructureLayoutRequest):
        if isinstance(request, dict):
            payload = dict(request)
            compatibility = dict(payload.get("compatibility") or {})
            lost_cities = dict(payload.get("lost_cities") or {})
            validate_compatibility_request(compatibility, lost_cities)
        return super().generate(request)


def generate_infrastructure_layout(request):
    return InfrastructureGenerator().generate(request)
