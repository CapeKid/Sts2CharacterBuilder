# Character sound effects

Optional `design/audio.json` follows [audio.schema.json](audio.schema.json). Set `character.json.features.audio` true and declare each sound with its exact path, SHA-256 and rights/provenance in `assets/manifest.json`.

```json
{
  "schema_version": 1,
  "cues": {
    "attack": {"asset": "assets/audio/strike.wav", "gain_percent": 60},
    "cast": {"asset": "assets/audio/cast.wav", "gain_percent": 45}
  }
}
```

Supported cues are `select`, `transition`, `attack`, `cast`, `death`, `hurt` and `victory`. Supply any subset; omitted cues retain their native placeholder routes. Missing or `{}` data generates no audio code or hooks. Enabled empty data remains an evidence gap. Set the feature false and clear the file to skip custom audio.

Clips must be complete RIFF PCM16 WAV files, mono/stereo, 8â€“48 kHz, nonempty and at most ten seconds. Metadata chunks may precede the sample data; a 44-byte header is not assumed. Truncated/duplicate chunks, unsupported encodings, silent clips and samples at either full-scale clipping endpoint fail validation. This endpoint check does not establish recording quality or prove that clipping never occurred earlier. Use a consistent perceived loudness, listen for distortion and record human observations. Compressed/looped audio, music and arbitrary FMOD parameters require separate extensions and evidence.

Run `generate` after authoring. Owned `src/Generated/Audio.cs` overrides only configured character getters, using BaseLib's custom attack/cast/death routes and the native selection/transition routes. A Harmony prefix handles only exact cue URIs containing this project's mod ID, in both native `NAudioManager.PlayOneShot` overloads. Other URIs and characters pass through. On v0.111.0 the native death sound is inside the Spine animator branch; a narrow StartDeathAnim hook supplies the configured death cue for this character when that animator is absent, matching the native repeat guard. It does not replace native Spine playback. Godot decodes the declared loose files without imports or a PCK; decoded streams are cached per asset, with a separate nonlooping player for each call.

`gain_percent` is 0â€“100; zero deliberately mutes a cue. Call volume is clamped to 0â€“1. Playback applies cue gain Ã— call volume Ã— masterÂ² Ã— SFXÂ², following the inspected native v0.111.0 slider curve. Active players follow settings changes each frame. At most eight voices from this character mod overlap; the oldest stops first. Finished players free themselves, and the frame callback detaches when none remain. This limits overlap; it does not guarantee that simultaneous sounds cannot clip the final output. Review the mix in context.

The native lab checks decoded samples/rate/channels, no looping, cache reuse, actual character getters and attack/cast/death commands, actual HP damage and combat victory, blocked/zero/foreign-target/direct-HP controls, lethal Fairy revival and subsequent hurt, duplicate victory callbacks and a fresh combat, both manager overloads, volume/mute changes, foreign-route controls, overlap and cleanup. A test-only two-second stream keeps mute/cleanup controls independent of authored clip duration; decoding/routing checks use the shipped clips. Selection/transition checks call the native manager with their getter results; they do not claim an interactive selection-screen review. Automated/headless checks do not prove audible quality or physical device behavior. Listen to every configured cue in the selected game branch, including death and subsequent revival, and keep unperformed reviews visible. No audio state is saved.
