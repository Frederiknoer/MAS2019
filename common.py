from pygridmas import Agent, Colors
from masparams import MasParams

BLOCK = "BLOCK"
COMPANY = "COMPANY"
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
    cargo = 0

    def __init__(self, mp: MasParams, comp_id):
        super().__init__()
        self.mp = mp
        self.company_id = comp_id
        self.group_ids.add(BASE + str(comp_id))
        self.group_ids.add(COMPANY + str(comp_id))

    def step(self):
        if self.cargo >= self.mp.C:
            self.emit_event(self.mp.I // 2, "BASE_FULL", None, COMPANY + str(self.company_id))

    def receive_event(self, event_type, data):
        if event_type == "ORE_DELIVERY":
            self.cargo = min(self.cargo + data, self.mp.C)

