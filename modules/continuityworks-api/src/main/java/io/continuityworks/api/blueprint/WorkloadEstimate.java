package io.continuityworks.api.blueprint;

public record WorkloadEstimate(long placements, long removals, long interactions, long estimatedServerTicks) {
    public WorkloadEstimate {
        if (placements < 0 || removals < 0 || interactions < 0 || estimatedServerTicks < 0) {
            throw new IllegalArgumentException("Workload values must be non-negative");
        }
    }
}
