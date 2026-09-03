"""Regenerate the modinfo Files section with current MD5 hashes."""

from __future__ import annotations

import hashlib
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODINFO = ROOT / "Gabriel The Relentless Projector (v 1).modinfo"


def digest(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest().upper()


def should_list(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    if relative in {".gitignore", MODINFO.name}:
        return False
    if any(part.startswith(".") for part in path.relative_to(ROOT).parts):
        return False
    if "__pycache__" in path.parts or path.suffix == ".pyc":
        return False
    return path.is_file()


def import_value(relative: str) -> str:
    if relative == "Art/Gabriel_LeaderScene.xml":
        return "1"
    if relative.startswith("Art/Atlases/") and relative.endswith(".dds"):
        return "1"
    if relative.startswith("Art/Screens/") and relative.endswith(".dds"):
        return "1"
    return "0"


def indent(element: ET.Element, level: int = 0) -> None:
    whitespace = "\n" + "  " * level
    if len(element):
        if not element.text or not element.text.strip():
            element.text = whitespace + "  "
        for child in element:
            indent(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = whitespace
    if level and (not element.tail or not element.tail.strip()):
        element.tail = whitespace


def main() -> None:
    tree = ET.parse(MODINFO)
    root = tree.getroot()
    files = root.find("Files")
    if files is None:
        raise RuntimeError("modinfo is missing its Files element")
    files.clear()
    paths = sorted(path for path in ROOT.rglob("*") if should_list(path))
    for path in paths:
        relative = path.relative_to(ROOT).as_posix()
        entry = ET.SubElement(
            files,
            "File",
            {"md5": digest(path), "import": import_value(relative)},
        )
        entry.text = relative
    indent(root)
    xml = ET.tostring(root, encoding="unicode", xml_declaration=False, short_empty_elements=True)
    MODINFO.write_text('<?xml version="1.0" encoding="utf-8"?>\n' + xml + "\n", encoding="utf-8")
    print(f"Updated {MODINFO.name} with {len(paths)} files.")


if __name__ == "__main__":
    main()
