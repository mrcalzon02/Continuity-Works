from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "modules" / "continuityworks_runtime" / "forge-1.20.1" / "src" / "main"
JAVA = RUNTIME / "java" / "io" / "continuityworks" / "blueprint" / "runtime"
RESOURCES = RUNTIME / "resources"


class SelectionEditorSourceTests(unittest.TestCase):
    def read(self, path: Path) -> str:
        self.assertTrue(path.is_file(), f"missing required selection-editor source: {path}")
        return path.read_text(encoding="utf-8")

    def test_unfolded_cube_has_all_six_faces(self) -> None:
        face = self.read(JAVA / "SelectionFace.java")
        for name in ("UP", "DOWN", "NORTH", "SOUTH", "WEST", "EAST"):
            self.assertIn(f'{name}("{name}")', face)

        screen = self.read(JAVA / "SelectionEditorScreen.java")
        expected_cells = (
            "SelectionFace.UP, 1, 0",
            "SelectionFace.WEST, 0, 1",
            "SelectionFace.NORTH, 1, 1",
            "SelectionFace.EAST, 2, 1",
            "SelectionFace.SOUTH, 3, 1",
            "SelectionFace.DOWN, 1, 2",
        )
        for cell in expected_cells:
            self.assertIn(cell, screen)
        self.assertIn("panelX = 6", screen)
        self.assertIn("height - PANEL_H - 6", screen)
        self.assertIn('Component.literal("-")', screen)
        self.assertIn('Component.literal("+")', screen)

    def test_plus_means_outward_and_minus_means_inward(self) -> None:
        store = self.read(JAVA / "ContinuityWorksSelectionStore.java")
        expected = (
            "case UP -> maxY = moved(maxY, outwardDelta);",
            "case DOWN -> minY = moved(minY, -outwardDelta);",
            "case NORTH -> minZ = moved(minZ, -outwardDelta);",
            "case SOUTH -> maxZ = moved(maxZ, outwardDelta);",
            "case WEST -> minX = moved(minX, -outwardDelta);",
            "case EAST -> maxX = moved(maxX, outwardDelta);",
        )
        for line in expected:
            self.assertIn(line, store)
        self.assertIn("current.volume().volumeId()", store)
        self.assertIn("epochs.merge(owner, 1L, Long::sum)", store)
        self.assertIn("Cannot shrink a Continuity Works selection below one block", store)
        self.assertIn("validate(player, a, b)", store)

    def test_edits_are_server_authoritative(self) -> None:
        network = self.read(JAVA / "ContinuityWorksSelectionNetwork.java")
        packet = self.read(JAVA / "SelectionAdjustPacket.java")
        client = self.read(JAVA / "ClientSelectionState.java")
        self.assertIn('private static final String PROTOCOL = "2"', network)
        self.assertIn("NetworkDirection.PLAY_TO_SERVER", network)
        self.assertIn("CHANNEL.sendToServer(new SelectionAdjustPacket", network)
        self.assertIn("ContinuityWorksSelectionStore.INSTANCE.adjustFace", packet)
        self.assertIn("ContinuityWorksSelectionNetwork.sync(player)", packet)
        self.assertIn("ContinuityWorksSelectionNetwork.requestAdjustment(face, delta)", client)

    def test_editor_and_highlight_fail_closed_without_selection(self) -> None:
        client = self.read(JAVA / "ClientSelectionState.java")
        self.assertIn("no selected build volume to edit", client)
        self.assertIn("no selected build volume to highlight", client)
        self.assertIn("minecraft.setScreen(new SelectionEditorScreen())", client)
        self.assertIn("minecraft.screen instanceof SelectionEditorScreen", client)

    def test_editor_hotkey_and_language_are_registered(self) -> None:
        keys = self.read(JAVA / "ContinuityWorksSelectionClientModEvents.java")
        events = self.read(JAVA / "ContinuityWorksSelectionClientEvents.java")
        lang = self.read(RESOURCES / "assets" / "continuityworks_blueprint" / "lang" / "en_us.json")
        self.assertIn("OPEN_SELECTION_EDITOR", keys)
        self.assertIn("GLFW.GLFW_KEY_G", keys)
        self.assertIn("KeyConflictContext.IN_GAME", keys)
        self.assertIn("OPEN_SELECTION_EDITOR.consumeClick()", events)
        self.assertIn('"key.continuityworks_blueprint.open_selection_editor"', lang)


if __name__ == "__main__":
    unittest.main()
