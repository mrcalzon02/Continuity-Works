package io.continuityworks.spawnprotection.data;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import io.continuityworks.spawnprotection.config.SpawnProtectionConfig;
import net.minecraft.core.Registry;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.tags.TagKey;
import net.minecraft.world.level.levelgen.structure.Structure;

import java.util.Collections;
import java.util.HashSet;
import java.util.Set;

/** Data-pack sidecar profile for enrolling foreign structure systems without replacing their JSON. */
public record ProtectionProfile(
    ResourceLocation sourceId,
    Set<ResourceLocation> structures,
    Set<ResourceLocation> tags,
    Set<String> namespaces,
    ResourceLocation family,
    int exclusionRadius,
    int jigsawPieceExclusionRadius,
    boolean protectJigsawPieces,
    int priority
) {
    public ProtectionProfile {
        structures = Collections.unmodifiableSet(new HashSet<>(structures));
        tags = Collections.unmodifiableSet(new HashSet<>(tags));
        namespaces = Collections.unmodifiableSet(new HashSet<>(namespaces));
        if (structures.isEmpty() && tags.isEmpty() && namespaces.isEmpty()) {
            throw new IllegalArgumentException("Protection profile requires at least one selector");
        }
        if (exclusionRadius < SpawnProtectionConfig.HARD_MINIMUM_RADIUS) {
            throw new IllegalArgumentException("exclusionRadius must be >= 500");
        }
        if (jigsawPieceExclusionRadius < SpawnProtectionConfig.HARD_MINIMUM_RADIUS) {
            throw new IllegalArgumentException("jigsawPieceExclusionRadius must be >= 500");
        }
    }

    public static ProtectionProfile parse(ResourceLocation sourceId, JsonObject json) {
        JsonObject selectors = requiredObject(json, "selectors");
        Set<ResourceLocation> structures = resourceLocations(selectors.getAsJsonArray("structures"));
        Set<ResourceLocation> tags = resourceLocations(selectors.getAsJsonArray("tags"));
        Set<String> namespaces = strings(selectors.getAsJsonArray("namespaces"));
        if (structures.isEmpty() && tags.isEmpty() && namespaces.isEmpty()) {
            throw new JsonParseException("Profile " + sourceId + " requires a structure, tag, or namespace selector");
        }

        int radius = json.has("exclusion_radius")
            ? json.get("exclusion_radius").getAsInt()
            : SpawnProtectionConfig.DEFAULT_EXCLUSION_RADIUS.get();
        int pieceRadius = json.has("jigsaw_piece_exclusion_radius")
            ? json.get("jigsaw_piece_exclusion_radius").getAsInt()
            : radius;
        if (radius < SpawnProtectionConfig.HARD_MINIMUM_RADIUS || pieceRadius < SpawnProtectionConfig.HARD_MINIMUM_RADIUS) {
            throw new JsonParseException("Profile " + sourceId + " attempts to lower the hard 500-block minimum");
        }

        ResourceLocation family = json.has("family") ? new ResourceLocation(json.get("family").getAsString()) : null;
        boolean protectPieces = !json.has("protect_jigsaw_pieces") || json.get("protect_jigsaw_pieces").getAsBoolean();
        if (!protectPieces) {
            throw new JsonParseException("Profile " + sourceId + " cannot disable per-piece jigsaw protection");
        }
        int priority = json.has("priority") ? json.get("priority").getAsInt() : 0;
        return new ProtectionProfile(sourceId, structures, tags, namespaces, family, radius, pieceRadius, protectPieces, priority);
    }

    public boolean matches(ResourceLocation structureId, Registry<Structure> registry) {
        if (structures.contains(structureId) || namespaces.contains(structureId.getNamespace())) {
            return true;
        }
        ResourceKey<Structure> key = ResourceKey.create(Registries.STRUCTURE, structureId);
        return registry.getHolder(key).map(holder -> tags.stream().anyMatch(tagId -> holder.is(TagKey.create(Registries.STRUCTURE, tagId)))).orElse(false);
    }

    private static JsonObject requiredObject(JsonObject parent, String name) {
        JsonElement element = parent.get(name);
        if (element == null || !element.isJsonObject()) {
            throw new JsonParseException("Missing object: " + name);
        }
        return element.getAsJsonObject();
    }

    private static Set<ResourceLocation> resourceLocations(JsonArray array) {
        Set<ResourceLocation> out = new HashSet<>();
        if (array != null) {
            for (JsonElement element : array) out.add(new ResourceLocation(element.getAsString()));
        }
        return out;
    }

    private static Set<String> strings(JsonArray array) {
        Set<String> out = new HashSet<>();
        if (array != null) {
            for (JsonElement element : array) out.add(element.getAsString());
        }
        return out;
    }
}
