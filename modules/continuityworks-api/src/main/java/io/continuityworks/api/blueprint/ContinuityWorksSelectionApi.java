package io.continuityworks.api.blueprint;

import java.util.Optional;
import java.util.UUID;

/** Read-only shared view of server-owned Continuity Works build-area selections. */
public interface ContinuityWorksSelectionApi {
    Optional<BuildAreaSelection> selectedArea(UUID ownerUuid);
}
