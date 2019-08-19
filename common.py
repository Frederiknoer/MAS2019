from pygridmas import Agent, Colors
from masparams import MasParams

BLOCK = "BLOCK"
BASE = "BASE"
ORE = "ORE"
EXPLORER = "EXPLORER"
TRANSPORTER = "TRANSPORTER"


class Ore(Agent):
    color = (.25, .25, 0)
    group_ids = {ORE}

    def initialize(self):
        self.deactivate()


class Base(Agent):
    color = Colors.BLUE
    group_ids = {BASE}

    def __init__(self, mp: MasParams):
        super().__init__()
        self.mp = mp


    def initialize(self):
        self.n_of_ores = 0

    def step(self):
        if self.n_of_ores >= self.mp.C:
            self.emit_event((self.mp.I)//2, "BASE_FULL")
        print(self.n_of_ores)


    def receive_event(self, event_type, data):
        if event_type == "ORE_DELIVERY":
            self.n_of_ores += data


