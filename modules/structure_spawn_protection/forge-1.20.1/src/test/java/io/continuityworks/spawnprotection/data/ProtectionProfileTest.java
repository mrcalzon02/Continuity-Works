package io.continuityworks.spawnprotection.data;

import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import com.google.gson.JsonParseException;
import net.minecraft.resources.ResourceLocation;
import org.junit.jupiter.api.Test;

import java.util.Set;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertThrows;

final class ProtectionProfileTest {
    private static final ResourceLocation SOURCE = new ResourceLocation("continuityworks", "test_profile");
    private static final ResourceLocation STRUCTURE = new ResourceLocation("minecraft", "village_plains");

    @Test
    void constructorRejectsExclusionRadiusAboveSupportedMaximum() {
        assertThrows(IllegalArgumentException.class, () -> new ProtectionProfile(
            SOURCE,
            Set.of(STRUCTURE),
            Set.of(),
            Set.of(),
            null,
            32769,
            500,
            true,
            0
        ));
    }

    @Test
    void constructorRejectsJigsawRadiusAboveSupportedMaximum() {
        assertThrows(IllegalArgumentException.class, () -> new ProtectionProfile(
            SOURCE,
            Set.of(STRUCTURE),
            Set.of(),
            Set.of(),
            null,
            500,
            32769,
            true,
            0
        ));
    }

    @Test
    void parserRejectsDatapackRadiusAboveSupportedMaximum() {
        JsonObject json = profileJson();
        json.addProperty("exclusion_radius", 32769);
        json.addProperty("jigsaw_piece_exclusion_radius", 500);

        assertThrows(JsonParseException.class, () -> ProtectionProfile.parse(SOURCE, json));
    }

    @Test
    void parserRejectsDatapackJigsawRadiusAboveSupportedMaximum() {
        JsonObject json = profileJson();
        json.addProperty("exclusion_radius", 500);
        json.addProperty("jigsaw_piece_exclusion_radius", 32769);

        assertThrows(JsonParseException.class, () -> ProtectionProfile.parse(SOURCE, json));
    }

    @Test
    void supportedMaximumRemainsAccepted() {
        JsonObject json = profileJson();
        json.addProperty("exclusion_radius", 32768);
        json.addProperty("jigsaw_piece_exclusion_radius", 32768);

        assertDoesNotThrow(() -> ProtectionProfile.parse(SOURCE, json));
    }

    private static JsonObject profileJson() {
        JsonArray namespaces = new JsonArray();
        namespaces.add("minecraft");

        JsonObject selectors = new JsonObject();
        selectors.add("namespaces", namespaces);

        JsonObject json = new JsonObject();
        json.add("selectors", selectors);
        return json;
    }
}
