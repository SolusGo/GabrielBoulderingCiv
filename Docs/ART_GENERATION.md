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

`Tools/build_art.py` converts those masters into independently rendered DXT5 screens and atlases. Symbolic ability and promotion art is drawn deterministically by the build script so its silhouettes remain readable at 16–45 pixels.
