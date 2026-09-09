package io.continuityworks.api.blueprint;

import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.UUID;

/**
 * Builds compact, versioned and state-bound candidate dictionaries for tiny inference controllers.
 *
 * <p>Local choice codes are ephemeral compression aids. They are resolved back to the authoritative
 * semantic value before the existing decision chain applies the mutation, so dictionary indices can
 * never leak into finalized BlueprintSpecifications.</p>
 */
public final class BlueprintDecisionCandidates {
    public static final int MAX_CHOICES = 256;
    private static final String FIXED_SOURCE_VERSION = "cw-fixed-1";

    public record Choice(String localCode, String semanticValue) {
        public Choice {
            localCode = requireNonBlank(localCode, "localCode");
            semanticValue = requireNonBlank(semanticValue, "semanticValue");
        }
    }

    /** Immutable candidate set tied to one request, revision, mutator and source snapshot. */
    public record Dictionary(
        String protocolVersion,
        UUID requestId,
        long revision,
        String mutatorCode,
        String sourceVersion,
        String dictionaryId,
        List<Choice> choices
    ) {
        public Dictionary {
            protocolVersion = requireNonBlank(protocolVersion, "protocolVersion");
            Objects.requireNonNull(requestId, "requestId");
            if (revision < 0) throw new IllegalArgumentException("revision must be non-negative");
            mutatorCode = normalizeCode(mutatorCode);
            sourceVersion = requireNonBlank(sourceVersion, "sourceVersion");
            dictionaryId = requireNonBlank(dictionaryId, "dictionaryId").toLowerCase(Locale.ROOT);
            choices = List.copyOf(choices == null ? List.of() : choices);
            if (choices.isEmpty()) throw new IllegalArgumentException("candidate dictionary must contain at least one choice");
            if (choices.size() > MAX_CHOICES) throw new IllegalArgumentException("candidate dictionary exceeds " + MAX_CHOICES + " choices");
            String expected = fingerprint(protocolVersion, requestId, revision, mutatorCode, sourceVersion, choices);
            if (!expected.equals(dictionaryId)) throw new IllegalArgumentException("candidate dictionary integrity mismatch");
        }
    }

    private BlueprintDecisionCandidates() {}

    public static Dictionary create(
        BlueprintRequest request,
        BlueprintDecisionChain.State state,
        String mutatorCode,
        BlueprintDecisionCandidateSource source
    ) {
        Objects.requireNonNull(request, "request");
        Objects.requireNonNull(state, "state");
        if (!request.requestId().equals(state.requestId())) {
            throw new IllegalArgumentException("request and decision state requestId must match");
        }
        if (state.finalized()) throw new IllegalStateException("decision state is already finalized");

        BlueprintDecisionChain.Mutator mutator = availableMutator(state, mutatorCode);
        String sourceVersion;
        List<String> semanticValues;
        if (mutator.valueSource() == BlueprintDecisionChain.ValueSource.FIXED) {
            sourceVersion = FIXED_SOURCE_VERSION;
            semanticValues = mutator.fixedValues();
        } else {
            if (source == null) {
                throw new IllegalArgumentException("dynamic decision mutator " + mutator.code() + " requires an authoritative candidate source");
            }
            BlueprintDecisionCandidateSource.CandidateSet supplied = Objects.requireNonNull(
                source.candidates(request, state, mutator), "candidate source result");
            sourceVersion = supplied.sourceVersion();
            semanticValues = supplied.values();
        }

        if (semanticValues.isEmpty()) throw new IllegalStateException("candidate source returned no legal choices for " + mutator.code());
        if (semanticValues.size() > MAX_CHOICES) {
            throw new IllegalArgumentException("candidate source exceeds " + MAX_CHOICES + " choices for " + mutator.code());
        }

        List<Choice> choices = new ArrayList<>(semanticValues.size());
        for (int i = 0; i < semanticValues.size(); i++) {
            String semanticValue = semanticValues.get(i);
            // Dry-run through the authoritative mutation parser so candidate providers cannot widen wire legality.
            BlueprintDecisionChain.apply(state, mutator.code() + "=" + semanticValue);
            choices.add(new Choice(Integer.toString(i, 36).toUpperCase(Locale.ROOT), semanticValue));
        }
        List<Choice> frozen = List.copyOf(choices);
        String id = fingerprint(
            BlueprintDecisionChain.PROTOCOL_VERSION,
            state.requestId(),
            state.revision(),
            mutator.code(),
            sourceVersion,
            frozen
        );
        return new Dictionary(
            BlueprintDecisionChain.PROTOCOL_VERSION,
            state.requestId(),
            state.revision(),
            mutator.code(),
            sourceVersion,
            id,
            frozen
        );
    }

    /** Resolve one compact code and apply the authoritative semantic mutation to the exact bound revision. */
    public static BlueprintDecisionChain.State apply(
        BlueprintDecisionChain.State state,
        Dictionary dictionary,
        String localChoiceCode
    ) {
        Objects.requireNonNull(state, "state");
        Objects.requireNonNull(dictionary, "dictionary");
        if (state.finalized()) throw new IllegalStateException("decision state is already finalized");
        if (!BlueprintDecisionChain.PROTOCOL_VERSION.equals(dictionary.protocolVersion())) {
            throw new IllegalStateException("candidate dictionary protocol is stale or incompatible");
        }
        if (!state.requestId().equals(dictionary.requestId())) {
            throw new IllegalStateException("candidate dictionary belongs to a different request");
        }
        if (state.revision() != dictionary.revision()) {
            throw new IllegalStateException("candidate dictionary is stale for decision revision " + state.revision());
        }
        // Reconstructing the record verifies the deterministic fingerprint even if data arrived over a transport.
        new Dictionary(
            dictionary.protocolVersion(), dictionary.requestId(), dictionary.revision(), dictionary.mutatorCode(),
            dictionary.sourceVersion(), dictionary.dictionaryId(), dictionary.choices());
        BlueprintDecisionChain.Mutator mutator = availableMutator(state, dictionary.mutatorCode());

        String code = normalizeLocalCode(localChoiceCode);
        Choice selected = null;
        for (Choice choice : dictionary.choices()) {
            if (choice.localCode().equals(code)) {
                selected = choice;
                break;
            }
        }
        if (selected == null) throw new IllegalArgumentException("unknown candidate local code: " + code);
        return BlueprintDecisionChain.apply(state, mutator.code() + "=" + selected.semanticValue());
    }

    private static BlueprintDecisionChain.Mutator availableMutator(
        BlueprintDecisionChain.State state,
        String mutatorCode
    ) {
        String code = normalizeCode(mutatorCode);
        for (BlueprintDecisionChain.Mutator mutator : BlueprintDecisionChain.profile().mutators()) {
            if (!mutator.code().equals(code)) continue;
            boolean dependenciesSatisfied = state.selections().keySet().containsAll(mutator.dependsOn());
            if (!dependenciesSatisfied) {
                throw new IllegalStateException("decision mutator " + code + " dependencies are not satisfied");
            }
            if (state.selection(code) != null) return mutator; // allow a state-bound correction dictionary
            boolean currentlyNext = BlueprintDecisionChain.next(state).nextMutators().stream()
                .anyMatch(candidate -> candidate.code().equals(code));
            if (!currentlyNext) throw new IllegalStateException("decision mutator " + code + " is not currently selectable");
            return mutator;
        }
        throw new IllegalArgumentException("unknown decision mutator: " + code);
    }

    private static String fingerprint(
        String protocolVersion,
        UUID requestId,
        long revision,
        String mutatorCode,
        String sourceVersion,
        List<Choice> choices
    ) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            digestField(digest, protocolVersion);
            digestField(digest, requestId.toString());
            digestField(digest, Long.toString(revision));
            digestField(digest, mutatorCode);
            digestField(digest, sourceVersion);
            digestField(digest, Integer.toString(choices.size()));
            for (Choice choice : choices) {
                digestField(digest, choice.localCode());
                digestField(digest, choice.semanticValue());
            }
            return toHex(digest.digest());
        } catch (NoSuchAlgorithmException impossible) {
            throw new IllegalStateException("SHA-256 is unavailable", impossible);
        }
    }

    private static void digestField(MessageDigest digest, String field) {
        byte[] bytes = field.getBytes(StandardCharsets.UTF_8);
        digest.update(ByteBuffer.allocate(Integer.BYTES).putInt(bytes.length).array());
        digest.update(bytes);
    }

    private static String toHex(byte[] bytes) {
        StringBuilder out = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) out.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        return out.toString();
    }

    private static String normalizeCode(String value) {
        return requireNonBlank(value, "mutatorCode").toUpperCase(Locale.ROOT);
    }

    private static String normalizeLocalCode(String value) {
        String code = requireNonBlank(value, "localChoiceCode").toUpperCase(Locale.ROOT);
        for (int i = 0; i < code.length(); i++) {
            char c = code.charAt(i);
            if (!(c >= '0' && c <= '9') && !(c >= 'A' && c <= 'Z')) {
                throw new IllegalArgumentException("candidate local code contains unsupported characters");
            }
        }
        return code;
    }

    private static String requireNonBlank(String value, String name) {
        Objects.requireNonNull(value, name);
        String normalized = value.trim();
        if (normalized.isEmpty()) throw new IllegalArgumentException(name + " must not be blank");
        return normalized;
    }
}
