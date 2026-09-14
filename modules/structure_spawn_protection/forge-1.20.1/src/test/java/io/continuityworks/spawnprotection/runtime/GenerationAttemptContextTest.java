package io.continuityworks.spawnprotection.runtime;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;

class GenerationAttemptContextTest {
    @AfterEach
    void clearContext() {
        GenerationAttemptContext.clear();
    }

    @Test
    void inactiveNestedInvocationShadowsAndRestoresOuterAttempt() {
        GenerationAttempt outer = attempt("outer");

        GenerationAttemptContext.begin(outer);
        assertSame(outer, GenerationAttemptContext.current());

        GenerationAttemptContext.begin(null);
        assertNull(GenerationAttemptContext.current());

        GenerationAttemptContext.end(null);
        assertSame(outer, GenerationAttemptContext.current());

        GenerationAttemptContext.end(outer);
        assertNull(GenerationAttemptContext.current());
    }

    @Test
    void rejectsOutOfOrderNestedUnwindWithoutCorruptingStack() {
        GenerationAttempt outer = attempt("outer");
        GenerationAttempt inner = attempt("inner");

        GenerationAttemptContext.begin(outer);
        GenerationAttemptContext.begin(inner);

        assertThrows(IllegalStateException.class, () -> GenerationAttemptContext.end(outer));
        assertSame(inner, GenerationAttemptContext.current());

        GenerationAttemptContext.end(inner);
        assertSame(outer, GenerationAttemptContext.current());
        GenerationAttemptContext.end(outer);
    }

    private static GenerationAttempt attempt(String assemblyId) {
        return new GenerationAttempt(null, null, assemblyId, null, false);
    }
}
