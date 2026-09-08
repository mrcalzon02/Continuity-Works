package io.continuityworks.blueprint.runtime;

/** One editable face of the selected build volume. Positive deltas move outward. */
enum SelectionFace {
    UP("UP"),
    DOWN("DOWN"),
    NORTH("NORTH"),
    SOUTH("SOUTH"),
    WEST("WEST"),
    EAST("EAST");

    private final String label;

    SelectionFace(String label) {
        this.label = label;
    }

    String label() {
        return label;
    }

    static SelectionFace fromOrdinal(int ordinal) {
        SelectionFace[] values = values();
        if (ordinal < 0 || ordinal >= values.length) {
            throw new IllegalArgumentException("Invalid Continuity Works selection face ordinal: " + ordinal);
        }
        return values[ordinal];
    }
}
