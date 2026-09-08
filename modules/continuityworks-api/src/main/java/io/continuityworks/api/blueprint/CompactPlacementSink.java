package io.continuityworks.api.blueprint;

/** Zero-retention placement callback. Return false to stop materialization early. */
@FunctionalInterface
public interface CompactPlacementSink {
    boolean accept(int sequence, PlacementOperation.Kind kind, BlockPosition relativePosition, String paletteKey);
}
