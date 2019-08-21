from pygridmas import Agent
from masparams import MasParams

# group id names
BLOCK = "BLOCK"
COMPANY = "COMPANY"
BASE = "BASE"
ORE = "ORE"
EXPLORER = "EXPLORER"
TRANSPORTER = "TRANSPORTER"
BROKER = "BROKER"

# communication names
BASE_FULL = "BASE_FULL"
ORE_DELIVERY = "ORE_DELIVERY"
ORE_POSITIONS = "ORE_POSITIONS"
TRANSPORTER_IDLE = "TRANSPORTER_IDLE"
TRANSPORTER_REQUEST = "TRANSPORTER_REQUEST"
TRANSPORTER_RESPONSE = "TRANSPORTER_RESPONSE"


class Ore(Agent):
    color = (.25, .25, 0)
    group_ids = {ORE}

    def initialize(self):
        self.deactivate()


class CompanyEntity(Agent):
    energy_logger = None

    def __init__(self, mp: MasParams, company_id):
        super().__init__()
        self.mp = mp
        self.energy = mp.E
        self.company_id = company_id

    def consume_energy(self, energy_consumption):
        self.energy -= energy_consumption
        if self.energy_logger:
            self.energy_logger(energy_consumption)

    def initialize(self):
        self.group_ids.add(self.idx)
        self.group_ids.add('{}{}'.format(COMPANY, self.company_id))
