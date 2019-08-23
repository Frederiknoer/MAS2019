import math


class MasParams:
    G = 200  # Size of planet (GxG)
    D = 0.05  # Ore density
    T = 3000  # Maximum number of cycles

    M = 1  # Coordination mode, cooperative = 1, competitive = 0
    N = 3  # Number of bases
    X = 10  # Number of explorers per base
    Y = 10  # Number of transporters per base

    C = math.inf  # Base capacity (n ores)
    P = 7  # Initial perception scope (P <= G/20 and P <= I)
    I = 21  # Communication scope  (I <= G/5)
    W = 20  # Transporter capacity
    E = 500  # Robot energy capacity
    S = 10  # memory size of each robot (S <= X+Y)
    Q = 2  # Cost of motion action

    #  own defined parameters
    K = 1  # Broker enabled
    R = 0  # Random explorer direction every time


class DefaultParams(MasParams):
    C = 175
    D = 0.04
    E = 960
    G = 225
    I = 33
    P = 7
    Q = 1.4
    S = 11
    T = 77500
    W = 7
    X = 6
    Y = 7
