from pygridmas import World, Agent, Vec2D, Visualizer, Colors
from explorer import Explorer
from transporter import Transporter
from common import Ore
from base import Base
from masparams import MasParams, DefaultParams
import random
import math


class BaseArea(Agent):
    color = (0.5, 0.5, 0.5)

    def initialize(self):
        self.deactivate()


def create_world(mp: MasParams, World=World, Base=Base, Transporter=Transporter, Explorer=Explorer, Ore=Ore):
    world = World(w=mp.G, h=mp.G, torus_enabled=True)

    n_ores = round(mp.G ** 2 * mp.D)
    for _ in range(n_ores):
        world.add_agent(Ore())

    positions = []
    for x in range(mp.G):
        for y in range(mp.G):
            positions.append(Vec2D(x, y))
    if mp.N == 1:
        base_positions = [Vec2D(mp.G // 2, mp.G // 2)]
    else:
        base_positions = random.sample(positions, mp.N)
    for base_pos in base_positions:
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                d_pos = Vec2D(dx, dy)
                world.add_agent(BaseArea(), world.torus(base_pos + d_pos))

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
    zoom = True
    mp = DefaultParams()
    mp.N = 1
    scale = 3
    if zoom:
        mp.G = 50
        scale = 10
    world = create_world(mp)
    vis = Visualizer(world, scale=scale, target_speed=40, start_paused=True)
    vis.start()


if __name__ == '__main__':
    main()


"""
Transporter:
    Default         : RED
    Can receive ores: Orange
    Can not --||--  : Pale red
    Received ores   : Bright red
    
Explorer
    Default         : Green
    Scan            : Yellow
    Request TP      : White
    Request Broker  : Blue
    Emit ore pos    : Magenta
    Can receive ores: Cyan
    Can not --||--  : Pale green
    Received ores   : Bright green
    
"""
