package io.continuityworks.api.blueprint;

import java.util.List;
import java.util.Objects;
import java.util.UUID;

/** Immutable compact blueprint. Geometry remains primitive-based until explicitly streamed/materialized. */
public record CompactBlueprintPlan(
    UUID blueprintId,
    String blueprintVersion,
    String integrityAlgorithm,
    String integrityHash,
    String dimensionId,
    ConstructionVolume constructionVolume,
    Bounds dimensions,
    BlockPosition anchor,
    Facing facing,
    List<SpecificationResolution> specificationResolutions,
    List<PaletteEntry> palette,
    MaterialManifest materials,
    List<CompactBlueprintPrimitive> primitives,
    List<MaterialIssue> materialIssues,
    WorkloadEstimate workload,
    PreviewMetadata preview,
    double confidence,
    List<BlueprintWarning> warnings
) {
    public CompactBlueprintPlan {
        Objects.requireNonNull(blueprintId, "blueprintId");
        Objects.requireNonNull(blueprintVersion, "blueprintVersion");
        Objects.requireNonNull(integrityAlgorithm, "integrityAlgorithm");
        Objects.requireNonNull(integrityHash, "integrityHash");
        Objects.requireNonNull(dimensionId, "dimensionId");
        Objects.requireNonNull(constructionVolume, "constructionVolume");
        Objects.requireNonNull(dimensions, "dimensions");
        Objects.requireNonNull(anchor, "anchor");
        Objects.requireNonNull(facing, "facing");
        Objects.requireNonNull(materials, "materials");
        Objects.requireNonNull(workload, "workload");
        Objects.requireNonNull(preview, "preview");
        if (!constructionVolume.contains(anchor)) throw new IllegalArgumentException("plan anchor must remain inside constructionVolume");
        if (!Double.isFinite(confidence) || confidence < 0.0 || confidence > 1.0) throw new IllegalArgumentException("confidence must be between 0 and 1");
        specificationResolutions = List.copyOf(specificationResolutions == null ? List.of() : specificationResolutions);
        palette = List.copyOf(palette == null ? List.of() : palette);
        primitives = List.copyOf(primitives == null ? List.of() : primitives);
        materialIssues = List.copyOf(materialIssues == null ? List.of() : materialIssues);
        warnings = List.copyOf(warnings == null ? List.of() : warnings);
        for (int i = 0; i < primitives.size(); i++) {
            if (primitives.get(i).sequence() != i) throw new IllegalArgumentException("primitive sequence must be contiguous from zero");
        }
    }

    public boolean allPrimitiveBoundsInsideConstructionVolume() {
        for (CompactBlueprintPrimitive primitive : primitives) {
            Bounds local = primitive.localBounds();
            if (!constructionVolume.contains(anchor.offset(local.min())) || !constructionVolume.contains(anchor.offset(local.max()))) return false;
        }
        return true;
    }

    public long rawPlacementUpperBound() {
        long total = 0L;
        for (CompactBlueprintPrimitive primitive : primitives) {
            long count = primitive.rawPlacementUpperBound();
            if (Long.MAX_VALUE - total < count) return Long.MAX_VALUE;
            total += count;
        }
        return total;
    }
}
