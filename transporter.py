import random

from pygridmas import Colors, Vec2D
from common import TRANSPORTER, EXPLORER, BASE
from robot import Robot


class Transporter(Robot):
    color = Colors.RED
    group_ids = {TRANSPORTER}
    state = 'IDLE'
    ores: list = None
    cargo = 0
    failed_collect_attempts = 0

    def step(self):
        super().before_step()

        if self.at_base() and self.cargo:
            self.emit_event(0, "ORE_DELIVERY", self.cargo, BASE)
            self.cargo = 0

        if self.state == 'IDLE':
            # Look for explorers and follow one of the nearest ones.
            # If there are none, go to the base.
            agents = self.box_scan(self.mp.P // 2)
            self.energy -= self.mp.P
            explorers = [a for a in agents if EXPLORER in a.group_ids]
            transporters = [a for a in agents if TRANSPORTER in a.group_ids]
            if explorers:
                self.target = random.choice(explorers).pos()
                if transporters:
                    if random.random() < 1 - 1 / (len(transporters) + 1):
                        v = random.choice(transporters).vec_to(self.pos())
                        v = v.normalize() if not v.is_zero_vec() else Vec2D.random_dir()
                        v *= 10
                        self.target = self.world.torus(self.pos() + v.round())
            else:
                self.target = self.base.pos()
            self.target = self.base.pos()  # TODO: temp
            self.state = 'MOVE_TO_TARGET'
        elif self.state == 'MOVE_TO_TARGET':
            if self.reached_target():
                self.state = 'IDLE' if not self.ores else 'COLLECT_ORES'
            else:
                if self.move_towards(self.target) or self.move_in_dir(Vec2D.random_grid_dir()):
                    self.energy -= self.mp.Q
        elif self.state == 'COLLECT_ORES':
            ore_idx, ore_pos = self.ores[0]
            if ore_pos == self.pos():
                self.ores.pop(0)
                if self.try_collect_ore(ore_idx):
                    self.cargo += 1
                else:
                    self.failed_collect_attempts += 1
                    if self.failed_collect_attempts >= 2:  # two failed attempts in a row
                        self.ores = []
                if len(self.ores) == 0:
                    self.state = 'IDLE'
                self.energy -= 1
            else:
                if self.move_towards(ore_pos) or self.move_in_dir(Vec2D.random_grid_dir()):
                    self.energy -= 1
        else:
            assert False, "shouldn't reach unknown state: '{}'".format(self.state)

        super().after_step()

    def try_collect_ore(self, idx):
        if idx in self.world.agents:
            self.world.remove_agent(idx)
            return True
        else:
            return False

    def receive_event(self, event_type, data):
        if event_type == "ORE_POSITIONS":
            if self.ores:
                return
            n_transporters, ores = data
            if random.random() < 1 / max(n_transporters, 1):
                # TODO: make communication and agree on who takes what
                self.ores = list(ores)
                self.failed_collect_attempts = 0
                self.state = 'COLLECT_ORES'
