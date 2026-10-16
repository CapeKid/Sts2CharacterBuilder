# Spire Legacy â€” Slay the Spire 2

Every climb ends. Your bloodline grows.

A custom character by **CapeKid** for solo and co-op on the regular and public-beta branches of **Slay the Spire 2**. Knight, Mage and Ranger heirs inherit traits and altered starters; crowns from each climb rebuild a permanent Family Manor. See [co-op setup and progression](docs/coop.md).

- **82 reward cards per class on regular, 85 on public-beta**, plus three basics. Each includes 34 shared family cards alongside class specialties. All 360 historical definitions, saved IDs and original illustrations are retained.
- 61 inherited traits, compatible inheritance, three new heirs after each climb and the first family's quick start.
- Six manor upgrades, family naming, visible banner emblems, full trait descriptions, confirmed purchases. Crown balances cannot be edited from the public Manor UI.
- Crowns reward completed progress and earned, unspent gold. Untouched or unfinished abandoned starts earn zero; a played combat loss retains participation credit. See [payout rules](docs/earned-crowns.md).
- Seven [Heir-exclusive relic drops](docs/heir-relics.md) support guarded attacks, exhaust, discard, mixed card types and class resources.
- Three [Heir potions](docs/heir-potions.md) support flexible defense, targeted Poison/Weak and one-use class resources, alongside a single shared potion pool.
- Native card, reward, shop and save integration; atomic family saves and backup recovery.
- Original trait icons, class badges, portraits, sprites and card art included in the mod. No game assets or extraction tools are distributed.
- Synesthesia's animated rainbow ring and paired cosmetic accents appear in combat, rest sites and shops. See the [complete trait-effect audit](docs/trait-effect-audit.md).

Supports **Slay the Spire 2 regular v0.107.1 and public-beta v0.111.0**. Requires **BaseLib 3.4.7**. The StS1 implementation remains as historical source; active releases now target StS2.

Both branches support the mod, but full native saves are not interchangeable: beta's 64-bit RNG data cannot load on regular's 32-bit save schema. Historical card data loads both ways; tested regular runs resume on beta. See the [card pool and branch-save audit](docs/adversarial-pools.md).

[Install, Steam Deck, Melty, Workshop, saves and build instructions](docs/sts2-port.md)

The port is a development release. Native automated and visual checks cover card registration, upgrades, inherited save round trips, combat effects, class mechanics, rewards, shops and manor controls. Full campaign balance, physical Deck gameplay and a Melty-installed launch still require verification. The Melty package is prepared with a Windows launch mapping; the Workshop package supports native Windows/Linux.

## Source

`sts2/` contains the native C# port. Design remains in `sheets/*.json`. Generate stable models with `scripts/sts2-generate.py`, build `sts2/SpireLegacy.csproj` and package with `scripts/sts2-package.py`. Your owned StS2 assemblies are local build dependencies and are not in Git. Original SVG trait/class icons are reproducible with `scripts/author-heir-icons.py`; see [icon provenance](docs/original-icons.md).

The active pools contain 187 distinct cards on regular and 196 on public-beta; the other historical definitions remain available to native model lookup and compatibility tools. [Pool guide](docs/card-pools.md), [card catalogue](docs/card-catalogue.md), [class mechanics and starter genetics](docs/classes-and-genes.md), [trait adaptations](docs/traits.md) and [manor balance](docs/manor-and-balance.md) describe the shared design. Their historical StS1 test results do not substitute for StS2 validation.

All 360 original illustrations are preserved. Current art-direction summaries replace the removed generation records. Review sheets: [Knight](media/card-art-knight.png), [Mage](media/card-art-mage.png), [Ranger](media/card-art-ranger.png).

Private game files, extracted content, logs, test saves and release archives are ignored. Never distribute owned game DLLs/PCKs or extracted images. The old StS1 Workshop item remains separate from the StS2 port.

Historical StS1 launchers, packagers and reconstruction writers fail before execution. Obsolete implementations and listing records have been removed; current configuration is exclusively under `sts2/`. See the [historical isolation audit](docs/historical-sts1-audit.md) before inspecting retired tools.

## License and credits

Original mod code and illustrations: **CapeKid, MIT**. Remixes with attribution are allowed. Slay the Spire 2 belongs to Mega Crit. The standalone StS2 package contains original mod assets; no extracted game assets are distributed.

BaseLib: Alchyr and contributors, MIT. universal-modder was used for development. The retired content-reader commands refuse execution; active StS2 packages do not include them. Historical StS1 source credits ModTheSpire and BaseMod; neither is required by the StS2 mod.
