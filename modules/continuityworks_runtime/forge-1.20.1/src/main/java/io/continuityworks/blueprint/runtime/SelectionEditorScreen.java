package io.continuityworks.blueprint.runtime;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.components.Button;
import net.minecraft.client.gui.screens.Screen;
import net.minecraft.network.chat.Component;
import org.lwjgl.glfw.GLFW;

import java.util.List;

/**
 * Compact lower-left unfolded-cube editor. '+' pushes the chosen face outward;
 * '-' pulls it inward. The server remains authoritative for every edit.
 */
final class SelectionEditorScreen extends Screen {
    private static final int CELL_W = 52;
    private static final int CELL_H = 36;
    private static final int HEADER_H = 28;
    private static final int PANEL_W = CELL_W * 4 + 8;
    private static final int PANEL_H = HEADER_H + CELL_H * 3 + 6;
    private static final List<FaceCell> CELLS = List.of(
        new FaceCell(SelectionFace.UP, 1, 0),
        new FaceCell(SelectionFace.WEST, 0, 1),
        new FaceCell(SelectionFace.NORTH, 1, 1),
        new FaceCell(SelectionFace.EAST, 2, 1),
        new FaceCell(SelectionFace.SOUTH, 3, 1),
        new FaceCell(SelectionFace.DOWN, 1, 2)
    );

    private SelectionFace activeFace = SelectionFace.NORTH;
    private int panelX;
    private int panelY;

    SelectionEditorScreen() {
        super(Component.literal("Continuity Works Build Area"));
    }

    @Override
    protected void init() {
        if (!ClientSelectionState.hasSelectionInCurrentDimension()) {
            onClose();
            return;
        }

        panelX = 6;
        panelY = Math.max(6, height - PANEL_H - 6);
        for (FaceCell cell : CELLS) {
            int x = panelX + 4 + cell.column() * CELL_W;
            int y = panelY + HEADER_H + cell.row() * CELL_H;
            addRenderableWidget(Button.builder(Component.literal(cell.face().label()), button -> activeFace = cell.face())
                .bounds(x + 4, y + 2, 44, 14).build());
            addRenderableWidget(Button.builder(Component.literal("-"), button -> adjust(cell.face(), -1))
                .bounds(x + 4, y + 19, 20, 14).build());
            addRenderableWidget(Button.builder(Component.literal("+"), button -> adjust(cell.face(), 1))
                .bounds(x + 28, y + 19, 20, 14).build());
        }
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        graphics.fill(panelX, panelY, panelX + PANEL_W, panelY + PANEL_H, 0xC0101010);
        ClientSelectionState.SelectionDimensions dimensions = ClientSelectionState.dimensions();
        String heading = "CW Build Area  " + dimensions.width() + "x" + dimensions.height() + "x" + dimensions.depth();
        graphics.drawString(font, heading, panelX + 6, panelY + 5, 0xFFFFFFFF, false);
        graphics.drawString(font, "+ outward / - inward   Esc closes", panelX + 6, panelY + 16, 0xFFB8C0C8, false);

        for (FaceCell cell : CELLS) {
            int x = panelX + 4 + cell.column() * CELL_W;
            int y = panelY + HEADER_H + cell.row() * CELL_H;
            int color = cell.face() == activeFace ? 0x805A6A78 : 0x50303030;
            graphics.fill(x + 1, y, x + CELL_W - 1, y + CELL_H - 1, color);
        }
        super.render(graphics, mouseX, mouseY, partialTick);
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == GLFW.GLFW_KEY_KP_ADD || keyCode == GLFW.GLFW_KEY_EQUAL) {
            adjust(activeFace, 1);
            return true;
        }
        if (keyCode == GLFW.GLFW_KEY_KP_SUBTRACT || keyCode == GLFW.GLFW_KEY_MINUS) {
            adjust(activeFace, -1);
            return true;
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    @Override
    public boolean isPauseScreen() {
        return false;
    }

    private void adjust(SelectionFace face, int delta) {
        activeFace = face;
        ClientSelectionState.requestAdjustment(face, delta);
    }

    private record FaceCell(SelectionFace face, int column, int row) {}
}
