# Patch Notes

## Version 1 — Lifecycle and compatibility hardening — 2026-09-22

- Made Gym Hopper visit identity independent of initial `UnitSetXY`/`UnitCreated` ordering and migrated visit history before post-conversion movement.
- Preserved physical-unit visit history through capture, gifting, conversion, upgrade, save/load, and UnitID reuse without changing the +2 XP reward.
- Scoped `UnitCreated`, upgrade, and conversion persistence writes to Gabriel projectors and Gym Hopper state instead of every unit globally.
- Raised the Community Patch dependency floor to v151 while preserving the CP UUID and `maxversion=999`.
- Added fail-closed discovery of future Scout/Barracks auxiliary-table mechanics with explicit copied and filtered classifications.
- Added deterministic lifecycle regression models for callback permutations, save/load, UnitID reuse, project bonuses, and Fresh Sets Era keys.
- Corrected documentation for the intentionally human-only civilization selection; retained AI flavors for forced/debug compatibility.
- Kept the target-death army scan as the correctness-first fallback; One More Go, Fresh Sets, unit/building values, rewards, and all other balance are unchanged.

## Version 1 — Player-only civilization selection — 2026-09-06

- Set Gabriel Bouldering to remain human-playable while preventing the AI from selecting it.

## Version 1 — Concept icon correction — 2026-09-04

- Replaced the civilization, leader, unit, building, ability, and promotion icons with direct crops of the supplied concept artwork, retaining its original gold borders.
- Rebuilt all 23 registered atlas files and extracted the civilization alpha icon and unit flag from the supplied climber motif.
- Reused the concept's related badges for promotions without dedicated artwork; preserved all existing portrait indices and filenames.
- Added reproducible source crops, an icon preview, provenance documentation, and regression checks for exact concept pixels, atlas contents, VFS imports, and database slot mappings.
- Added an icons-only rebuild option and excluded Python bytecode caches from the mod manifest.
- Gameplay, localization, saves, full-screen art, and mod version are unchanged. Offline validation and visual asset inspection are covered; in-game presentation remains a manual check.

## Version 1 — Initial release

- Added Gabriel, The Relentless Projector, as leader of The Boulder Circuit.
- Implemented target-specific **One More Go** combat projects using Community Patch battle hooks.
- Added three visible Determination stages and exact +5%, +10%, and +15% temporary attack modifiers.
- Added 15 HP and 5 XP rewards for sending a target from Determination II or III.
- Implemented **Fresh Sets** for once-per-destination, once-per-Era land Trade Route Science and Culture.
- Added the **Gym Hopper** Scout replacement with 3 Movement, focused Hill mobility and defense, first-visit XP, and upgrade-safe Hill Familiarity.
- Added the **Bouldering Gym** Barracks replacement with Culture, Local Happiness, inherited training XP, and permanent Route Reading for trained land units.
- Added a hills start bias, science/defense/recon/training/trade-oriented AI flavors, full city and spy name lists, diplomacy responses, strategy text, and Civilopedia entries.
- Added custom civilization, leader, unit, building, ability, promotion, unit-flag, Dawn of Man, map, and diplomacy art.
- Added save/load reconciliation, target-death cleanup, capture handling, unit-ID generation keys, upgrade conversion handling, and mid-combat temporary-promotion cleanup.
- Added reproducible art and modinfo tooling plus database and asset validation.
