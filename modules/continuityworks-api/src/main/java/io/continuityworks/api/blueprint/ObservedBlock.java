package io.continuityworks.api.blueprint;

import java.util.Objects;

public record ObservedBlock(BlockPosition position, String blockState, boolean protectedBlock) {
    public ObservedBlock {
        Objects.requireNonNull(position, "position");
        Objects.requireNonNull(blockState, "blockState");
    }
}
