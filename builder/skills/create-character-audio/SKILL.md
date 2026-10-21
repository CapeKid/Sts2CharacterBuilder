---
name: create-character-audio
description: Prepare and integrate supplied or generated character sound effects.
---

Ask whether sounds are wanted, gather supplied recordings and offer AI completion. Establish provider/budget before paid generation and record provenance.
Read [the audio contract](../../AUDIO.md). For short select/transition/attack/cast/death/hurt/victory effects, author optional `design/audio.json` with declared project-owned PCM16 WAV paths and bounded gain. Enable audio, validate and generate; omit individual cues to preserve native routes. Do not hand-edit generated Audio.cs or implement the reserved InitializeAudio partial method.
Review consistent perceived loudness and listen for distortion in context. Run the isolated native suite for actual routing, decoding, volume/mute, overlap and cleanup, including blocked/lethal damage, Fairy revival and once-per-combat victory controls; record audible observations separately. Automated/headless evidence is not a listening test. Use project-owned extensions for compressed/looped audio, music or unsupported routing, and verify those paths on the selected branch. An asset-manifest entry alone does not make a cue play. Keep environment-specific export tools in ignored local configuration.
Skip outcome: audio false; retain native runtime placeholder cues and disclose them.
