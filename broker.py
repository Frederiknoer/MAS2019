from common import CompanyEntity, TRANSPORTER_IDLE, COMPANY, BROKER
from common import TRANSPORTER_REQUEST, TRANSPORTER, TRANSPORTER_RESPONSE, ORE_POSITIONS
import random

BROKER_PING = "BROKER_PING"
BROKER_REQUEST = "BROKER_REQUEST"
BROKER_REQUESTING = "BROKER_REQUESTING"
BROKER_RESPONSE = "BROKER_RESPONSE"
BROKER_RESPONDING = "BROKER_RESPONDING"
TRANSPORTER_REQUESTING = "TRANSPORTER_REQUESTING"


class Broker:
    nearby_idle_transporters = 0
    distant_idle_transporters = 0

    request_id = None
    status_cb = None
    state = None
    ping_counter = 0
    counter = 0
    nearby = []
    status = None
    ore_data = None

    def __init__(self, comp_entity: CompanyEntity):
        self.ce = comp_entity
        self.ce.group_ids.add(BROKER)
        self.ping_counter = random.randint(5, 10)

    def attempt_ore_data_delegation(self, ore_data, status_cb):
        self.ore_data = ore_data
        if self.nearby_idle_transporters:
            self.request_transporter()
        else:
            ores, ttl = ore_data
            if ttl > 0:
                self.request_broker()
            else:
                status_cb(False)
        self.status_cb = status_cb

    def request_transporter(self):
        self.state = TRANSPORTER_REQUESTING
        self.ce.emit_event(
            self.ce.mp.I // 2, TRANSPORTER_REQUEST, self.ce.idx,
            '{}{}'.format(TRANSPORTER, self.ce.company_id)
        )
        self.nearby = []
        self.counter = 0

    def request_broker(self):
        self.state = BROKER_REQUESTING
        self.ce.emit_event(
            self.ce.mp.I // 2, BROKER_REQUEST, self.ce.idx,
            '{}{}'.format(COMPANY, self.ce.company_id)
        )
        self.nearby = []
        self.counter = 0

    def step(self):
        active = self.state is not None
        if self.state == BROKER_RESPONDING:
            data = (self.nearby_idle_transporters, self.distant_idle_transporters, self.ce.idx)
            self.ce.emit_event(self.ce.mp.I // 2, BROKER_RESPONSE, data, self.request_id)
            self.state = None
        elif self.state == TRANSPORTER_REQUESTING:
            self.counter += 1
            if self.counter == 2:
                self.state = None
                if self.nearby:
                    self.nearby.sort()
                    self.ce.emit_event(self.ce.mp.I // 2, ORE_POSITIONS, self.ore_data, self.nearby[0][1])
                    self.status_cb(True)
                else:
                    self.request_broker()
        elif self.state == BROKER_REQUESTING:
            self.counter += 1
            if self.counter == 2:
                self.state = None
                if self.nearby:
                    self.nearby.sort(reverse=True)
                    self.ce.emit_event(self.ce.mp.I // 2, ORE_POSITIONS, self.ore_data, self.nearby[0][2])
                    self.status_cb(True)
                else:
                    self.status_cb(False)
        elif self.ping_counter <= 0:
            self.ping_counter = random.randint(5, 10)
            self.ce.emit_event(
                self.ce.mp.I // 2, BROKER_PING,
                (self.nearby_idle_transporters, self.distant_idle_transporters),
                '{}{}'.format(COMPANY, self.ce.company_id)
            )
            active = True
        else:
            self.ping_counter -= 1
        self.distant_idle_transporters *= 0.5
        return active

    def receive_event(self, event_type, data):
        if event_type == TRANSPORTER_IDLE:
            self.nearby_idle_transporters += 1
        elif event_type == BROKER_PING:
            other_nearby_tps, other_distant_tps = data
            self.distant_idle_transporters += other_nearby_tps + 0.1 * other_distant_tps
        elif event_type == BROKER_RESPONSE and self.state == BROKER_REQUESTING:
            self.nearby.append(data)
        elif event_type == TRANSPORTER_RESPONSE and self.state == TRANSPORTER_REQUESTING:
            pos, idx = data
            dist = self.ce.vec_to(pos).inf_magnitude()
            self.nearby.append((dist, idx))
        elif self.state is not None:
            # can only handle one broker state at a time
            return
        elif event_type == BROKER_REQUEST:
            self.state = BROKER_RESPONDING
            self.request_id = data
