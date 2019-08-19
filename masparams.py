class MasParams:
    G = 200  # Size of planet (GxG)
    D = 0.1  # Ore density
    T = 3500  # Maximum number of cycles

    M = 1  # Coordination mode, cooperative = 1, competitive = 0
    N = 1  # Number of bases
    X = 10  # Number of explorers per base
    Y = 10  # Number of transporters per base

    C = 200  # Base capacity (n ores)
    P = G // 20  # Initial perception scope (P <= G/20 and P <= I)
    I = G // 5  # Communication scope  (I <= G/5)
    W = 10  # Transporter capacity
    E = 1000  # Robot energy capacity
    S = X + Y  # memory size of each robot (S <= X+Y)
    Q = 1  # Cost of motion action
