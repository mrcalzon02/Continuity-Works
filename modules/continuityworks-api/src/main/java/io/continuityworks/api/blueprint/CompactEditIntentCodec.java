package io.continuityworks.api.blueprint;

import java.util.LinkedHashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/** Strict allocation-light KEY=VALUE transport for plan-level compact edits. */
public final class CompactEditIntentCodec {
    public static final int MAX_TEXT_CHARS = 1_024;
    public static final int MAX_FIELDS = 12;
    public static final int MAX_KEY_CHARS = 32;
    public static final int MAX_VALUE_CHARS = 96;
    public static final int MAX_ABSOLUTE_DELTA = 4_096;

    private static final Set<String> FORBIDDEN_RAW_KEYS = Set.of(
        "BLOCK", "BLOCKS", "BLOCK_STATE", "BLOCKSTATE", "NBT", "SNBT", "COMMAND", "COMMANDS",
        "SETBLOCK", "FILL", "PLACEMENT", "PLACEMENTS", "OPERATION", "OPERATIONS", "PRIMITIVE", "PRIMITIVES"
    );

    private CompactEditIntentCodec() {}

    public static CompactEditIntent parse(String text) {
        Objects.requireNonNull(text, "text");
        if (text.length() > MAX_TEXT_CHARS) {
            throw new IllegalArgumentException("Compact edit intent exceeds " + MAX_TEXT_CHARS + " characters");
        }
        rejectControlCharacters(text);
        Map<String, String> fields = new LinkedHashMap<>();
        int count = 0;
        for (String raw : text.replace('\r', '\n').split("[\\n;]+")) {
            String line = raw.trim();
            if (line.isEmpty()) continue;
            if (++count > MAX_FIELDS) throw new IllegalArgumentException("Too many compact edit intent fields");
            int equals = line.indexOf('=');
            if (equals <= 0 || equals != line.lastIndexOf('=')) {
                throw new IllegalArgumentException("Each compact edit field must contain exactly one '=': " + line);
            }
            String key = normalizeKey(line.substring(0, equals));
            String value = unquote(line.substring(equals + 1).trim());
            if (value.isBlank()) throw new IllegalArgumentException(key + " value must not be blank");
            if (value.length() > MAX_VALUE_CHARS) throw new IllegalArgumentException(key + " value exceeds " + MAX_VALUE_CHARS + " characters");
            if (FORBIDDEN_RAW_KEYS.contains(key)) {
                throw new IllegalArgumentException("Raw placement/geometry field is forbidden at the compact edit boundary: " + key);
            }
            if (fields.putIfAbsent(key, value) != null) throw new IllegalArgumentException("Duplicate compact edit field: " + key);
        }

        String task = semantic(fields.getOrDefault("TASK", "EDIT"));
        if (!"EDIT".equals(task)) throw new IllegalArgumentException("TASK must be EDIT");
        String actionValue = fields.get("ACTION");
        if (actionValue == null) throw new IllegalArgumentException("ACTION is required for compact edit intent");

        CompactEditIntent.Action action;
        try {
            action = CompactEditIntent.Action.valueOf(semantic(actionValue));
        } catch (IllegalArgumentException error) {
            throw new IllegalArgumentException("Unsupported compact edit ACTION: " + actionValue, error);
        }

        return switch (action) {
            case TRANSLATE -> {
                requireOnly(fields, Set.of("TASK", "ACTION", "DX", "DY", "DZ"));
                yield CompactEditIntent.translate(new BlockPosition(
                    integer(fields, "DX", 0), integer(fields, "DY", 0), integer(fields, "DZ", 0)
                ));
            }
            case ROTATE -> {
                requireOnly(fields, Set.of("TASK", "ACTION", "TURN"));
                String turn = required(fields, "TURN").trim();
                CompactBlueprintModifier.Rotation rotation = switch (turn) {
                    case "90", "+90" -> CompactBlueprintModifier.Rotation.CLOCKWISE_90;
                    case "180", "+180", "-180" -> CompactBlueprintModifier.Rotation.CLOCKWISE_180;
                    case "270", "+270", "-90" -> CompactBlueprintModifier.Rotation.CLOCKWISE_270;
                    default -> throw new IllegalArgumentException("TURN must be 90, 180, 270, or -90 degrees");
                };
                yield CompactEditIntent.rotate(rotation);
            }
            case MIRROR -> {
                requireOnly(fields, Set.of("TASK", "ACTION", "AXIS"));
                CompactBlueprintModifier.MirrorAxis axis;
                try {
                    axis = CompactBlueprintModifier.MirrorAxis.valueOf(semantic(required(fields, "AXIS")));
                } catch (IllegalArgumentException error) {
                    throw new IllegalArgumentException("AXIS must be X or Z", error);
                }
                yield CompactEditIntent.mirror(axis);
            }
            case PALETTE_REMAP -> {
                requireOnly(fields, Set.of("TASK", "ACTION", "FROM", "TO"));
                yield CompactEditIntent.paletteRemap(identifier(required(fields, "FROM"), "FROM"), identifier(required(fields, "TO"), "TO"));
            }
            case COMPOSE -> {
                requireOnly(fields, Set.of("TASK", "ACTION", "MODULE", "OFFSET_X", "OFFSET_Y", "OFFSET_Z"));
                yield CompactEditIntent.compose(
                    identifier(required(fields, "MODULE"), "MODULE"),
                    new BlockPosition(integer(fields, "OFFSET_X", 0), integer(fields, "OFFSET_Y", 0), integer(fields, "OFFSET_Z", 0))
                );
            }
            case REPEAT -> {
                requireOnly(fields, Set.of(
                    "TASK", "ACTION", "MODULE", "COUNT", "FIRST_X", "FIRST_Y", "FIRST_Z", "STEP_X", "STEP_Y", "STEP_Z"
                ));
                int repeatCount = integerRequired(fields, "COUNT", 1, CompactBlueprintModifier.MAX_REPEAT_COPIES);
                yield CompactEditIntent.repeat(
                    identifier(required(fields, "MODULE"), "MODULE"),
                    repeatCount,
                    new BlockPosition(integer(fields, "FIRST_X", 0), integer(fields, "FIRST_Y", 0), integer(fields, "FIRST_Z", 0)),
                    new BlockPosition(integer(fields, "STEP_X", 0), integer(fields, "STEP_Y", 0), integer(fields, "STEP_Z", 0))
                );
            }
        };
    }

    public static String encode(CompactEditIntent intent) {
        Objects.requireNonNull(intent, "intent");
        StringBuilder out = new StringBuilder(160);
        out.append("TASK=EDIT\nACTION=").append(intent.action());
        switch (intent.action()) {
            case TRANSLATE -> vector(out, "D", intent.offset());
            case ROTATE -> out.append("\nTURN=").append(switch (intent.rotation()) {
                case CLOCKWISE_90 -> 90;
                case CLOCKWISE_180 -> 180;
                case CLOCKWISE_270 -> 270;
                case NONE -> throw new IllegalArgumentException("ROTATE intent cannot encode NONE");
            });
            case MIRROR -> out.append("\nAXIS=").append(intent.mirrorAxis());
            case PALETTE_REMAP -> out.append("\nFROM=").append(intent.fromPaletteKey()).append("\nTO=").append(intent.toPaletteKey());
            case COMPOSE -> {
                out.append("\nMODULE=").append(intent.moduleId());
                vector(out, "OFFSET_", intent.offset());
            }
            case REPEAT -> {
                out.append("\nMODULE=").append(intent.moduleId()).append("\nCOUNT=").append(intent.repeatCount());
                vector(out, "FIRST_", intent.offset());
                vector(out, "STEP_", intent.step());
            }
        }
        if (out.length() > MAX_TEXT_CHARS) throw new IllegalArgumentException("Encoded compact edit intent exceeds transport budget");
        return out.toString();
    }

    private static void vector(StringBuilder out, String prefix, BlockPosition vector) {
        if ("D".equals(prefix)) {
            out.append("\nDX=").append(vector.x()).append("\nDY=").append(vector.y()).append("\nDZ=").append(vector.z());
        } else {
            out.append('\n').append(prefix).append("X=").append(vector.x())
                .append('\n').append(prefix).append("Y=").append(vector.y())
                .append('\n').append(prefix).append("Z=").append(vector.z());
        }
    }

    private static int integer(Map<String, String> fields, String key, int fallback) {
        String value = fields.get(key);
        if (value == null) return fallback;
        return boundedInteger(value, key, -MAX_ABSOLUTE_DELTA, MAX_ABSOLUTE_DELTA);
    }

    private static int integerRequired(Map<String, String> fields, String key, int min, int max) {
        return boundedInteger(required(fields, key), key, min, max);
    }

    private static int boundedInteger(String value, String key, int min, int max) {
        final int parsed;
        try {
            parsed = Integer.parseInt(value.trim());
        } catch (NumberFormatException error) {
            throw new IllegalArgumentException(key + " must be an integer", error);
        }
        if (parsed < min || parsed > max) throw new IllegalArgumentException(key + " must be between " + min + " and " + max);
        return parsed;
    }

    private static String required(Map<String, String> fields, String key) {
        String value = fields.get(key);
        if (value == null) throw new IllegalArgumentException(key + " is required for this compact edit action");
        return value;
    }

    private static void requireOnly(Map<String, String> fields, Set<String> allowed) {
        for (String key : fields.keySet()) {
            if (!allowed.contains(key)) throw new IllegalArgumentException("Field " + key + " is not valid for ACTION=" + fields.get("ACTION"));
        }
    }

    private static String identifier(String value, String label) {
        String trimmed = value.trim();
        if (trimmed.isEmpty()) throw new IllegalArgumentException(label + " must not be blank");
        if (trimmed.length() > MAX_VALUE_CHARS) throw new IllegalArgumentException(label + " identifier is too long");
        for (int i = 0; i < trimmed.length(); i++) {
            char c = trimmed.charAt(i);
            if (!(Character.isLetterOrDigit(c) || c == '_' || c == '-' || c == '.' || c == ':' || c == '/')) {
                throw new IllegalArgumentException(label + " contains unsupported identifier character");
            }
        }
        return trimmed;
    }

    private static String normalizeKey(String value) {
        String normalized = value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_');
        if (normalized.isEmpty()) throw new IllegalArgumentException("Compact edit key must not be blank");
        if (normalized.length() > MAX_KEY_CHARS) throw new IllegalArgumentException("Compact edit key is too long");
        for (int i = 0; i < normalized.length(); i++) {
            char c = normalized.charAt(i);
            if (!(c == '_' || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9'))) {
                throw new IllegalArgumentException("Compact edit key contains unsupported character: " + normalized);
            }
        }
        return normalized;
    }

    private static String semantic(String value) {
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
                throw new IllegalArgumentException("Compact edit intent contains control characters");
            }
        }
    }
}
