# Private staging and Workshop delivery

The portable CLI stages a private-test ZIP and prepares/checks an offline workspace for Mega Crit's official uploader. These commands never upload. In-game lifecycle, balance, device and branch evidence must be reviewed before making release claims. The inherited publishers remain reference-mod tools and must not be invoked for a new character.

## Prepare a private workspace

Create project-owned `publishing.json` using [publishing.schema.json](publishing.schema.json):

```json
{
  "schema_version": 1,
  "description": "Your reviewed Workshop description, credits and dependency instructions.",
  "preview": "assets/publishing/preview.png",
  "baselib_workshop_id": 1234567890,
  "tags": ["Characters"],
  "dependencies": [],
  "content_descriptors": [],
  "change_note": "First private test."
}
```

The numeric ID above is an example, not BaseLib's real item ID. Supply and verify the official BaseLib Workshop item ID; extra dependency IDs are optional. The title comes from `character.json`. Declare the preview PNG with its exact path, hash and provenance in `assets/manifest.json`; it must be smaller than 1,000,000 bytes. Preview changes affect the shared asset/build fingerprint. Description-only changes invalidate publication preparation without rebuilding gameplay. Review real preview appearance separately from structural PNG checks.

Download a matching archive from the official [v0.2.0 release](https://github.com/megacrit/sts2-mod-uploader/releases/tag/v0.2.0). The toolkit pins all five official platform archives by SHA-256 in [uploader-release.json](uploader-release.json), alongside source commit `4c4db1262cdce6a1c4550a494f2e1088dbeda346`. Preparation verifies bytes rather than trusting the filename. It extracts the verified official tool under the private workspace, never into uploaded `content/`. Updating this pin requires a reviewed toolkit upgrade.

```powershell
python tools/character-builder/scripts/character-builder.py --project . prepare-publish --workspace first-private --uploader-archive "C:/downloads/ModUploader-win-x64.zip"
python tools/character-builder/scripts/character-builder.py --project . check-publish --workspace first-private
```

The workspace is `private/workshop/first-private/`. It contains the exact closed staged payload under `content/<mod-id>/`, `workshop.json`, your `image.png`, the verified tool/archive under `tools/`, and a preparation receipt. Private visibility is fixed by this adapter. Native/balance/device gaps remain open. The `publish` workflow step becomes `ready`, with hashes of metadata, content, tools and receipt; preparation never marks it complete. Output includes an argument array and working directory for the later official command, without executing it.

New-item preparation omits `mod_id.txt` and ignores unrelated markers/configuration elsewhere in the project. To prepare an update, put the project's explicitly selected `existing_item_id` in `publishing.json` and pass the same integer with `--existing-item` to both commands. The generated marker contains that exact ID. This is identity selection, not authenticated proof of ownership. Verify ownership and publication authorization before uploading. A mismatched/missing selection fails before creating the workspace.

Existing workspace names are refused, preserving their files and item markers. Prepare a new named snapshot for changed metadata/content or a later update. A write failure retains a partial directory for inspection; choose a new name rather than overwriting it. `check-publish` rebuilds the expected staged inventory and rechecks the stored official archive, tool bytes, preview, metadata and item marker. It rejects stale preparation, changed files, links and unexpected files, including an edited package report. The receipt alone is not trusted as a replacement for pinned tool bytes or current staged content. Run the check immediately before an authorized upload; uploader logs/marker changes after execution can make the prepared snapshot differ.

## Upload and verify delivery

1. Run structural checks and a native build against the selected installed game. Inspect the package report, DLL/reference hashes, provenance and known gaps. `stage` ships only an explicit allowlist; neither game DLLs nor BaseLib are bundled.
2. Prepare and check a **new project-owned** private workspace with the commands above. The adapter uses the pinned release's actual configuration fields. Alternatively follow a separately reviewed official release's instructions manually and record its exact version/hash; unsupported archive bytes are deliberately refused by the adapter.
3. Review the prepared description, preview, dependencies, credits and licenses. Inspect `mod_id.txt`: a new item has no marker; an update must match the project's explicitly selected existing item. Never copy the reference mod's marker/configuration. Public/unlisted/friends-only publication is outside the private preparation adapter; deliberately review those metadata changes and authorization separately rather than claiming they pass its private preflight.
4. With publication authorized for this project and visibility, run `ModUploader.exe upload -w <workspace-folder>` from the uploader directory. Preserve the item marker for later updates. Stop on failure and inspect the log before retrying; do not silently switch to a new item.
5. Authenticate to confirm the resulting item ID, owner and visibility. Subscribe/download to a separate directory and compare the content root containing the mod-ID folder:

```powershell
python tools/character-builder/scripts/character-builder.py --project . compare-delivery --directory "C:/downloaded/content"
```

This checks exact payload hashes and rejects extra/missing files. It does not prove Steam visibility, ownership or native correctness. Record those observations separately with the Workshop URL and package SHA-256. The official uploader's [instructions](https://github.com/megacrit/sts2-mod-uploader/blob/main/README.md) describe creation and existing-item updates; the uploader workspace remains the authority for release-specific fields.
