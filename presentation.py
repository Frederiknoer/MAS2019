from pygridmas import Visualizer
from masparams import DefaultParams
from main import create_world
import random
import numpy as np


def default_demo(N=1, M=1):
    random.seed(0)
    world = create_world(DefaultParams(N=N, M=M))
    Visualizer(world, scale=3, target_speed=40, start_paused=True).start()


def base_full_test():
    durations = []
    mp = DefaultParams(N=1)
    for i in range(30):
        print(i)
        world = create_world(mp)
        base = [a for a in world.agents.values() if "BASE" in a.group_ids][0]
        while base.cargo < mp.C:
            world.step()
        durations.append(world.time)
    mu, std = np.mean(durations), np.std(durations, ddof=1)
    print(mu, std, mu - 1.96 * std, mu + 1.96 * std)


def broker_transporter():
    random.seed(0)
    world = create_world(DefaultParams(N=1, G=50))
    while world.time < 30:
        world.step()
    Visualizer(world, scale=10, target_speed=1, start_paused=True).start()


def broker_broker():
    random.seed(0)
    mp = DefaultParams()
    mp.N, mp.G = 1, 50
    world = create_world(mp)
    while world.time < 110:
        world.step()
    Visualizer(world, scale=10, target_speed=1, start_paused=True).start()


def presentation():
    default_demo()
    default_demo(N=2, M=1)
    default_demo(N=2, M=0)
    broker_transporter()
    broker_broker()


if __name__ == '__main__':
    presentation()
