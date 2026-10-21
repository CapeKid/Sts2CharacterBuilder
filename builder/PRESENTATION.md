# Rest and shop presentation

Optional `design/presentation.json` follows [presentation.schema.json](presentation.schema.json). Set `features.presentation` true. Missing/`{}` data installs no presentation hooks; the original icon and native imagery remain available. Supply `rooms`, `selection` or both. A design needs at least one room or selection-art choice; omitted sections keep their native imagery.

```json
{
  "schema_version": 1,
  "rooms": {
    "rest": {
      "atlas": "assets/presentation/rest.png",
      "width": 128, "height": 96,
      "position": [0, 0], "scale_percent": 200, "filter": "nearest",
      "frames": [
        {"rect": [0, 0, 64, 96], "anchor": [32, 90]},
        {"rect": [64, 0, 64, 96], "anchor": [33, 90]}
      ],
      "states": {
        "idle": {"fps": 4, "frames": [0, 1]},
        "action": {"fps": 10, "frames": [1, 0]}
      }
    }
  }
}
```

The atlas must be an exact declared SVG/PNG asset with SHA-256 and provenance in `assets/manifest.json`. SVGs require explicit integer width/height and a viewBox. Crops, ground anchors, filter, frame count and timing follow the [combat atlas rules](SPRITES.md): up to 256 source frames, 64 indices/state, FPS 1–30, scale 10–400%, union bounds at most 512×512 local pixels, and action at most five seconds. `idle` loops; `action` restarts from frame zero and returns to idle. Room art is independent of combat sprites and can use a different atlas. No combat sprite feature or custom card/resource is required.

`position` is an integer `[x,y]` offset in the native character root's local units, each within −512…512. The authored ground origin follows the native body's position; horizontal facing mirrors the offset, scale and frame anchors together. Native room/viewport transforms still apply, so a local scale is not a promise of screen size. Review each room at 1280×800 and other supported aspect ratios. This contract does not resize native hitboxes, controls, thought bubbles or panels to match the art.

Generated `src/Generated/Presentation.cs` attaches one private `AnimatedSprite2D` per matching player scene after native initialization and hides that scene's native Spine body. Rest responses follow successful native option selections; failed selections do not animate. Native rest flips preserve the ground origin. Shop loop/nonloop animation requests map to idle/action; completed purchases restart action for the entry's owner, while rejected purchases do not. The code leaves native transactions, healing, controls and save data in place. Other characters and unconfigured rooms retain native visuals.

Each actor owns its frames/playback and uses cached atlas textures. Leaving/recreating a room releases/rebuilds the actor; reentering the scene tree starts idle. Actors use weak scene ownership and node signals, with no global per-frame room watcher or new saved state. A native rest pre-entry map checkpoint and full run reload reconstruct the authored actor at idle. Debug room entry alone does not bind the saved map coordinate and is not room-resume evidence. No Godot imports, editor export or PCK is required.

Selection art uses a separate optional section:

```json
{
  "schema_version": 1,
  "selection": {
    "portrait": "assets/selection/portrait.png",
    "locked_portrait": "assets/selection/locked.svg",
    "background": "assets/selection/background.svg",
    "background_fit": "contain"
  }
}
```

Each image is an exact declared SVG/PNG asset with provenance. Supply any subset of the three image roles. Unassigned roles retain native artwork; `background_fit` requires a background and accepts `cover` (default, crop to fill) or `contain` (preserve the whole image with unused space). Selection art requires neither room nor combat-sprite data. It owns `src/Generated/Selection.cs` and the reserved `ModEntry.InitializeSelection` partial method.

Native button initialization and lock/unlock controls refresh this character's assigned portrait. The animation-only lock uses locked art without changing unlock availability. A guarded replacement of the native unlock animation's single icon assignment keeps both the portrait and glow on authored art during the animation; other characters use the native getter. An unsupported native assignment layout is rejected instead of silently patching it. The native lock glyph, shaders, availability, focus and activation behavior stay native; artwork does not unlock a character. An unlocked, explicit selection of this character displays a noninteractive full-container texture behind the native information panel and controls. Locked and random selections retain native backgrounds. Switching to another character lets native selection replace the background normally. Cached image textures are shared; background nodes follow the native screen's lifecycle. This integration covers the selection screen, not the run-start transition or ending screens.

Run `validate`, `generate`, `generate --check`, an owned-game build and a fresh isolated native lab. Current native evidence must cover every configured room and selection-art role, selection/fallback controls and rest reconstruction on save/resume when authored. Native geometry/action checks do not establish art quality, human layout review, physical device navigation or co-op campaign behavior. Transition/ending imagery, energy counters, arms, trails and VFX still require extensions and their own evidence. Do not combine another body/selection-art replacer with the corresponding generated integration. Project-owned extensions must not implement the reserved generated initializers.
