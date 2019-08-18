import random

from pygridmas import Agent, Colors, Vec2D
from common import TRANSPORTER, BLOCK, EXPLORER


class Transporter(Agent):
    color = Colors.RED
    group_ids = {TRANSPORTER}
    group_collision_ids = {BLOCK}
    state = 'IDLE'
    base: Agent = None
    target: Vec2D = None
    ores: list = None
    cargo = 0
    collected = set()
    failed_collect_attempts = 0

    def __init__(self, base):
        super().__init__()
        self.base = base

    def step(self):
        if self.state == 'IDLE':
            # Look for explorers and follow one of the nearest ones.
            # If there are none, go to the base.
            agents = self.box_scan(10)
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
            if self.pos() == self.target:
                self.state = 'IDLE'
            else:
                if not self.move_towards(self.target):
                    self.move_in_dir(Vec2D.random_grid_dir())
        elif self.state == 'COLLECT_ORES':
            ore_idx, ore_pos = self.ores[0]
            if ore_pos == self.pos():
                self.ores.pop(0)
                if self.try_collect_ore(ore_idx):
                    self.cargo += 1
                    self.collected.add(ore_idx)
                else:
                    self.failed_collect_attempts += 1
                    if self.failed_collect_attempts >= 2:  # two failed attempts in a row
                        self.ores = []
                if len(self.ores) == 0:
                    self.state = 'IDLE'
            else:
                if not self.move_towards(ore_pos):
                    self.move_in_dir(Vec2D.random_grid_dir())
        else:
            assert False, "shouldn't reach unknown state: '{}'".format(self.state)

        # do not block on base station
        if self.pos() == self.base.pos():
            if BLOCK in self.group_ids:
                self.group_ids.remove(BLOCK)
        else:
            self.group_ids.add(BLOCK)

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
                self.ores = list(ores)
                self.failed_collect_attempts = 0
                self.state = 'COLLECT_ORES'
