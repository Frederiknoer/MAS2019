from pygridmas import Colors, Vec2D
from masparams import MasParams
from common import BLOCK, CompanyEntity
from base import Base
from typing import List
import math


class Robot(CompanyEntity):
    state = ""
    target: Vec2D = None
    group_collision_ids = {BLOCK}

    def __init__(self, bases: List[Base], mp: MasParams, company_id):
        super().__init__(mp, company_id)
        self.energy = mp.E
        self.bases = bases
        self.base_full = False

    def at_base(self):
        return self.pos() == self.closest_base().pos()

    def closest_base(self):
        mi = math.inf
        closest_base = None
        for base in self.bases:
            dist = self.vec_to(base.pos()).inf_magnitude()
            if dist < mi:
                closest_base = base
                mi = dist
        return closest_base

    def reached_target(self):
        return self.target == self.pos()

    def reactive_move_towards(self, pos: Vec2D):
        if self.move_towards(pos) or self.move_in_dir(Vec2D.random_grid_dir()):
            self.consume_energy(self.mp.Q)
            return True
        return False

    def reactive_move_in_dir(self, pos: Vec2D):
        if self.move_in_dir(pos) or self.move_in_dir(Vec2D.random_grid_dir()):
            self.consume_energy(self.mp.Q)
            return True
        return False

    def energy_low(self):
        # TODO: possibly remove the self.mp.P and make sure not to use that energy
        dist_to_base = self.vec_to(self.closest_base().pos()).inf_magnitude()
        margin = self.mp.P + self.mp.Q * 5
        return self.energy <= dist_to_base * self.mp.Q + margin

    def before_step(self):
        if self.at_base():
            self.energy = self.mp.E

    def after_step(self):
        if self.at_base():
            if BLOCK in self.group_ids:
                self.group_ids.remove(BLOCK)
        else:
            self.group_ids.add(BLOCK)

        if self.world.time >= self.mp.T or self.base_full:
            self.target = self.closest_base().pos()
            if self.at_base():
                self.deactivate()

        if self.energy <= 0:
            self.deactivate()
            self.group_ids = {BLOCK} if not self.at_base() else set()
            self.color = Colors.MAGENTA
