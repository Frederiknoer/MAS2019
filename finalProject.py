from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import random
import math

size = 100
world = World(w=size, h=size, torus_enabled=True)
worldCenter = Vec2D(size // 2, size // 2)
n_ores = 50
n_explorers = 10
n_transporters = 10

BLOCK = "BLOCK"
BASE = "BASE"
ORE = "ORE"
EXPLORER = "EXPLORER"
TRANSPORTER = "TRANSPORTER"


class Ore(Agent):
    color = Colors.YELLOW
    group_ids = {ORE}


class Base(Agent):
    color = Colors.BLUE
    group_ids = {BASE}


class Explorer(Agent):
    color = Colors.GREEN
    group_ids = {EXPLORER}

    def step(self):
        explorers = self.box_scan(10, EXPLORER)
        if explorers:
            for explorer in explorers:
                if explorer.pos() != explorer.pos():
                    self.move_away_from(explorers[0].pos())
                    return
        self.move_rel(Vec2D.random_grid_dir())


class Transporter(Agent):
    color = Colors.RED
    group_ids = {TRANSPORTER}
    state = 'idle'
    base: Agent = None
    target: Vec2D = None
    ore_pos: list = None

    def __init__(self, base):
        super(Transporter).__init__()
        self.base = base

    def step(self):
        if self.state == 'idle':
            # Look for explorers and follow one of the nearest ones.
            # If there are none, go to the base.
            explorers = self.box_scan(10, EXPLORER)
            if explorers:
                dist = self.inf_dist(explorers[0].pos())
                explorers = [a for a in explorers if self.inf_dist(a.pos()) == dist]
                self.target = random.choice(explorers).pos()
            else:
                self.target = self.base.pos()
            self.state = 'go to target'
        elif self.state == 'go to target':
            if self.pos() == self.target:
                self.state = 'idle'
                self.step()
            else:
                self.move_towards(self.target)

base = Base()
world.add_agent(base, pos=worldCenter)

for _ in range(n_ores):
    world.add_agent(Ore())

for _ in range(n_explorers):
    world.add_agent(Explorer(), pos=worldCenter)

for _ in range(n_transporters):
    world.add_agent(Transporter(base), pos=worldCenter)

vis = Visualizer(world, scale=3, target_speed=40)
vis.start()
