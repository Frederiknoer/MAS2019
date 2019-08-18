import random

from pygridmas import Colors, Vec2D
from robot import Robot
from common import ORE, EXPLORER, TRANSPORTER
import tsm


class Explorer(Robot):
    color = Colors.GREEN
    group_ids = {EXPLORER}
    state = "MOVE_TO_TARGET"
    step_size = 10
    ore_data = None
    dir: Vec2D = None

    def set_new_random_rel_target(self):
        v = self.dir * self.step_size
        self.target = self.world.torus(self.pos() + v.round())

    def initialize(self):
        self.target = self.base.pos()

    def step(self):
        super().before_step()

        if self.state == "MOVE_TO_TARGET":
            self.color = Colors.GREEN
            if self.reached_target():
                if self.at_base():
                    self.dir = Vec2D.random_dir()
                if self.ore_data:
                    transporters = self.box_scan(self.mp.P // 2, TRANSPORTER)
                    self.charge_energy(self.mp.P)
                    self.ore_data = (len(transporters), self.ore_data[1])
                    self.state = "EMIT_EVENT_ORE_POS"
                else:
                    self.state = "SCAN"
            else:
                if not self.move_towards(self.target):
                    self.move_in_dir(Vec2D.random_grid_dir())
                    self.charge_energy(self.mp.Q)

        elif self.state == "SCAN":
            self.color = Colors.GREY25
            agents = self.box_scan(self.mp.P // 2)
            self.charge_energy(self.mp.P)
            ores = [a for a in agents if ORE in a.group_ids]
            explorers = [a for a in agents if EXPLORER in a.group_ids]
            transporters = [a for a in agents if TRANSPORTER in a.group_ids]

            if ores:
                rel_ore_pos = [self.vec_to(o.pos()) for o in ores]
                rel_ore_cog = sum(rel_ore_pos, Vec2D()) / len(ores)
                if rel_ore_cog.magnitude() > self.mp.P / 4:
                    # TODO: set max iterations
                    self.color = Colors.MAGENTA
                    self.target = self.world.torus(self.pos() + rel_ore_cog.round())
                    self.state = "MOVE_TO_TARGET"
                else:
                    rel_ore_pos = [self.vec_to(o.pos()) for o in ores]
                    tsm_idx = tsm.iterative_inf_norm_tsm(rel_ore_pos, n=1000)
                    ores = [ores[i] for i in tsm_idx]
                    ore_data = [(o.idx, o.pos()) for o in ores]
                    self.ore_data = (len(transporters), ore_data)
                    if transporters:
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

        super().after_step()
