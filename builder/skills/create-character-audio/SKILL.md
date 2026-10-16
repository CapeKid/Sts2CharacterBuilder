---
name: create-character-audio
description: Prepare and integrate supplied or generated character sound effects.
---

Ask whether sounds are wanted, gather supplied recordings and offer AI completion. Establish provider/budget before paid generation and record provenance.
Use project-owned WAV/OGG files with stable paths, consistent gain and no clipping. Listen to select/attack/skill/hurt/death/victory cues in context. Wire the selected branch's sound routing explicitly; an asset-manifest entry alone does not make a cue play.
The baseline generator does not route custom audio. Implement an extension and native audible checks for an enabled audio request. Keep environment-specific export tools in ignored local configuration.
Skip outcome: audio false; retain native runtime placeholder cues and disclose them.
