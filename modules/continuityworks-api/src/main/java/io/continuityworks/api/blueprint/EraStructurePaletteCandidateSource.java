package io.continuityworks.api.blueprint;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Stream;

/**
 * Supplies PALETTE candidates from the selected archetype's authoritative hero specification.
 *
 * <p>The source accepts only explicit profile labels inside the Material Palette Logic section.
 * Ordinary bullets and narrative prose remain descriptive authority and are never promoted into
 * inference vocabulary. Palette discovery also requires the biome decision because K is defined
 * as an archetype-and-environment-dependent mutator.</p>
 */
public final class EraStructurePaletteCandidateSource implements BlueprintDecisionCandidateSource {
    private static final String MUTATOR_CODE = "K";
    private static final Pattern SAFE_ARCHETYPE = Pattern.compile("[A-Z0-9]+(?:-[A-Z0-9]+)+");
    private static final Pattern SECTION = Pattern.compile("(?i)^##\\s+Material\\s+palette\\s+logic\\s*$");
    private static final Pattern PROFILE_HEADING = Pattern.compile("^###\\s+(.+?)\\s*$");
    private static final Pattern PROFILE_BULLET = Pattern.compile("^-\\s+\\*\\*([^*]+?)(?::)?\\*\\*(?::)?(?:\\s+.*)?$");

    private final Path heroSpecDirectory;

    public EraStructurePaletteCandidateSource(Path heroSpecDirectory) {
        this.heroSpecDirectory = Objects.requireNonNull(heroSpecDirectory, "heroSpecDirectory").toAbsolutePath().normalize();
        if (!Files.isDirectory(this.heroSpecDirectory)) {
            throw new IllegalArgumentException("hero specification directory does not exist: " + this.heroSpecDirectory);
        }
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
        if (!MUTATOR_CODE.equals(mutator.code())) {
            throw new IllegalArgumentException("hero-spec palette source only answers mutator K");
        }
        if (!request.requestId().equals(state.requestId())) {
            throw new IllegalArgumentException("request and decision state requestId must match");
        }

        String archetype = state.selection("A");
        if (archetype == null) throw new IllegalStateException("PALETTE candidates require selected archetype A");
        if (state.selection("B") == null) {
            throw new IllegalArgumentException("PALETTE candidates require selected biome B");
        }
        archetype = archetype.toUpperCase(Locale.ROOT);
        if (!SAFE_ARCHETYPE.matcher(archetype).matches()) {
            throw new IllegalArgumentException("selected archetype is not a safe catalog identifier: " + archetype);
        }

        Path specification = resolveSpecification(archetype);
        byte[] bytes;
        try {
            bytes = Files.readAllBytes(specification);
        } catch (IOException error) {
            throw new IllegalStateException("failed to read hero specification for " + archetype, error);
        }
        List<String> values = extractExplicitProfiles(new String(bytes, StandardCharsets.UTF_8));
        if (values.isEmpty()) {
            throw new IllegalStateException(
                "hero specification " + specification.getFileName()
                    + " has no explicit palette profile labels; refusing to infer candidates from prose"
            );
        }
        return new CandidateSet("cw-hero-palette-sha256:" + sha256(bytes), values);
    }

    private Path resolveSpecification(String archetype) {
        String prefix = archetype + "_";
        List<Path> matches;
        try (Stream<Path> files = Files.list(heroSpecDirectory)) {
            matches = files
                .filter(Files::isRegularFile)
                .filter(path -> {
                    String name = path.getFileName().toString();
                    return name.startsWith(prefix) && name.endsWith(".md");
                })
                .sorted()
                .toList();
        } catch (IOException error) {
            throw new IllegalStateException("failed to inspect hero specification directory", error);
        }
        if (matches.size() != 1) {
            throw new IllegalStateException(
                "expected exactly one hero specification for " + archetype + " but found " + matches.size()
            );
        }
        Path resolved = matches.get(0).toAbsolutePath().normalize();
        if (!resolved.getParent().equals(heroSpecDirectory)) {
            throw new IllegalStateException("hero specification resolved outside authoritative directory");
        }
        return resolved;
    }

    static List<String> extractExplicitProfiles(String text) {
        Objects.requireNonNull(text, "text");
        List<String> values = new ArrayList<>();
        Set<String> unique = new LinkedHashSet<>();
        boolean inSection = false;
        for (String line : text.split("\\R", -1)) {
            if (!inSection) {
                if (SECTION.matcher(line.trim()).matches()) inSection = true;
                continue;
            }
            String trimmed = line.trim();
            if (trimmed.startsWith("## ")) break;

            Matcher heading = PROFILE_HEADING.matcher(trimmed);
            Matcher bullet = PROFILE_BULLET.matcher(trimmed);
            String label = null;
            if (heading.matches()) label = heading.group(1);
            else if (bullet.matches()) label = bullet.group(1);
            if (label == null) continue;

            String canonical = canonicalProfile(label);
            if (!unique.add(canonical)) {
                throw new IllegalArgumentException("duplicate canonical palette profile: " + canonical);
            }
            values.add(canonical);
        }
        if (!inSection) throw new IllegalArgumentException("hero specification has no material palette logic section");
        return List.copyOf(values);
    }

    private static String canonicalProfile(String label) {
        String canonical = label.trim().toUpperCase(Locale.ROOT)
            .replaceAll("[^A-Z0-9]+", "_")
            .replaceAll("^_+|_+$", "");
        if (canonical.isEmpty()) throw new IllegalArgumentException("palette profile label has no canonical identifier");
        if (canonical.length() > BlueprintDecisionChain.MAX_VALUE_CHARS) {
            throw new IllegalArgumentException("palette profile identifier exceeds decision value limit: " + canonical);
        }
        return canonical;
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
