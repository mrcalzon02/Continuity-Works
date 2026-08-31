package io.continuityworks.spawnprotection.data;

import io.continuityworks.spawnprotection.ContinuityWorksSpawnProtection;
import io.continuityworks.spawnprotection.config.SpawnProtectionConfig;
import net.minecraft.core.Registry;
import net.minecraft.core.RegistryAccess;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.levelgen.structure.Structure;
import net.minecraft.world.level.levelgen.structure.structures.JigsawStructure;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Registry scan result. Every structure respects reservations; enrolled entries also create them. */
public final class ProtectionCatalog {
    public static final TagKey<Structure> PROTECTED = tag("protected");
    public static final TagKey<Structure> JIGSAW_PIECE_PROTECTED = tag("jigsaw_piece_protected");
    public static final TagKey<Structure> IGNORED = tag("ignored");

    private static volatile Map<ResourceLocation, ResolvedProtection> resolved = Map.of();

    public static synchronized void rebuild(RegistryAccess registryAccess) {
        Registry<Structure> registry = registryAccess.registryOrThrow(Registries.STRUCTURE);
        List<ProtectionProfile> profiles = ProtectionProfileReloadListener.instance().profiles();
        Map<ResourceLocation, ResolvedProtection> next = new HashMap<>();
        int enrolled = 0;
        int jigsaws = 0;
        int ignored = 0;

        for (ResourceLocation id : registry.keySet()) {
            Structure structure = registry.get(id);
            if (structure == null) continue;
            boolean isJigsaw = structure instanceof JigsawStructure;
            if (isJigsaw) jigsaws++;

            if (inTag(registry, id, IGNORED)) {
                next.put(id, ResolvedProtection.respectOnly(id));
                ignored++;
                continue;
            }

            ProtectionProfile profile = profiles.stream()
                .filter(candidate -> candidate.matches(id, registry))
                .findFirst()
                .orElse(null);

            boolean explicitTag = inTag(registry, id, PROTECTED);
            boolean explicitJigsawTag = inTag(registry, id, JIGSAW_PIECE_PROTECTED);
            boolean autoRegistered = SpawnProtectionConfig.AUTO_INCLUDE_REGISTERED_STRUCTURES.get();
            boolean emits = profile != null || explicitTag || explicitJigsawTag || autoRegistered;

            if (!emits) {
                next.put(id, ResolvedProtection.respectOnly(id));
                continue;
            }

            int radius = profile != null
                ? profile.exclusionRadius()
                : SpawnProtectionConfig.DEFAULT_EXCLUSION_RADIUS.get();
            int pieceRadius = profile != null
                ? profile.jigsawPieceExclusionRadius()
                : SpawnProtectionConfig.DEFAULT_JIGSAW_PIECE_RADIUS.get();
            ResourceLocation family = profile != null && profile.family() != null ? profile.family() : id;
            boolean pieces = isJigsaw;
            String source = profile != null ? "profile:" + profile.sourceId()
                : explicitJigsawTag ? "tag:jigsaw_piece_protected"
                : explicitTag ? "tag:protected"
                : "scan:registered";

            next.put(id, new ResolvedProtection(id, family, true, pieces, radius, pieceRadius, source));
            enrolled++;
        }

        resolved = Map.copyOf(next);
        ContinuityWorksSpawnProtection.LOGGER.info(
            "Structure protection scan: {} registered, {} jigsaw, {} enrolled, {} explicitly ignored",
            registry.size(), jigsaws, enrolled, ignored
        );
    }

    public static ResolvedProtection resolve(ResourceLocation structureId) {
        return resolved.getOrDefault(structureId, ResolvedProtection.respectOnly(structureId));
    }

    private static TagKey<Structure> tag(String path) {
        return TagKey.create(Registries.STRUCTURE, new ResourceLocation(ContinuityWorksSpawnProtection.MOD_ID, path));
    }

    private static boolean inTag(Registry<Structure> registry, ResourceLocation id, TagKey<Structure> tag) {
        ResourceKey<Structure> key = ResourceKey.create(Registries.STRUCTURE, id);
        return registry.getHolder(key).map(holder -> holder.is(tag)).orElse(false);
    }

    private ProtectionCatalog() { }
}
