from common import CompanyEntity, TRANSPORTER_IDLE, COMPANY, BROKER
from common import TRANSPORTER_REQUEST, TRANSPORTER, TRANSPORTER_RESPONSE, ORE_POSITIONS
from pygridmas import Colors

BROKER_PING = "BROKER_PING"
BROKER_REQUEST = "BROKER_REQUEST"
BROKER_REQUESTING = "BROKER_REQUESTING"
BROKER_RESPONSE = "BROKER_RESPONSE"
BROKER_RESPONDING = "BROKER_RESPONDING"
TRANSPORTER_REQUESTING = "TRANSPORTER_REQUESTING"


class Broker:
    request_id = None
    status_cb = None
    state = None
    counter = 0
    nearby = []
    status = None
    ore_data = None

    def __init__(self, comp_entity: CompanyEntity):
        self.ce = comp_entity
        self.ce.group_ids.add(BROKER)

    def base_dist(self):
        return self.ce.vec_to(self.ce.closest_base().pos()).inf_magnitude()

    def attempt_ore_data_delegation(self, ore_data, status_cb):
        self.ore_data = ore_data
        self.status_cb = status_cb
        self.request_transporter()

    def request_transporter(self):
        self.state = TRANSPORTER_REQUESTING
        data = (self.ce.idx, self.ore_data[0])
        self.ce.emit_event(
            self.ce.mp.I // 2, TRANSPORTER_REQUEST, data,
            '{}{}'.format(TRANSPORTER, self.ce.company_id)
        )
        self.ce.consume_energy(1)
        self.ce.color = Colors.WHITE
        self.nearby = []
        self.counter = 0

    def request_broker(self):
        self.state = BROKER_REQUESTING
        _, _, idxs = self.ore_data
        data = (self.base_dist(), idxs, self.ore_data[0])
        self.ce.emit_event(
            self.ce.mp.I // 2, BROKER_REQUEST, data,
            '{}{}'.format(COMPANY, self.ce.company_id)
        )
        self.ce.consume_energy(1)
        self.ce.color = Colors.BLUE
        self.nearby = []
        self.counter = 0

    def step(self):
        active = self.state is not None
        if self.state == BROKER_RESPONDING:
            data = (self.base_dist(), self.ce.idx)
            self.ce.emit_event(self.ce.mp.I // 2, BROKER_RESPONSE, data, self.request_id)
            self.ce.consume_energy(1)
            self.state = None
        elif self.state == TRANSPORTER_REQUESTING:
            self.counter += 1
            if self.counter == 2:
                self.state = None
                if self.nearby:
                    self.nearby.sort()
                    self.ce.emit_event(self.ce.mp.I // 2, ORE_POSITIONS, self.ore_data, self.nearby[0][1])
                    self.ce.color = Colors.MAGENTA
                    self.ce.consume_energy(1)
                    self.status_cb(True)
                else:
                    if self.ce.at_base():
                        self.request_transporter()
                    else:
                        ttl = self.ore_data[1]
                        if ttl > 0 and self.ce.mp.K == 1:
                            self.request_broker()
                        else:
                            self.status_cb(False)
        elif self.state == BROKER_REQUESTING:
            self.counter += 1
            if self.counter == 2:
                self.state = None
                if self.nearby:
                    self.nearby.sort()
                    self.ce.emit_event(self.ce.mp.I // 2, ORE_POSITIONS, self.ore_data, self.nearby[0][1])
                    self.ce.color = Colors.MAGENTA
                    self.ce.consume_energy(1)
                    self.status_cb(True)
                else:
                    self.status_cb(False)
        return active

    def receive_event(self, event_type, data):
        if event_type == BROKER_RESPONSE and self.state == BROKER_REQUESTING:
            self.nearby.append(data)
        elif event_type == TRANSPORTER_RESPONSE and self.state == TRANSPORTER_REQUESTING:
            pos, idx = data
            dist = self.ce.vec_to(pos).inf_magnitude()
            self.nearby.append((dist, idx))
        elif self.state is not None:
            # can only handle one broker state at a time
            return
        elif event_type == BROKER_REQUEST:
            dist, idxs, ores = data
            new_ores = [o for o in ores if o not in self.ce.ores]
            self.ce.color = (0.4, 0.6, 0.4)
            if self.ce.idx not in idxs and self.base_dist() < dist and len(self.ce.ores) + len(new_ores) <= self.ce.mp.S:
                self.state = BROKER_RESPONDING
                self.request_id = idxs[-1]
                self.ce.color = Colors.CYAN
