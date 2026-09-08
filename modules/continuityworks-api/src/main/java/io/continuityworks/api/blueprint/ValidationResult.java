package io.continuityworks.api.blueprint;

import java.util.List;
import java.util.UUID;

public record ValidationResult(
    UUID blueprintId,
    UUID validationId,
    Status status,
    List<ProtectedBlockConflict> protectedBlockConflicts,
    List<MaterialIssue> materialIssues,
    List<BlueprintWarning> warnings
) {
    public enum Status { VALID, INVALID, STALE_CONTEXT }

    public ValidationResult {
        if (blueprintId == null) throw new NullPointerException("blueprintId");
        if (validationId == null) throw new NullPointerException("validationId");
        if (status == null) throw new NullPointerException("status");
        protectedBlockConflicts = List.copyOf(protectedBlockConflicts == null ? List.of() : protectedBlockConflicts);
        materialIssues = List.copyOf(materialIssues == null ? List.of() : materialIssues);
        warnings = List.copyOf(warnings == null ? List.of() : warnings);
    }

    public boolean validForPreview() {
        return status == Status.VALID;
    }
}
