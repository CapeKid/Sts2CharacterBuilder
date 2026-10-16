# Private staging and Workshop delivery

The portable CLI produces a private-test ZIP, not a published Workshop item. In-game lifecycle, balance, device and branch evidence must be reviewed before making release claims. The inherited publishers remain reference-mod tools and must not be invoked for a new character.

1. Run structural checks and a native build against the selected installed game. Inspect the package report, DLL/reference hashes, provenance and known gaps. `stage` ships only an explicit allowlist; neither game DLLs nor BaseLib are bundled.
2. Download an official [Mega Crit mod uploader](https://github.com/megacrit/sts2-mod-uploader) release, record its version/hash, and initialize a **new project-owned** workspace using its supplied instructions. Use the workspace's actual `workshop.json` schema rather than a guessed one.
3. Extract the staged ZIP into the workspace's `content/`. Provide a project preview named `image.png` under 1 MB, credits, dependency declaration and description. Select private visibility in the uploader workspace. Inspect `mod_id.txt`: a new item has no inherited marker; an update must match the project's explicitly selected existing item. Never copy the reference mod's marker/configuration.
4. With publication authorized for this project and visibility, run `ModUploader.exe upload -w <workspace-folder>` from the uploader directory. Preserve the item marker for later updates. Stop on failure and inspect the log before retrying; do not silently switch to a new item.
5. Authenticate to confirm the resulting item ID, owner and visibility. Subscribe/download to a separate directory and compare the content root containing the mod-ID folder:

```powershell
python tools/character-builder/scripts/character-builder.py --project . compare-delivery --directory "C:/downloaded/content"
```

This checks exact payload hashes and rejects extra/missing files. It does not prove Steam visibility, ownership or native correctness. Record those observations separately with the Workshop URL and package SHA-256. The official uploader's [instructions](https://github.com/megacrit/sts2-mod-uploader/blob/main/README.md) describe creation and existing-item updates; the uploader workspace remains the authority for release-specific fields.
