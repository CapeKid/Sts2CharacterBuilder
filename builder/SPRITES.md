# Combat sprites

Optional `design/sprites.json` follows [sprites.schema.json](sprites.schema.json).
Missing data or `{}` generates no sprite override or sprite hooks. Set
`features.sprites` to true before supplying an atlas design. Enabled empty data
remains a gap. Clear data before disabling the feature.

```json
{
  "schema_version": 1,
  "atlas": "assets/sprites/actor.png",
  "width": 128,
  "height": 96,
  "scale_percent": 200,
  "filter": "nearest",
  "frames": [
    {"rect": [0, 0, 64, 96], "anchor": [32, 90]},
    {"rect": [64, 0, 64, 96], "anchor": [33, 90]}
  ],
  "states": {
    "idle": {"fps": 4, "frames": [0, 1]},
    "attack": {"fps": 10, "frames": [0, 1]},
    "skill": {"fps": 10, "frames": [1]},
    "hurt": {"fps": 10, "frames": [1]},
    "death": {"fps": 4, "frames": [0, 1]},
    "victory": {"fps": 4, "frames": [0, 1]}
  }
}
```

The atlas must be a declared SVG/PNG asset with provenance and an exact path.
PNG dimensions come from its validated header. SVG atlases need explicit integer
`width`/`height` (unitless or `px`), as well as the normal asset SVG requirements.
Declared dimensions must match the decoded image. No imports, Godot editor or PCK
are needed. This integrates supplied artwork; it does not generate or repair art.

Frame rectangles are `[x, y, width, height]` in atlas pixels. Anchors are `[x, y]`
inside each cropped frame, usually the point on the ground between the feet.
Every frame is drawn at negative anchor offset, so differently cropped frames can
share a stable ground origin. Rectangles must be positive and stay inside the
atlas; anchors may touch frame edges. There are at most 256 source frames and 64
indices per state. Repeated indices are allowed. FPS is 1–30, scale is 10–400%,
and the union of all displayed frames must fit within 512 by 512 logical pixels.
This cap does not establish screen readability or prevent overlap with other UI.

All six states are required. Idle and victory loop; attack, skill and hurt return
to idle. One-shots, including death, are limited to five seconds. Death holds its
last frame and rejects later native triggers until explicit revive or creation of
a new visual. Repeating an attack/skill/hurt trigger restarts that action. Native
Cast/Powerup map to skill, Hit to hurt, and Dead/Die to death. Victory starts from
the game's `CombatWon` event. Scene removal detaches that event subscription.

Fairy in a Bottle is verified through native lethal damage and automatic potion
activation, not just a direct revive-animation call. The suite checks ordinary
lethal-hit recovery, recovery while the sprite is holding its death pose, and a
subsequent lethal hit with another Fairy. It requires the same visible authored
sprite/atlas, idle frame anchors and scale, correct HP restoration and consumption
of only the Fairy, plus a working attack and return to idle afterward. The held-pose
case is an explicit visual-state control, not a claim of a separate full death.

The generated `src/Generated/Sprites.cs` overrides only this character's combat
visual factory. It creates native bounds, intent/orb/talk/center markers and a form
VFX holder around an `AnimatedSprite2D`. BaseLib routes native animation triggers;
a narrowly scoped hook handles restart/death guards only for these sprite nodes.
Cached atlas textures are shared, while each visual owns its playback state.
Sprites add no saved state. Native save/resume reconstructs the visuals from the
character identity and current design; it does not resume an animation mid-frame.

Rest/shop art can use independent [room presentation data](PRESENTATION.md); short sounds use [audio data](AUDIO.md). Selection, defeat/victory screens, arms, trails and other unconfigured presentation retain disclosed native runtime fallbacks. Different atlases, skeletal
animation, custom shaders or unusual animation triggers require project-owned
extensions and their own evidence. Do not combine an extension factory override
with the generated factory override. No inherited mod identity or artwork ships.

Run `validate`, `generate` and `generate --check`, then build and use a fresh native
lab. Sprite data, asset bytes, generated code and toolkit pins invalidate evidence.
The suite checks decoded atlas pixels/cache, crops, anchors, bounds/markers, state
timing and visible pixels, native triggers/restarts, one-shot completion, death and
revive, actual combat victory, new-combat reset and save/resume reconstruction.
Current evidence must also contain all three Fairy revival cases; older sprite
receipts without this coverage are incomplete.
Human style/crop/1280x800 review, physical controls, online co-op, human room layouts
and final defeat/victory screens remain separate completion gates.
