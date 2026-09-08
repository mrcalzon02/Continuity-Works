package io.continuityworks.blueprint.runtime;

import io.continuityworks.api.blueprint.ContinuityWorksBlueprintServices;
import net.minecraftforge.fml.common.Mod;

@Mod(ContinuityWorksBlueprintMod.MOD_ID)
public final class ContinuityWorksBlueprintMod {
    public static final String MOD_ID = "continuityworks_blueprint";

    public ContinuityWorksBlueprintMod() {
        ContinuityWorksBlueprintServices.install(new ResourceBudgetedBlueprintApi());
    }
}
