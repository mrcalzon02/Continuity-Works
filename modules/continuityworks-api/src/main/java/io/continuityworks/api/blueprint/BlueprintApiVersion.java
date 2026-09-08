package io.continuityworks.api.blueprint;

public record BlueprintApiVersion(int major, int minor, int patch) {
    public static final BlueprintApiVersion CURRENT = new BlueprintApiVersion(1, 6, 0);

    public BlueprintApiVersion {
        if (major < 0 || minor < 0 || patch < 0) {
            throw new IllegalArgumentException("API version components must be non-negative");
        }
    }

    public boolean isCompatibleWith(BlueprintApiVersion other) {
        return other != null && major == other.major;
    }

    @Override
    public String toString() {
        return major + "." + minor + "." + patch;
    }
}
