package io.continuityworks.api.blueprint;

public record BlockPosition(int x, int y, int z) {
    public BlockPosition offset(BlockPosition delta) {
        return new BlockPosition(x + delta.x, y + delta.y, z + delta.z);
    }
}
