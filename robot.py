from pygridmas import Colors, Vec2D
from masparams import MasParams
from common import BLOCK, CompanyEntity
from base import Base


class Robot(CompanyEntity):
    state = ""
    target: Vec2D = None
    group_collision_ids = {BLOCK}

    def __init__(self, base: Base, mp: MasParams, company_id):
        super().__init__(mp, company_id)
        self.energy = mp.E
        self.base = base
        self.base_full = False

    def at_base(self):
        return self.pos() == self.base.pos()

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
        dist_to_base = self.vec_to(self.base.pos()).inf_magnitude()
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

        if self.world.time >= self.mp.T:
            self.target = self.base.pos()
            if self.pos() == self.base.pos():
                self.deactivate()

        if self.base_full:
            self.target = self.base.pos()
            if self.pos() == self.base.pos():
                self.deactivate()

        if self.energy <= 0:
            self.deactivate()
            self.group_ids = {BLOCK} if not self.at_base() else set()
            self.color = Colors.MAGENTA
