from main import create_world
from masparams import MasParams
from common import Ore
from transporter import Transporter
from explorer import Explorer
from pygridmas import Visualizer
from pygridmas.examples.log import AgentCountLogger
import matplotlib.pyplot as plt
import numpy as np


class EnergyLogger:
    energy = 0

    def bind(self, robot_class):
        class RobotLog(robot_class):
            energy_logger = self

        return RobotLog

    def __call__(self, energy_used):
        self.energy += energy_used


def draw_sample(mp, N, T):
    data = np.empty((N, 2, T))
    for i in range(N):
        ore_counter = AgentCountLogger()
        OreLog = ore_counter.bind(Ore)

        energy_logger = EnergyLogger()
        ExplorerLog = energy_logger.bind(Explorer)
        TransporterLog = energy_logger.bind(Transporter)

        world = create_world(mp, Ore=OreLog, Transporter=TransporterLog, Explorer=ExplorerLog)

        start_ore_count = ore_counter.count
        for j in range(T):
            data[i, 0, j] = (ore_counter.count - start_ore_count) / start_ore_count
            data[i, 1, j] = energy_logger.energy
            world.step()
    return data


def main():
    N = 30
    T = 3000
    #  test X vs Y
    XY = False
    P = False
    I = False
    E = False
    S = False
    W = False
    M = True

    if XY:
        data = np.empty((3, N, 2, T))
        for i, (X, Y) in enumerate([(5, 15), (10, 10), (15, 5)]):
            mp = MasParams()
            mp.N, mp.X, mp.Y = 1, X, Y
            data[i] = draw_sample(mp, N, T)
            print(i)
        np.save("stats/XY", data)

    if P:
        data = np.empty((3, N, 2, T))
        for i, P in enumerate([3, 7, 15]):
            mp = MasParams()
            mp.N, mp.P = 1, P
            data[i] = draw_sample(mp, N, T)
            print(i)
        np.save("stats/P", data)

    if I:
        data = np.empty((3, N, 2, T))
        for i, I in enumerate([9, 19, 39]):
            mp = MasParams()
            mp.N, mp.I = 1, I
            data[i] = draw_sample(mp, N, T)
            print(i)
        np.save("stats/I", data)

    if E:
        data = np.empty((3, N, 2, T))
        for i, E in enumerate([250, 500, 1000]):
            mp = MasParams()
            mp.N, mp.E = 1, E
            data[i] = draw_sample(mp, N, T)
            print(i)
        np.save("stats/E", data)

    if S:
        data = np.empty((3, N, 2, T))
        for i, S in enumerate([5, 10, 20]):
            mp = MasParams()
            mp.N, mp.S = 1, S
            data[i] = draw_sample(mp, N, T)
            print(i)
        np.save("stats/S", data)

    if W:
        data = np.empty((3, N, 2, T))
        for i, W in enumerate([10, 20, 40]):
            mp = MasParams()
            mp.N, mp.W = 1, W
            data[i] = draw_sample(mp, N, T)
            print(i)
        np.save("stats/W", data)

    if M:
        data = np.empty((2, N, 2, T))
        for i, M in enumerate([1, 0]):
            mp = MasParams()
            mp.N, mp.M = 1, M
            data[i] = draw_sample(mp, N, T)
            print(i)
        np.save("stats/M", data)


if __name__ == '__main__':
    main()
