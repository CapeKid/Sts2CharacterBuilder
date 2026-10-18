# Ancient dialogue

Optional `design/dialogue.json` follows [dialogue.schema.json](dialogue.schema.json).
Enable `features.dialogue`, author original lines, then run `validate` and `generate`.
Missing or empty data generates no dialogue file or dialogue patches. Enabled empty data
remains an implementation gap. Disabling the feature requires clearing its data.

```json
[
  {
    "ancient": "NEOW",
    "visit": "first",
    "lines": [
      {"speaker": "Ancient", "text": "The climb begins here.", "next": "Answer"},
      {"speaker": "Character", "text": "Then I am ready."}
    ]
  }
]
```

Supported Ancient entries are `NEOW`, `DARV`, `TEZCATARA`, `OROBAS`, `PAEL`,
`NONUPEIPE`, `TANX` and `VAKUU`. Each may have one `first` and one `repeat`
conversation. The game's character visit count selects first at zero (or below),
repeat thereafter. Total visits and the native “allow any character” selector do
not suppress an explicitly authored conversation. No new saved state is added.
These are dialogue conditions, not a progression system.

Each conversation has 1–12 nonblank lines, speakers `Ancient` or `Character`,
and optional `next` labels before the final line. Missing labels use `Continue`.
The final line hands off to the native Ancient reward buttons and cannot specify
`next`. Text is bounded to 1,000 characters per line and labels to 80. Native
formatting markup may be used; no project-specific interpolation variables are
provided. Review text wrapping, markup, voice and legibility in the game.

The generated `src/Generated/Dialogue.cs` identifies sets through the native
Ancient getter and replaces only the selected project's character/Ancient/visit
combination. Omitted visits, unconfigured Ancients, anonymous sets and other
characters retain the native result, including native empty behavior. Rewards,
Ancient cards, encounters and eligibility are not replaced. English text is
merged into namespaced keys in the active localization table on selection, so a
language change still receives the authored English fallback. The character template also restores this assembly's inline model localization before native locale-change UI listeners run; character/card/item text survives switching languages and switching back. Translations,
voice/SFX, custom Ancients, victory/ending text and The Architect's separate ending
dialogue require project-owned extensions and separate evidence.

Dialogue data, generated code and toolkit pins participate in evidence hashes.
Editing lines requires regeneration, a fresh build and a fresh native lab. Normal
packages contain the embedded authored text; no copied native text or game assets
are distributed. Generated file ownership rules apply; customize authoring data
or `src/Extensions`, never the generated file.

The native suite checks first/repeat/late-repeat selection, other-character and
omitted-content fallback against the unpatched native selector, anonymous empty
sets, every authored conversation's visible text/speakers/next labels, native
advance controls, reward-button access, and native checkpoint reload/replay.
Reloading a checkpoint replays the conversation from its beginning; line position
is not independently persisted. These synthetic solo fixtures do not establish
campaign behavior, translated layout quality, physical controller usability or
online co-op correctness. Keep those review gaps explicit.
