# Card portraits

For optional relic/potion normal, outline and large artwork, use the separate [item artwork contract](ITEMS.md). Those assignments also require declared assets and `features.art`.

Each generated card can select its own SVG or PNG through an optional `portrait` property in `design/cards.json`:

```json
"portrait": "assets/cards/strike.png"
```

Add this property alongside `id`, `name`, `base` and the other card fields. Paths are project-relative, case-sensitive and must match an entry in `assets/manifest.json` exactly. The manifest records SHA-256, method, license and credit as described in [assets.schema.json](assets.schema.json). Nested directories and spaces are supported. Portraits require `features.art` to be enabled. Unknown paths, traversal, unsupported formats, changed hashes and portraits configured while art is disabled fail validation.

Keep supplied source art intact. Create a separate exported file if cropping or resizing is needed, and record its provenance. A 500×380 canvas matches the supplied card placeholder; inspect the actual in-game crop and readability before approving an export. The generator does not crop, resize, generate or overwrite art. Validation checks file structure, not composition or visual quality.

Omit `portrait` to use `assets/card.svg`, including when custom art is skipped. Required `assets/icon.svg` and `assets/card.svg` remain visible original fallbacks. Disabling custom art requires removing card portrait assignments; declared source assets can remain in the project. Adding a file to the manifest without assigning it to a card does not integrate that portrait.

Run `validate`, `generate`, `build` and the isolated native suite after assigning art. Generated cards return the selected texture through BaseLib's `CustomPortrait`. Runtime loading reads declared SVG/PNG bytes beside the DLL and caches textures by exact asset path; no Godot import or PCK is needed. A decode failure throws an explicit error rather than silently replacing supplied artwork. Base and upgraded cards share the selected portrait. There is no separate upgraded-art field in this contract.

Portrait assignments and declared bytes participate in build/evidence fingerprints. Changing either requires a fresh build and native lab. The native probe checks decoded pixels, dimensions, cache reuse and save/load identity for each generated card in both upgrade states. This is headless integration evidence; human visual review remains necessary. Staging preserves the exact declared asset bytes in the character ZIP.

After upgrading an existing toolkit pin, run `generate` to adopt the reviewed loader/template change. Preserve any edits rejected by generated-file ownership checks in `src/Extensions` before regenerating. Card model IDs do not change when art is assigned or removed.
