# Licensing notice

This export package intentionally does **not** invent a license for either this new standalone project or material derived from the source repository.

Before publishing the standalone GitHub repository, select an appropriate license for the new API code and confirm that any source/reference material retained from Infinite Domain may be redistributed under that license.

`reference/infinite_domain/SOURCE_MANIFEST.json` records provenance and extraction roles so vendored/reference material can be separated or removed cleanly.

## donjon upstream reference

The requested upstream `https://donjon.bin.sh/code/dungeon/dungeon.pl` states in its own source header that it is provided under the **Creative Commons Attribution-NonCommercial 3.0 Unported License**.

For that reason, donjon code is not linked into the native reusable runtime. `reference/donjon/` contains attribution, the upstream URL, and a fetch helper so the source can be obtained as an isolated reference or explicitly noncommercial provider. The native modular dungeon engine is kept separate so this project does not silently acquire a noncommercial runtime restriction.
