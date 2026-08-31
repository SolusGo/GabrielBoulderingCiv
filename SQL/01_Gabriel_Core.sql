-- Gabriel — The Relentless Projector
-- Core database definitions. Requires the Community Patch DLL and its database schema.

-- These documented Community Patch events default to disabled in a CP-only
-- installation. Enable only the hooks used by this mod.
UPDATE CustomModOptions SET Value = 1
WHERE Name IN
    ('EVENTS_BATTLES', 'EVENTS_UNIT_CAPTURE', 'EVENTS_UNIT_CONVERTS',
     'EVENTS_UNIT_CREATED', 'EVENTS_UNIT_PREKILL', 'EVENTS_UNIT_UPGRADES');

-- ---------------------------------------------------------------------------
-- Art atlases and player colours
-- ---------------------------------------------------------------------------

INSERT INTO IconTextureAtlases (Atlas, IconSize, Filename, IconsPerRow, IconsPerColumn) VALUES
('GABRIEL_BOULDER_CIV_COLOR_ATLAS', 256, 'Gabriel_Civ_256.dds', 1, 1),
('GABRIEL_BOULDER_CIV_COLOR_ATLAS', 128, 'Gabriel_Civ_128.dds', 1, 1),
('GABRIEL_BOULDER_CIV_COLOR_ATLAS',  80, 'Gabriel_Civ_80.dds',  1, 1),
('GABRIEL_BOULDER_CIV_COLOR_ATLAS',  64, 'Gabriel_Civ_64.dds',  1, 1),
('GABRIEL_BOULDER_CIV_COLOR_ATLAS',  45, 'Gabriel_Civ_45.dds',  1, 1),
('GABRIEL_BOULDER_CIV_COLOR_ATLAS',  32, 'Gabriel_Civ_32.dds',  1, 1),
('GABRIEL_BOULDER_CIV_ALPHA_ATLAS', 128, 'Gabriel_Civ_Alpha_128.dds', 1, 1),
('GABRIEL_BOULDER_CIV_ALPHA_ATLAS',  64, 'Gabriel_Civ_Alpha_64.dds',  1, 1),
('GABRIEL_BOULDER_CIV_ALPHA_ATLAS',  48, 'Gabriel_Civ_Alpha_48.dds',  1, 1),
('GABRIEL_BOULDER_CIV_ALPHA_ATLAS',  32, 'Gabriel_Civ_Alpha_32.dds',  1, 1),
('GABRIEL_BOULDER_CIV_ALPHA_ATLAS',  24, 'Gabriel_Civ_Alpha_24.dds',  1, 1),
('GABRIEL_BOULDER_CIV_ALPHA_ATLAS',  16, 'Gabriel_Civ_Alpha_16.dds',  1, 1),
('GABRIEL_BOULDER_LEADER_ATLAS', 256, 'Gabriel_Leader_256.dds', 1, 1),
('GABRIEL_BOULDER_LEADER_ATLAS', 128, 'Gabriel_Leader_128.dds', 1, 1),
('GABRIEL_BOULDER_LEADER_ATLAS',  64, 'Gabriel_Leader_64.dds',  1, 1),
('GABRIEL_BOULDER_OBJECT_ATLAS', 256, 'Gabriel_Objects_256.dds', 8, 1),
('GABRIEL_BOULDER_OBJECT_ATLAS', 128, 'Gabriel_Objects_128.dds', 8, 1),
('GABRIEL_BOULDER_OBJECT_ATLAS',  80, 'Gabriel_Objects_80.dds',  8, 1),
('GABRIEL_BOULDER_OBJECT_ATLAS',  64, 'Gabriel_Objects_64.dds',  8, 1),
('GABRIEL_BOULDER_OBJECT_ATLAS',  45, 'Gabriel_Objects_45.dds',  8, 1),
('GABRIEL_BOULDER_OBJECT_ATLAS',  32, 'Gabriel_Objects_32.dds',  8, 1),
('GABRIEL_BOULDER_OBJECT_ATLAS',  16, 'Gabriel_Objects_16.dds',  8, 1),
('GABRIEL_BOULDER_UNIT_FLAG_ATLAS', 32, 'Gabriel_UnitFlag_32.dds', 1, 1);

INSERT INTO Colors (Type, Red, Green, Blue, Alpha) VALUES
('COLOR_PLAYER_GABRIEL_BOULDER_PRIMARY',   0.055, 0.160, 0.184, 1.0),
('COLOR_PLAYER_GABRIEL_BOULDER_SECONDARY', 0.812, 0.596, 0.255, 1.0);

INSERT INTO PlayerColors (Type, PrimaryColor, SecondaryColor, TextColor) VALUES
('PLAYERCOLOR_GABRIEL_BOULDER', 'COLOR_PLAYER_GABRIEL_BOULDER_PRIMARY',
 'COLOR_PLAYER_GABRIEL_BOULDER_SECONDARY', 'COLOR_PLAYER_WHITE_TEXT');

-- ---------------------------------------------------------------------------
-- Promotions
-- ---------------------------------------------------------------------------

INSERT INTO UnitPromotions
    (Type, Description, Help, CannotBeChosen, LostWithUpgrade,
     HillsDoubleMove, HillsDefense, HillsAttack, AttackMod,
     PortraitIndex, IconAtlas, PediaType, PediaEntry, OrderPriority)
VALUES
('PROMOTION_GABRIEL_TRY_SOMETHING_NEW',
 'TXT_KEY_PROMOTION_GABRIEL_TRY_SOMETHING_NEW',
 'TXT_KEY_PROMOTION_GABRIEL_TRY_SOMETHING_NEW_HELP',
 1, 1, 1, 15, 0, 0, 4, 'GABRIEL_BOULDER_OBJECT_ATLAS',
 'PEDIA_ATTRIBUTES', 'TXT_KEY_PROMOTION_GABRIEL_TRY_SOMETHING_NEW', 90),
('PROMOTION_GABRIEL_HILL_FAMILIARITY',
 'TXT_KEY_PROMOTION_GABRIEL_HILL_FAMILIARITY',
 'TXT_KEY_PROMOTION_GABRIEL_HILL_FAMILIARITY_HELP',
 1, 0, 0, 10, 0, 0, 5, 'GABRIEL_BOULDER_OBJECT_ATLAS',
 'PEDIA_ATTRIBUTES', 'TXT_KEY_PROMOTION_GABRIEL_HILL_FAMILIARITY', 89),
('PROMOTION_GABRIEL_ROUTE_READING',
 'TXT_KEY_PROMOTION_GABRIEL_ROUTE_READING',
 'TXT_KEY_PROMOTION_GABRIEL_ROUTE_READING_HELP',
 1, 0, 0, 10, 10, 0, 6, 'GABRIEL_BOULDER_OBJECT_ATLAS',
 'PEDIA_ATTRIBUTES', 'TXT_KEY_PROMOTION_GABRIEL_ROUTE_READING', 88),
('PROMOTION_GABRIEL_DETERMINATION_1',
 'TXT_KEY_PROMOTION_GABRIEL_DETERMINATION_1',
 'TXT_KEY_PROMOTION_GABRIEL_DETERMINATION_1_HELP',
 1, 1, 0, 0, 0, 0, 7, 'GABRIEL_BOULDER_OBJECT_ATLAS',
 NULL, NULL, 87),
('PROMOTION_GABRIEL_DETERMINATION_2',
 'TXT_KEY_PROMOTION_GABRIEL_DETERMINATION_2',
 'TXT_KEY_PROMOTION_GABRIEL_DETERMINATION_2_HELP',
 1, 1, 0, 0, 0, 0, 7, 'GABRIEL_BOULDER_OBJECT_ATLAS',
 NULL, NULL, 87),
('PROMOTION_GABRIEL_DETERMINATION_3',
 'TXT_KEY_PROMOTION_GABRIEL_DETERMINATION_3',
 'TXT_KEY_PROMOTION_GABRIEL_DETERMINATION_3_HELP',
 1, 1, 0, 0, 0, 0, 7, 'GABRIEL_BOULDER_OBJECT_ATLAS',
 NULL, NULL, 87),
('PROMOTION_GABRIEL_PROJECT_ATTACK_5',
 'TXT_KEY_PROMOTION_GABRIEL_PROJECT_ATTACK_5',
 'TXT_KEY_PROMOTION_GABRIEL_PROJECT_ATTACK_5_HELP',
 1, 1, 0, 0, 0, 5, 2, 'GABRIEL_BOULDER_OBJECT_ATLAS',
 NULL, NULL, 0),
('PROMOTION_GABRIEL_PROJECT_ATTACK_10',
 'TXT_KEY_PROMOTION_GABRIEL_PROJECT_ATTACK_10',
 'TXT_KEY_PROMOTION_GABRIEL_PROJECT_ATTACK_10_HELP',
 1, 1, 0, 0, 0, 10, 2, 'GABRIEL_BOULDER_OBJECT_ATLAS',
 NULL, NULL, 0),
('PROMOTION_GABRIEL_PROJECT_ATTACK_15',
 'TXT_KEY_PROMOTION_GABRIEL_PROJECT_ATTACK_15',
 'TXT_KEY_PROMOTION_GABRIEL_PROJECT_ATTACK_15_HELP',
 1, 1, 0, 0, 0, 15, 2, 'GABRIEL_BOULDER_OBJECT_ATLAS',
 NULL, NULL, 0);

INSERT INTO UnitPromotions_UnitCombats (PromotionType, UnitCombatType, PediaType)
SELECT 'PROMOTION_GABRIEL_ROUTE_READING', Type, 'PEDIA_ATTRIBUTES'
FROM UnitCombatInfos
WHERE Type IN
    ('UNITCOMBAT_ARCHER', 'UNITCOMBAT_ARMOR', 'UNITCOMBAT_GUN',
     'UNITCOMBAT_HELICOPTER', 'UNITCOMBAT_MELEE', 'UNITCOMBAT_MOUNTED',
     'UNITCOMBAT_RECON', 'UNITCOMBAT_SIEGE');

-- ---------------------------------------------------------------------------
-- Unique unit and building. Temporary-table cloning preserves Community Patch
-- columns and later balance changes to the base Scout and Barracks.
-- ---------------------------------------------------------------------------

CREATE TEMP TABLE Gabriel_GymHopper AS
SELECT * FROM Units WHERE Type = 'UNIT_SCOUT';

UPDATE Gabriel_GymHopper SET
    ID = NULL,
    Type = 'UNIT_GABRIEL_GYM_HOPPER',
    Description = 'TXT_KEY_UNIT_GABRIEL_GYM_HOPPER',
    Civilopedia = 'TXT_KEY_CIVILOPEDIA_UNITS_GABRIEL_GYM_HOPPER_TEXT',
    Strategy = 'TXT_KEY_UNIT_GABRIEL_GYM_HOPPER_STRATEGY',
    Help = 'TXT_KEY_UNIT_GABRIEL_GYM_HOPPER_HELP',
    Cost = 30,
    Combat = 5,
    Moves = 3,
    BaseSightRange = 2,
    PortraitIndex = 0,
    IconAtlas = 'GABRIEL_BOULDER_OBJECT_ATLAS',
    UnitFlagIconOffset = 0,
    UnitFlagAtlas = 'GABRIEL_BOULDER_UNIT_FLAG_ATLAS';

INSERT INTO Units SELECT * FROM Gabriel_GymHopper;
DROP TABLE Gabriel_GymHopper;

INSERT INTO Unit_AITypes (UnitType, UnitAIType)
SELECT 'UNIT_GABRIEL_GYM_HOPPER', UnitAIType
FROM Unit_AITypes WHERE UnitType = 'UNIT_SCOUT';

INSERT INTO Unit_ClassUpgrades (UnitType, UnitClassType)
SELECT 'UNIT_GABRIEL_GYM_HOPPER', UnitClassType
FROM Unit_ClassUpgrades WHERE UnitType = 'UNIT_SCOUT';

INSERT INTO Unit_Flavors (UnitType, FlavorType, Flavor)
SELECT 'UNIT_GABRIEL_GYM_HOPPER', FlavorType, Flavor
FROM Unit_Flavors WHERE UnitType = 'UNIT_SCOUT';

INSERT INTO UnitGameplay2DScripts (UnitType, SelectionSound, FirstSelectionSound)
SELECT 'UNIT_GABRIEL_GYM_HOPPER', SelectionSound, FirstSelectionSound
FROM UnitGameplay2DScripts WHERE UnitType = 'UNIT_SCOUT';

-- The Gym Hopper deliberately trades the Scout's all-terrain movement for a
-- focused hill movement bonus.
INSERT INTO Unit_FreePromotions (UnitType, PromotionType)
SELECT 'UNIT_GABRIEL_GYM_HOPPER', PromotionType
FROM Unit_FreePromotions
WHERE UnitType = 'UNIT_SCOUT'
  AND PromotionType <> 'PROMOTION_IGNORE_TERRAIN_COST';

INSERT INTO Unit_FreePromotions (UnitType, PromotionType) VALUES
('UNIT_GABRIEL_GYM_HOPPER', 'PROMOTION_GABRIEL_TRY_SOMETHING_NEW');

CREATE TEMP TABLE Gabriel_BoulderingGym AS
SELECT * FROM Buildings WHERE Type = 'BUILDING_BARRACKS';

UPDATE Gabriel_BoulderingGym SET
    ID = NULL,
    Type = 'BUILDING_GABRIEL_BOULDERING_GYM',
    Description = 'TXT_KEY_BUILDING_GABRIEL_BOULDERING_GYM',
    Civilopedia = 'TXT_KEY_CIVILOPEDIA_BUILDINGS_GABRIEL_BOULDERING_GYM_TEXT',
    Strategy = 'TXT_KEY_BUILDING_GABRIEL_BOULDERING_GYM_STRATEGY',
    Help = 'TXT_KEY_BUILDING_GABRIEL_BOULDERING_GYM_HELP',
    Happiness = 1,
    TrainedFreePromotion = 'PROMOTION_GABRIEL_ROUTE_READING',
    PortraitIndex = 1,
    IconAtlas = 'GABRIEL_BOULDER_OBJECT_ATLAS';

INSERT INTO Buildings SELECT * FROM Gabriel_BoulderingGym;
DROP TABLE Gabriel_BoulderingGym;

INSERT INTO Building_DomainFreeExperiences (BuildingType, DomainType, Experience)
SELECT 'BUILDING_GABRIEL_BOULDERING_GYM', DomainType, Experience
FROM Building_DomainFreeExperiences WHERE BuildingType = 'BUILDING_BARRACKS';

INSERT INTO Building_Flavors (BuildingType, FlavorType, Flavor)
SELECT 'BUILDING_GABRIEL_BOULDERING_GYM', FlavorType, Flavor
FROM Building_Flavors WHERE BuildingType = 'BUILDING_BARRACKS';

INSERT INTO Building_YieldChanges (BuildingType, YieldType, Yield) VALUES
('BUILDING_GABRIEL_BOULDERING_GYM', 'YIELD_CULTURE', 1);

-- ---------------------------------------------------------------------------
-- Trait, leader, and civilization
-- ---------------------------------------------------------------------------

INSERT INTO Traits (Type, Description, ShortDescription) VALUES
('TRAIT_GABRIEL_ONE_MORE_GO',
 'TXT_KEY_TRAIT_GABRIEL_ONE_MORE_GO_HELP',
 'TXT_KEY_TRAIT_GABRIEL_ONE_MORE_GO');

INSERT INTO Leaders
    (Type, Description, Civilopedia, CivilopediaTag, ArtDefineTag,
     VictoryCompetitiveness, WonderCompetitiveness, MinorCivCompetitiveness,
     Boldness, DiploBalance, WarmongerHate, WorkAgainstWillingness,
     WorkWithWillingness, DenounceWillingness, DoFWillingness, Loyalty,
     Neediness, Forgiveness, Chattiness, Meanness,
     PortraitIndex, IconAtlas)
VALUES
    ('LEADER_GABRIEL_BOULDER', 'TXT_KEY_LEADER_GABRIEL_BOULDER',
     'TXT_KEY_LEADER_GABRIEL_PEDIA',
     'TXT_KEY_CIVILOPEDIA_LEADERS_GABRIEL',
     'Gabriel_LeaderScene.xml',
     6, 4, 5, 6, 7, 7, 4, 7, 5, 7, 8, 4, 7, 5, 3,
     0, 'GABRIEL_BOULDER_LEADER_ATLAS');

INSERT INTO Leader_Traits (LeaderType, TraitType) VALUES
('LEADER_GABRIEL_BOULDER', 'TRAIT_GABRIEL_ONE_MORE_GO');

-- Begin with a complete flavor set so omitted categories never fall to zero.
INSERT INTO Leader_Flavors (LeaderType, FlavorType, Flavor)
SELECT 'LEADER_GABRIEL_BOULDER', FlavorType, Flavor
FROM Leader_Flavors WHERE LeaderType = 'LEADER_WASHINGTON';

UPDATE Leader_Flavors SET Flavor =
    CASE FlavorType
        WHEN 'FLAVOR_EXPANSION' THEN 6
        WHEN 'FLAVOR_GROWTH' THEN 6
        WHEN 'FLAVOR_SCIENCE' THEN 7
        WHEN 'FLAVOR_CULTURE' THEN 6
        WHEN 'FLAVOR_OFFENSE' THEN 6
        WHEN 'FLAVOR_DEFENSE' THEN 8
        WHEN 'FLAVOR_RECON' THEN 9
        WHEN 'FLAVOR_MOBILE' THEN 4
        WHEN 'FLAVOR_RANGED' THEN 5
        WHEN 'FLAVOR_MILITARY_TRAINING' THEN 9
        WHEN 'FLAVOR_I_LAND_TRADE_ROUTE' THEN 8
        WHEN 'FLAVOR_WONDER' THEN 4
        WHEN 'FLAVOR_HAPPINESS' THEN 6
        WHEN 'FLAVOR_INFRASTRUCTURE' THEN 6
        ELSE Flavor
    END
WHERE LeaderType = 'LEADER_GABRIEL_BOULDER';

INSERT INTO Leader_MajorCivApproachBiases
    (LeaderType, MajorCivApproachType, Bias) VALUES
('LEADER_GABRIEL_BOULDER', 'MAJOR_CIV_APPROACH_WAR', 4),
('LEADER_GABRIEL_BOULDER', 'MAJOR_CIV_APPROACH_HOSTILE', 3),
('LEADER_GABRIEL_BOULDER', 'MAJOR_CIV_APPROACH_DECEPTIVE', 2),
('LEADER_GABRIEL_BOULDER', 'MAJOR_CIV_APPROACH_GUARDED', 7),
('LEADER_GABRIEL_BOULDER', 'MAJOR_CIV_APPROACH_AFRAID', 3),
('LEADER_GABRIEL_BOULDER', 'MAJOR_CIV_APPROACH_FRIENDLY', 7),
('LEADER_GABRIEL_BOULDER', 'MAJOR_CIV_APPROACH_NEUTRAL', 5);

INSERT INTO Leader_MinorCivApproachBiases
    (LeaderType, MinorCivApproachType, Bias) VALUES
('LEADER_GABRIEL_BOULDER', 'MINOR_CIV_APPROACH_IGNORE', 2),
('LEADER_GABRIEL_BOULDER', 'MINOR_CIV_APPROACH_FRIENDLY', 7),
('LEADER_GABRIEL_BOULDER', 'MINOR_CIV_APPROACH_PROTECTIVE', 7),
('LEADER_GABRIEL_BOULDER', 'MINOR_CIV_APPROACH_CONQUEST', 3),
('LEADER_GABRIEL_BOULDER', 'MINOR_CIV_APPROACH_BULLY', 2);

INSERT INTO Civilizations
    (Type, Description, Civilopedia, CivilopediaTag, Strategy,
     Playable, AIPlayable, ShortDescription, Adjective, DefaultPlayerColor,
     ArtDefineTag, ArtStyleType, ArtStyleSuffix, ArtStylePrefix,
     PortraitIndex, IconAtlas, AlphaIconAtlas, MapImage,
     DawnOfManQuote, DawnOfManImage, DawnOfManAudio, SoundtrackTag)
VALUES
    ('CIVILIZATION_GABRIEL_BOULDER',
     'TXT_KEY_CIV_GABRIEL_BOULDER_DESC',
     'TXT_KEY_CIV5_GABRIEL',
     'TXT_KEY_CIV5_GABRIEL',
     'TXT_KEY_CIV_GABRIEL_BOULDER_STRATEGY',
     1, 1,
     'TXT_KEY_CIV_GABRIEL_BOULDER_SHORT_DESC',
     'TXT_KEY_CIV_GABRIEL_BOULDER_ADJECTIVE',
     'PLAYERCOLOR_GABRIEL_BOULDER',
     'ART_DEF_CIVILIZATION_AMERICA', 'ARTSTYLE_EUROPEAN', '_EURO', 'EUROPEAN ',
     0, 'GABRIEL_BOULDER_CIV_COLOR_ATLAS', 'GABRIEL_BOULDER_CIV_ALPHA_ATLAS',
     'Gabriel_Map.dds',
     'TXT_KEY_CIV_GABRIEL_BOULDER_DAWN', 'Gabriel_DOM.dds', NULL, 'AMERICA');

INSERT INTO Civilization_Leaders (CivilizationType, LeaderheadType) VALUES
('CIVILIZATION_GABRIEL_BOULDER', 'LEADER_GABRIEL_BOULDER');

INSERT INTO Civilization_FreeBuildingClasses (CivilizationType, BuildingClassType)
SELECT 'CIVILIZATION_GABRIEL_BOULDER', BuildingClassType
FROM Civilization_FreeBuildingClasses WHERE CivilizationType = 'CIVILIZATION_AMERICA';

INSERT INTO Civilization_FreeTechs (CivilizationType, TechType)
SELECT 'CIVILIZATION_GABRIEL_BOULDER', TechType
FROM Civilization_FreeTechs WHERE CivilizationType = 'CIVILIZATION_AMERICA';

INSERT INTO Civilization_FreeUnits (CivilizationType, UnitClassType, UnitAIType, Count)
SELECT 'CIVILIZATION_GABRIEL_BOULDER', UnitClassType, UnitAIType, Count
FROM Civilization_FreeUnits WHERE CivilizationType = 'CIVILIZATION_AMERICA';

INSERT INTO Civilization_Start_Region_Priority (CivilizationType, RegionType) VALUES
('CIVILIZATION_GABRIEL_BOULDER', 'REGION_HILLS');

INSERT INTO Civilization_UnitClassOverrides
    (CivilizationType, UnitClassType, UnitType) VALUES
('CIVILIZATION_GABRIEL_BOULDER', 'UNITCLASS_SCOUT', 'UNIT_GABRIEL_GYM_HOPPER');

INSERT INTO Civilization_BuildingClassOverrides
    (CivilizationType, BuildingClassType, BuildingType) VALUES
('CIVILIZATION_GABRIEL_BOULDER', 'BUILDINGCLASS_BARRACKS',
 'BUILDING_GABRIEL_BOULDERING_GYM');

INSERT INTO Civilization_CityNames (CivilizationType, CityName) VALUES
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_PROJECT'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_CRUX'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_HIGHBALL'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_ARETE'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_MANTLE'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_SLAB'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_OVERHANG'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_TRAVERSE'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_CAMPUS'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_SUMMIT'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_CHALKSTONE'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_CITY_NAME_GABRIEL_BETA');

INSERT INTO Civilization_SpyNames (CivilizationType, SpyName) VALUES
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_SPY_NAME_GABRIEL_0'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_SPY_NAME_GABRIEL_1'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_SPY_NAME_GABRIEL_2'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_SPY_NAME_GABRIEL_3'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_SPY_NAME_GABRIEL_4'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_SPY_NAME_GABRIEL_5'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_SPY_NAME_GABRIEL_6'),
('CIVILIZATION_GABRIEL_BOULDER', 'TXT_KEY_SPY_NAME_GABRIEL_7');
