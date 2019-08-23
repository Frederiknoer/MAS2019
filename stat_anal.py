import scipy.stats as st
import numpy as np
from stats import experiments
import math

for range_name, rng in experiments.items():
    data = np.load("stats/{}.npy".format(range_name))
    K, N, _, T = data.shape
    data[:, :, 0] *= 100
    print(range_name)

    mu = []
    ssqr = []
    labels = []
    emu = []
    epos = []

    for k, params in enumerate(rng):
        if type(params) == int or type(params) == float:
            params = (params,)

        label = []
        for p, val in zip(range_name, params):
            label.append('{}={}'.format(p, val))
        label = ', '.join(label)
        labels.append(label)

        ores = data[k, :, 0, -1]
        mu.append(ores.mean())
        ssqr.append(ores.var(ddof=1))

        energy = data[k, :, 1, -1]
        emu.append(energy.mean())

        ores *= 0.01 * 200 ** 2 * 0.05
        epo = (energy / ores).mean()
        epos.append(epo)

    print(mu)
    #print(emu)
    print(epos)

    for i in range(K):
        for j in range(i+1, K):
            val = mu[i] - mu[j]
            std = math.sqrt((ssqr[i] + ssqr[j]) / N)
            z = val / std
            p = st.norm.cdf(-abs(z)) * 2
            #p = st.t.cdf(-abs(z), N + N - 2) * 2
            print('{} !vs! {}: p={}'.format(labels[i], labels[j], p))
