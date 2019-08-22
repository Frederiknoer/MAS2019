import matplotlib.pyplot as plt
import numpy as np
from stats import experiments
import sys

args = sys.argv[1:] if len(sys.argv) > 1 else experiments.keys()
_experiments = [(name, rng) for (name, rng) in experiments.items() if name in args]

a = 0.05
colors = [(1, 0, 0, a), (0, 1, 0, a), (0, 0, 1, a)]

i = 0
for range_name, rng in _experiments:
    plt.figure(figsize=(3, 2))

    i += 1
    data = np.load("stats/{}.npy".format(range_name))
    K, N, _, T = data.shape
    data[:, :, 0] *= 100
    print(range_name)
    for k, params in enumerate(rng):
        if type(params) == int or type(params) == float:
            params = (params,)
        for j in range(N):
            plt.plot(data[k, j, 0], c=colors[k])

        label = []
        for p, val in zip(range_name, params):
            label.append('{}={}'.format(p, val))
        label = ', '.join(label)

        plt.plot(data[k, :, 0].reshape((N, T)).mean(axis=0), c=colors[k][:-1], label=label)
    """
    ax = plt.gca()
    ax.tick_params(axis='x', length=0)
    ax.xaxis.set_major_formatter(plt.NullFormatter())
    if i % 2 == 0:
        ax.tick_params(axis='y', length=0)
        ax.yaxis.set_major_formatter(plt.NullFormatter())
    plt.ylim([0, 60 if i < 7 else 100])
    """
    plt.grid()
    plt.legend(loc='upper left')
    plt.tight_layout(pad=0)
    plt.savefig("plots/{}.png".format(range_name), dpi=300)
