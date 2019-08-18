from pygridmas import World, Vec2D, Visualizer
from explorer import Explorer
from transporter import Transporter
from common import Base, Ore

size = 200
ore_density = 0.1
world = World(w=size, h=size, torus_enabled=True)
base_pos = Vec2D(size // 3, size // 3)
n_ores = round(size ** 2 * ore_density)
n_explorers = 10
n_transporters = 30

base = Base()
world.add_agent(base, pos=base_pos)

for _ in range(n_explorers):
    world.add_agent(Explorer(base), pos=base_pos)

for _ in range(n_transporters):
    world.add_agent(Transporter(base), pos=base_pos)

for _ in range(n_ores):
    world.add_agent(Ore())

vis = Visualizer(world, scale=3, target_speed=15)
vis.start()
