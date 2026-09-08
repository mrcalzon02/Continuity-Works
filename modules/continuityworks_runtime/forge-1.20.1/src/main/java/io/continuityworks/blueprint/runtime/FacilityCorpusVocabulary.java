package io.continuityworks.blueprint.runtime;

import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.Locale;
import java.util.Set;
import java.util.TreeSet;

/** Manifest-only vocabulary projection for tiny inference clients. */
final class FacilityCorpusVocabulary {
    private static final String MANIFEST = "continuityworks/facility_library/manifest.json";
    private volatile Snapshot snapshot;

    Snapshot snapshot() {
        Snapshot current = snapshot;
        if (current != null) return current;
        synchronized (this) {
            if (snapshot != null) return snapshot;
            return snapshot = load();
        }
    }

    private static Snapshot load() {
        try (InputStream in = FacilityCorpusVocabulary.class.getClassLoader().getResourceAsStream(MANIFEST)) {
            if (in == null) throw new IllegalStateException("Missing bundled facility manifest " + MANIFEST);
            JsonObject manifest = JsonParser.parseReader(new InputStreamReader(in, StandardCharsets.UTF_8)).getAsJsonObject();
            Set<String> categories = new TreeSet<>();
            Set<String> archetypes = new TreeSet<>();
            Set<String> references = new TreeSet<>();
            for (JsonElement element : manifest.getAsJsonArray("entries")) {
                JsonObject entry = element.getAsJsonObject();
                String kind = entry.get("kind").getAsString();
                String id = entry.get("id").getAsString();
                if ("archetype".equals(kind)) {
                    archetypes.add(slug(id));
                } else if ("facility_reference".equals(kind)) {
                    references.add(slug(id));
                    if (entry.has("category")) categories.add(normalize(entry.get("category").getAsString()));
                }
            }
            return new Snapshot(
                manifest.get("library_version").getAsString(),
                immutable(categories), immutable(archetypes), immutable(references)
            );
        } catch (IOException error) {
            throw new IllegalStateException("Unable to read bundled facility vocabulary", error);
        }
    }

    private static Set<String> immutable(Set<String> values) {
        return Collections.unmodifiableSet(new LinkedHashSet<>(values));
    }

    private static String slug(String id) {
        int slash = id.lastIndexOf('/');
        if (slash >= 0) return normalize(id.substring(slash + 1));
        int colon = id.lastIndexOf(':');
        return normalize(colon >= 0 ? id.substring(colon + 1) : id);
    }

    private static String normalize(String value) {
        return value.trim().toUpperCase(Locale.ROOT).replace('-', '_').replace(' ', '_');
    }

    record Snapshot(String libraryVersion, Set<String> categories, Set<String> archetypes, Set<String> references) {}
}
