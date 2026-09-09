package io.continuityworks.api.blueprint;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.Reader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Pattern;

/**
 * Candidate source backed directly by the authoritative era-structure hero ledger.
 *
 * <p>The ledger remains project authority. This adapter does not carry a second catalog:
 * it reads the materialized catalog IDs from the supplied ledger snapshot and derives its
 * source version from the exact ledger bytes. Entries are selectable only after their
 * Stage-1 hero specification is complete, which prevents placeholder or not-yet-developed
 * catalog rows from becoming inference choices.</p>
 */
public final class EraStructureCatalogCandidateSource implements BlueprintDecisionCandidateSource {
    private static final Pattern CATALOG_ID = Pattern.compile("[A-Z][0-9]{2}-[0-9]{3}");
    private static final String HERO_SPEC_COMPLETE = "HERO_SPEC_COMPLETE";
    private static final String SOURCE_PREFIX = "cw-era-ledger-sha256:";

    private final String sourceVersion;
    private final List<String> catalogIds;

    private EraStructureCatalogCandidateSource(String sourceVersion, List<String> catalogIds) {
        this.sourceVersion = Objects.requireNonNull(sourceVersion, "sourceVersion");
        this.catalogIds = List.copyOf(catalogIds);
        if (this.catalogIds.isEmpty()) {
            throw new IllegalArgumentException("era structure ledger contains no materialized hero-spec catalog entries");
        }
    }

    /** Read an authoritative ledger snapshot from disk once and freeze its selectable IDs. */
    public static EraStructureCatalogCandidateSource fromHeroLedger(Path ledgerPath) throws IOException {
        Objects.requireNonNull(ledgerPath, "ledgerPath");
        try (BufferedReader reader = Files.newBufferedReader(ledgerPath, StandardCharsets.UTF_8)) {
            return fromHeroLedger(reader);
        }
    }

    /** Parse a supplied authoritative ledger snapshot without embedding catalog labels in API code. */
    public static EraStructureCatalogCandidateSource fromHeroLedger(Reader reader) throws IOException {
        Objects.requireNonNull(reader, "reader");
        StringBuilder text = new StringBuilder(16_384);
        char[] buffer = new char[4096];
        int read;
        while ((read = reader.read(buffer)) >= 0) {
            if (read > 0) text.append(buffer, 0, read);
        }
        String ledger = text.toString();
        return new EraStructureCatalogCandidateSource(
            SOURCE_PREFIX + sha256(ledger.getBytes(StandardCharsets.UTF_8)),
            parseMaterializedCatalogIds(ledger)
        );
    }

    /** Exact immutable IDs exposed from the parsed authoritative ledger snapshot. */
    public List<String> catalogIds() {
        return catalogIds;
    }

    /** Content-derived version used to invalidate dictionaries when the ledger changes. */
    public String sourceVersion() {
        return sourceVersion;
    }

    @Override
    public CandidateSet candidates(
        BlueprintRequest request,
        BlueprintDecisionChain.State state,
        BlueprintDecisionChain.Mutator mutator
    ) {
        Objects.requireNonNull(request, "request");
        Objects.requireNonNull(state, "state");
        Objects.requireNonNull(mutator, "mutator");
        if (!"A".equals(mutator.code())
            || mutator.valueSource() != BlueprintDecisionChain.ValueSource.STRUCTURE_CATALOG) {
            throw new IllegalArgumentException("era structure catalog source only supplies the STRUCTURE_CATALOG archetype mutator");
        }
        if (!request.requestId().equals(state.requestId())) {
            throw new IllegalArgumentException("request and decision state requestId must match");
        }
        return new CandidateSet(sourceVersion, catalogIds);
    }

    private static List<String> parseMaterializedCatalogIds(String ledger) {
        Set<String> ids = new LinkedHashSet<>();
        for (String rawLine : ledger.split("\\R")) {
            String line = rawLine.trim();
            if (!line.startsWith("|")) continue;
            if (line.endsWith("|")) line = line.substring(1, line.length() - 1);
            else line = line.substring(1);
            String[] cells = line.split("\\|", -1);
            if (cells.length < 4) continue;

            String id = cells[0].trim().toUpperCase(Locale.ROOT);
            if (!CATALOG_ID.matcher(id).matches()) continue;
            String archetype = stripMarkdown(cells[2]);
            String stageOne = stripMarkdown(cells[3]);
            if (!HERO_SPEC_COMPLETE.equals(stageOne)) continue;
            if (archetype.isEmpty() || archetype.toLowerCase(Locale.ROOT).contains("not yet materialized")) continue;
            if (!ids.add(id)) throw new IllegalArgumentException("duplicate era structure catalog ID: " + id);
        }
        return Collections.unmodifiableList(new ArrayList<>(ids));
    }

    private static String stripMarkdown(String value) {
        String normalized = value.trim();
        while (normalized.startsWith("*") && normalized.endsWith("*") && normalized.length() >= 2) {
            normalized = normalized.substring(1, normalized.length() - 1).trim();
        }
        return normalized;
    }

    private static String sha256(byte[] bytes) {
        try {
            byte[] digest = MessageDigest.getInstance("SHA-256").digest(bytes);
            StringBuilder out = new StringBuilder(digest.length * 2);
            for (byte value : digest) out.append(String.format(Locale.ROOT, "%02x", value & 0xff));
            return out.toString();
        } catch (NoSuchAlgorithmException impossible) {
            throw new IllegalStateException("SHA-256 is unavailable", impossible);
        }
    }
}
