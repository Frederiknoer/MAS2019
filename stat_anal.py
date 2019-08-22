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

    for k, params in enumerate(rng):
        if type(params) == int or type(params) == float:
            params = (params,)

        label = []
        for p, val in zip(range_name, params):
            label.append('{}={}'.format(p, val))
        label = ', '.join(label)
        labels.append(label)

        _data = data[k, :, 0, -1]
        mu.append(_data.mean())
        ssqr.append(_data.var(ddof=1))

    print(mu)

    for i in range(K):
        for j in range(i+1, K):
            val = mu[i] - mu[j]
            std = math.sqrt((ssqr[i] + ssqr[j]) / N)
            z = val / std
            p = st.norm.cdf(-abs(z)) * 2
            #p = st.t.cdf(-abs(z), N + N - 2) * 2
            print('{} !vs! {}: p={}'.format(labels[i], labels[j], p))
