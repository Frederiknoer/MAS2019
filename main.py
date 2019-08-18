from pygridmas import World, Vec2D, Visualizer
from explorer import Explorer
from transporter import Transporter
from common import Base, Ore
from masparams import MasParams

mp = MasParams()
world = World(w=mp.G, h=mp.G, torus_enabled=True)
base_pos = Vec2D(mp.G // 3, mp.G // 3)
n_ores = round(mp.G ** 2 * mp.D)

base = Base()
world.add_agent(base, pos=base_pos)

for _ in range(mp.X):
    world.add_agent(Explorer(base), pos=base_pos)

for _ in range(mp.Y):
    world.add_agent(Transporter(base, mp), pos=base_pos)

for _ in range(n_ores):
    world.add_agent(Ore())

vis = Visualizer(world, scale=3, target_speed=40)
vis.start()
