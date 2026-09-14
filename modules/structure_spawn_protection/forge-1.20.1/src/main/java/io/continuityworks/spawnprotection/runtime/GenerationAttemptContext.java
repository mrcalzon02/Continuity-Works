package io.continuityworks.spawnprotection.runtime;

import java.util.ArrayDeque;
import java.util.Deque;

/** Stack-scoped worldgen context; supports nested structure generation on the same worker thread. */
public final class GenerationAttemptContext {
    private static final ThreadLocal<Deque<Frame>> CURRENT = ThreadLocal.withInitial(ArrayDeque::new);

    /**
     * Open one tryGenerateStructure invocation frame. A null attempt deliberately shadows any outer
     * attempt when the current invocation cannot be associated with a ServerLevel.
     */
    public static void begin(GenerationAttempt attempt) {
        CURRENT.get().push(new Frame(attempt));
    }

    public static GenerationAttempt current() {
        Frame frame = CURRENT.get().peek();
        return frame == null ? null : frame.attempt();
    }

    /** Close exactly the current invocation frame; nested generation must unwind in strict LIFO order. */
    public static void end(GenerationAttempt attempt) {
        Deque<Frame> stack = CURRENT.get();
        Frame frame = stack.peek();
        if (frame == null) {
            CURRENT.remove();
            throw new IllegalStateException("No generation attempt frame is active");
        }
        if (frame.attempt() != attempt) {
            throw new IllegalStateException("Generation attempt frames must end in LIFO order");
        }
        stack.pop();
        if (stack.isEmpty()) CURRENT.remove();
    }

    public static void clear() {
        CURRENT.remove();
    }

    private record Frame(GenerationAttempt attempt) { }

    private GenerationAttemptContext() { }
}
