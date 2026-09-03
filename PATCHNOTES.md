# Patch Notes

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
