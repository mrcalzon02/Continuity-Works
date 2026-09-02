package io.continuityworks.spawnprotection.runtime;

import io.continuityworks.spawnprotection.ContinuityWorksSpawnProtection;
import io.continuityworks.spawnprotection.config.SpawnProtectionConfig;
import io.continuityworks.spawnprotection.data.ProtectionCatalog;
import io.continuityworks.spawnprotection.data.ResolvedProtection;
import io.continuityworks.spawnprotection.data.SpawnProtectionSavedData;
import io.continuityworks.spawnprotection.model.BlockBox;
import io.continuityworks.spawnprotection.model.Reservation;
import io.continuityworks.spawnprotection.model.ReservationConflict;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.MinecraftServer;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.ChunkPos;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.chunk.ChunkAccess;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.StructurePiece;
import net.minecraft.world.level.levelgen.structure.StructureStart;
import net.minecraft.world.level.levelgen.structure.structures.JigsawStructure;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicLong;

/** Server-side coordinator for dimension reservation indexes and structure transactions. */
public final class SpawnProtectionService {
    private static final Map<ResourceKey<Level>, LevelState> LEVELS = new ConcurrentHashMap<>();
    private static final AtomicLong ASSEMBLY_SEQUENCE = new AtomicLong();
    private static volatile MinecraftServer server;

    public static void attachServer(MinecraftServer minecraftServer) {
        server = minecraftServer;
    }

    public static void detachServer() {
        LEVELS.clear();
        server = null;
        GenerationAttemptContext.clear();
    }

    public static LevelState attachLevel(ServerLevel level) {
        return LEVELS.computeIfAbsent(level.dimension(), ignored -> {
            SpawnProtectionSavedData data = SpawnProtectionSavedData.get(level);
            LevelState state = new LevelState(level, data, new ReservationIndex(data.reservations()));
            ContinuityWorksSpawnProtection.LOGGER.info(
                "Loaded {} committed structure reservations for {}",
                state.index().size(), level.dimension().location()
            );
            return state;
        });
    }

    public static GenerationAttempt beginAttempt(
        ServerLevel level,
        RegistryAccess registryAccess,
        Structure structure,
        ChunkPos chunkPos
    ) {
        LevelState state = attachLevel(level);
        Registry<Structure> registry = registryAccess.registryOrThrow(Registries.STRUCTURE);
        ResourceLocation structureId = registry.getKey(structure);
        if (structureId == null) {
            structureId = new ResourceLocation("continuityworks_spawn_protection", "unregistered_structure");
        }
        ResolvedProtection protection = ProtectionCatalog.resolve(structureId);
        String assemblyId = structureId + "@" + chunkPos.x + "," + chunkPos.z + "#" + ASSEMBLY_SEQUENCE.incrementAndGet();
        return new GenerationAttempt(state, structureId, assemblyId, protection, structure instanceof JigsawStructure);
    }

    public static boolean finishAttempt(GenerationAttempt attempt, StructureStart start) {
        return attempt.finish(start);
    }

    public static void rollbackAttempt(GenerationAttempt attempt) {
        attempt.rollback();
    }

    /**
     * Import structure starts from already-generated chunks. This makes upgrades non-destructive:
     * old structures become obstacles as chunks are encountered, without rewriting their data.
     */
    public static void indexExistingChunk(ServerLevel level, ChunkAccess chunk) {
        if (!SpawnProtectionConfig.INDEX_EXISTING_CHUNK_STARTS.get()) return;
        LevelState state = attachLevel(level);
        Registry<Structure> registry = level.registryAccess().registryOrThrow(Registries.STRUCTURE);
        int imported = 0;

        for (Map.Entry<Structure, StructureStart> entry : chunk.getAllStarts().entrySet()) {
            Structure structure = entry.getKey();
            StructureStart start = entry.getValue();
            if (start == null || !start.isValid()) continue;
            ResourceLocation structureId = registry.getKey(structure);
            if (structureId == null) continue;
            ResolvedProtection protection = ProtectionCatalog.resolve(structureId);
            if (!protection.emitsReservations()) continue;

            ChunkPos startChunk = start.getChunkPos();
            String assemblyId = "existing:" + structureId + "@" + startChunk.x + "," + startChunk.z;
            if (structure instanceof JigsawStructure && !start.getPieces().isEmpty()) {
                int pieceIndex = 0;
                for (StructurePiece piece : start.getPieces()) {
                    BlockBox box = BlockBox.from(piece.getBoundingBox());
                    String id = assemblyId + "|piece:" + pieceIndex + "|" + box.compactKey();
                    if (state.index().containsCommittedEquivalent(structureId, box)) { pieceIndex++; continue; }
                    Reservation reservation = new Reservation(
                        id, structureId, assemblyId, protection.familyId(), box,
                        protection.jigsawPieceExclusionRadius(), "piece:" + pieceIndex, false
                    );
                    if (state.index().importCommitted(reservation)) imported++;
                    pieceIndex++;
                }
            } else {
                BlockBox box = BlockBox.from(start.getBoundingBox());
                String id = assemblyId + "|start:" + box.compactKey();
                if (state.index().containsCommittedEquivalent(structureId, box)) continue;
                Reservation reservation = new Reservation(
                    id, structureId, assemblyId, protection.familyId(), box,
                    protection.exclusionRadius(), null, false
                );
                if (state.index().importCommitted(reservation)) imported++;
            }
        }

        if (imported > 0) state.markDirty();
    }

    /** Flush worker-thread index changes into SavedData on the server thread. */
    public static void flushDirty() {
        for (LevelState state : LEVELS.values()) {
            if (state.takeDirty()) {
                state.savedData().replaceReservations(state.index().committedSnapshot());
            }
        }
    }

    public static final class LevelState {
        private final ServerLevel level;
        private final SpawnProtectionSavedData savedData;
        private final ReservationIndex index;
        private final AtomicBoolean dirty = new AtomicBoolean(false);

        private LevelState(ServerLevel level, SpawnProtectionSavedData savedData, ReservationIndex index) {
            this.level = level;
            this.savedData = savedData;
            this.index = index;
        }

        public ServerLevel level() { return level; }
        public SpawnProtectionSavedData savedData() { return savedData; }
        public ReservationIndex index() { return index; }
        public void markDirty() { dirty.set(true); }
        boolean takeDirty() { return dirty.getAndSet(false); }
    }

    private SpawnProtectionService() { }
}
