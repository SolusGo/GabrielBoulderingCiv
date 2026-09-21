"""Deterministic regression model for Gabriel's persistent gameplay protocols.

This does not emulate Civ V combat. It exercises the callback-order and keying
rules that the Lua implementation uses around creation, conversion, save/load,
UnitID reuse, One More Go stack progression, and Fresh Sets destination keys.
"""

from __future__ import annotations

import unittest
from collections import defaultdict


GYM_HOPPER = "UNIT_GABRIEL_GYM_HOPPER"


class VisitStateModel:
    def __init__(self) -> None:
        self.generation = defaultdict(int)
        self.visits: set[tuple[int, int, int, int]] = set()
        self.ready: set[tuple[int, int]] = set()
        self.precreated: set[tuple[int, int]] = set()
        self.creation_position: dict[tuple[int, int], tuple[int, int]] = {}
        self.unit_types: dict[tuple[int, int], str] = {}
        self.xp = defaultdict(int)

    def _bump(self, unit: tuple[int, int]) -> None:
        self.generation[unit] += 1

    def create(self, unit: tuple[int, int], unit_type: str, position: tuple[int, int]) -> None:
        self.unit_types[unit] = unit_type
        if unit_type != GYM_HOPPER:
            return
        if unit not in self.precreated:
            self._bump(unit)
        self.precreated.discard(unit)
        self.ready.add(unit)
        self.creation_position[unit] = position

    def prepare_transfer(self, unit: tuple[int, int], position: tuple[int, int]) -> None:
        if unit not in self.ready:
            self._bump(unit)
            self.ready.add(unit)
            self.precreated.add(unit)
        self.creation_position[unit] = position

    def transfer(self, old: tuple[int, int], new: tuple[int, int],
                 position: tuple[int, int]) -> None:
        self.prepare_transfer(new, position)
        old_generation = self.generation[old]
        new_generation = self.generation[new]
        for player, unit_id, generation, foreign_owner in tuple(self.visits):
            if (player, unit_id, generation) == (*old, old_generation):
                self.visits.add((*new, new_generation, foreign_owner))

    def set_xy(self, unit: tuple[int, int], position: tuple[int, int],
               plot_owner: int | None, barbarian: bool = False) -> None:
        if self.unit_types.get(unit) != GYM_HOPPER or unit not in self.ready:
            return
        creation = self.creation_position.get(unit)
        if creation is not None:
            if creation == position:
                return
            del self.creation_position[unit]
        if plot_owner is None or plot_owner == unit[0] or barbarian:
            return
        visit = (*unit, self.generation[unit], plot_owner)
        if visit not in self.visits:
            self.visits.add(visit)
            self.xp[unit] += 2

    def reload(self) -> None:
        self.ready.clear()
        self.precreated.clear()
        self.creation_position.clear()
        for unit, unit_type in self.unit_types.items():
            if unit_type == GYM_HOPPER:
                if self.generation[unit] <= 0:
                    self.generation[unit] = 1
                self.ready.add(unit)

    def prekill(self, unit: tuple[int, int]) -> None:
        self.ready.discard(unit)
        self.precreated.discard(unit)
        self.creation_position.pop(unit, None)
        self.unit_types.pop(unit, None)


class GameplayLifecycleTests(unittest.TestCase):
    def test_new_hopper_and_first_visits(self) -> None:
        model = VisitStateModel()
        unit = (0, 4)
        model.set_xy(unit, (1, 1), 0)  # Initial SetXY before UnitCreated.
        model.create(unit, GYM_HOPPER, (1, 1))
        model.set_xy(unit, (1, 1), 0)
        self.assertEqual(model.xp[unit], 0)
        model.set_xy(unit, (2, 1), 1)
        model.set_xy(unit, (3, 1), 1)
        self.assertEqual(model.xp[unit], 2)
        model.set_xy(unit, (4, 1), 2)
        self.assertEqual(model.xp[unit], 4)

    def test_capture_transfer_with_normal_callback_order(self) -> None:
        model = VisitStateModel()
        old, new = (0, 7), (3, 2)
        model.create(old, GYM_HOPPER, (0, 0))
        model.set_xy(old, (1, 0), 1)
        model.unit_types[new] = GYM_HOPPER
        model.set_xy(new, (6, 6), 1)  # Placement before UnitCreated: no award.
        model.create(new, GYM_HOPPER, (6, 6))
        model.transfer(old, new, (6, 6))
        model.set_xy(new, (7, 6), 1)
        self.assertEqual(model.xp[new], 0)
        model.set_xy(new, (8, 6), 2)
        self.assertEqual(model.xp[new], 2)

    def test_transfer_before_created_is_idempotent(self) -> None:
        model = VisitStateModel()
        old, new = (0, 7), (3, 2)
        model.create(old, GYM_HOPPER, (0, 0))
        model.set_xy(old, (1, 0), 1)
        model.unit_types[new] = GYM_HOPPER
        model.transfer(old, new, (6, 6))  # Reversed callback order.
        transferred_generation = model.generation[new]
        model.create(new, GYM_HOPPER, (6, 6))
        self.assertEqual(model.generation[new], transferred_generation)
        model.set_xy(new, (7, 6), 1)
        self.assertEqual(model.xp[new], 0)

    def test_save_load_and_unit_id_reuse(self) -> None:
        model = VisitStateModel()
        unit = (0, 4)
        model.create(unit, GYM_HOPPER, (0, 0))
        model.set_xy(unit, (1, 0), 1)
        first_generation = model.generation[unit]
        model.reload()
        model.set_xy(unit, (2, 0), 1)
        self.assertEqual(model.xp[unit], 2)
        model.prekill(unit)
        model.create(unit, GYM_HOPPER, (0, 0))
        self.assertGreater(model.generation[unit], first_generation)
        model.set_xy(unit, (1, 0), 1)
        self.assertEqual(model.xp[unit], 4)

    def test_upgrade_retains_visit_history_without_global_unit_writes(self) -> None:
        model = VisitStateModel()
        old, upgraded, irrelevant = (0, 4), (0, 9), (5, 12)
        model.create(old, GYM_HOPPER, (0, 0))
        model.set_xy(old, (1, 0), 1)
        model.create(upgraded, "UNIT_SPEARMAN", (1, 0))
        model.transfer(old, upgraded, (1, 0))
        self.assertIn((*upgraded, model.generation[upgraded], 1), model.visits)
        model.create(irrelevant, "UNIT_WARRIOR", (5, 5))
        self.assertEqual(model.generation[irrelevant], 0)

    def test_unchanged_project_and_fresh_sets_rules(self) -> None:
        attack_bonus = lambda stacks: 0 if stacks == 0 else min(stacks, 3) * 5
        self.assertEqual([attack_bonus(n) for n in (0, 1, 2, 3, 4)], [0, 5, 10, 15, 15])
        temporary_bonus = attack_bonus(3)
        self.assertEqual(temporary_bonus, 15)
        temporary_bonus = 0  # BattleFinished/reconciliation cleanup.
        self.assertEqual(temporary_bonus, 0)
        projects = {(0, 4): (2, 11, 2, 90)}
        projects[(0, 9)] = projects.pop((0, 4))
        self.assertEqual(projects, {(0, 9): (2, 11, 2, 90)})
        paid: set[tuple[int, int, int]] = set()
        destination = (12, 19)
        rewards = []
        for era in (0, 0, 1):
            key = (era, *destination)
            if key not in paid:
                paid.add(key)
                rewards.append(15 + 5 * era)
        self.assertEqual(rewards, [15, 20])


def run_regressions() -> None:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GameplayLifecycleTests)
    result = unittest.TestResult()
    suite.run(result)
    if not result.wasSuccessful():
        details = [message for _, message in result.failures + result.errors]
        raise AssertionError("; ".join(details))


if __name__ == "__main__":
    unittest.main(verbosity=2)
