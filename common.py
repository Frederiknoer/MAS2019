from pygridmas import Agent, Colors

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
