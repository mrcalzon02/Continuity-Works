from __future__ import annotations
from .audit import audit_source
from .fitness import evaluate_plan
from .planning import build_plan

class StructurePipeline:
    def __init__(self, snapshot_store, registry_resolver):
        self.snapshots = snapshot_store
        self.registry = registry_resolver

    def audit(self, request):
        audit = audit_source(request.source, request)
        fitness = evaluate_plan(request, audit)
        snapshot = self.snapshots.create(
            request.structure_id, "audit",
            {"request": request.to_dict(), "audit": audit, "fitness": fitness},
            artifacts=[request.source] if request.source else [],
        )
        return {"request": request.to_dict(), "audit": audit, "fitness": fitness, "snapshot": snapshot}

    def plan(self, request):
        audit = audit_source(request.source, request)
        plan = build_plan(request, audit)
        fitness = evaluate_plan(request, audit)
        snapshot = self.snapshots.create(
            request.structure_id, "plan",
            {"request": request.to_dict(), "audit": audit, "plan": plan, "fitness": fitness},
            artifacts=[request.source] if request.source else [],
        )
        return {"request": request.to_dict(), "audit": audit, "plan": plan, "fitness": fitness, "snapshot": snapshot}

    def generate(self, request):
        # Generation is provider-oriented: the generic core emits an authoritative
        # generation dossier and snapshot, then a format/provider applies mutations.
        # This avoids pretending generic code can infer a high-quality building from
        # nothing without an authoring provider.
        result = self.plan(request)
        result["generation"] = {
            "status": "READY_FOR_PROVIDER" if result["audit"]["status"] != "FAIL" else "BLOCKED",
            "provider_contract": {
                "must_obey_preserve": result["plan"]["preserve"],
                "must_use_verified_registry_ids": True,
                "vanilla_first_fallback": True,
                "must_snapshot_each_verified_batch": True,
                "server_visual_review_required": False,
                "server_side_rendering": False,
                "client_rendering_responsibility": True,
                "visual_review_advisory_only": True,
            },
        }
        return result
