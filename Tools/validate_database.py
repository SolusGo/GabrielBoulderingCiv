"""Validate Gabriel against a Civilization V debug database and built assets.

The script copies the supplied Civ5DebugDatabase.db into memory, applies the
mod's SQL, and checks the gameplay rows, localization, atlases, screens, and
modinfo hashes without altering the user's game cache.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

import build_art


ROOT = Path(__file__).resolve().parents[1]
MODINFO = ROOT / "Gabriel The Relentless Projector (v 1).modinfo"


class ValidationError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def scalar(db: sqlite3.Connection, query: str, params=()):
    row = db.execute(query, params).fetchone()
    return None if row is None else row[0]


def default_database() -> Path:
    return (
        Path.home()
        / "Documents"
        / "My Games"
        / "Sid Meier's Civilization 5"
        / "cache"
        / "Civ5DebugDatabase.db"
    )


def load_database(source: Path) -> sqlite3.Connection:
    require(source.is_file(), f"Civ V debug database not found: {source}")
    disk = sqlite3.connect(source)
    memory = sqlite3.connect(":memory:")
    disk.backup(memory)
    disk.close()
    # The debug cache does not always retain localization tables. A minimal
    # compatible table is sufficient for loading and validating this mod's text.
    memory.execute(
        "CREATE TABLE IF NOT EXISTS Language_en_US "
        "(Tag TEXT NOT NULL UNIQUE, Text TEXT)"
    )
    memory.execute(
        "CREATE TABLE IF NOT EXISTS CustomModOptions "
        "(Name TEXT NOT NULL UNIQUE, Value INTEGER, Class INTEGER, DbUpdates INTEGER)"
    )
    for name in (
        "EVENTS_BATTLES", "EVENTS_UNIT_CAPTURE", "EVENTS_UNIT_CONVERTS",
        "EVENTS_UNIT_CREATED", "EVENTS_UNIT_PREKILL", "EVENTS_UNIT_UPGRADES",
    ):
        memory.execute(
            "INSERT OR IGNORE INTO CustomModOptions(Name, Value, Class, DbUpdates) "
            "VALUES (?, 0, 3, 0)",
            (name,),
        )
    return memory


def apply_sql(db: sqlite3.Connection) -> None:
    for relative in ("SQL/01_Gabriel_Core.sql", "SQL/02_Gabriel_Text.sql"):
        path = ROOT / relative
        require(path.is_file(), f"Missing SQL file: {relative}")
        try:
            db.executescript(path.read_text(encoding="utf-8"))
        except sqlite3.Error as exc:
            raise ValidationError(f"{relative} failed: {exc}") from exc


def validate_database_rows(db: sqlite3.Connection) -> None:
    disabled_hooks = db.execute(
        "SELECT Name FROM CustomModOptions "
        "WHERE Name IN "
        "('EVENTS_BATTLES','EVENTS_UNIT_CAPTURE','EVENTS_UNIT_CONVERTS',"
        " 'EVENTS_UNIT_CREATED','EVENTS_UNIT_PREKILL','EVENTS_UNIT_UPGRADES') "
        "AND Value <> 1"
    ).fetchall()
    require(not disabled_hooks, f"Required Community Patch hooks remain disabled: {disabled_hooks}")

    expected_types = {
        "Civilizations": "CIVILIZATION_GABRIEL_BOULDER",
        "Leaders": "LEADER_GABRIEL_BOULDER",
        "Traits": "TRAIT_GABRIEL_ONE_MORE_GO",
        "Units": "UNIT_GABRIEL_GYM_HOPPER",
        "Buildings": "BUILDING_GABRIEL_BOULDERING_GYM",
    }
    for table, row_type in expected_types.items():
        require(
            scalar(db, f"SELECT COUNT(*) FROM {table} WHERE Type = ?", (row_type,)) == 1,
            f"Expected exactly one {row_type} row in {table}",
        )

    require(
        scalar(
            db,
            "SELECT ArtDefineTag FROM Leaders WHERE Type='LEADER_GABRIEL_BOULDER'",
        ) == "Gabriel_LeaderScene.xml",
        "Leader ArtDefineTag does not point to the imported static scene XML",
    )

    unit = db.execute(
        "SELECT Cost, Combat, Moves, BaseSightRange, Class, CombatClass, Domain "
        "FROM Units WHERE Type = 'UNIT_GABRIEL_GYM_HOPPER'"
    ).fetchone()
    require(unit == (30, 5, 3, 2, "UNITCLASS_SCOUT", "UNITCOMBAT_RECON", "DOMAIN_LAND"),
            f"Gym Hopper stats or classes are incorrect: {unit}")

    require(
        scalar(
            db,
            "SELECT COUNT(*) FROM Unit_FreePromotions "
            "WHERE UnitType='UNIT_GABRIEL_GYM_HOPPER' "
            "AND PromotionType='PROMOTION_GABRIEL_TRY_SOMETHING_NEW'",
        ) == 1,
        "Gym Hopper is missing Try Something New",
    )
    require(
        scalar(
            db,
            "SELECT COUNT(*) FROM UnitGameplay2DScripts "
            "WHERE UnitType='UNIT_GABRIEL_GYM_HOPPER'",
        ) == 1,
        "Gym Hopper did not inherit Scout selection sounds",
    )
    require(
        scalar(
            db,
            "SELECT COUNT(*) FROM Unit_FreePromotions "
            "WHERE UnitType='UNIT_GABRIEL_GYM_HOPPER' "
            "AND PromotionType='PROMOTION_IGNORE_TERRAIN_COST'",
        ) == 0,
        "Gym Hopper incorrectly retained the Scout's all-terrain movement promotion",
    )

    building = db.execute(
        "SELECT Happiness, TrainedFreePromotion, BuildingClass "
        "FROM Buildings WHERE Type='BUILDING_GABRIEL_BOULDERING_GYM'"
    ).fetchone()
    require(
        building == (1, "PROMOTION_GABRIEL_ROUTE_READING", "BUILDINGCLASS_BARRACKS"),
        f"Bouldering Gym fields are incorrect: {building}",
    )
    require(
        scalar(
            db,
            "SELECT Yield FROM Building_YieldChanges "
            "WHERE BuildingType='BUILDING_GABRIEL_BOULDERING_GYM' "
            "AND YieldType='YIELD_CULTURE'",
        ) == 1,
        "Bouldering Gym does not yield +1 Culture",
    )

    base_xp = set(
        db.execute(
            "SELECT DomainType, Experience FROM Building_DomainFreeExperiences "
            "WHERE BuildingType='BUILDING_BARRACKS'"
        ).fetchall()
    )
    gym_xp = set(
        db.execute(
            "SELECT DomainType, Experience FROM Building_DomainFreeExperiences "
            "WHERE BuildingType='BUILDING_GABRIEL_BOULDERING_GYM'"
        ).fetchall()
    )
    require(base_xp == gym_xp and ("DOMAIN_LAND", 15) in gym_xp,
            f"Bouldering Gym did not clone Barracks experience: {gym_xp}")

    expected_land_combats = {
        "UNITCOMBAT_ARCHER", "UNITCOMBAT_ARMOR", "UNITCOMBAT_GUN",
        "UNITCOMBAT_HELICOPTER", "UNITCOMBAT_MELEE", "UNITCOMBAT_MOUNTED",
        "UNITCOMBAT_RECON", "UNITCOMBAT_SIEGE",
    }
    route_combats = {
        row[0]
        for row in db.execute(
            "SELECT UnitCombatType FROM UnitPromotions_UnitCombats "
            "WHERE PromotionType='PROMOTION_GABRIEL_ROUTE_READING'"
        )
    }
    require(route_combats == expected_land_combats,
            f"Route Reading has incorrect combat classes: {sorted(route_combats)}")

    promotion_values = {
        row[0]: row[1:]
        for row in db.execute(
            "SELECT Type, HillsDoubleMove, HillsDefense, HillsAttack, AttackMod, LostWithUpgrade "
            "FROM UnitPromotions WHERE Type LIKE 'PROMOTION_GABRIEL_%'"
        )
    }
    require(promotion_values["PROMOTION_GABRIEL_TRY_SOMETHING_NEW"] == (1, 15, 0, 0, 1),
            "Try Something New values are incorrect")
    require(promotion_values["PROMOTION_GABRIEL_HILL_FAMILIARITY"] == (0, 10, 0, 0, 0),
            "Hill Familiarity values are incorrect")
    require(promotion_values["PROMOTION_GABRIEL_ROUTE_READING"] == (0, 10, 10, 0, 0),
            "Route Reading values are incorrect")
    require(
        [promotion_values[f"PROMOTION_GABRIEL_PROJECT_ATTACK_{n}"][3] for n in (5, 10, 15)]
        == [5, 10, 15],
        "One More Go temporary combat modifiers are incorrect",
    )

    require(
        scalar(
            db,
            "SELECT DawnOfManAudio IS NULL FROM Civilizations "
            "WHERE Type='CIVILIZATION_GABRIEL_BOULDER'",
        ) == 1,
        "DawnOfManAudio must be NULL when no compatible audio is supplied",
    )
    require(
        scalar(
            db,
            "SELECT COUNT(*) FROM Civilization_Start_Region_Priority "
            "WHERE CivilizationType='CIVILIZATION_GABRIEL_BOULDER' "
            "AND RegionType='REGION_HILLS'",
        ) == 1,
        "The civilization is missing its hills start priority",
    )

    require(
        scalar(
            db,
            "SELECT COUNT(*) FROM Diplomacy_Responses "
            "WHERE LeaderType='LEADER_GABRIEL_BOULDER'",
        ) >= 25,
        "Diplomacy coverage is unexpectedly sparse",
    )
    require(
        scalar(
            db,
            "SELECT COUNT(*) FROM Leader_Flavors "
            "WHERE LeaderType='LEADER_GABRIEL_BOULDER'",
        ) >= 35,
        "Gabriel does not have a complete AI flavor profile",
    )

    required_text = {
        "TXT_KEY_CIV_GABRIEL_BOULDER_DESC",
        "TXT_KEY_CIV_GABRIEL_BOULDER_DAWN",
        "TXT_KEY_LEADER_GABRIEL_BOULDER",
        "TXT_KEY_TRAIT_GABRIEL_ONE_MORE_GO_HELP",
        "TXT_KEY_UNIT_GABRIEL_GYM_HOPPER_HELP",
        "TXT_KEY_BUILDING_GABRIEL_BOULDERING_GYM_HELP",
        "TXT_KEY_PROMOTION_GABRIEL_ROUTE_READING_HELP",
        "TXT_KEY_CIV5_GABRIEL_TITLE",
        "TXT_KEY_CIV5_GABRIEL_HEADING_4",
        "TXT_KEY_CIV5_GABRIEL_TEXT_4",
        "TXT_KEY_CIVILOPEDIA_LEADERS_GABRIEL_NAME",
        "TXT_KEY_CIVILOPEDIA_LEADERS_GABRIEL_FACTS_1",
    }
    present = {
        row[0]
        for row in db.execute(
            "SELECT Tag FROM Language_en_US WHERE Tag LIKE 'TXT_KEY_%GABRIEL%'"
        )
    }
    require(required_text <= present,
            f"Missing required localized tags: {sorted(required_text - present)}")

    gameplay_sources = (
        (ROOT / "SQL" / "01_Gabriel_Core.sql").read_text(encoding="utf-8")
        + "\n"
        + (ROOT / "Lua" / "Gabriel_Gameplay.lua").read_text(encoding="utf-8")
    )
    referenced_text = set(re.findall(r"TXT_KEY_[A-Z0-9_]+", gameplay_sources))
    require(referenced_text <= present,
            f"Gameplay references undefined text tags: {sorted(referenced_text - present)}")

    missing_responses = []
    for response, in db.execute(
        "SELECT Response FROM Diplomacy_Responses "
        "WHERE LeaderType='LEADER_GABRIEL_BOULDER'"
    ):
        prefix = response.rstrip("%")
        count = scalar(db, "SELECT COUNT(*) FROM Language_en_US WHERE Tag LIKE ?", (prefix + "%",))
        if count == 0:
            missing_responses.append(response)
    require(not missing_responses,
            f"Diplomacy responses without localized lines: {missing_responses}")


def atlas_path(filename: str) -> Path:
    for folder in (ROOT / "Art" / "Atlases", ROOT / "Art" / "Screens"):
        candidate = folder / filename
        if candidate.is_file():
            return candidate
    raise ValidationError(f"Registered art file does not exist: {filename}")


def validate_art(db: sqlite3.Connection) -> None:
    expected_portraits = [
        ("Civilizations", "CIVILIZATION_GABRIEL_BOULDER", "CIV_COLOR", 0),
        ("Leaders", "LEADER_GABRIEL_BOULDER", "LEADER", 0),
        ("Units", "UNIT_GABRIEL_GYM_HOPPER", "OBJECT", 0),
        ("Buildings", "BUILDING_GABRIEL_BOULDERING_GYM", "OBJECT", 1),
    ]
    promotion_slots = {
        "TRY_SOMETHING_NEW": 4, "HILL_FAMILIARITY": 5, "ROUTE_READING": 6,
        "DETERMINATION_1": 7, "DETERMINATION_2": 7, "DETERMINATION_3": 7,
        "PROJECT_ATTACK_5": 2, "PROJECT_ATTACK_10": 2, "PROJECT_ATTACK_15": 2,
    }
    expected_portraits.extend(
        ("UnitPromotions", f"PROMOTION_GABRIEL_{name}", "OBJECT", slot)
        for name, slot in promotion_slots.items()
    )
    for table, row_type, atlas, slot in expected_portraits:
        actual = db.execute(
            f"SELECT IconAtlas, PortraitIndex FROM {table} WHERE Type = ?", (row_type,)
        ).fetchone()
        require(actual == (f"GABRIEL_BOULDER_{atlas}_ATLAS", slot),
                f"Incorrect icon atlas or portrait slot for {row_type}: {actual}")
    require(scalar(db, "SELECT AlphaIconAtlas FROM Civilizations "
                   "WHERE Type='CIVILIZATION_GABRIEL_BOULDER'")
            == "GABRIEL_BOULDER_CIV_ALPHA_ATLAS", "Incorrect civilization alpha atlas")
    flag = db.execute("SELECT UnitFlagAtlas, UnitFlagIconOffset FROM Units "
                      "WHERE Type='UNIT_GABRIEL_GYM_HOPPER'").fetchone()
    require(flag == ("GABRIEL_BOULDER_UNIT_FLAG_ATLAS", 0), "Incorrect Gym Hopper flag")

    atlas_rows = db.execute(
        "SELECT Atlas, IconSize, Filename, CAST(IconsPerRow AS INTEGER), "
        "CAST(IconsPerColumn AS INTEGER) FROM IconTextureAtlases "
        "WHERE Atlas LIKE 'GABRIEL_BOULDER_%'"
    ).fetchall()
    require(len(atlas_rows) == 23, f"Expected 23 Gabriel atlas registrations, found {len(atlas_rows)}")

    for atlas, size, filename, per_row, per_column in atlas_rows:
        path = atlas_path(filename)
        header = path.read_bytes()[:128]
        require(header[:4] == b"DDS " and header[84:88] == b"DXT5",
                f"{path.name} is not a DXT5 DDS")
        with Image.open(path) as image:
            expected = (size * per_row, size * per_column)
            require(image.size == expected,
                    f"{atlas} {size}px is {image.size}, expected {expected}: {path.name}")

    for filename in ("Gabriel_Diplomacy.dds", "Gabriel_DOM.dds", "Gabriel_Map.dds"):
        path = ROOT / "Art" / "Screens" / filename
        require(path.is_file(), f"Missing full-screen art: {filename}")
        header = path.read_bytes()[:128]
        require(header[:4] == b"DDS " and header[84:88] == b"DXT5",
                f"{filename} is not a DXT5 DDS")
        with Image.open(path) as image:
            require(image.size == (1600, 900),
                    f"{filename} is {image.size}, expected 1600x900")

    scene = ET.parse(ROOT / "Art" / "Gabriel_LeaderScene.xml").getroot()
    require(scene.tag == "LeaderScene", "Leader scene XML has the wrong root")
    require(scene.attrib.get("FallbackImage") == "Gabriel_Diplomacy.dds",
            "Leader scene does not reference the diplomacy fallback")


def validate_concept_icons() -> None:
    require(build_art.CONCEPT.is_file(), "Missing supplied concept sheet")
    require(hashlib.sha256(build_art.CONCEPT.read_bytes()).hexdigest()
            == "17efd7afadb18f4c2c98c6d9a09348a07f537d3042f5922d29da238b137ae026",
            "The supplied concept sheet changed; review icon provenance and crop bounds")
    require(build_art.OBJECT_ICON_NAMES == (
        "Gym_Hopper", "Bouldering_Gym", "One_More_Go", "Fresh_Sets",
        "Gym_Hopper", "Route_Reading", "Route_Reading", "One_More_Go",
    ), "Concept icons no longer match the database portrait slots")
    icons = build_art.extract_concept_icons()
    with Image.open(build_art.CONCEPT) as concept:
        for name, box in build_art.CONCEPT_ICON_BOXES.items():
            require(icons[name].convert("RGB").tobytes()
                    == concept.crop(box).convert("RGB").tobytes(),
                    f"{name} has been redrawn or altered instead of cropped from the concept")
            alpha = icons[name].getchannel("A")
            require(alpha.getpixel((0, 0)) == 0
                    and alpha.getpixel((alpha.width // 2, alpha.height // 2)) == 255,
                    f"{name} is missing its transparent outside/opaque interior")
    for name in ("Civ_Alpha", "Unit_Flag"):
        icons[name] = build_art.extract_gold_symbol(icons["Gym_Hopper"])
        require(icons[name].getchannel("A").getextrema() == (0, 255),
                f"{name} has no usable silhouette transparency")
    for name, expected in icons.items():
        path = build_art.CONCEPT_ICONS / f"Gabriel_{name}_Concept.png"
        require(path.is_file(), f"Missing extracted source: {path.name}")
        with Image.open(path) as actual:
            require(actual.size == expected.size
                    and actual.convert("RGBA").tobytes() == expected.tobytes(),
                    f"Saved concept crop is stale or altered: {path.name}")

    expected_atlases = {}
    for name, sizes in (("Civ", build_art.CIV_SIZES), ("Leader", build_art.LEADER_SIZES),
                        ("Civ_Alpha", build_art.ALPHA_SIZES)):
        for size in sizes:
            expected_atlases[f"Gabriel_{name}_{size}.dds"] = build_art.fit_icon(icons[name], size)
    for size in build_art.OBJECT_SIZES:
        expected_atlases[f"Gabriel_Objects_{size}.dds"] = build_art.object_atlas(icons, size)
    expected_atlases["Gabriel_UnitFlag_32.dds"] = build_art.fit_icon(icons["Unit_Flag"], 32)
    require(len(expected_atlases) == 23, "Expected all 23 concept-derived atlas files")
    for filename, expected in expected_atlases.items():
        encoded = io.BytesIO()
        expected.save(encoded, format="DDS", pixel_format="DXT5")
        path = build_art.ATLASES / filename
        require(path.is_file() and path.read_bytes() == encoded.getvalue(),
                f"Atlas does not match a fresh build from the concept: {filename}")
    require((build_art.PREVIEW / "Gabriel_Concept_Icons.png").is_file(),
            "Missing concept icon preview")


def validate_lua() -> None:
    path = ROOT / "Lua" / "Gabriel_Gameplay.lua"
    require(path.is_file(), "Missing Lua/Gabriel_Gameplay.lua")
    text = path.read_text(encoding="utf-8")
    required_hooks = {
        "GameEvents.BattleStarted", "GameEvents.BattleJoined",
        "GameEvents.BattleFinished", "GameEvents.UnitPrekill",
        "GameEvents.UnitSetXY", "GameEvents.UnitUpgraded",
        "GameEvents.PlayerDoTurn", "Modding.OpenSaveData",
    }
    missing = sorted(item for item in required_hooks if item not in text)
    require(not missing, f"Lua is missing required hooks/helpers: {missing}")
    require("PROMOTION_GABRIEL_PROJECT_ATTACK_15" in text,
            "Lua does not reference the maximum project promotion")
    require("15 + (5 * era)" in text,
            "Fresh Sets reward formula is missing or changed")


def md5(path: Path) -> str:
    digest = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def validate_modinfo() -> None:
    require(MODINFO.is_file(), f"Missing modinfo: {MODINFO.name}")
    root = ET.parse(MODINFO).getroot()
    require(root.tag == "Mod" and root.attrib.get("version") == "1",
            "modinfo root or version is invalid")
    dependency = root.find("./Dependencies/Mod")
    require(
        dependency is not None
        and dependency.attrib.get("id") == "d1b6328c-ff44-4b0d-aad7-c657f83610cd",
        "Community Patch dependency is missing or incorrect",
    )
    entries = root.findall("./Files/File")
    require(entries, "modinfo Files list is empty")
    listed = set()
    for entry in entries:
        relative = (entry.text or "").replace("\\", "/")
        listed.add(relative)
        path = ROOT / relative
        require(path.is_file(), f"modinfo lists a missing file: {relative}")
        require(entry.attrib.get("md5", "").upper() == md5(path),
                f"modinfo MD5 is stale for {relative}")
        if relative.startswith(("Art/Atlases/", "Art/Screens/")) and relative.endswith(".dds"):
            require(entry.attrib.get("import") == "1", f"DDS is not imported into VFS: {relative}")
    for required in (
        "SQL/01_Gabriel_Core.sql", "SQL/02_Gabriel_Text.sql",
        "Lua/Gabriel_Gameplay.lua", "Art/Gabriel_LeaderScene.xml",
        "Art/Screens/Gabriel_Diplomacy.dds",
    ):
        require(required in listed, f"modinfo does not list {required}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=default_database())
    args = parser.parse_args()
    try:
        database = load_database(args.database)
        apply_sql(database)
        validate_database_rows(database)
        validate_art(database)
        validate_concept_icons()
        validate_lua()
        validate_modinfo()
    except (ValidationError, ET.ParseError) as exc:
        print(f"VALIDATION FAILED: {exc}", file=sys.stderr)
        return 1
    finally:
        if "database" in locals():
            database.close()
    print("Validation passed: database, localization, concept icons, art, Lua hooks, and modinfo are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
