from main import create_world
from masparams import MasParams
from common import Ore
from transporter import Transporter
from explorer import Explorer
from pygridmas.examples.log import AgentCountLogger
import numpy as np
import sys


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
        print(i)
        ore_counter = AgentCountLogger()
        OreLog = ore_counter.bind(Ore)

        energy_logger = EnergyLogger()
        ExplorerLog = energy_logger.bind(Explorer)
        TransporterLog = energy_logger.bind(Transporter)

        world = create_world(mp, Ore=OreLog, Transporter=TransporterLog, Explorer=ExplorerLog)

        start_ore_count = ore_counter.count
        for j in range(T):
            data[i, 0, j] = (start_ore_count - ore_counter.count) / start_ore_count
            data[i, 1, j] = energy_logger.energy
            world.step()
    return data


experiments = {
    'XY': [(5, 15), (10, 10), (15, 5)],
    'P': [3, 7, 15],
    'I': [9, 19, 39],
    'E': [250, 500, 1000],
    'S': [5, 10, 20],
    'W': [10, 20, 40],
    'NM': [(3, 1), (3, 0)],
    'KI': [(1, 39), (0, 39)],
}


def main():
    N = 30
    T = 3000

    args = sys.argv[1:] if len(sys.argv) > 1 else experiments.keys()
    _experiments = [(name, rng) for (name, rng) in experiments.items() if name in args]

    for range_name, rng in _experiments:
        data = np.empty((len(rng), N, 2, T))
        for i, params in enumerate(rng):
            if type(params) == int or type(params) == float:
                params = (params,)
            mp = MasParams()
            mp.N = 1
            for param_name, val in zip(range_name, params):
                mp.__setattr__(param_name, val)
            print(range_name, i)
            data[i] = draw_sample(mp, N, T)
        np.save("stats/{}".format(range_name), data)


if __name__ == '__main__':
    main()
