package io.continuityworks.api.blueprint;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Set;

/**
 * Strict allocation-light KEY=VALUE transport for tiny inference clients.
 * Raw block placement, commands, NBT, palettes and operation lists are forbidden.
 */
public final class BlueprintIntentCodec {
    public static final int MAX_TEXT_CHARS = 2_048;
    public static final int MAX_FIELDS = 32;
    public static final int MAX_KEY_CHARS = 48;
    public static final int MAX_VALUE_CHARS = 160;

    private static final Set<String> RESERVED = Set.of("TASK", "PURPOSE", "SITE");
    private static final Set<String> FORBIDDEN_PLACEMENT_KEYS = Set.of(
        "BLOCK", "BLOCKS", "BLOCK_STATE", "PALETTE", "PLACE", "PLACEMENT", "PLACEMENTS",
        "OPERATION", "OPERATIONS", "SETBLOCK", "FILL_COMMAND", "COMMAND", "COMMANDS", "NBT", "SNBT"
    );

    private BlueprintIntentCodec() {}

    public static BlueprintIntent parse(String text) {
        Objects.requireNonNull(text, "text");
        if (text.length() > MAX_TEXT_CHARS) {
            throw new IllegalArgumentException("Blueprint intent exceeds " + MAX_TEXT_CHARS + " characters");
        }
        rejectControlCharacters(text);

        String task = "BLUEPRINT";
        String purpose = null;
        String site = "";
        List<BlueprintSpecification> specifications = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        int fieldCount = 0;

        for (String raw : text.replace('\r', '\n').split("[\\n;]+")) {
            String line = raw.trim();
            if (line.isEmpty()) continue;
            if (++fieldCount > MAX_FIELDS) throw new IllegalArgumentException("Too many blueprint intent fields");
            int equals = line.indexOf('=');
            if (equals <= 0 || equals != line.lastIndexOf('=')) {
                throw new IllegalArgumentException("Each blueprint intent field must contain exactly one '=': " + line);
            }

            ParsedKey parsed = parseKey(line.substring(0, equals));
            String value = unquote(line.substring(equals + 1).trim());
            if (value.isEmpty()) throw new IllegalArgumentException(parsed.key() + " value must not be blank");
            if (value.length() > MAX_VALUE_CHARS) throw new IllegalArgumentException(parsed.key() + " value exceeds " + MAX_VALUE_CHARS + " characters");
            if (!seen.add(parsed.key())) throw new IllegalArgumentException("Duplicate blueprint intent field: " + parsed.key());

            if (RESERVED.contains(parsed.key())) {
                if (parsed.requirement() != BlueprintSpecification.Requirement.PREFERRED) {
                    throw new IllegalArgumentException("Requirement prefixes are not valid for " + parsed.key());
                }
                switch (parsed.key()) {
                    case "TASK" -> {
                        task = normalizeSemantic(value);
                        if (!"BLUEPRINT".equals(task)) throw new IllegalArgumentException("TASK must be BLUEPRINT");
                    }
                    case "PURPOSE" -> purpose = normalizeSemantic(value);
                    case "SITE" -> site = normalizeSemantic(value);
                    default -> throw new IllegalStateException();
                }
                continue;
            }

            if (FORBIDDEN_PLACEMENT_KEYS.contains(parsed.key())) {
                throw new IllegalArgumentException("Raw placement field is forbidden at the semantic intent boundary: " + parsed.key());
            }
            specifications.add(new BlueprintSpecification(parsed.key(), value, parsed.requirement()));
        }

        if (purpose == null || purpose.isBlank()) throw new IllegalArgumentException("PURPOSE is required for blueprint intent");
        return new BlueprintIntent(task, purpose, site, specifications);
    }

    public static String encode(BlueprintIntent intent) {
        Objects.requireNonNull(intent, "intent");
        StringBuilder out = new StringBuilder();
        out.append("TASK=BLUEPRINT\nPURPOSE=").append(intent.purpose());
        if (!intent.preferredSiteId().isBlank()) out.append("\nSITE=").append(intent.preferredSiteId());
        for (BlueprintSpecification spec : intent.specifications()) {
            out.append('\n');
            if (spec.requirement() == BlueprintSpecification.Requirement.REQUIRED) out.append("REQUIRED.");
            else if (spec.requirement() == BlueprintSpecification.Requirement.AVOID) out.append("AVOID.");
            out.append(spec.key()).append('=').append(spec.value());
        }
        if (out.length() > MAX_TEXT_CHARS) throw new IllegalArgumentException("Encoded blueprint intent exceeds transport budget");
        return out.toString();
    }

    static String normalizeKey(String value) {
        Objects.requireNonNull(value, "key");
        String normalized = value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_');
        if (normalized.isEmpty()) throw new IllegalArgumentException("Blueprint intent key must not be blank");
        if (normalized.length() > MAX_KEY_CHARS) throw new IllegalArgumentException("Blueprint intent key exceeds " + MAX_KEY_CHARS + " characters");
        for (int i = 0; i < normalized.length(); i++) {
            char c = normalized.charAt(i);
            if (!(c == '_' || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9'))) {
                throw new IllegalArgumentException("Blueprint intent key contains unsupported character: " + normalized);
            }
        }
        return normalized;
    }

    private static ParsedKey parseKey(String raw) {
        String key = raw.trim();
        BlueprintSpecification.Requirement requirement = BlueprintSpecification.Requirement.PREFERRED;
        String upper = key.toUpperCase(Locale.ROOT);
        if (upper.startsWith("REQUIRED.")) {
            requirement = BlueprintSpecification.Requirement.REQUIRED;
            key = key.substring("REQUIRED.".length());
        } else if (upper.startsWith("PREFERRED.")) {
            key = key.substring("PREFERRED.".length());
        } else if (upper.startsWith("AVOID.")) {
            requirement = BlueprintSpecification.Requirement.AVOID;
            key = key.substring("AVOID.".length());
        }
        return new ParsedKey(normalizeKey(key), requirement);
    }

    private static String normalizeSemantic(String value) {
        return value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_');
    }

    private static String unquote(String value) {
        if (value.length() >= 2) {
            char first = value.charAt(0), last = value.charAt(value.length() - 1);
            if ((first == '"' && last == '"') || (first == '\'' && last == '\'')) return value.substring(1, value.length() - 1).trim();
        }
        return value;
    }

    private static void rejectControlCharacters(String text) {
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c < 0x20 && c != '\n' && c != '\r' && c != '\t') {
                throw new IllegalArgumentException("Blueprint intent contains control characters");
            }
        }
    }

    private record ParsedKey(String key, BlueprintSpecification.Requirement requirement) {}
}
