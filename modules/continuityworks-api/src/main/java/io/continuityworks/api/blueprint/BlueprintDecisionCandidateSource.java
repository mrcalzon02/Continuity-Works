package io.continuityworks.api.blueprint;

import java.util.LinkedHashSet;
import java.util.List;
import java.util.Objects;
import java.util.Set;

/**
 * Supplies authoritative legal semantic candidates for one dynamic decision mutator.
 *
 * <p>The source is intentionally external to the decision chain so catalog and
 * archetype-profile data can evolve independently without embedding guessed values in
 * the API. Candidate order is significant because compact local codes are derived from it.</p>
 */
@FunctionalInterface
public interface BlueprintDecisionCandidateSource {
    CandidateSet candidates(
        BlueprintRequest request,
        BlueprintDecisionChain.State state,
        BlueprintDecisionChain.Mutator mutator
    );

    /** A versioned authoritative candidate snapshot supplied for one decision state. */
    record CandidateSet(String sourceVersion, List<String> values) {
        public static final int MAX_SOURCE_VERSION_CHARS = 128;

        public CandidateSet {
            Objects.requireNonNull(sourceVersion, "sourceVersion");
            sourceVersion = sourceVersion.trim();
            if (sourceVersion.isEmpty()) {
                throw new IllegalArgumentException("candidate sourceVersion must not be blank");
            }
            if (sourceVersion.length() > MAX_SOURCE_VERSION_CHARS) {
                throw new IllegalArgumentException("candidate sourceVersion exceeds " + MAX_SOURCE_VERSION_CHARS + " characters");
            }
            rejectControlCharacters(sourceVersion, "candidate sourceVersion");

            values = List.copyOf(values == null ? List.of() : values);
            Set<String> unique = new LinkedHashSet<>();
            for (String raw : values) {
                Objects.requireNonNull(raw, "candidate value");
                String value = raw.trim();
                if (value.isEmpty()) throw new IllegalArgumentException("candidate value must not be blank");
                if (!value.equals(raw)) {
                    throw new IllegalArgumentException("candidate values must already be canonical and trimmed");
                }
                if (!unique.add(value)) throw new IllegalArgumentException("duplicate candidate value: " + value);
            }
        }

        private static void rejectControlCharacters(String text, String label) {
            for (int i = 0; i < text.length(); i++) {
                if (text.charAt(i) < 0x20) throw new IllegalArgumentException(label + " contains control characters");
            }
        }
    }
}
