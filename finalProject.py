from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import random
import math
import tsm

size = 200
ore_density = 0.1
world = World(w=size, h=size, torus_enabled=True)
base_pos = Vec2D(size // 3, size // 3)
n_ores = round(size ** 2 * ore_density)
n_explorers = 10
n_transporters = 10

BLOCK = "BLOCK"
BASE = "BASE"
ORE = "ORE"
EXPLORER = "EXPLORER"
TRANSPORTER = "TRANSPORTER"


class Ore(Agent):
    color = (.1, .1, 0)
    group_ids = {ORE}

    def initialize(self):
        self.deactivate()


class Base(Agent):
    color = Colors.BLUE
    group_ids = {BASE}


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

    def __init__(self, base):
        super().__init__()
        self.base = base

    def set_new_random_rel_target(self):
        self.target = Vec2D(
            random.randint(self.pos().x - self.step_size, self.pos().x + self.step_size),
            random.randint(self.pos().y - self.step_size, self.pos().y + self.step_size)
        )
        self.target = world.torus(self.target)

    def initialize(self):
        self.set_new_random_rel_target()

    def reached_target(self):
        return self.target == self.pos()

    def step(self):
        if self.state == "MOVE_TO_TARGET":
            self.color = Colors.GREEN
            if self.reached_target():
                if self.ore_data:
                    transporters = self.box_scan(10, TRANSPORTER)
                    self.ore_data = (len(transporters), self.ore_data)
                    self.state = "EMIT_EVENT_ORE_POS"
                else:
                    self.state = "SCAN"
            else:
                if not self.move_towards(self.target):
                    self.move_in_dir(Vec2D.random_grid_dir())

        elif self.state == "SCAN":
            self.color = Colors.GREY25
            agents = self.box_scan(10)
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
            self.emit_event(rng=25, data=self.ore_data, group_id=TRANSPORTER)
            self.ore_data = None
            self.set_new_random_rel_target()
            self.state = "MOVE_TO_TARGET"

        # do not block on base station
        if self.pos() == self.base.pos():
            if BLOCK in self.group_ids:
                self.group_ids.remove(BLOCK)
        else:
            self.group_ids.add(BLOCK)


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
                        dir = random.choice(transporters).vec_to(self.pos())
                        dir = dir.normalize() if not dir.is_zero_vec() else Vec2D.random_dir()
                        dir *= 10
                        self.target = self.world.torus(self.pos() + dir.round())
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

    def receive_event(self, _, ore_data):
        if self.ores:
            return
        n_transporters, ores = ore_data
        if random.random() < 1 / max(n_transporters, 1):
            self.ores = list(ores)
            self.failed_collect_attempts = 0
            self.state = 'COLLECT_ORES'


base = Base()
world.add_agent(base, pos=base_pos)

for _ in range(n_explorers):
    world.add_agent(Explorer(base), pos=base_pos)

for _ in range(n_transporters):
    world.add_agent(Transporter(base), pos=base_pos)

for _ in range(n_ores):
    world.add_agent(Ore())

vis = Visualizer(world, scale=3, target_speed=40)
vis.start()
