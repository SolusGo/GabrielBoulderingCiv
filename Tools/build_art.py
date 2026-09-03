"""Build Civ V DDS assets; all icons are extracted from the supplied concept.

Requires Pillow 12+. Every atlas size is rendered independently from its
original concept crop. No icon is redrawn or generated. Use --icons-only to
leave the full-screen art untouched while rebuilding icons and previews.
"""

import argparse
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Art" / "Source"
CONCEPT = SOURCE / "Gabriel_Bouldering_Concept.png"
CONCEPT_ICONS = SOURCE / "Concept_Icons"
ATLASES = ROOT / "Art" / "Atlases"
SCREENS = ROOT / "Art" / "Screens"
PREVIEW = ROOT / "Art" / "Preview"

RESAMPLE = Image.Resampling.LANCZOS

# Pixel coordinates in the unmodified 1448x1086 concept sheet. These bounds
# contain the existing gold frames, but not their labels or surrounding panels.
CONCEPT_ICON_BOXES = {
    "Civ": (18, 846, 174, 1008),
    "Leader": (189, 842, 350, 1009),
    "Gym_Hopper": (943, 851, 1060, 973),
    "Bouldering_Gym": (1068, 851, 1188, 973),
    "One_More_Go": (1194, 851, 1310, 973),
    "Fresh_Sets": (1317, 851, 1433, 972),
    "Route_Reading": (1167, 721, 1233, 787),
}

# Preserve the existing database portrait indices. Promotions without their
# own concept badge reuse the relevant supplied art instead of new symbols.
OBJECT_ICON_NAMES = (
    "Gym_Hopper",       # 0: unique unit
    "Bouldering_Gym",   # 1: unique building
    "One_More_Go",      # 2: temporary project attack bonuses
    "Fresh_Sets",       # 3: secondary ability
    "Gym_Hopper",       # 4: Try Something New
    "Route_Reading",    # 5: Hill Familiarity
    "Route_Reading",    # 6: Route Reading
    "One_More_Go",      # 7: Determination I / II / III
)
CIV_SIZES = (256, 128, 80, 64, 45, 32)
LEADER_SIZES = (256, 128, 64)
OBJECT_SIZES = (256, 128, 80, 64, 45, 32, 16)
ALPHA_SIZES = (128, 64, 48, 32, 24, 16)


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


def ellipse_mask(size: tuple[int, int], inset: int = 0) -> Image.Image:
    """An antialiased mask outside the existing badge, not a replacement frame."""
    scale = 4
    width, height = size
    mask = Image.new("L", (width * scale, height * scale), 0)
    ImageDraw.Draw(mask).ellipse(
        (inset * scale, inset * scale,
         (width - inset) * scale - 1, (height - inset) * scale - 1),
        fill=255,
    )
    return mask.resize(size, RESAMPLE)


def extract_concept_icons() -> dict[str, Image.Image]:
    """Keep every RGB pixel in each source badge; mask only its outside corners."""
    with Image.open(CONCEPT) as image:
        concept = image.convert("RGBA")
    if concept.size != (1448, 1086):
        raise ValueError("Concept dimensions changed; review the explicit icon crop bounds.")
    icons = {}
    for name, box in CONCEPT_ICON_BOXES.items():
        icon = concept.crop(box)
        icon.putalpha(ellipse_mask(icon.size))
        icons[name] = icon
    return icons


def fit_icon(source: Image.Image, size: int) -> Image.Image:
    """Contain the original badge, including its frame, without stretching it."""
    inset = max(1, round(size * 0.025))
    inner = size - inset * 2
    icon = ImageOps.contain(source, (inner, inner), RESAMPLE)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(icon, ((size - icon.width) // 2, (size - icon.height) // 2))
    return canvas


def extract_gold_symbol(badge: Image.Image) -> Image.Image:
    """Derive the white alpha/flag silhouette from the supplied gold motif.

    The interior ellipse excludes the gold frame. Gold-vs-teal chroma separates
    the actual climber and rock; small isolated texture specks are discarded.
    No hand-drawn replacement geometry is used.
    """
    width, height = badge.size
    matte = Image.new("L", badge.size, 0)
    source_pixels = badge.load()
    matte.putdata([
        round(max(0.0, min(1.0, (min(r - b, 2 * (g - b)) - 10) / 18.0)) * 255)
        for y in range(height) for x in range(width)
        for r, g, b, _ in (source_pixels[x, y],)
    ])
    interior = ellipse_mask(badge.size, inset=round(min(badge.size) * 0.11))
    matte = ImageChops.multiply(matte, interior)
    matte = matte.point(lambda value: 0 if value < 32 else value)

    # Keep sizeable pieces of the source symbol and remove isolated gold flecks.
    pixels = matte.load()
    visited = set()
    for y in range(height):
        for x in range(width):
            if (x, y) in visited or pixels[x, y] < 32:
                continue
            component = []
            pending = deque([(x, y)])
            visited.add((x, y))
            while pending:
                px, py = pending.popleft()
                component.append((px, py))
                for nx, ny in ((px - 1, py), (px + 1, py), (px, py - 1), (px, py + 1)):
                    if (0 <= nx < width and 0 <= ny < height
                            and (nx, ny) not in visited and pixels[nx, ny] >= 32):
                        visited.add((nx, ny))
                        pending.append((nx, ny))
            if len(component) < 16:
                for px, py in component:
                    pixels[px, py] = 0

    matte = matte.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    symbol = Image.new("RGBA", badge.size, (255, 255, 255, 0))
    symbol.putalpha(matte)
    bounds = matte.getbbox()
    if bounds is None:
        raise ValueError("No gold symbol found in the supplied concept badge.")
    return symbol.crop(bounds)


def object_atlas(icons: dict[str, Image.Image], size: int) -> Image.Image:
    row = Image.new("RGBA", (size * len(OBJECT_ICON_NAMES), size), (0, 0, 0, 0))
    for index, name in enumerate(OBJECT_ICON_NAMES):
        row.alpha_composite(fit_icon(icons[name], size), (index * size, 0))
    return row


def build_icons() -> dict[str, Image.Image]:
    icons = extract_concept_icons()
    # The Gym Hopper badge repeats the civ's motif without the background rocks
    # in the large civ portrait, making it the clean source for both UI masks.
    icons["Civ_Alpha"] = extract_gold_symbol(icons["Gym_Hopper"])
    icons["Unit_Flag"] = extract_gold_symbol(icons["Gym_Hopper"])
    CONCEPT_ICONS.mkdir(parents=True, exist_ok=True)
    for name, icon in icons.items():
        icon.save(CONCEPT_ICONS / f"Gabriel_{name}_Concept.png", optimize=True)

    for size in CIV_SIZES:
        save_dds(fit_icon(icons["Civ"], size), ATLASES / f"Gabriel_Civ_{size}.dds")
    for size in LEADER_SIZES:
        save_dds(fit_icon(icons["Leader"], size), ATLASES / f"Gabriel_Leader_{size}.dds")
    for size in OBJECT_SIZES:
        save_dds(object_atlas(icons, size), ATLASES / f"Gabriel_Objects_{size}.dds")
    for size in ALPHA_SIZES:
        save_dds(fit_icon(icons["Civ_Alpha"], size), ATLASES / f"Gabriel_Civ_Alpha_{size}.dds")
    save_dds(fit_icon(icons["Unit_Flag"], 32), ATLASES / "Gabriel_UnitFlag_32.dds")
    return icons


def add_dom_shading(image: Image.Image) -> Image.Image:
    shade = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(shade)
    for x in range(image.width):
        fraction = x / image.width
        alpha = round(145 * max(0.0, 1.0 - fraction / 0.62))
        draw.line((x, 0, x, image.height), fill=(0, 8, 12, alpha))
    return Image.alpha_composite(image, shade)


def build_screens() -> None:
    leader = Image.open(SOURCE / "Gabriel_Leader_Master.png").convert("RGBA")
    dom_master = Image.open(SOURCE / "Gabriel_DOM_Master.png").convert("RGBA")
    gym = Image.open(SOURCE / "Gabriel_Bouldering_Gym_Master.png").convert("RGBA")
    save_dds(cover(leader, (1600, 900), center=(0.50, 0.50)), SCREENS / "Gabriel_Diplomacy.dds")
    save_dds(add_dom_shading(cover(dom_master, (1600, 900), center=(0.50, 0.48))),
             SCREENS / "Gabriel_DOM.dds")
    save_dds(cover(gym, (1600, 900), center=(0.50, 0.48)), SCREENS / "Gabriel_Map.dds")


def build_previews(icons: dict[str, Image.Image]) -> None:
    PREVIEW.mkdir(parents=True, exist_ok=True)
    preview = Image.new("RGB", (1600, 1120), (7, 18, 22))
    for filename, size, position in (
        ("Gabriel_DOM.dds", (960, 540), (0, 0)),
        ("Gabriel_Diplomacy.dds", (640, 360), (960, 0)),
        ("Gabriel_Map.dds", (640, 360), (960, 360)),
    ):
        with Image.open(SCREENS / filename) as screen:
            preview.paste(screen.convert("RGB").resize(size, RESAMPLE), position)
    civ = fit_icon(icons["Civ"], 256)
    preview.paste(civ, (45, 715), civ)
    with Image.open(ATLASES / "Gabriel_Objects_128.dds") as atlas:
        objects = atlas.convert("RGBA")
        preview.paste(objects, (355, 800), objects)
    preview.save(PREVIEW / "Gabriel_Art_Preview.png", optimize=True)

    # Native-size QA: all supplied badges plus their monochrome derivatives.
    names = tuple(CONCEPT_ICON_BOXES) + ("Civ_Alpha", "Unit_Flag")
    sheet = Image.new("RGB", (144 * len(names), 340), (14, 30, 35))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=14)
    for column, name in enumerate(names):
        center = column * 144 + 72
        draw.text((center, 166), name.replace("_", " "), font=font,
                  fill=(240, 221, 180), anchor="mt")
        for size, y in ((128, 24), (64, 205), (32, 292)):
            icon = fit_icon(icons[name], size)
            sheet.paste(icon, (center - size // 2, y), icon)
    sheet.save(PREVIEW / "Gabriel_Concept_Icons.png", optimize=True)


def build(icons_only: bool = False) -> None:
    if not icons_only:
        build_screens()
    icons = build_icons()
    build_previews(icons)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--icons-only", action="store_true")
    args = parser.parse_args()
    build(icons_only=args.icons_only)
    print("Built concept-derived Gabriel icons, DDS atlases, and previews.")
