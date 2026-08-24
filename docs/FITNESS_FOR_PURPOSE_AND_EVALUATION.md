# Fitness-for-Purpose and Evaluation

The default evaluation dimensions are:

- mechanical validity;
- accessibility;
- circulation;
- functional readability;
- purpose fit;
- geospatial fit;
- cultural consistency;
- structural plausibility;
- site infrastructure;
- progression/economy safety when relevant;
- worldgen suitability;
- performance budget;
- visual quality.

## Evidence discipline

A check can only prove what it tests.

Examples:
- NBT parsing does not prove circulation.
- Block count does not prove detail.
- a render does not prove loot or quest integration.
- an image similarity metric does not prove professional visual quality.
- structure-map resolution does not prove terrain integration.
- a hash proves identity of bytes, not quality.

## Evaluation outputs

Each gate returns:
- state (`PASS`, `REVISION_REQUIRED`, `REVIEW_NEEDED`, `BLOCKED`);
- evidence;
- uncertainties;
- accepted aspects to freeze;
- narrowest coherent revision scope;
- next action.

## Promotion

Require project-defined thresholds, but do not collapse `visual_quality = REVIEW_NEEDED` into a numeric pass merely to automate promotion.
