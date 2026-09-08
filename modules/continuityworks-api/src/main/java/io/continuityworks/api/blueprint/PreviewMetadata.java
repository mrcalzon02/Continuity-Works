package io.continuityworks.api.blueprint;

import java.util.Map;

public record PreviewMetadata(String title, String description, String styleId, Map<String, String> attributes) {
    public PreviewMetadata {
        title = title == null ? "Blueprint" : title;
        description = description == null ? "" : description;
        styleId = styleId == null ? "unspecified" : styleId;
        attributes = Map.copyOf(attributes == null ? Map.of() : attributes);
    }
}
