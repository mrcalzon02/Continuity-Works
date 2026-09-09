package io.continuityworks.api.blueprint;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.file.Path;
import java.util.Objects;
import java.util.concurrent.Executor;

/**
 * Production composition helpers for the Continuity Works decision authority.
 *
 * <p>This class owns wiring only. The supplied hero ledger remains the structure-catalog
 * authority, {@link EraStructureCatalogCandidateSource} owns catalog extraction, and
 * {@link ContinuityWorksDecisionAuthorityHttpServer} remains the transport. No decision,
 * candidate, validation, or generation semantics are duplicated here.</p>
 */
public final class ContinuityWorksDecisionAuthorityBootstrap {
    private ContinuityWorksDecisionAuthorityBootstrap() {}

    /**
     * Construct the normal HTTP authority with STRUCTURE_CATALOG candidates sourced from
     * the supplied authoritative era-structure hero ledger snapshot.
     */
    public static ContinuityWorksDecisionAuthorityHttpServer fromEraStructureHeroLedger(
        ContinuityWorksCompactBlueprintApi api,
        Path heroLedger,
        InetSocketAddress address
    ) throws IOException {
        Objects.requireNonNull(api, "api");
        Objects.requireNonNull(heroLedger, "heroLedger");
        Objects.requireNonNull(address, "address");
        return new ContinuityWorksDecisionAuthorityHttpServer(
            api,
            EraStructureCatalogCandidateSource.fromHeroLedger(heroLedger),
            address
        );
    }

    /**
     * Same production wiring with explicit transport bounds/executor for an embedding host.
     * The adapter is still the sole decision-authority seam.
     */
    public static ContinuityWorksDecisionAuthorityHttpServer fromEraStructureHeroLedger(
        ContinuityWorksDecisionAuthorityAdapter authority,
        Path heroLedger,
        InetSocketAddress address,
        int maxBodyBytes,
        Executor executor
    ) throws IOException {
        Objects.requireNonNull(authority, "authority");
        Objects.requireNonNull(heroLedger, "heroLedger");
        Objects.requireNonNull(address, "address");
        return new ContinuityWorksDecisionAuthorityHttpServer(
            authority,
            EraStructureCatalogCandidateSource.fromHeroLedger(heroLedger),
            address,
            maxBodyBytes,
            executor
        );
    }
}
