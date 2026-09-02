package io.continuityworks.spawnprotection.data;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import io.continuityworks.spawnprotection.ContinuityWorksSpawnProtection;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.server.packs.resources.ResourceManager;
import net.minecraft.util.profiling.ProfilerFiller;
import net.minecraft.server.packs.resources.SimpleJsonResourceReloadListener;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Map;

public final class ProtectionProfileReloadListener extends SimpleJsonResourceReloadListener {
    private static final Gson GSON = new GsonBuilder().create();
    private static final ProtectionProfileReloadListener INSTANCE = new ProtectionProfileReloadListener();
    private volatile List<ProtectionProfile> profiles = List.of();

    private ProtectionProfileReloadListener() {
        super(GSON, "continuityworks_spawn_protection/profiles");
    }

    public static ProtectionProfileReloadListener instance() {
        return INSTANCE;
    }

    public List<ProtectionProfile> profiles() {
        return profiles;
    }

    @Override
    protected void apply(Map<ResourceLocation, JsonElement> objects, ResourceManager resourceManager, ProfilerFiller profiler) {
        List<ProtectionProfile> parsed = new ArrayList<>();
        objects.forEach((id, element) -> {
            try {
                parsed.add(ProtectionProfile.parse(id, element.getAsJsonObject()));
            } catch (RuntimeException ex) {
                // Invalid metadata can never lower protection. The registry scanner will fall back to
                // tag/automatic defaults for the affected structures instead of accepting unsafe values.
                ContinuityWorksSpawnProtection.LOGGER.error("Rejected unsafe/invalid spawn-protection profile {}: {}", id, ex.getMessage());
            }
        });
        parsed.sort(Comparator.comparingInt(ProtectionProfile::priority).reversed());
        profiles = List.copyOf(parsed);
        ContinuityWorksSpawnProtection.LOGGER.info("Loaded {} structure spawn-protection profiles", profiles.size());
    }
}
