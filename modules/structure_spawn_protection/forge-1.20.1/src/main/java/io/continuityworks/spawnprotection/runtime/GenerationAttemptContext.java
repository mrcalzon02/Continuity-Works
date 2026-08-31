package io.continuityworks.spawnprotection.runtime;

import java.util.ArrayDeque;
import java.util.Deque;

/** Stack-scoped worldgen context; supports nested structure generation on the same worker thread. */
public final class GenerationAttemptContext {
    private static final ThreadLocal<Deque<GenerationAttempt>> CURRENT = ThreadLocal.withInitial(ArrayDeque::new);

    public static void begin(GenerationAttempt attempt) {
        CURRENT.get().push(attempt);
    }

    public static GenerationAttempt current() {
        return CURRENT.get().peek();
    }

    public static void end(GenerationAttempt attempt) {
        Deque<GenerationAttempt> stack = CURRENT.get();
        if (stack.peek() == attempt) stack.pop();
        else stack.remove(attempt);
        if (stack.isEmpty()) CURRENT.remove();
    }

    public static void clear() {
        CURRENT.remove();
    }

    private GenerationAttemptContext() { }
}
