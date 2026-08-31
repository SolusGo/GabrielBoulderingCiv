"""Build Civilization V DDS screens and icon atlases from the project masters.

Requires Pillow 12+. Run from the repository root. Every atlas size is rendered
directly from a source master or vector recipe; no output is resized from a
smaller output.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Art" / "Source"
ATLASES = ROOT / "Art" / "Atlases"
SCREENS = ROOT / "Art" / "Screens"
PREVIEW = ROOT / "Art" / "Preview"

RESAMPLE = Image.Resampling.LANCZOS
DARK = (9, 32, 38, 255)
DARKER = (3, 13, 17, 255)
GOLD = (211, 158, 67, 255)
PALE_GOLD = (245, 213, 139, 255)
CHALK = (221, 218, 205, 255)
TEAL = (30, 91, 101, 255)


def cover(image: Image.Image, size: tuple[int, int], center=(0.5, 0.5)) -> Image.Image:
    src = image.convert("RGBA")
    ratio = max(size[0] / src.width, size[1] / src.height)
    resized = src.resize((round(src.width * ratio), round(src.height * ratio)), RESAMPLE)
    left = round((resized.width - size[0]) * center[0])
    top = round((resized.height - size[1]) * center[1])
    left = max(0, min(left, resized.width - size[0]))
    top = max(0, min(top, resized.height - size[1]))
    return resized.crop((left, top, left + size[0], top + size[1]))


def save_dds(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGBA").save(path, format="DDS", pixel_format="DXT5")


def circular_photo(source: Image.Image, size: int, center=(0.5, 0.5)) -> Image.Image:
    supersample = 4
    large = size * supersample
    inset = round(large * 0.07)
    ring = max(3, round(large * 0.025))
    canvas = Image.new("RGBA", (large, large), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.ellipse((0, 0, large - 1, large - 1), fill=DARKER, outline=GOLD, width=ring * 2)
    portrait = cover(source, (large - inset * 2, large - inset * 2), center)
    mask = Image.new("L", portrait.size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, portrait.width - 1, portrait.height - 1), fill=255)
    portrait.putalpha(mask)
    canvas.alpha_composite(portrait, (inset, inset))
    draw.ellipse((inset, inset, large - inset - 1, large - inset - 1),
                 outline=PALE_GOLD, width=ring)
    return canvas.resize((size, size), RESAMPLE)


def climber_mark(size: int, alpha_only: bool = False) -> Image.Image:
    """Render the civilization's climbing silhouette at a requested size."""
    supersample = 4
    n = size * supersample
    s = n / 256.0
    transparent = (0, 0, 0, 0)
    canvas = Image.new("RGBA", (n, n), transparent if alpha_only else DARK)
    draw = ImageDraw.Draw(canvas)
    ink = (255, 255, 255, 255) if alpha_only else GOLD
    width = max(4, round(14 * s))

    if not alpha_only:
        draw.ellipse((4 * s, 4 * s, 252 * s, 252 * s), fill=DARK,
                     outline=GOLD, width=max(3, round(7 * s)))
        draw.ellipse((15 * s, 15 * s, 241 * s, 241 * s),
                     outline=(105, 73, 28, 255), width=max(2, round(3 * s)))

    # Head and torso leaning into the wall.
    draw.ellipse((117 * s, 43 * s, 153 * s, 79 * s), fill=ink)
    draw.line((128 * s, 79 * s, 105 * s, 137 * s), fill=ink, width=width + round(4 * s))
    # Right arm reaching for the final hold; left arm bracing.
    draw.line((122 * s, 91 * s, 169 * s, 61 * s, 187 * s, 35 * s), fill=ink, width=width)
    draw.ellipse((180 * s, 25 * s, 194 * s, 41 * s), fill=ink)
    draw.line((116 * s, 99 * s, 78 * s, 83 * s, 58 * s, 101 * s), fill=ink, width=width)
    draw.ellipse((49 * s, 94 * s, 64 * s, 109 * s), fill=ink)
    # Hips and widely placed legs.
    draw.ellipse((91 * s, 126 * s, 119 * s, 151 * s), fill=ink)
    draw.line((101 * s, 143 * s, 65 * s, 176 * s, 39 * s, 207 * s), fill=ink, width=width + round(2 * s))
    draw.ellipse((28 * s, 201 * s, 48 * s, 215 * s), fill=ink)
    draw.line((109 * s, 143 * s, 149 * s, 166 * s, 181 * s, 202 * s), fill=ink, width=width + round(2 * s))
    draw.ellipse((174 * s, 197 * s, 195 * s, 211 * s), fill=ink)
    # Three small holds make the silhouette read as climbing rather than running.
    for x, y, rx, ry in ((42, 77, 10, 6), (188, 22, 9, 6), (190, 207, 11, 6)):
        draw.ellipse(((x - rx) * s, (y - ry) * s, (x + rx) * s, (y + ry) * s), fill=ink)

    return canvas.resize((size, size), RESAMPLE)


def symbolic_icon(size: int, kind: str) -> Image.Image:
    supersample = 4
    n = size * supersample
    s = n / 256.0
    canvas = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    ring = max(3, round(7 * s))
    line = max(4, round(12 * s))
    draw.ellipse((4 * s, 4 * s, 252 * s, 252 * s), fill=DARKER, outline=GOLD, width=ring)
    draw.ellipse((16 * s, 16 * s, 240 * s, 240 * s), outline=(87, 106, 89, 255), width=max(2, ring // 2))

    if kind == "one_more_go":
        # Chalked fist with a small upward spark.
        draw.rounded_rectangle((82 * s, 92 * s, 173 * s, 190 * s), radius=22 * s,
                               fill=CHALK, outline=GOLD, width=max(2, round(4 * s)))
        for x in (88, 108, 128, 148):
            draw.rounded_rectangle((x * s, 59 * s, (x + 22) * s, 119 * s),
                                   radius=10 * s, fill=CHALK)
        draw.polygon([(185 * s, 42 * s), (193 * s, 62 * s), (214 * s, 69 * s),
                      (195 * s, 79 * s), (190 * s, 101 * s), (179 * s, 81 * s),
                      (158 * s, 78 * s), (176 * s, 65 * s)], fill=GOLD)
    elif kind == "fresh_sets":
        # Chalk bag and fresh route dots.
        draw.ellipse((70 * s, 58 * s, 178 * s, 97 * s), fill=CHALK, outline=GOLD, width=ring)
        draw.polygon([(77 * s, 82 * s), (172 * s, 82 * s), (160 * s, 198 * s),
                      (91 * s, 198 * s)], fill=(93, 91, 81, 255), outline=GOLD)
        draw.arc((59 * s, 38 * s, 190 * s, 119 * s), 198, 342, fill=GOLD, width=line)
        for x, y in ((195, 73), (205, 110), (185, 142)):
            draw.ellipse(((x - 7) * s, (y - 7) * s, (x + 7) * s, (y + 7) * s), fill=PALE_GOLD)
    elif kind == "try_new":
        # Three holds and a changing path.
        for x, y in ((66, 177), (121, 119), (190, 67)):
            draw.ellipse(((x - 18) * s, (y - 12) * s, (x + 18) * s, (y + 12) * s), fill=GOLD)
        draw.line((70 * s, 161 * s, 112 * s, 129 * s, 177 * s, 78 * s), fill=CHALK, width=line)
        draw.polygon([(175 * s, 55 * s), (211 * s, 62 * s), (190 * s, 91 * s)], fill=CHALK)
    elif kind == "hill_familiarity":
        draw.polygon([(42 * s, 190 * s), (111 * s, 70 * s), (143 * s, 125 * s),
                      (171 * s, 84 * s), (220 * s, 190 * s)], fill=TEAL, outline=GOLD)
        draw.line((68 * s, 170 * s, 111 * s, 98 * s, 132 * s, 134 * s), fill=CHALK, width=line)
        draw.ellipse((103 * s, 87 * s, 119 * s, 103 * s), fill=CHALK)
    elif kind == "route_reading":
        draw.polygon([(35 * s, 190 * s), (104 * s, 61 * s), (146 * s, 135 * s),
                      (173 * s, 96 * s), (226 * s, 190 * s)], fill=TEAL, outline=GOLD)
        draw.line((54 * s, 188 * s, 88 * s, 154 * s, 116 * s, 163 * s,
                   145 * s, 126 * s, 182 * s, 141 * s, 208 * s, 109 * s),
                  fill=PALE_GOLD, width=line)
        draw.ellipse((200 * s, 99 * s, 218 * s, 117 * s), fill=PALE_GOLD)
    elif kind == "determination":
        draw.polygon([(128 * s, 42 * s), (202 * s, 128 * s), (128 * s, 216 * s),
                      (54 * s, 128 * s)], fill=TEAL, outline=GOLD)
        draw.polygon([(128 * s, 73 * s), (177 * s, 130 * s), (128 * s, 188 * s),
                      (79 * s, 130 * s)], fill=GOLD)
        draw.polygon([(128 * s, 91 * s), (158 * s, 128 * s), (128 * s, 164 * s),
                      (98 * s, 128 * s)], fill=DARKER)
    else:
        raise ValueError(f"Unknown icon kind: {kind}")

    return canvas.resize((size, size), RESAMPLE)


def add_dom_shading(image: Image.Image) -> Image.Image:
    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shade)
    for x in range(image.width):
        fraction = x / image.width
        alpha = round(145 * max(0.0, 1.0 - fraction / 0.62))
        draw.line((x, 0, x, image.height), fill=(0, 8, 12, alpha))
    return Image.alpha_composite(image, shade)


def build() -> None:
    leader = Image.open(SOURCE / "Gabriel_Leader_Master.png").convert("RGBA")
    dom_master = Image.open(SOURCE / "Gabriel_DOM_Master.png").convert("RGBA")
    hopper = Image.open(SOURCE / "Gabriel_Gym_Hopper_Master.png").convert("RGBA")
    gym = Image.open(SOURCE / "Gabriel_Bouldering_Gym_Master.png").convert("RGBA")

    diplomacy = cover(leader, (1600, 900), center=(0.50, 0.50))
    dom = add_dom_shading(cover(dom_master, (1600, 900), center=(0.50, 0.48)))
    map_image = cover(gym, (1600, 900), center=(0.50, 0.48))
    save_dds(diplomacy, SCREENS / "Gabriel_Diplomacy.dds")
    save_dds(dom, SCREENS / "Gabriel_DOM.dds")
    save_dds(map_image, SCREENS / "Gabriel_Map.dds")

    for size in (256, 128, 80, 64, 45, 32, 16):
        if size != 16:
            save_dds(climber_mark(size), ATLASES / f"Gabriel_Civ_{size}.dds")
        row = Image.new("RGBA", (size * 8, size), (0, 0, 0, 0))
        row.alpha_composite(circular_photo(hopper, size, center=(0.49, 0.48)), (0, 0))
        row.alpha_composite(circular_photo(gym, size, center=(0.50, 0.50)), (size, 0))
        row.alpha_composite(symbolic_icon(size, "one_more_go"), (size * 2, 0))
        row.alpha_composite(symbolic_icon(size, "fresh_sets"), (size * 3, 0))
        row.alpha_composite(symbolic_icon(size, "try_new"), (size * 4, 0))
        row.alpha_composite(symbolic_icon(size, "hill_familiarity"), (size * 5, 0))
        row.alpha_composite(symbolic_icon(size, "route_reading"), (size * 6, 0))
        row.alpha_composite(symbolic_icon(size, "determination"), (size * 7, 0))
        save_dds(row, ATLASES / f"Gabriel_Objects_{size}.dds")

    # Tight face crop for a readable leader portrait in the civ-select UI.
    leader_portrait = leader.crop((300, 70, 1050, 970))
    for size in (256, 128, 64):
        save_dds(circular_photo(leader_portrait, size, center=(0.5, 0.28)),
                 ATLASES / f"Gabriel_Leader_{size}.dds")

    for size in (128, 64, 48, 32, 24, 16):
        save_dds(climber_mark(size, alpha_only=True),
                 ATLASES / f"Gabriel_Civ_Alpha_{size}.dds")

    save_dds(climber_mark(32, alpha_only=True), ATLASES / "Gabriel_UnitFlag_32.dds")

    PREVIEW.mkdir(parents=True, exist_ok=True)
    preview = Image.new("RGB", (1600, 1120), (7, 18, 22))
    preview.paste(dom.convert("RGB").resize((960, 540), RESAMPLE), (0, 0))
    preview.paste(diplomacy.convert("RGB").resize((640, 360), RESAMPLE), (960, 0))
    preview.paste(map_image.convert("RGB").resize((640, 360), RESAMPLE), (960, 360))
    preview.paste(climber_mark(256).convert("RGBA"), (45, 715), climber_mark(256))
    object_preview = Image.open(ATLASES / "Gabriel_Objects_128.dds").convert("RGBA")
    preview.paste(object_preview, (355, 800), object_preview)
    preview.save(PREVIEW / "Gabriel_Art_Preview.png", optimize=True)


if __name__ == "__main__":
    build()
    print("Built Gabriel DDS screens, atlases, and preview.")
