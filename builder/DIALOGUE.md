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
merged into namespaced keys in the active localization table on selection and before locale-change listeners run. Configured translations replace individual fields; other fields receive authored English fallback. The character template also restores this assembly's inline model localization before native locale-change UI listeners run; character/card/item text survives switching languages and switching back. Voice/SFX, custom Ancients and other victory/defeat text require project-owned extensions and separate evidence.

A conversation can add `translations`, an array of `{ "language": "fra", "lines": [...] }` entries. Each lines array must have exactly the English line count and keeps the English speakers/order. A translated line can override `text`, `next`, both, or neither (`{}`). Missing text uses English text; missing labels use the English label or `Continue`. Blank strings, repeated locales, all-empty translations and final-line next labels are rejected. English remains in the base `lines`; do not add an `eng` translation. Bounds remain 1,000 characters per text and 80 per label.

The pinned locale codes are `deu`, `esp`, `fra`, `ind`, `ita`, `jpn`, `kor`, `pol`, `ptb`, `rus`, `spa`, `tha`, `tur`, `zhs` and `zht`. They must exist in the selected owned build for native verification. Exact codes are used, with no language alias or regional fallback. The original [partial French/Japanese example](examples/translated-dialogue/dialogue.json) demonstrates field-level fallback and a separate English-only repeat conversation.

An open authored conversation refreshes its rendered text and next label when language changes, preserving its line index, speakers and sound-call count. The refresh touches only this mod's dialogue keys; it adds no progress/save data or reward behavior. Other inline character/card/item text retains the existing English behavior. Human translation, font/layout and voice review remain separate.

Dialogue data, generated code and toolkit pins participate in evidence hashes.
Editing lines requires regeneration, a fresh build and a fresh native lab. Normal
packages contain the embedded authored text; no copied native text or game assets
are distributed. Generated file ownership rules apply; customize authoring data
or `src/Extensions`, never the generated file.

The native suite checks first/repeat/late-repeat selection, other-character and
omitted-content fallback against the unpatched native selector, anonymous empty
sets, every authored conversation's visible text/speakers/next labels, native
advance controls, reward-button access, and native checkpoint reload/replay.
Translated conversations additionally run every configured locale, English and one unconfigured supported locale (if one remains). Checks inspect rendered labels, switch languages and back at every line without reselecting the conversation, preserve progress/sound calls, verify ordinary inline localization and replay each locale through the native checkpoint. Missing/duplicate/failed locale or locale-resume evidence is rejected. Reloading a checkpoint replays the conversation from its beginning; line position
is not independently persisted. These synthetic solo fixtures do not establish
campaign behavior, translated layout quality, physical controller usability or
online co-op correctness. Keep those review gaps explicit.

## Architect ending dialogue

`THE_ARCHITECT` additionally accepts one `first` and one `repeat` conversation in the same file. These use the native character win count (zero versus positive), rather than ordinary Ancient visit counts. This reads existing native statistics; it adds no saved state or progression mechanics. See the original [ending example](examples/ending-dialogue/dialogue.json), including a one-line repeat control.

The same 1–12 lines, speakers, optional nonfinal labels and final-label prohibition apply. Endings accept the same partial `translations` contract and locale codes as ordinary Ancient conversations. Missing fields/locales use authored English; speakers, line count and native attack metadata remain fixed. See the original [French/Japanese ending example](examples/translated-endings/dialogue.json). The last line leads to the native Proceed action rather than Ancient rewards. Omitted ending visits and other characters retain the exact native selected dialogue.

After the game selects its ending, the generator replaces only this character's authored lines and preserves the selected conversation's start/end attackers, visit index and repeat metadata. The game still owns combat-room speech bubbles, animations, line advancement and the Proceed/WinRun callback. Custom attack choreography, ending art, defeat text and alternate endings are outside this contract.

The native suite separately checks zero/one/100-win selection, foreign/omitted fallback by reference, exact native metadata, rendered speech and next labels, actual option-button advancement, a native pre-entry map checkpoint and replay from the first line after partial advancement, and exact equality with the native Proceed callback. A single-line ending also reaches Proceed. The current probe then invokes the actual final button and awaits native closing attacks and WinRun. Separate completion evidence checks exactly-once win/score/stat updates, saved winning history, removal of the completed checkpoint, native post-win result/score and character presentation, and return through the native menu button. Native save/history processing uses the isolated backend; test-only hooks keep the platform Architect statistic local and suppress telemetry/achievement reporting. Normal character packages contain none of these test hooks. Synthetic forced ending entry does not establish campaign reachability or balance. Missing, duplicate or failed ending/control/completion evidence is rejected. Translated endings require `ending-locale`, `ending-locale-resume` and `ending-locale-completion` evidence for every configured locale, English and one unconfigured supported fallback. Each case verifies rendered speech/next/Proceed labels, live switches and switch-back at every line, checkpoint replay and actual native ending completion. Text-only refresh keeps the same dialogue/options/callbacks, bubble, tween, lifetime and reveal ratio, without replaying speech or sounds. The fixture explicitly sets a fractional reveal ratio as a preservation control; it does not certify human animation quality. Human translation/font/layout, voice, physical controls, co-op and regular-branch checks remain separate.

If native selection is empty for a new character, an authored ending uses no opening attacks and both native closing attacks, with first/repeat visit metadata. Existing native selections keep their exact metadata. Omitted rows preserve even an empty native result; a missing ending is not evidence of campaign completion.
