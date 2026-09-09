package io.continuityworks.api.blueprint;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;

/**
 * Deterministic state machine for very small inference controllers.
 *
 * <p>The inference layer selects compact semantic mutations. Continuity Works owns
 * the vocabulary contract, dependency graph, validation, geometry and materialization.
 * Raw blocks, NBT, commands and primitive geometry are intentionally not representable
 * at this boundary.</p>
 */
public final class BlueprintDecisionChain {
    public static final String PROTOCOL_VERSION = "cw-decision-1";
    public static final String REFERENCE_INFERENCE_PROFILE = "Qwen 2.5 Instruct Q4-class";
    public static final int MAX_OUTPUT_TOKENS = 64;
    public static final int RECOMMENDED_OUTPUT_TOKENS = 32;
    public static final int MAX_MUTATIONS_PER_INFERENCE = 4;
    public static final int MAX_WIRE_CHARS = 256;
    public static final int MAX_VALUE_CHARS = 64;

    public enum ValueSource {
        FIXED,
        STRUCTURE_CATALOG,
        ARCHETYPE_PROFILE
    }

    /** One compact mutation slot exposed to the inference controller. */
    public record Mutator(
        String code,
        String specificationKey,
        ValueSource valueSource,
        List<String> fixedValues,
        List<String> dependsOn,
        boolean required,
        String description
    ) {
        public Mutator {
            code = normalizeCode(code);
            if (code.length() != 1) throw new IllegalArgumentException("decision mutator code must be one character");
            specificationKey = normalizeSemantic(specificationKey);
            Objects.requireNonNull(valueSource, "valueSource");
            fixedValues = List.copyOf(fixedValues == null ? List.of() : fixedValues);
            dependsOn = List.copyOf(dependsOn == null ? List.of() : dependsOn);
            description = description == null ? "" : description;
            if (valueSource == ValueSource.FIXED && fixedValues.isEmpty()) {
                throw new IllegalArgumentException("fixed decision mutator must expose legal values");
            }
        }
    }

    /** Discoverable contract for tiny local inference engines. */
    public record Profile(
        String protocolVersion,
        String referenceInferenceProfile,
        int maxOutputTokens,
        int recommendedOutputTokens,
        int maxMutationsPerInference,
        boolean stateCarriedAcrossInferences,
        boolean deterministicValidation,
        boolean deterministicFinalization,
        List<String> principles,
        List<Mutator> mutators
    ) {
        public Profile {
            principles = List.copyOf(principles == null ? List.of() : principles);
            mutators = List.copyOf(mutators == null ? List.of() : mutators);
        }
    }

    /** Rich deterministic state is carried outside the model's token budget. */
    public record State(
        UUID requestId,
        long revision,
        Map<String, String> selections,
        boolean finalized
    ) {
        public State {
            Objects.requireNonNull(requestId, "requestId");
            if (revision < 0) throw new IllegalArgumentException("revision must be non-negative");
            LinkedHashMap<String, String> copy = new LinkedHashMap<>();
            if (selections != null) {
                for (Map.Entry<String, String> entry : selections.entrySet()) {
                    copy.put(normalizeCode(entry.getKey()), normalizeValue(entry.getValue()));
                }
            }
            selections = Collections.unmodifiableMap(copy);
        }

        public String selection(String code) {
            return selections.get(normalizeCode(code));
        }
    }

    public record Validation(
        boolean valid,
        boolean readyToFinalize,
        List<String> missingRequired,
        List<String> findings
    ) {
        public Validation {
            missingRequired = List.copyOf(missingRequired == null ? List.of() : missingRequired);
            findings = List.copyOf(findings == null ? List.of() : findings);
        }
    }

    /** The API can expose only these next legal semantic questions to the tiny model. */
    public record Step(
        State state,
        List<Mutator> nextMutators,
        Validation validation,
        String compactPrompt
    ) {
        public Step {
            Objects.requireNonNull(state, "state");
            nextMutators = List.copyOf(nextMutators == null ? List.of() : nextMutators);
            Objects.requireNonNull(validation, "validation");
            compactPrompt = compactPrompt == null ? "" : compactPrompt;
        }
    }

    /** Final semantic selections; generation remains owned by Continuity Works. */
    public record FinalizedDecision(
        State state,
        List<BlueprintSpecification> specifications
    ) {
        public FinalizedDecision {
            Objects.requireNonNull(state, "state");
            specifications = List.copyOf(specifications == null ? List.of() : specifications);
            if (!state.finalized()) throw new IllegalArgumentException("finalized decision must carry finalized state");
        }
    }

    private static final Set<String> FORBIDDEN_RAW_KEYS = Set.of(
        "BLOCK", "BLOCKS", "BLOCK_STATE", "BLOCKSTATE", "NBT", "SNBT", "COMMAND", "COMMANDS",
        "SETBLOCK", "FILL", "PLACEMENT", "PLACEMENTS", "OPERATION", "OPERATIONS", "PRIMITIVE", "PRIMITIVES"
    );

    private static final List<Mutator> ORDERED_MUTATORS = List.of(
        new Mutator("A", "ARCHETYPE", ValueSource.STRUCTURE_CATALOG, List.of(), List.of(), true,
            "Select one authoritative Continuity Works structure archetype/catalog ID."),
        new Mutator("Z", "SCALE", ValueSource.FIXED, List.of("S", "M", "L"), List.of("A"), true,
            "Select small, medium or large scale class."),
        new Mutator("B", "BIOME", ValueSource.ARCHETYPE_PROFILE, List.of(), List.of("A"), true,
            "Select one biome/environment adaptation exposed by the chosen archetype."),
        new Mutator("C", "CULTURE", ValueSource.ARCHETYPE_PROFILE, List.of(), List.of("A"), false,
            "Select one culture-variant hook exposed by the chosen archetype."),
        new Mutator("F", "FAMILY_MODE", ValueSource.FIXED, List.of("I", "P"), List.of("A"), true,
            "Select independent placement or explicit same-parent compatible-family composition."),
        new Mutator("O", "ORIENTATION", ValueSource.FIXED, List.of("AUTO", "N", "E", "S", "W"), List.of("B"), false,
            "Select automatic or cardinal orientation without emitting geometry."),
        new Mutator("Q", "CONDITION", ValueSource.ARCHETYPE_PROFILE, List.of(), List.of("A"), false,
            "Select an intact/active, damaged, abandoned, ruined or repurposed archetype condition."),
        new Mutator("K", "PALETTE", ValueSource.ARCHETYPE_PROFILE, List.of(), List.of("A", "B"), false,
            "Select one legal material/palette profile exposed after archetype and environment resolution."),
        new Mutator("D", "DETAIL", ValueSource.FIXED, List.of("L", "N", "H"), List.of("A", "Z"), false,
            "Select low, normal or high detail density; geometry remains deterministic.")
    );

    private static final Map<String, Mutator> MUTATORS = indexMutators();
    private static final Profile PROFILE = new Profile(
        PROTOCOL_VERSION,
        REFERENCE_INFERENCE_PROFILE,
        MAX_OUTPUT_TOKENS,
        RECOMMENDED_OUTPUT_TOKENS,
        MAX_MUTATIONS_PER_INFERENCE,
        true,
        true,
        true,
        List.of(
            "inference_selects",
            "state_accumulates",
            "mutators_invalidate_dependent_choices",
            "catalog_defines",
            "generator_builds",
            "validator_decides_legality",
            "raw_world_mutation_is_forbidden"
        ),
        ORDERED_MUTATORS
    );

    private BlueprintDecisionChain() {}

    public static Profile profile() {
        return PROFILE;
    }

    public static State begin(BlueprintRequest request) {
        Objects.requireNonNull(request, "request");
        return new State(request.requestId(), 0, Map.of(), false);
    }

    public static Step next(State state) {
        Objects.requireNonNull(state, "state");
        Validation validation = validate(state);
        if (state.finalized()) return new Step(state, List.of(), validation, "FINAL");

        List<Mutator> available = new ArrayList<>();
        for (Mutator mutator : ORDERED_MUTATORS) {
            if (state.selections().containsKey(mutator.code())) continue;
            if (dependenciesSatisfied(mutator, state.selections())) available.add(mutator);
        }
        return new Step(state, available, validation, compactPrompt(available, validation.readyToFinalize()));
    }

    /**
     * Apply one compact inference response. One response may contain up to four semantic
     * KEY=VALUE mutations separated by semicolons/newlines, but a one-mutation chain is preferred.
     */
    public static State apply(State state, String encodedMutations) {
        Objects.requireNonNull(state, "state");
        Objects.requireNonNull(encodedMutations, "encodedMutations");
        if (state.finalized()) throw new IllegalStateException("decision state is already finalized");
        if (encodedMutations.length() > MAX_WIRE_CHARS) {
            throw new IllegalArgumentException("decision mutation exceeds " + MAX_WIRE_CHARS + " characters");
        }
        rejectControlCharacters(encodedMutations);

        LinkedHashMap<String, String> selections = new LinkedHashMap<>(state.selections());
        int count = 0;
        Set<String> seenThisInference = new LinkedHashSet<>();
        for (String raw : encodedMutations.replace('\r', '\n').split("[\\n;]+")) {
            String field = raw.trim();
            if (field.isEmpty()) continue;
            if (++count > MAX_MUTATIONS_PER_INFERENCE) {
                throw new IllegalArgumentException("too many decision mutations in one inference");
            }
            int equals = field.indexOf('=');
            if (equals <= 0 || equals != field.lastIndexOf('=')) {
                throw new IllegalArgumentException("each decision mutation must contain exactly one '='");
            }
            String code = normalizeCode(field.substring(0, equals));
            if (FORBIDDEN_RAW_KEYS.contains(code)) {
                throw new IllegalArgumentException("raw world mutation field is forbidden: " + code);
            }
            Mutator mutator = MUTATORS.get(code);
            if (mutator == null) throw new IllegalArgumentException("unknown decision mutator: " + code);
            if (!seenThisInference.add(code)) throw new IllegalArgumentException("duplicate decision mutator: " + code);
            if (!dependenciesSatisfied(mutator, selections)) {
                throw new IllegalArgumentException("decision mutator " + code + " requires " + mutator.dependsOn());
            }

            String value = normalizeValue(field.substring(equals + 1));
            if (mutator.valueSource() == ValueSource.FIXED) value = value.toUpperCase(Locale.ROOT);
            validateValue(mutator, value);
            String previous = selections.get(code);
            if (previous != null && !previous.equals(value)) invalidateDependents(code, selections);
            selections.put(code, value);
        }
        if (count == 0) throw new IllegalArgumentException("decision mutation response is empty");
        return new State(state.requestId(), state.revision() + 1, selections, false);
    }

    public static Validation validate(State state) {
        Objects.requireNonNull(state, "state");
        List<String> missing = new ArrayList<>();
        List<String> findings = new ArrayList<>();
        for (Map.Entry<String, String> entry : state.selections().entrySet()) {
            Mutator mutator = MUTATORS.get(entry.getKey());
            if (mutator == null) {
                findings.add("UNKNOWN_MUTATOR:" + entry.getKey());
                continue;
            }
            try {
                validateValue(mutator, mutator.valueSource() == ValueSource.FIXED
                    ? entry.getValue().toUpperCase(Locale.ROOT)
                    : entry.getValue());
            } catch (IllegalArgumentException error) {
                findings.add("INVALID_VALUE:" + mutator.code());
            }
        }
        for (Mutator mutator : ORDERED_MUTATORS) {
            String value = state.selections().get(mutator.code());
            if (mutator.required() && value == null) missing.add(mutator.code());
            if (value != null && !dependenciesSatisfied(mutator, state.selections())) {
                findings.add("DEPENDENCY_UNSATISFIED:" + mutator.code());
            }
        }
        if (state.finalized() && !missing.isEmpty()) findings.add("FINALIZED_WITH_MISSING_REQUIRED");
        boolean valid = findings.isEmpty();
        return new Validation(valid, valid && missing.isEmpty(), missing, findings);
    }

    public static FinalizedDecision finalizeDecision(State state) {
        Validation validation = validate(state);
        if (!validation.readyToFinalize()) {
            throw new IllegalStateException("decision state is not ready to finalize; missing=" + validation.missingRequired());
        }
        State finalized = new State(state.requestId(), state.revision() + 1, state.selections(), true);
        List<BlueprintSpecification> specifications = new ArrayList<>();
        for (Mutator mutator : ORDERED_MUTATORS) {
            String value = finalized.selections().get(mutator.code());
            if (value == null) continue;
            BlueprintSpecification.Requirement requirement = mutator.required()
                ? BlueprintSpecification.Requirement.REQUIRED
                : BlueprintSpecification.Requirement.PREFERRED;
            specifications.add(new BlueprintSpecification(mutator.specificationKey(), value, requirement));
        }
        return new FinalizedDecision(finalized, specifications);
    }

    private static Map<String, Mutator> indexMutators() {
        LinkedHashMap<String, Mutator> index = new LinkedHashMap<>();
        for (Mutator mutator : ORDERED_MUTATORS) {
            if (index.put(mutator.code(), mutator) != null) {
                throw new IllegalStateException("duplicate decision mutator code " + mutator.code());
            }
        }
        return Collections.unmodifiableMap(index);
    }

    private static boolean dependenciesSatisfied(Mutator mutator, Map<String, String> selections) {
        return selections.keySet().containsAll(mutator.dependsOn());
    }

    private static void invalidateDependents(String changedCode, LinkedHashMap<String, String> selections) {
        Set<String> invalid = new LinkedHashSet<>();
        invalid.add(changedCode);
        boolean changed;
        do {
            changed = false;
            for (Mutator mutator : ORDERED_MUTATORS) {
                if (invalid.contains(mutator.code())) continue;
                for (String dependency : mutator.dependsOn()) {
                    if (invalid.contains(dependency)) {
                        invalid.add(mutator.code());
                        changed = true;
                        break;
                    }
                }
            }
        } while (changed);
        invalid.remove(changedCode);
        for (String code : invalid) selections.remove(code);
    }

    private static void validateValue(Mutator mutator, String value) {
        if (value.length() > MAX_VALUE_CHARS) {
            throw new IllegalArgumentException(mutator.code() + " value exceeds " + MAX_VALUE_CHARS + " characters");
        }
        if (mutator.valueSource() == ValueSource.FIXED && !mutator.fixedValues().contains(value)) {
            throw new IllegalArgumentException(mutator.code() + " must be one of " + mutator.fixedValues());
        }
        for (int i = 0; i < value.length(); i++) {
            char c = value.charAt(i);
            if (!(Character.isLetterOrDigit(c) || c == '_' || c == '-' || c == '.' || c == ':' || c == '/')) {
                throw new IllegalArgumentException(mutator.code() + " contains unsupported identifier character");
            }
        }
    }

    private static String compactPrompt(List<Mutator> available, boolean canFinalize) {
        StringBuilder out = new StringBuilder(96);
        for (Mutator mutator : available) {
            if (out.length() > 0) out.append(' ');
            out.append(mutator.code()).append('=');
            if (mutator.valueSource() == ValueSource.FIXED) out.append(String.join("|", mutator.fixedValues()));
            else if (mutator.valueSource() == ValueSource.STRUCTURE_CATALOG) out.append("<CAT>");
            else out.append("<A>");
        }
        if (canFinalize) {
            if (out.length() > 0) out.append(' ');
            out.append("FINAL?");
        }
        return out.toString();
    }

    private static String normalizeCode(String value) {
        Objects.requireNonNull(value, "code");
        String normalized = value.trim().toUpperCase(Locale.ROOT);
        if (normalized.isEmpty()) throw new IllegalArgumentException("decision mutator code must not be blank");
        return normalized;
    }

    private static String normalizeSemantic(String value) {
        Objects.requireNonNull(value, "semantic value");
        String normalized = value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_');
        if (normalized.isEmpty()) throw new IllegalArgumentException("semantic value must not be blank");
        return normalized;
    }

    private static String normalizeValue(String value) {
        Objects.requireNonNull(value, "value");
        String normalized = value.trim();
        if (normalized.isEmpty()) throw new IllegalArgumentException("decision mutation value must not be blank");
        return normalized;
    }

    private static void rejectControlCharacters(String text) {
        for (int i = 0; i < text.length(); i++) {
            char c = text.charAt(i);
            if (c < 0x20 && c != '\n' && c != '\r' && c != '\t') {
                throw new IllegalArgumentException("decision mutation contains control characters");
            }
        }
    }
}
