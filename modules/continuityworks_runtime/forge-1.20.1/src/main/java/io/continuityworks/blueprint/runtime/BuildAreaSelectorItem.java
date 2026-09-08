package io.continuityworks.blueprint.runtime;

import net.minecraft.ChatFormatting;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;
import net.minecraft.world.InteractionResult;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.TooltipFlag;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.UseOnContext;
import net.minecraft.world.level.Level;

import java.util.List;

public final class BuildAreaSelectorItem extends Item {
    public BuildAreaSelectorItem(Properties properties) {
        super(properties);
    }

    @Override
    public InteractionResult useOn(UseOnContext context) {
        if (context.getLevel().isClientSide()) return InteractionResult.SUCCESS;
        if (!(context.getPlayer() instanceof ServerPlayer player)) return InteractionResult.PASS;

        if (player.isShiftKeyDown()) {
            boolean changed = ContinuityWorksSelectionStore.INSTANCE.clear(player);
            ContinuityWorksSelectionNetwork.sync(player);
            player.displayClientMessage(Component.literal(changed
                ? "Continuity Works build-area selection cleared."
                : "Continuity Works has no build-area selection to clear."), true);
            return InteractionResult.CONSUME;
        }

        BlockPos clicked = context.getClickedPos();
        try {
            ContinuityWorksSelectionStore.SelectionAction action = ContinuityWorksSelectionStore.INSTANCE.selectCorner(player, clicked);
            if (action.state() == ContinuityWorksSelectionStore.SelectionAction.State.FIRST_CORNER) {
                player.displayClientMessage(Component.literal("Continuity Works corner 1: " + coords(clicked) + ". Select corner 2."), true);
            } else {
                ContinuityWorksSelectionNetwork.sync(player);
                var bounds = action.selection().volume().bounds();
                player.displayClientMessage(Component.literal(
                    "Continuity Works build area selected: " + coords(bounds.min()) + " to " + coords(bounds.max())), true);
            }
            return InteractionResult.CONSUME;
        } catch (IllegalArgumentException error) {
            player.displayClientMessage(Component.literal(error.getMessage()).withStyle(ChatFormatting.RED), true);
            return InteractionResult.FAIL;
        }
    }

    @Override
    public void appendHoverText(ItemStack stack, Level level, List<Component> tooltip, TooltipFlag flag) {
        tooltip.add(Component.literal("Right-click two blocks to select a bounded build area.").withStyle(ChatFormatting.GRAY));
        tooltip.add(Component.literal("Shift-right-click to clear the selection.").withStyle(ChatFormatting.GRAY));
    }

    private static String coords(BlockPos pos) {
        return pos.getX() + "," + pos.getY() + "," + pos.getZ();
    }

    private static String coords(io.continuityworks.api.blueprint.BlockPosition pos) {
        return pos.x() + "," + pos.y() + "," + pos.z();
    }
}
