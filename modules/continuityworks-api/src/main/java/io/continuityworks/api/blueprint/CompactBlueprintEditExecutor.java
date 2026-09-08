package io.continuityworks.api.blueprint;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;

/** Deterministically applies a resolved semantic edit intent to compact IR. */
public final class CompactBlueprintEditExecutor {
    private CompactBlueprintEditExecutor() {}

    public static CompactBlueprintPlan parseAndApply(CompactBlueprintPlan source, String encodedIntent) {
        return parseAndApply(source, encodedIntent, CompactBlueprintModuleResolver.none());
    }

    public static CompactBlueprintPlan parseAndApply(
        CompactBlueprintPlan source,
        String encodedIntent,
        CompactBlueprintModuleResolver modules
    ) {
        return apply(source, CompactEditIntentCodec.parse(encodedIntent), modules);
    }

    public static CompactBlueprintPlan apply(CompactBlueprintPlan source, CompactEditIntent intent) {
        return apply(source, intent, CompactBlueprintModuleResolver.none());
    }

    public static CompactBlueprintPlan apply(
        CompactBlueprintPlan source,
        CompactEditIntent intent,
        CompactBlueprintModuleResolver modules
    ) {
        Objects.requireNonNull(source, "source");
        Objects.requireNonNull(intent, "intent");
        Objects.requireNonNull(modules, "modules");

        return switch (intent.action()) {
            case TRANSLATE -> CompactBlueprintModifier.translate(source, intent.offset());
            case ROTATE -> CompactBlueprintModifier.rotate(source, intent.rotation());
            case MIRROR -> CompactBlueprintModifier.mirror(source, intent.mirrorAxis());
            case PALETTE_REMAP -> CompactBlueprintModifier.remapPalette(source, Map.of(
                resolvePaletteKey(source, intent.fromPaletteKey()),
                resolvePaletteKey(source, intent.toPaletteKey())
            ));
            case COMPOSE -> CompactBlueprintModifier.compose(source, requireModule(modules, intent.moduleId()), intent.offset());
            case REPEAT -> CompactBlueprintModifier.repeat(
                source,
                requireModule(modules, intent.moduleId()),
                intent.repeatCount(),
                intent.offset(),
                intent.step()
            );
        };
    }

    private static CompactBlueprintModule requireModule(CompactBlueprintModuleResolver modules, String moduleId) {
        return modules.resolve(moduleId).orElseThrow(
            () -> new IllegalArgumentException("Unknown pre-authored compact module: " + moduleId)
        );
    }

    private static String resolvePaletteKey(CompactBlueprintPlan source, String requested) {
        Map<String, String> caseInsensitive = new HashMap<>();
        for (PaletteEntry entry : source.palette()) {
            String normalized = entry.key().toLowerCase(java.util.Locale.ROOT);
            String prior = caseInsensitive.putIfAbsent(normalized, entry.key());
            if (prior != null && !prior.equals(entry.key())) {
                throw new IllegalArgumentException("Compact plan has ambiguous case-insensitive palette keys: " + prior + " and " + entry.key());
            }
        }
        String resolved = caseInsensitive.get(requested.toLowerCase(java.util.Locale.ROOT));
        if (resolved == null) throw new IllegalArgumentException("Unknown compact palette key: " + requested);
        return resolved;
    }
}
