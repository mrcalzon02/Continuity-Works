package io.continuityworks.blueprint.runtime;

import com.mojang.blaze3d.platform.InputConstants;
import net.minecraft.client.KeyMapping;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.client.event.RegisterKeyMappingsEvent;
import net.minecraftforge.eventbus.api.SubscribeEvent;
import net.minecraftforge.fml.common.Mod;
import org.lwjgl.glfw.GLFW;

@Mod.EventBusSubscriber(modid = ContinuityWorksBlueprintMod.MOD_ID, bus = Mod.EventBusSubscriber.Bus.MOD, value = Dist.CLIENT)
public final class ContinuityWorksSelectionClientModEvents {
    static final KeyMapping TOGGLE_HIGHLIGHT = new KeyMapping(
        "key.continuityworks_blueprint.toggle_selection_highlight",
        InputConstants.Type.KEYSYM,
        GLFW.GLFW_KEY_H,
        "key.categories.continuityworks_blueprint"
    );

    private ContinuityWorksSelectionClientModEvents() {}

    @SubscribeEvent
    public static void onRegisterKeyMappings(RegisterKeyMappingsEvent event) {
        event.register(TOGGLE_HIGHLIGHT);
    }
}
