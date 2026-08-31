# Manual Test Matrix

The offline validator covers database and asset integrity. The cases below should be exercised in Civilization V with only the Community Patch and this mod enabled, then repeated in a heavier mod set if desired.

## Setup and presentation

- [ ] Mod appears in the browser and refuses activation without the Community Patch dependency.
- [ ] The Boulder Circuit is selectable by a human and available to the AI.
- [ ] Civilization colour icon, alpha icon, leader portrait, map image, Dawn of Man image, unit/building icons, promotion icons, and Gym Hopper flag render without pink squares or atlas bleed.
- [ ] Static diplomacy scene loads and does not request missing audio.
- [ ] Dawn of Man, trait, strategy, Civilopedia sections, city names, spy names, and diplomacy lines resolve without raw `TXT_KEY` strings.
- [ ] Starting Settler, starting technologies, Palace, and hills region priority behave as expected.

## One More Go

- [ ] First nonlethal attack produces Determination I with no combat bonus on that first attack.
- [ ] Second attack by the same unit against the same target resolves with +5% and advances to Determination II if nonlethal.
- [ ] Third attack resolves with +10% and advances to Determination III if nonlethal.
- [ ] Fourth and later attacks remain capped at +15%.
- [ ] Attacking another enemy clears the old project and starts the new target at stack 1 only if it survives.
- [ ] Attacking a city clears the project and never starts a city project.
- [ ] Being attacked does not alter the defender's project.
- [ ] Waiting one complete turn preserves the project; waiting two complete turns clears it before a third idle turn.
- [ ] Killing a target from Determination I gives no send reward.
- [ ] Killing a target from Determination II or III heals exactly 15 HP, grants exactly 5 XP, and clears the project.
- [ ] Healing clamps correctly near full health.
- [ ] A kill made by another unit clears all projects aimed at that target without rewarding them.
- [ ] Capturing a projected unit clears the project without a send reward.
- [ ] Barbarian and City-State units can be projected.
- [ ] Naval, air, civilian, and city attackers cannot project.
- [ ] Ranged land attacks follow the same attempt sequence.
- [ ] Multiple Gabriel units can independently project the same target.
- [ ] Save and reload at each Determination stage preserves the target and timeout.
- [ ] Save/reload after combat leaves none of the hidden +5/+10/+15 promotions generically active.
- [ ] Upgrading an active projector transfers its valid project and visible Determination state.
- [ ] Gifting or capturing a projector clears UA state.

## Fresh Sets

- [ ] First outward land route to a destination pays Ancient 15 Science and 15 Culture at the next Gabriel turn.
- [ ] Keeping or re-establishing a route to the same destination in the same Era gives no duplicate reward.
- [ ] A different destination in the same Era pays once.
- [ ] Domestic, major-civilization, and City-State destinations all qualify.
- [ ] Sea routes never qualify.
- [ ] An incoming foreign route never qualifies for Gabriel.
- [ ] Classical through Information Era rewards are 20/25/30/35/40/45/50 of each yield.
- [ ] The same destination becomes eligible in a new Era.
- [ ] Capturing, razing, or refounding on the same plot cannot duplicate a reward within one Era.
- [ ] Save/load does not duplicate an already paid route.

## Gym Hopper

- [ ] Unit costs 30 Production and has 5 Strength, 3 Movement, and 2 Sight.
- [ ] Hills use the intended double-movement behavior and flat/rough non-Hill terrain does not receive global Scout movement immunity.
- [ ] The unit receives +15% Defense on Hills.
- [ ] First entry into each foreign major civilization grants 2 XP once.
- [ ] First entry into each City-State grants 2 XP once.
- [ ] Re-entering the same owner's territory grants no extra XP, including after save/load.
- [ ] Barbarian, unowned, and the unit owner's territory grant no visit XP.
- [ ] Two Gym Hoppers can each earn their own first-visit reward.
- [ ] A captured or gifted Gym Hopper continues to earn genuinely new first visits but cannot re-earn civilizations the physical unit already visited.
- [ ] Upgrade removes Try Something New and grants permanent +10% Hill Defense.
- [ ] A second later upgrade retains Hill Familiarity.

## Bouldering Gym and AI

- [ ] Building replaces Barracks, has the current CP Barracks cost/maintenance/technology, and supplies its normal training XP.
- [ ] Building provides +1 Culture and +1 Local Happiness.
- [ ] Newly trained land combat classes receive Route Reading; civilian, sea, and air units do not.
- [ ] Route Reading supplies +10% attack and defense on Hills only and survives upgrades.
- [ ] AI Gabriel explores, builds training infrastructure, and uses land routes without Lua errors.
- [ ] A late-game large-army turn shows no noticeable processing spike.

## Logs and regression checks

- [ ] `Database.log` contains no Gabriel SQL errors.
- [ ] `xml.log` contains no Gabriel reference failures.
- [ ] `Lua.log` contains no exceptions during combat, capture, route creation, unit conversion, upgrade, save, or load.
- [ ] Non-Gabriel civilizations retain normal Scouts, Barracks, unit combat, and trade-route yields.
