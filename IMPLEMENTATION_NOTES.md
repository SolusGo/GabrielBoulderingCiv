# Implementation Notes

## Compatibility target

The mod targets Brave New World plus `(1) Community Patch` and declares that dependency in the modinfo. CP-only interfaces used by the runtime are:

- `GameEvents.BattleStarted`
- `GameEvents.BattleJoined`
- `GameEvents.BattleFinished`
- `GameEvents.UnitCaptured`
- `GameEvents.UnitUpgraded`
- `GameEvents.UnitConverted`
- `Player:GetTradeRoutes()` with structured route fields
- the `Buildings.TrainedFreePromotion` and `UnitPromotions.AttackMod` database columns

The implementation does not use full-Vox-Populi balance tables or UI components.
The core SQL explicitly enables the six listed CP event families because their
public options default to disabled in a CP-only install.

## One More Go state machine

Project state is stored per Gabriel attacker using owner and unit IDs:

- projected target owner
- projected target unit ID
- Determination stack count from 1 to 3
- game turn of the most recent valid attack

`BattleStarted` opens one transient battle record. `BattleJoined` identifies attacker and defender before strength calculation. If the combat is eligible and the defender matches the stored target, exactly one hidden `AttackMod` promotion is attached to the attacker. `BattleFinished` removes the hidden promotion and commits the result.

Failed attacks set or increment Determination. The first failure creates stack 1, so the second attack receives +5%; stack 2 gives the third attack +10%; stack 3 gives all later attempts +15%. A lethal attack rewards the unit only when the battle began at stack 2 or 3.

### Reset policy

- Attacking a different enemy unit clears the old project before combat.
- Attacking a city clears the project; cities cannot be projected.
- Defensive combat neither advances nor clears a project.
- Any projected unit's `UnitPrekill` event clears every Gabriel project aimed at it.
- `UnitCaptured` marks a captured defender so disappearance is not treated as a kill reward.
- At the start of Gabriel's third turn after the last attempt, two complete skipped turns have elapsed and the project clears.
- Missing target objects clear during turn reconciliation even if an unusual removal path skipped `UnitPrekill`.

Barbarian and City-State military units are eligible targets. Sea and air attackers cannot project, while all land combat classes—including ranged land units—can.

### Temporary promotion safety

The hidden combat modifier is deliberately not persistent. It is removed on `BattleFinished`, at the beginning of a later battle if a prior record exists, on every Gabriel turn, and when the Lua context initializes. This prevents a save taken in an unusual combat/UI window from leaving a generic combat bonus behind.

The normal pre-combat preview is drawn before the target-specific promotion is applied. Actual combat math is correct, but the stock preview does not include it. A custom combat-preview replacement was rejected because it would be substantially more fragile and conflict-prone than the mechanic itself.

## Fresh Sets

The Community Patch exposes a trade-route completion event, not a reliable universal route-establishment event. `PlayerDoTurn` therefore polls Gabriel's own active route list, which is small and bounded by trade-route capacity. It does not scan the map.

Each qualifying outward land route is keyed by Gabriel player ID, current Era, and destination plot coordinates. Coordinates were chosen over city IDs because city IDs can be recycled by capture and refounding. This prevents repeated capture/refound rewards in an Era. Adding the Era to the key makes all destinations eligible automatically when the Era changes without a cleanup scan.

Rewards use `ChangeOverflowResearch` and `ChangeJONSCulture`. The literal design values are not game-speed scaled. Domestic routes, major-civilization destinations, and City-State destinations are valid.

## Gym Hopper persistence

`UnitSetXY` evaluates only units whose current type is Gym Hopper. On first entry into land owned by each alive non-barbarian foreign player, a generation-scoped persistence key awards 2 XP. A per-unit generation counter prevents a newly created unit that reuses an old unit ID from inheriting visit records.

Gym Hopper lineage is stored separately. `UnitUpgraded` transfers any active Gabriel project, records lineage, and grants Hill Familiarity to the successor. Hill Familiarity is not lost on later upgrades. `UnitConverted` preserves lineage for gifting/capture while clearing One More Go state, because the UA belongs to Gabriel rather than to the acquired unit.

When an unupgraded Gym Hopper changes owners, its per-civilization visit flags
are copied to the new unit generation. The physical explorer therefore cannot
re-earn a civilization it already visited merely by being gifted or captured.

## Static database design

The Gym Hopper and Bouldering Gym are cloned at SQL activation time from the live Scout and Barracks rows. Temporary-table `SELECT *` cloning preserves CP-added columns and later base balance adjustments. Related AI, flavor, upgrade, and domain-experience rows are copied separately.

The Scout's global `PROMOTION_IGNORE_TERRAIN_COST` is excluded on purpose. Try Something New implements the specified Hill-only movement benefit with `HillsDoubleMove`.

Route Reading is restricted through `UnitPromotions_UnitCombats` to the eight land combat classes: Archer, Armor, Gun, Helicopter, Melee, Mounted, Recon, and Siege. It is installed through the CP `TrainedFreePromotion` column and persists on upgrade.

## Performance and AI

- No full-map loop is used.
- Battle work is constant-time except target death, which scans only Gabriel's current military roster to clear references.
- Per-turn work scans only Gabriel's units and active trade routes.
- The AI uses the unit and building normally. It cannot plan around a particular stored project as precisely as a human, but repeated attacks naturally receive the bonus and target switching safely resets it.
- The AI's high Recon, Training, Defense, Science, and Land Trade Route flavors align normal build and movement priorities with the kit.

## Multiplayer

The runtime is deterministic in its arithmetic and uses no random values. Nevertheless, project and visit records live in `Modding.OpenSaveData`, whose synchronization model is not suitable for promising network multiplayer safety. `SupportsMultiplayer` and `SupportsHotSeat` are therefore set to 0 rather than advertising an unverified mode.

## Art pipeline

The user-supplied concept board remains unmodified in `Art/Source`. Every colour icon is now extracted directly from that board, including the original gold border. Explicit source coordinates and stable atlas-slot mappings live in `Tools/build_art.py`; the seven colour crops and two monochrome derivatives are retained under `Art/Source/Concept_Icons`. Each required DDS size is rendered independently from its crop with aspect ratio preserved.

Try Something New reuses Gym Hopper, Hill Familiarity reuses Route Reading, and all Determination stages reuse the One More Go fist because the concept supplies no separate badges for those promotions. Fresh Sets remains available in object slot 3; no new UI is added. Both alpha/flag masks are extracted from the clean Gym Hopper climber motif. The offline validator verifies original colour pixels, crop transparency, portrait slots, and every encoded atlas against a fresh concept-derived rendering.

The existing generated masters still supply the 1600×900 diplomacy, Dawn of Man, and map screens, which this icon correction does not change. The static leader XML uses the diplomacy image as its fallback and no nonexistent audio is referenced. Use `--icons-only` when rebuilding just the icon assets; full art provenance is in `Docs/ART_GENERATION.md`.
