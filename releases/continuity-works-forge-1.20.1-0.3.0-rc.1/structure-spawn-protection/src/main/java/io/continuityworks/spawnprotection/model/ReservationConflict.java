package io.continuityworks.spawnprotection.model;

public record ReservationConflict(
    String code,
    Reservation existing,
    double horizontalGap,
    int requiredGap
) { }
