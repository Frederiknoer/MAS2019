from pygridmas import World, Vec2D, Visualizer
from explorer import Explorer
from transporter import Transporter
from common import Ore
from base import Base
from masparams import MasParams
import random
import math


def create_world(mp: MasParams, World=World, Base=Base, Transporter=Transporter, Explorer=Explorer, Ore=Ore):
    world = World(w=mp.G, h=mp.G, torus_enabled=True)

    n_ores = round(mp.G ** 2 * mp.D)
    for _ in range(n_ores):
        world.add_agent(Ore())

    positions = []
    for x in range(mp.G):
        for y in range(mp.G):
            positions.append(Vec2D(x, y))
    base_positions = random.sample(positions, mp.N)
    if mp.M == 1:  # cooperation
        company_ids = [0] * mp.N
    else:  # competitive
        company_ids = list(range(mp.N))
    bases = []
    for base_pos, comp_id in zip(base_positions, company_ids):
        base = Base(mp, comp_id)
        world.add_agent(base, base_pos)
        bases.append(base)

    for base_pos, comp_id in zip(base_positions, company_ids):
        _bases = bases if mp.M == 1 else [bases[comp_id]]

        for _ in range(mp.X):
            world.add_agent(Explorer(_bases, mp, comp_id), pos=base_pos)
        for _ in range(mp.Y):
            world.add_agent(Transporter(_bases, mp, comp_id), pos=base_pos)

    return world


def main():
    mp = MasParams()
    mp.T = math.inf
    mp.M = 1
    mp.I = 39
    world = create_world(mp)
    vis = Visualizer(world, scale=3, target_speed=40, start_paused=True)
    vis.start()


if __name__ == '__main__':
    main()
