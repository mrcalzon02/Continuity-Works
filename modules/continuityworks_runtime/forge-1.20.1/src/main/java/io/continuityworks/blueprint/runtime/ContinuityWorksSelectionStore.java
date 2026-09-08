package io.continuityworks.blueprint.runtime;

import io.continuityworks.api.blueprint.BuildAreaSelection;
import io.continuityworks.api.blueprint.ConstructionVolume;
import io.continuityworks.api.blueprint.ContinuityWorksSelectionApi;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerPlayer;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

/** Session-local, server-authoritative build-area selections. No block snapshots are retained. */
public final class ContinuityWorksSelectionStore implements ContinuityWorksSelectionApi {
    public static final ContinuityWorksSelectionStore INSTANCE = new ContinuityWorksSelectionStore();
    public static final int MAX_AXIS = 1_024;
    public static final long MAX_SELECTED_BLOCKS = 134_217_728L;

    private final Map<UUID, Draft> drafts = new HashMap<>();
    private final Map<UUID, BuildAreaSelection> selections = new HashMap<>();
    private final Map<UUID, Long> epochs = new HashMap<>();

    private ContinuityWorksSelectionStore() {}

    @Override
    public synchronized Optional<BuildAreaSelection> selectedArea(UUID ownerUuid) {
        return Optional.ofNullable(selections.get(ownerUuid));
    }

    public synchronized SelectionAction selectCorner(ServerPlayer player, BlockPos position) {
        UUID owner = player.getUUID();
        String dimension = dimensionId(player);
        Draft draft = drafts.get(owner);
        if (draft == null || !draft.dimensionId().equals(dimension)) {
            drafts.put(owner, new Draft(dimension, position.immutable()));
            return new SelectionAction(SelectionAction.State.FIRST_CORNER, position.immutable(), null);
        }
        drafts.remove(owner);
        BuildAreaSelection completed = set(player, draft.first(), position, "selector_token");
        return new SelectionAction(SelectionAction.State.COMPLETE, draft.first(), completed);
    }

    public synchronized BuildAreaSelection set(ServerPlayer player, BlockPos a, BlockPos b, String source) {
        validate(player, a, b);
        int minX = Math.min(a.getX(), b.getX()), minY = Math.min(a.getY(), b.getY()), minZ = Math.min(a.getZ(), b.getZ());
        int maxX = Math.max(a.getX(), b.getX()), maxY = Math.max(a.getY(), b.getY()), maxZ = Math.max(a.getZ(), b.getZ());
        UUID owner = player.getUUID();
        String dimension = dimensionId(player);
        long epoch = epochs.merge(owner, 1L, Long::sum);
        io.continuityworks.api.blueprint.Bounds bounds = new io.continuityworks.api.blueprint.Bounds(
            new io.continuityworks.api.blueprint.BlockPosition(minX, minY, minZ),
            new io.continuityworks.api.blueprint.BlockPosition(maxX, maxY, maxZ)
        );
        ConstructionVolume volume = new ConstructionVolume(
            UUID.randomUUID(),
            bounds,
            epoch,
            Map.of(
                "dimension", dimension,
                "owner", owner.toString(),
                "source", source == null || source.isBlank() ? "unknown" : source
            )
        );
        BuildAreaSelection selection = new BuildAreaSelection(owner, dimension, volume);
        selections.put(owner, selection);
        drafts.remove(owner);
        return selection;
    }

    public synchronized boolean clear(ServerPlayer player) {
        UUID owner = player.getUUID();
        boolean changed = drafts.remove(owner) != null;
        changed |= selections.remove(owner) != null;
        if (changed) epochs.merge(owner, 1L, Long::sum);
        return changed;
    }

    public synchronized void clearRuntime() {
        drafts.clear();
        selections.clear();
        epochs.clear();
    }

    private static void validate(ServerPlayer player, BlockPos a, BlockPos b) {
        int minBuild = player.serverLevel().getMinBuildHeight();
        int maxBuild = player.serverLevel().getMaxBuildHeight() - 1;
        if (a.getY() < minBuild || a.getY() > maxBuild || b.getY() < minBuild || b.getY() > maxBuild) {
            throw new IllegalArgumentException("Selection Y coordinates must stay inside the dimension build height " + minBuild + ".." + maxBuild);
        }
        long width = Math.abs((long)a.getX() - b.getX()) + 1L;
        long height = Math.abs((long)a.getY() - b.getY()) + 1L;
        long depth = Math.abs((long)a.getZ() - b.getZ()) + 1L;
        if (width > MAX_AXIS || height > MAX_AXIS || depth > MAX_AXIS) {
            throw new IllegalArgumentException("Selection axis exceeds Continuity Works limit of " + MAX_AXIS + " blocks");
        }
        long blocks = width * height * depth;
        if (blocks > MAX_SELECTED_BLOCKS) {
            throw new IllegalArgumentException("Selection volume exceeds Continuity Works limit of " + MAX_SELECTED_BLOCKS + " blocks");
        }
    }

    private static String dimensionId(ServerPlayer player) {
        return player.serverLevel().dimension().location().toString();
    }

    private record Draft(String dimensionId, BlockPos first) {}

    public record SelectionAction(State state, BlockPos firstCorner, BuildAreaSelection selection) {
        public enum State { FIRST_CORNER, COMPLETE }
    }
}
