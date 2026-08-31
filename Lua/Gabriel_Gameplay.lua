-- Gabriel — The Relentless Projector
-- Runtime mechanics for One More Go, Fresh Sets, and Gym Hopper progression.
-- The battle hooks used here are supplied by the Community Patch DLL.

local CIVILIZATION_GABRIEL = GameInfoTypes.CIVILIZATION_GABRIEL_BOULDER
local UNIT_GYM_HOPPER = GameInfoTypes.UNIT_GABRIEL_GYM_HOPPER

local PROMOTION_TRY_NEW = GameInfoTypes.PROMOTION_GABRIEL_TRY_SOMETHING_NEW
local PROMOTION_HILL_FAMILIARITY = GameInfoTypes.PROMOTION_GABRIEL_HILL_FAMILIARITY
local PROMOTION_DETERMINATION = {
    GameInfoTypes.PROMOTION_GABRIEL_DETERMINATION_1,
    GameInfoTypes.PROMOTION_GABRIEL_DETERMINATION_2,
    GameInfoTypes.PROMOTION_GABRIEL_DETERMINATION_3
}
local PROMOTION_PROJECT_ATTACK = {
    GameInfoTypes.PROMOTION_GABRIEL_PROJECT_ATTACK_5,
    GameInfoTypes.PROMOTION_GABRIEL_PROJECT_ATTACK_10,
    GameInfoTypes.PROMOTION_GABRIEL_PROJECT_ATTACK_15
}

local DOMAIN_LAND = GameInfoTypes.DOMAIN_LAND
local NO_PLAYER = -1
local MAX_PROJECT_STACKS = 3
local PROJECT_TIMEOUT_TURNS = 3

local g_SaveData = Modding.OpenSaveData()
local g_CurrentBattle = nil

local function SaveKey(category, playerID, unitID, suffix)
    if suffix ~= nil then
        return string.format("GABRIEL_BOULDER_%s_%d_%d_%s", category, playerID, unitID, tostring(suffix))
    end
    return string.format("GABRIEL_BOULDER_%s_%d_%d", category, playerID, unitID)
end

local function GetNumber(key, defaultValue)
    local value = g_SaveData:GetValue(key)
    if value == nil then
        return defaultValue
    end
    return tonumber(value) or defaultValue
end

local function SetNumber(key, value)
    g_SaveData:SetValue(key, value)
end

local function IsGabrielPlayer(playerID)
    local player = Players[playerID]
    return player ~= nil
        and player:IsAlive()
        and player:GetCivilizationType() == CIVILIZATION_GABRIEL
end

local function GetUnit(playerID, unitID)
    local player = Players[playerID]
    if player == nil then
        return nil
    end
    return player:GetUnitByID(unitID)
end

local function IsEligibleProjector(playerID, unit)
    return IsGabrielPlayer(playerID)
        and unit ~= nil
        and unit:GetDomainType() == DOMAIN_LAND
        and unit:IsCombatUnit()
end

local function SetPromotion(unit, promotionID, enabled)
    if unit ~= nil and promotionID ~= nil and promotionID >= 0 then
        unit:SetHasPromotion(promotionID, enabled)
    end
end

local function ClearTemporaryAttackPromotions(unit)
    if unit == nil then
        return
    end
    for _, promotionID in ipairs(PROMOTION_PROJECT_ATTACK) do
        SetPromotion(unit, promotionID, false)
    end
end

local function ApplyTemporaryAttackPromotion(unit, stacks)
    ClearTemporaryAttackPromotions(unit)
    if stacks <= 0 then
        return
    end
    local index = math.min(stacks, MAX_PROJECT_STACKS)
    SetPromotion(unit, PROMOTION_PROJECT_ATTACK[index], true)
end

local function UpdateDeterminationPromotion(unit, stacks)
    if unit == nil then
        return
    end
    for index, promotionID in ipairs(PROMOTION_DETERMINATION) do
        SetPromotion(unit, promotionID, index == stacks)
    end
end

local function ReadProject(playerID, unitID)
    return {
        targetOwner = GetNumber(SaveKey("PROJECT_OWNER", playerID, unitID), NO_PLAYER),
        targetUnit = GetNumber(SaveKey("PROJECT_UNIT", playerID, unitID), -1),
        stacks = GetNumber(SaveKey("PROJECT_STACKS", playerID, unitID), 0),
        lastAttackTurn = GetNumber(SaveKey("PROJECT_TURN", playerID, unitID), -1000)
    }
end

local function ClearProject(playerID, unitID)
    SetNumber(SaveKey("PROJECT_OWNER", playerID, unitID), NO_PLAYER)
    SetNumber(SaveKey("PROJECT_UNIT", playerID, unitID), -1)
    SetNumber(SaveKey("PROJECT_STACKS", playerID, unitID), 0)
    SetNumber(SaveKey("PROJECT_TURN", playerID, unitID), -1000)
    local unit = GetUnit(playerID, unitID)
    UpdateDeterminationPromotion(unit, 0)
    ClearTemporaryAttackPromotions(unit)
end

local function WriteProject(playerID, unitID, targetOwner, targetUnit, stacks, turn)
    stacks = math.max(0, math.min(stacks, MAX_PROJECT_STACKS))
    SetNumber(SaveKey("PROJECT_OWNER", playerID, unitID), targetOwner)
    SetNumber(SaveKey("PROJECT_UNIT", playerID, unitID), targetUnit)
    SetNumber(SaveKey("PROJECT_STACKS", playerID, unitID), stacks)
    SetNumber(SaveKey("PROJECT_TURN", playerID, unitID), turn)
    UpdateDeterminationPromotion(GetUnit(playerID, unitID), stacks)
end

local function ProjectTargetStillExists(project)
    if project.targetOwner == NO_PLAYER or project.targetUnit < 0 then
        return false
    end
    return GetUnit(project.targetOwner, project.targetUnit) ~= nil
end

local function NotifyPlayer(playerID, textKey, ...)
    local player = Players[playerID]
    if player ~= nil and player:IsHuman() then
        Events.GameplayAlertMessage(Locale.ConvertTextKey(textKey, ...))
    end
end

-- ---------------------------------------------------------------------------
-- One More Go
-- ---------------------------------------------------------------------------

local function OnBattleStarted(battleType, plotX, plotY)
    if g_CurrentBattle ~= nil and g_CurrentBattle.attacker ~= nil then
        ClearTemporaryAttackPromotions(
            GetUnit(g_CurrentBattle.attacker.playerID, g_CurrentBattle.attacker.unitID))
    end
    g_CurrentBattle = {
        battleType = battleType,
        x = plotX,
        y = plotY,
        attacker = nil,
        defender = nil,
        prepared = false,
        eligible = false,
        startingStacks = 0,
        targetKilled = false,
        targetCaptured = false
    }
end

local function PrepareBattle()
    local battle = g_CurrentBattle
    if battle == nil or battle.prepared or battle.attacker == nil or battle.defender == nil then
        return
    end
    battle.prepared = true

    local attacker = GetUnit(battle.attacker.playerID, battle.attacker.unitID)
    if not IsEligibleProjector(battle.attacker.playerID, attacker) then
        return
    end

    -- Attacking a city or a unit from the same team cannot continue a project.
    if battle.defender.isCity then
        ClearProject(battle.attacker.playerID, battle.attacker.unitID)
        return
    end

    local defender = GetUnit(battle.defender.playerID, battle.defender.unitID)
    if defender == nil then
        return
    end

    local attackerPlayer = Players[battle.attacker.playerID]
    local defenderPlayer = Players[battle.defender.playerID]
    if attackerPlayer == nil or defenderPlayer == nil
        or attackerPlayer:GetTeam() == defenderPlayer:GetTeam() then
        ClearProject(battle.attacker.playerID, battle.attacker.unitID)
        return
    end

    battle.eligible = true
    battle.targetOwner = battle.defender.playerID
    battle.targetUnit = battle.defender.unitID

    local project = ReadProject(battle.attacker.playerID, battle.attacker.unitID)
    local sameTarget = project.targetOwner == battle.targetOwner
        and project.targetUnit == battle.targetUnit
        and project.stacks > 0

    if sameTarget then
        battle.startingStacks = project.stacks
        ApplyTemporaryAttackPromotion(attacker, project.stacks)
    else
        -- Choosing another enemy immediately drops the old project.
        ClearProject(battle.attacker.playerID, battle.attacker.unitID)
        battle.startingStacks = 0
    end
end

local function OnBattleJoined(playerID, unitOrCityID, role, isCity)
    if g_CurrentBattle == nil then
        return
    end

    -- Community Patch battle roles: attacker = 0, defender = 1.
    if role == 0 then
        g_CurrentBattle.attacker = {
            playerID = playerID,
            unitID = unitOrCityID,
            isCity = isCity
        }
    elseif role == 1 then
        g_CurrentBattle.defender = {
            playerID = playerID,
            unitID = unitOrCityID,
            isCity = isCity
        }
    end
    PrepareBattle()
end

local function OnUnitCaptured(byPlayer, byUnit, capturedPlayer, capturedUnit, willBeKilled, captureType)
    if not willBeKilled
        and g_CurrentBattle ~= nil
        and g_CurrentBattle.targetOwner == capturedPlayer
        and g_CurrentBattle.targetUnit == capturedUnit then
        g_CurrentBattle.targetCaptured = true
    end
end

local function ClearProjectsAimedAt(targetOwner, targetUnit)
    for playerID = 0, GameDefines.MAX_MAJOR_CIVS - 1 do
        if IsGabrielPlayer(playerID) then
            local player = Players[playerID]
            for unit in player:Units() do
                local project = ReadProject(playerID, unit:GetID())
                if project.targetOwner == targetOwner and project.targetUnit == targetUnit then
                    ClearProject(playerID, unit:GetID())
                end
            end
        end
    end
end

local function OnUnitPrekill(ownerID, unitID, unitType, x, y, delay, killerPlayer)
    if g_CurrentBattle ~= nil
        and g_CurrentBattle.targetOwner == ownerID
        and g_CurrentBattle.targetUnit == unitID then
        g_CurrentBattle.targetKilled = true
    end
    ClearProjectsAimedAt(ownerID, unitID)
end

local function OnBattleFinished()
    local battle = g_CurrentBattle
    g_CurrentBattle = nil
    if battle == nil or battle.attacker == nil then
        return
    end

    local attacker = GetUnit(battle.attacker.playerID, battle.attacker.unitID)
    ClearTemporaryAttackPromotions(attacker)
    if not battle.eligible or attacker == nil then
        return
    end

    local targetSurvived = GetUnit(battle.targetOwner, battle.targetUnit) ~= nil
    if battle.targetCaptured then
        ClearProject(battle.attacker.playerID, battle.attacker.unitID)
        return
    end

    if battle.targetKilled or not targetSurvived then
        if battle.startingStacks >= 2 then
            attacker:ChangeDamage(-15)
            attacker:ChangeExperience(5)
            NotifyPlayer(battle.attacker.playerID,
                "TXT_KEY_GABRIEL_PROJECT_COMPLETED_NOTIFICATION", attacker:GetName())
        end
        ClearProject(battle.attacker.playerID, battle.attacker.unitID)
        return
    end

    local newStacks = math.min(MAX_PROJECT_STACKS, battle.startingStacks + 1)
    WriteProject(
        battle.attacker.playerID,
        battle.attacker.unitID,
        battle.targetOwner,
        battle.targetUnit,
        newStacks,
        Game.GetGameTurn())
end

-- ---------------------------------------------------------------------------
-- Fresh Sets
-- ---------------------------------------------------------------------------

local function FreshDestinationKey(playerID, era, city)
    return string.format(
        "GABRIEL_BOULDER_FRESH_%d_%d_%d_%d",
        playerID, era, city:GetX(), city:GetY())
end

local function CheckFreshSets(playerID)
    if not IsGabrielPlayer(playerID) then
        return
    end
    local player = Players[playerID]
    local routes = player:GetTradeRoutes()
    if routes == nil then
        return
    end

    local era = player:GetCurrentEra()
    local reward = 15 + (5 * era)
    for _, route in ipairs(routes) do
        local destination = route.ToCity
        if route.Domain == DOMAIN_LAND
            and route.FromID == playerID
            and destination ~= nil then
            local key = FreshDestinationKey(playerID, era, destination)
            if GetNumber(key, 0) == 0 then
                SetNumber(key, 1)
                player:ChangeOverflowResearch(reward)
                player:ChangeJONSCulture(reward)
                NotifyPlayer(playerID, "TXT_KEY_GABRIEL_FRESH_SETS_NOTIFICATION",
                    destination:GetName(), reward)
            end
        end
    end
end

-- ---------------------------------------------------------------------------
-- Gym Hopper exploration and upgrade inheritance
-- ---------------------------------------------------------------------------

local function GenerationKey(playerID, unitID)
    return SaveKey("GENERATION", playerID, unitID)
end

local function LineageKey(playerID, unitID)
    return SaveKey("GYM_LINEAGE", playerID, unitID)
end

local function SetGymLineage(playerID, unitID, enabled)
    SetNumber(LineageKey(playerID, unitID), enabled and 1 or 0)
end

local function HasGymLineage(playerID, unitID)
    return GetNumber(LineageKey(playerID, unitID), 0) == 1
end

local function ExplorationKey(playerID, unitID, foreignOwner)
    local generation = GetNumber(GenerationKey(playerID, unitID), 0)
    return SaveKey("GYM_VISIT", playerID, unitID,
        string.format("%d_%d", generation, foreignOwner))
end

local function OnUnitCreated(playerID, unitID, unitType, x, y)
    -- Unit IDs can be reused, so every new unit receives a new persistence generation.
    SetNumber(GenerationKey(playerID, unitID),
        GetNumber(GenerationKey(playerID, unitID), 0) + 1)
    ClearProject(playerID, unitID)
    SetGymLineage(playerID, unitID, unitType == UNIT_GYM_HOPPER)
end

local function OnUnitSetXY(playerID, unitID, x, y)
    if x == nil or y == nil or x < 0 or y < 0 then
        return
    end
    local unit = GetUnit(playerID, unitID)
    if unit == nil or unit:GetUnitType() ~= UNIT_GYM_HOPPER then
        return
    end
    local plot = Map.GetPlot(x, y)
    if plot == nil then
        return
    end
    local foreignOwner = plot:GetOwner()
    if foreignOwner == NO_PLAYER or foreignOwner == playerID then
        return
    end
    local foreignPlayer = Players[foreignOwner]
    if foreignPlayer == nil or not foreignPlayer:IsAlive() or foreignPlayer:IsBarbarian() then
        return
    end

    local key = ExplorationKey(playerID, unitID, foreignOwner)
    if GetNumber(key, 0) == 0 then
        SetNumber(key, 1)
        unit:ChangeExperience(2)
        NotifyPlayer(playerID, "TXT_KEY_GABRIEL_GYM_HOPPER_VISIT_NOTIFICATION",
            unit:GetName(), foreignPlayer:GetName())
    end
end

local function CopyProjectToUpgrade(playerID, oldUnitID, newUnitID)
    local project = ReadProject(playerID, oldUnitID)
    if project.stacks > 0 and ProjectTargetStillExists(project) then
        WriteProject(playerID, newUnitID, project.targetOwner, project.targetUnit,
            project.stacks, project.lastAttackTurn)
    end
    ClearProject(playerID, oldUnitID)
end

local function OnUnitUpgraded(playerID, oldUnitID, newUnitID, isGoodyHutUpgrade)
    local newUnit = GetUnit(playerID, newUnitID)
    if newUnit == nil then
        return
    end
    local inheritedGymLineage = HasGymLineage(playerID, oldUnitID)
        or newUnit:GetUnitType() == UNIT_GYM_HOPPER

    CopyProjectToUpgrade(playerID, oldUnitID, newUnitID)
    SetGymLineage(playerID, newUnitID, inheritedGymLineage)
end

local function TransferGymVisits(oldPlayerID, oldUnitID, newPlayerID, newUnitID)
    -- Conversions are rare, so a bounded player-slot loop is preferable to
    -- allowing a captured or gifted Gym Hopper to re-earn old destinations.
    for foreignOwner = 0, GameDefines.MAX_CIV_PLAYERS - 1 do
        local oldKey = ExplorationKey(oldPlayerID, oldUnitID, foreignOwner)
        if GetNumber(oldKey, 0) == 1 then
            SetNumber(ExplorationKey(newPlayerID, newUnitID, foreignOwner), 1)
        end
    end
end

local function OnUnitConverted(oldPlayerID, newPlayerID, oldUnitID, newUnitID, isUpgrade)
    local newUnit = GetUnit(newPlayerID, newUnitID)
    if newUnit == nil then
        return
    end
    local inheritedGymLineage = HasGymLineage(oldPlayerID, oldUnitID)
        or HasGymLineage(newPlayerID, newUnitID)
        or newUnit:GetUnitType() == UNIT_GYM_HOPPER
    SetGymLineage(newPlayerID, newUnitID, inheritedGymLineage)

    if isUpgrade then
        -- UnitUpgraded fires before CvUnit::convert copies promotions. UnitConverted
        -- fires after that copy, so persistent promotion state must be finalized here.
        local project = ReadProject(newPlayerID, newUnitID)
        UpdateDeterminationPromotion(newUnit, project.stacks)
        if inheritedGymLineage then
            SetPromotion(newUnit, PROMOTION_HILL_FAMILIARITY, true)
        end
        return
    end

    ClearProject(newPlayerID, newUnitID)
    ClearProject(oldPlayerID, oldUnitID)
    if newUnit:GetUnitType() == UNIT_GYM_HOPPER then
        TransferGymVisits(oldPlayerID, oldUnitID, newPlayerID, newUnitID)
    end
    if inheritedGymLineage and newUnit:GetUnitType() ~= UNIT_GYM_HOPPER then
        SetPromotion(newUnit, PROMOTION_HILL_FAMILIARITY, true)
    end
end

-- ---------------------------------------------------------------------------
-- Turn maintenance and initialization
-- ---------------------------------------------------------------------------

local function ReconcileGabrielUnits(playerID)
    local player = Players[playerID]
    local currentTurn = Game.GetGameTurn()
    for unit in player:Units() do
        ClearTemporaryAttackPromotions(unit)
        local unitID = unit:GetID()
        local project = ReadProject(playerID, unitID)
        if project.stacks > 0 then
            if currentTurn - project.lastAttackTurn >= PROJECT_TIMEOUT_TURNS
                or not ProjectTargetStillExists(project) then
                ClearProject(playerID, unitID)
            else
                UpdateDeterminationPromotion(unit, project.stacks)
            end
        else
            UpdateDeterminationPromotion(unit, 0)
        end
        if unit:GetUnitType() == UNIT_GYM_HOPPER then
            SetGymLineage(playerID, unitID, true)
        elseif HasGymLineage(playerID, unitID) then
            SetPromotion(unit, PROMOTION_HILL_FAMILIARITY, true)
        end
    end
end

local function OnPlayerDoTurn(playerID)
    if not IsGabrielPlayer(playerID) then
        return
    end
    ReconcileGabrielUnits(playerID)
    CheckFreshSets(playerID)
end

local function Initialize()
    -- Remove any temporary combat modifier left behind by a mid-combat save or an
    -- interrupted event chain, then restore only persistent visible state.
    for playerID = 0, GameDefines.MAX_CIV_PLAYERS - 1 do
        local player = Players[playerID]
        if player ~= nil and player:IsAlive() then
            for unit in player:Units() do
                ClearTemporaryAttackPromotions(unit)
            end
        end
        if IsGabrielPlayer(playerID) then
            ReconcileGabrielUnits(playerID)
        end
    end
end

if GameEvents.BattleStarted ~= nil then
    GameEvents.BattleStarted.Add(OnBattleStarted)
end
if GameEvents.BattleJoined ~= nil then
    GameEvents.BattleJoined.Add(OnBattleJoined)
end
if GameEvents.BattleFinished ~= nil then
    GameEvents.BattleFinished.Add(OnBattleFinished)
end
if GameEvents.UnitCaptured ~= nil then
    GameEvents.UnitCaptured.Add(OnUnitCaptured)
end
if GameEvents.UnitPrekill ~= nil then
    GameEvents.UnitPrekill.Add(OnUnitPrekill)
end
if GameEvents.UnitCreated ~= nil then
    GameEvents.UnitCreated.Add(OnUnitCreated)
end
if GameEvents.UnitSetXY ~= nil then
    GameEvents.UnitSetXY.Add(OnUnitSetXY)
end
if GameEvents.UnitUpgraded ~= nil then
    GameEvents.UnitUpgraded.Add(OnUnitUpgraded)
end
if GameEvents.UnitConverted ~= nil then
    GameEvents.UnitConverted.Add(OnUnitConverted)
end
GameEvents.PlayerDoTurn.Add(OnPlayerDoTurn)

Initialize()
