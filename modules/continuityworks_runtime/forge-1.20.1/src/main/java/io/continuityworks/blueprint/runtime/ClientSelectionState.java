package io.continuityworks.blueprint.runtime;

import com.mojang.blaze3d.systems.RenderSystem;
import com.mojang.blaze3d.vertex.PoseStack;
import com.mojang.blaze3d.vertex.VertexConsumer;
import net.minecraft.client.Minecraft;
import net.minecraft.client.renderer.LevelRenderer;
import net.minecraft.client.renderer.MultiBufferSource;
import net.minecraft.client.renderer.RenderType;
import net.minecraft.network.chat.Component;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.client.event.RenderLevelStageEvent;

import java.util.UUID;

final class ClientSelectionState {
    private static volatile SyncedSelection selection;
    private static volatile boolean highlightEnabled;

    private ClientSelectionState() {}

    static void accept(SelectionSyncPacket packet) {
        Minecraft minecraft = Minecraft.getInstance();
        if (!packet.present()) {
            selection = null;
            highlightEnabled = false;
            if (minecraft.screen instanceof SelectionEditorScreen) minecraft.setScreen(null);
            return;
        }
        selection = new SyncedSelection(
            packet.dimensionId(), packet.volumeId(), packet.snapshotEpoch(),
            packet.minX(), packet.minY(), packet.minZ(), packet.maxX(), packet.maxY(), packet.maxZ()
        );
        if (minecraft.screen instanceof SelectionEditorScreen && !hasSelectionInCurrentDimension()) {
            minecraft.setScreen(null);
        }
    }

    static boolean hasSelectionInCurrentDimension() {
        Minecraft minecraft = Minecraft.getInstance();
        return selection != null
            && minecraft.level != null
            && selection.dimensionId().equals(minecraft.level.dimension().location().toString());
    }

    static SelectionDimensions dimensions() {
        SyncedSelection current = selection;
        if (current == null) return new SelectionDimensions(0, 0, 0);
        return new SelectionDimensions(
            current.maxX() - current.minX() + 1,
            current.maxY() - current.minY() + 1,
            current.maxZ() - current.minZ() + 1
        );
    }

    static void openEditor() {
        Minecraft minecraft = Minecraft.getInstance();
        if (selection == null) {
            if (minecraft.player != null) minecraft.player.displayClientMessage(
                Component.literal("Continuity Works: no selected build volume to edit."), true);
            return;
        }
        if (!hasSelectionInCurrentDimension()) {
            if (minecraft.player != null) minecraft.player.displayClientMessage(
                Component.literal("Continuity Works: selected build volume is in " + selection.dimensionId() + "."), true);
            return;
        }
        minecraft.setScreen(new SelectionEditorScreen());
    }

    static void requestAdjustment(SelectionFace face, int delta) {
        Minecraft minecraft = Minecraft.getInstance();
        if (!hasSelectionInCurrentDimension()) {
            if (minecraft.player != null) minecraft.player.displayClientMessage(
                Component.literal("Continuity Works: no editable build volume in this dimension."), true);
            return;
        }
        ContinuityWorksSelectionNetwork.requestAdjustment(face, delta);
    }

    static void toggleHighlight() {
        Minecraft minecraft = Minecraft.getInstance();
        if (selection == null) {
            highlightEnabled = false;
            if (minecraft.player != null) minecraft.player.displayClientMessage(
                Component.literal("Continuity Works: no selected build volume to highlight."), true);
            return;
        }
        if (!hasSelectionInCurrentDimension()) {
            highlightEnabled = false;
            if (minecraft.player != null) minecraft.player.displayClientMessage(
                Component.literal("Continuity Works: selected build volume is in " + selection.dimensionId() + "."), true);
            return;
        }
        highlightEnabled = !highlightEnabled;
        if (minecraft.player != null) minecraft.player.displayClientMessage(
            Component.literal("Continuity Works build-volume highlight " + (highlightEnabled ? "enabled." : "disabled.")), true);
    }

    static void render(RenderLevelStageEvent event) {
        if (!highlightEnabled || selection == null || event.getStage() != RenderLevelStageEvent.Stage.AFTER_TRANSLUCENT_BLOCKS) return;
        Minecraft minecraft = Minecraft.getInstance();
        if (!hasSelectionInCurrentDimension()) return;

        Vec3 camera = event.getCamera().getPosition();
        AABB box = new AABB(
            selection.minX(), selection.minY(), selection.minZ(),
            selection.maxX() + 1.0, selection.maxY() + 1.0, selection.maxZ() + 1.0
        );
        PoseStack poseStack = event.getPoseStack();
        MultiBufferSource.BufferSource buffers = minecraft.renderBuffers().bufferSource();
        VertexConsumer lines = buffers.getBuffer(RenderType.lines());

        RenderSystem.disableDepthTest();
        RenderSystem.depthMask(false);
        poseStack.pushPose();
        try {
            poseStack.translate(-camera.x, -camera.y, -camera.z);
            LevelRenderer.renderLineBox(poseStack, lines, box, 0.20F, 0.90F, 1.00F, 1.00F);
        } finally {
            poseStack.popPose();
            buffers.endBatch(RenderType.lines());
            RenderSystem.depthMask(true);
            RenderSystem.enableDepthTest();
        }
    }

    record SelectionDimensions(int width, int height, int depth) {}

    private record SyncedSelection(
        String dimensionId,
        UUID volumeId,
        long snapshotEpoch,
        int minX, int minY, int minZ,
        int maxX, int maxY, int maxZ
    ) {}
}
