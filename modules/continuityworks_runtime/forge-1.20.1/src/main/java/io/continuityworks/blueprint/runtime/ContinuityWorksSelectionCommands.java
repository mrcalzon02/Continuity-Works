package io.continuityworks.blueprint.runtime;

import com.mojang.brigadier.CommandDispatcher;
import net.minecraft.commands.CommandSourceStack;
import net.minecraft.commands.Commands;
import net.minecraft.commands.arguments.coordinates.BlockPosArgument;
import net.minecraft.core.BlockPos;
import net.minecraft.network.chat.Component;
import net.minecraft.server.level.ServerPlayer;

final class ContinuityWorksSelectionCommands {
    private ContinuityWorksSelectionCommands() {}

    static void register(CommandDispatcher<CommandSourceStack> dispatcher) {
        dispatcher.register(Commands.literal("continuityworks")
            .then(Commands.literal("selection")
                .then(Commands.literal("set")
                    .then(Commands.argument("from", BlockPosArgument.blockPos())
                        .then(Commands.argument("to", BlockPosArgument.blockPos())
                            .executes(context -> set(
                                context.getSource(),
                                BlockPosArgument.getBlockPos(context, "from"),
                                BlockPosArgument.getBlockPos(context, "to")
                            )))))
                .then(Commands.literal("clear").executes(context -> clear(context.getSource())))
                .then(Commands.literal("status").executes(context -> status(context.getSource()))))
        );
    }

    private static int set(CommandSourceStack source, BlockPos from, BlockPos to) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = source.getPlayerOrException();
        try {
            var selection = ContinuityWorksSelectionStore.INSTANCE.set(player, from, to, "command");
            ContinuityWorksSelectionNetwork.sync(player);
            var bounds = selection.volume().bounds();
            source.sendSuccess(() -> Component.literal(
                "Continuity Works build area set: " + coords(bounds.min()) + " to " + coords(bounds.max())
                    + " in " + selection.dimensionId()), false);
            return 1;
        } catch (IllegalArgumentException error) {
            source.sendFailure(Component.literal(error.getMessage()));
            return 0;
        }
    }

    private static int clear(CommandSourceStack source) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = source.getPlayerOrException();
        boolean changed = ContinuityWorksSelectionStore.INSTANCE.clear(player);
        ContinuityWorksSelectionNetwork.sync(player);
        if (!changed) {
            source.sendFailure(Component.literal("Continuity Works has no build-area selection to clear."));
            return 0;
        }
        source.sendSuccess(() -> Component.literal("Continuity Works build-area selection cleared."), false);
        return 1;
    }

    private static int status(CommandSourceStack source) throws com.mojang.brigadier.exceptions.CommandSyntaxException {
        ServerPlayer player = source.getPlayerOrException();
        var selected = ContinuityWorksSelectionStore.INSTANCE.selectedArea(player.getUUID());
        if (selected.isEmpty()) {
            source.sendFailure(Component.literal("Continuity Works has no selected build area."));
            return 0;
        }
        var selection = selected.get();
        var bounds = selection.volume().bounds();
        source.sendSuccess(() -> Component.literal(
            "Continuity Works selection " + selection.volume().volumeId() + " epoch " + selection.volume().snapshotEpoch()
                + ": " + coords(bounds.min()) + " to " + coords(bounds.max()) + " in " + selection.dimensionId()), false);
        return 1;
    }

    private static String coords(io.continuityworks.api.blueprint.BlockPosition pos) {
        return pos.x() + "," + pos.y() + "," + pos.z();
    }
}
