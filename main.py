from pygridmas import World, Vec2D, Visualizer
from explorer import Explorer
from transporter import Transporter
from common import Base, Ore
from masparams import MasParams
import random


def create_world(mp: MasParams):
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

    for base_pos, comp_id in zip(base_positions, company_ids):
        base = Base(mp, comp_id)
        world.add_agent(base, base_pos)

        for _ in range(mp.X):
            world.add_agent(Explorer(base, mp, comp_id), pos=base_pos)
        for _ in range(mp.Y):
            world.add_agent(Transporter(base, mp, comp_id), pos=base_pos)

    return world


def main():
    mp = MasParams()
    mp.N = 1
    mp.M = 0
    world = create_world(mp)
    vis = Visualizer(world, scale=3, target_speed=40)
    vis.start()


if __name__ == '__main__':
    main()
