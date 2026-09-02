package io.continuityworks.spawnprotection.event;

import io.continuityworks.spawnprotection.ContinuityWorksSpawnProtection;
import io.continuityworks.spawnprotection.data.ProtectionCatalog;
import io.continuityworks.spawnprotection.data.ProtectionProfileReloadListener;
import io.continuityworks.spawnprotection.runtime.LevelResolver;
import io.continuityworks.spawnprotection.runtime.SpawnProtectionService;
import net.minecraft.server.level.ServerLevel;
import net.minecraftforge.event.AddReloadListenerEvent;
import net.minecraftforge.event.TagsUpdatedEvent;
import net.minecraftforge.event.TickEvent;
import net.minecraftforge.event.level.ChunkEvent;
import net.minecraftforge.event.level.LevelEvent;
import net.minecraftforge.event.server.ServerAboutToStartEvent;
import net.minecraftforge.event.server.ServerStoppingEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;

@Mod.EventBusSubscriber(modid = ContinuityWorksSpawnProtection.MOD_ID, bus = Mod.EventBusSubscriber.Bus.FORGE)
public final class SpawnProtectionEvents {
    @SubscribeEvent
    public static void onAddReloadListener(AddReloadListenerEvent event) {
        event.addListener(ProtectionProfileReloadListener.instance());
    }

    @SubscribeEvent
    public static void onTagsUpdated(TagsUpdatedEvent event) {
        if (event.shouldUpdateStaticData()) ProtectionCatalog.rebuild(event.getRegistryAccess());
    }

    @SubscribeEvent
    public static void onServerAboutToStart(ServerAboutToStartEvent event) {
        SpawnProtectionService.attachServer(event.getServer());
        ProtectionCatalog.rebuild(event.getServer().registryAccess());
    }

    @SubscribeEvent
    public static void onLevelLoad(LevelEvent.Load event) {
        if (event.getLevel() instanceof ServerLevel level) {
            SpawnProtectionService.attachLevel(level);
        }
    }

    @SubscribeEvent
    public static void onChunkLoad(ChunkEvent.Load event) {
        ServerLevel level = LevelResolver.serverLevel(event.getLevel());
        if (level != null) SpawnProtectionService.indexExistingChunk(level, event.getChunk());
    }

    @SubscribeEvent
    public static void onServerTick(TickEvent.ServerTickEvent event) {
        if (event.phase == TickEvent.Phase.END) SpawnProtectionService.flushDirty();
    }

    @SubscribeEvent
    public static void onServerStopping(ServerStoppingEvent event) {
        SpawnProtectionService.flushDirty();
        SpawnProtectionService.detachServer();
    }

    private SpawnProtectionEvents() { }
}
