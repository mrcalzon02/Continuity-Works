# donjon dungeon.pl upstream reference

Upstream source: `https://donjon.bin.sh/code/dungeon/dungeon.pl`

The upstream file identifies itself as **Random Dungeon Generator by drow** and states that it is provided under the **Creative Commons Attribution-NonCommercial 3.0 Unported License**.

Because this API is intended to be reusable by unrelated projects and developers, including projects that may be commercial, the CC BY-NC code is **not linked into the native runtime implementation**. The native generator in `src/structure_capability/generators/dungeon.py` is an original implementation using general procedural-layout concepts (room packing, connectivity routing, modular quantization and fitness gates).

`fetch_donjon_reference.py` can retrieve the exact upstream source into this directory for comparison, research, or an explicitly noncommercial legacy provider. Do not silently combine that code into a commercial runtime without reviewing the license obligations.
