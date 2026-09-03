# Art Generation Record

## Source reference

`Art/Source/Gabriel_Bouldering_Concept.png` is the supplied visual brief and is preserved unchanged.

## Generated masters

The following masters were made with Codex's built-in image generation mode and then copied into the repository:

- `Gabriel_Leader_Master.png`
- `Gabriel_DOM_Master.png`
- `Gabriel_Gym_Hopper_Master.png`
- `Gabriel_Bouldering_Gym_Master.png`

## Prompt set

1. **Leader diplomacy:** Identity-preserving Civilization V leader diplomacy scene, landscape 3:2. Same young Asian male climber from the reference, charcoal shirt, chalked hand and chalk bag, warm late-afternoon mountain crag, painterly realism, three-quarter body slightly right of center, no UI, text, logo, or watermark.
2. **Dawn of Man:** Identity-preserving Civilization V loading art. Gabriel seated from behind on a high boulder at sunrise over a vast mountain valley, a distant subtle gym, painterly realism, subject in the right third, no UI, text, logo, or watermark.
3. **Gym Hopper:** Identity-preserving square unit portrait. Same climber in three-quarter rear view with backpack, shorts, climbing shoes, and chalk bag in an alpine boulder field, bright morning, full body and readable silhouette, no border, UI, text, or logo.
4. **Bouldering Gym:** Square stylized concept art of a modern timber-and-dark-metal alpine bouldering gym with a faceted climbing-wall facade, warm windows, cool teal dusk mountains, secondary people for scale, no text, signage, logo, UI, or border.

The leader, Dawn of Man, and gym masters still supply the three full-screen DXT5 images. The generated Gym Hopper master is retained as an archival source, but it is no longer used for an icon. None of these generated masters supplies an icon after the correction below.

## Concept icon correction — 2026-09-04

All colour icons now come directly from the supplied 1448×1086 concept sheet. No image generation or redrawing was used for this correction. `Tools/build_art.py` records explicit crop coordinates, preserves the original RGB artwork and gold frames, masks the outside corners, and independently resizes each crop into every required atlas size.

| Concept badge | Game asset / object atlas slot |
| --- | --- |
| Bottom-left Civ Icon | Civilization colour atlas, slot 0 |
| Bottom-left Leader Icon | Leader atlas, slot 0 |
| Gym Hopper | Object slots 0 (unit) and 4 (Try Something New) |
| Bouldering Gym | Object slot 1 |
| One More Go fist | Object slots 2 (project attack bonuses) and 7 (Determination stages) |
| Fresh Sets chalk bag | Object slot 3, retained for ability/UI use |
| Route Reading mountain | Object slots 5 (Hill Familiarity) and 6 (Route Reading) |

The concept has no separate Try Something New, Hill Familiarity, or Determination badges, so those promotions reuse the related concept symbols. Fresh Sets has no separate icon-bearing gameplay database row; its supplied badge is packaged in its existing atlas slot without adding a new UI or mechanic.

The civilization alpha icon and Gym Hopper unit flag are white silhouettes extracted from the concept's Gym Hopper motif. That badge repeats the civilization's climber-and-rock design without the background rocks in the larger civ portrait. Gold/teal colour separation, frame exclusion, and removal of small isolated specks produce the required transparent masks; no substitute figure is drawn.

Seven exact colour crops and two monochrome derivatives are saved in `Art/Source/Concept_Icons`. See `Art/Preview/Gabriel_Concept_Icons.png` for the 128px, 64px, and 32px preview. All 23 registered DDS atlases are rebuilt. The source sheet, full-screen art, SQL portrait indices, gameplay, and save state remain unchanged.

```powershell
python Tools/build_art.py --icons-only
python Tools/update_modinfo_hashes.py
python Tools/validate_database.py
```

The validator checks the concept SHA-256, exact source pixels, saved crop transparency, database-to-atlas slots, and byte-for-byte reproducibility of every DXT5 atlas. Source resolution is limited to the supplied sheet (roughly 116–167 pixels per main badge and 66 pixels for Route Reading); larger sizes are faithful resamples, not invented detail. In-game rendering still requires the manual presentation checks in `TESTING.md`.
