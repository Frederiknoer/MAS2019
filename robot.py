from pygridmas import Agent, Colors, Vec2D
from masparams import MasParams
from common import BLOCK, Base


class Robot(Agent):
    state = ""
    target: Vec2D = None
    group_collision_ids = {BLOCK}

    def __init__(self, base: Base, mp: MasParams):
        super().__init__()
        self.mp = mp
        self.energy = mp.E
        self.base = base
        self.base_full = False

    def at_base(self):
        return self.pos() == self.base.pos()

    def reached_target(self):
        return self.target == self.pos()

    def charge_energy(self, energy_consumption):
        self.energy -= energy_consumption

    def before_step(self):
        if self.at_base():
            self.energy = self.mp.E

        if self.energy <= 0:
            self.deactivate()
            self.group_ids = {BLOCK} if not self.at_base() else set()
            self.color = Colors.MAGENTA

        if self.energy <= self.vec_to(self.base.pos()).inf_magnitude() * self.mp.Q + self.mp.P + 10:
            self.target = self.base.pos()
            self.state = "MOVE_TO_TARGET"

    def after_step(self):
        if self.at_base():
            if BLOCK in self.group_ids:
                self.group_ids.remove(BLOCK)
        else:
            self.group_ids.add(BLOCK)

        if self.world.time >= self.mp.T:
            self.target = self.base.pos()
            if self.pos() == self.base.pos():
                self.deactivate()

        if self.base_full:
            self.target = self.base.pos()
            if self.pos() == self.base.pos():
                self.deactivate()
