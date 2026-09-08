package io.continuityworks.api.blueprint;

import java.util.List;
import java.util.Objects;
import java.util.UUID;

public record BlueprintProposal(
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
    List<PlacementOperation> operations,
    List<ProtectedBlockConflict> protectedBlockConflicts,
    List<MaterialIssue> materialIssues,
    WorkloadEstimate workload,
    PreviewMetadata preview,
    double confidence,
    List<BlueprintWarning> warnings
) {
    public BlueprintProposal {
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
        if (!constructionVolume.contains(anchor)) {
            throw new IllegalArgumentException("proposal anchor must remain inside constructionVolume");
        }
        if (!Double.isFinite(confidence) || confidence < 0.0 || confidence > 1.0) {
            throw new IllegalArgumentException("confidence must be between 0 and 1");
        }
        specificationResolutions = List.copyOf(specificationResolutions == null ? List.of() : specificationResolutions);
        palette = List.copyOf(palette == null ? List.of() : palette);
        operations = List.copyOf(operations == null ? List.of() : operations);
        protectedBlockConflicts = List.copyOf(protectedBlockConflicts == null ? List.of() : protectedBlockConflicts);
        materialIssues = List.copyOf(materialIssues == null ? List.of() : materialIssues);
        warnings = List.copyOf(warnings == null ? List.of() : warnings);
    }

    public boolean allOperationsInsideConstructionVolume() {
        for (PlacementOperation operation : operations) {
            if (!constructionVolume.contains(anchor.offset(operation.relativePosition()))) return false;
        }
        return true;
    }
}
