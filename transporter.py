import random

from pygridmas import Colors
from common import TRANSPORTER, BASE, BASE_FULL
from common import TRANSPORTER_REQUEST, TRANSPORTER_RESPONSE, ORE_POSITIONS, ORE_DELIVERY
from robot import Robot

IDLE = 'IDLE'
COLLECT_ORES = 'COLLECT_ORES'
BROKER_RESPONDING = 'BROKER_RESPONDING'


class Transporter(Robot):
    color = Colors.RED
    group_ids = {TRANSPORTER}
    state = IDLE
    ores: list = None
    cargo = 0
    broker_id = None
    counter = 0

    def initialize(self):
        super().initialize()
        self.group_ids.add('{}{}'.format(TRANSPORTER, self.company_id))
        self.group_ids.add(self.idx)
        self.ores = []

    def full(self):
        assert (self.cargo <= self.mp.W)
        return self.cargo == self.mp.W

    def step(self):
        super().before_step()

        if self.at_base() and self.cargo:
            self.emit_event(0, ORE_DELIVERY, self.cargo, BASE)
            self.cargo = 0
        elif self.full() or self.energy_low() or self.base_full:
            self.reactive_move_towards(self.closest_base().pos())
        elif self.state == IDLE:
            if random.random() < self.counter * 0.005:
                self.reactive_move_towards(self.closest_base().pos())
            self.counter += 1
        elif self.state == BROKER_RESPONDING:
            if self.counter == 0:
                self.emit_event(self.mp.I // 2, TRANSPORTER_RESPONSE, (self.pos(), self.idx), self.broker_id)
                self.consume_energy(1)
            elif self.counter == 2:
                #  didn't get it  :/
                self.state = IDLE
                self.counter = 0
            self.counter += 1
        elif self.state == COLLECT_ORES:
            ore_idx, ore_pos = self.ores[0]
            if ore_pos == self.pos():
                self.ores.pop(0)
                if self.try_collect_ore(ore_idx):
                    self.cargo += 1
                self.consume_energy(1)
                if not self.ores:
                    self.state = IDLE
                    self.counter = 0
            else:
                self.reactive_move_towards(ore_pos)

        super().after_step()

    def try_collect_ore(self, idx):
        if idx in self.world.agents:
            self.world.remove_agent(idx)
            return True
        else:
            return False

    def receive_event(self, event_type, data):
        if event_type == ORE_POSITIONS:
            ores = data[0]
            self.ores += list(ores)
            self.state = COLLECT_ORES
        elif event_type == TRANSPORTER_REQUEST:
            broker_id, N = data
            if self.state == IDLE or len(self.ores) + N <= self.mp.S:
                self.state = BROKER_RESPONDING
                self.counter = 0
                self.broker_id = broker_id
        elif event_type == BASE_FULL:
            self.base_full = True
