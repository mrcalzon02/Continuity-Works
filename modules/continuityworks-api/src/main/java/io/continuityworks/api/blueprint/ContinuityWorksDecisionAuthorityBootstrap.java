package io.continuityworks.api.blueprint;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.Objects;
import java.util.concurrent.Executor;

/**
 * Production composition helpers for the Continuity Works decision authority.
 *
 * <p>This class owns wiring only. The supplied hero ledger and sibling hero specifications
 * remain authoritative, their candidate-source adapters own extraction, and
 * {@link ContinuityWorksDecisionAuthorityHttpServer} remains the transport. No decision,
 * candidate, validation, or generation semantics are duplicated here.</p>
 */
public final class ContinuityWorksDecisionAuthorityBootstrap {
    private ContinuityWorksDecisionAuthorityBootstrap() {}

    /**
     * Construct the normal HTTP authority with STRUCTURE_CATALOG candidates sourced from
     * the supplied hero ledger and BIOME/CULTURE/CONDITION/PALETTE candidates sourced from the selected sibling hero spec.
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
            productionCandidateSource(heroLedger),
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
            productionCandidateSource(heroLedger),
            address,
            maxBodyBytes,
            executor
        );
    }

    /** Build the transport-neutral production candidate routing from the existing hero authority. */
    public static BlueprintDecisionCandidateSource productionCandidateSource(Path heroLedger) throws IOException {
        Objects.requireNonNull(heroLedger, "heroLedger");
        Path absoluteLedger = heroLedger.toAbsolutePath().normalize();
        Path heroDirectory = absoluteLedger.getParent();
        if (heroDirectory == null) throw new IllegalArgumentException("hero ledger must have a parent directory");
        LinkedHashMap<String, BlueprintDecisionCandidateSource> routes = new LinkedHashMap<>();
        routes.put("A", EraStructureCatalogCandidateSource.fromHeroLedger(absoluteLedger));
        routes.put("B", new EraStructureBiomeCandidateSource(heroDirectory));
        routes.put("C", new EraStructureCultureCandidateSource(heroDirectory));
        routes.put("Q", new EraStructureConditionCandidateSource(heroDirectory));
        routes.put("K", new EraStructurePaletteCandidateSource(heroDirectory));
        return new RoutingBlueprintDecisionCandidateSource(routes);
    }
}
