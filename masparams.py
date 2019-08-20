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
    W = 10  # Transporter capacity
    E = 500  # Robot energy capacity
    S = 20  # memory size of each robot (S <= X+Y)
    Q = 2  # Cost of motion action
