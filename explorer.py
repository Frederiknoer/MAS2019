import random
from pygridmas import Agent, Colors, Vec2D

from common import ORE, BLOCK, EXPLORER, TRANSPORTER
import tsm
from masparams import MasParams


class Explorer(Agent):
    color = Colors.GREEN
    group_ids = {EXPLORER}
    group_collision_ids = {BLOCK}
    target: Vec2D = None
    moveType = ""
    state = "MOVE_TO_TARGET"
    step_size = 10
    ore_data = None
    base: Agent = None
    dir: Vec2D = None

    def __init__(self, base, masparams: MasParams):
        super().__init__()
        self.masparams = masparams
        self.energy = masparams.E
        self.perception_range = masparams.P
        self.base = base

    def set_new_random_rel_target(self):
        v = Vec2D.random_dir() * self.step_size
        self.target = self.world.torus(self.pos() + v.round())

    def initialize(self):
        self.set_new_random_rel_target()

    def reached_target(self):
        return self.target == self.pos()

    def charge_energy(self, energy_comsumption):
        self.energy -= energy_comsumption

    def step(self):
        if self.pos() == self.base.pos():
            self.energy = self.masparams.E

        if self.energy <= 0:
            self.deactivate()
            self.group_ids.remove(Explorer)
            self.color = Colors.MAGENTA
            return

        if self.energy <= self.vec_to(self.base.pos()).inf_magnitude() * self.masparams.Q - self.masparams.P:
            self.target = self.base.pos()
            self.state = "MOVE_TO_TARGET"

        if self.state == "MOVE_TO_TARGET":
            self.color = Colors.GREEN
            if self.reached_target():
                if self.ore_data:
                    transporters = self.box_scan(self.perception_range // 2, TRANSPORTER)
                    self.charge_energy(self.perception_range)
                    self.ore_data = (len(transporters), self.ore_data)
                    self.state = "EMIT_EVENT_ORE_POS"
                else:
                    self.state = "SCAN"
            else:
                if not self.move_towards(self.target):
                    self.move_in_dir(Vec2D.random_grid_dir())
                    self.charge_energy(self.masparams.Q)

        elif self.state == "SCAN":
            self.color = Colors.GREY25
            agents = self.box_scan(self.perception_range // 2)
            self.charge_energy(self.perception_range)
            ores = [a for a in agents if ORE in a.group_ids]
            explorers = [a for a in agents if EXPLORER in a.group_ids]
            transporters = [a for a in agents if TRANSPORTER in a.group_ids]

            if ores:
                rel_ore_pos = [self.vec_to(o.pos()) for o in ores]
                rel_ore_cog = sum(rel_ore_pos, Vec2D()) / len(ores)
                if rel_ore_cog.magnitude() > 3:
                    # TODO: set max iterations
                    self.color = Colors.MAGENTA
                    self.target = self.world.torus(self.pos() + rel_ore_cog.round())
                    self.state = "MOVE_TO_TARGET"
                else:
                    rel_ore_pos = [self.vec_to(o.pos()) for o in ores]
                    tsm_idx = tsm.iterative_inf_norm_tsm(rel_ore_pos, n=1000)
                    ores = [ores[i] for i in tsm_idx]
                    self.ore_data = [(o.idx, o.pos()) for o in ores]
                    if transporters:
                        self.ore_data = (len(transporters), self.ore_data)
                        self.state = "EMIT_EVENT_ORE_POS"
                    else:
                        self.target = self.base.pos()
                        self.state = "MOVE_TO_TARGET"
            elif explorers:
                other_expl = random.choice(explorers)
                dir = other_expl.vec_to(self.pos())
                dir = dir / dir.magnitude() if not dir.is_zero_vec() else Vec2D.random_dir()
                self.target = self.world.torus(other_expl.pos() + (dir * 20).round())
                self.state = "MOVE_TO_TARGET"
            else:
                self.set_new_random_rel_target()
                self.state = "MOVE_TO_TARGET"

        elif self.state == "EMIT_EVENT_ORE_POS":
            self.color = Colors.WHITE
            self.emit_event(25, "ORE_POSITIONS", self.ore_data, TRANSPORTER)
            self.charge_energy(1)
            self.ore_data = None
            self.set_new_random_rel_target()
            self.state = "MOVE_TO_TARGET"

        # do not block on base station
        if self.pos() == self.base.pos():
            if BLOCK in self.group_ids:
                self.group_ids.remove(BLOCK)
        else:
            self.group_ids.add(BLOCK)
