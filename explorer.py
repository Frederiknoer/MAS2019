import random

from pygridmas import Colors, Vec2D
from robot import Robot
from broker import Broker
from common import ORE, EXPLORER, TRANSPORTER, ORE_POSITIONS, BASE_FULL


ATTEMPT_DELEGATION = "ATTEMPT_DELEGATION"
MOVE_TO_TARGET = "MOVE_TO_TARGET"
SCAN = "SCAN"


class Explorer(Robot):
    color = Colors.GREEN
    state = MOVE_TO_TARGET
    step_size = 10
    ore_data = None
    ores = []
    dir: Vec2D = None
    broker: Broker = None

    def initialize(self):
        super().initialize()
        self.group_ids.add(EXPLORER)
        self.group_ids.add('{}{}'.format(EXPLORER, self.company_id))
        self.target = self.base.pos()
        self.broker = Broker(self)

    def set_new_random_rel_target(self):
        v = self.dir * random.randint(self.step_size * 0.5, self.step_size * 1.5)
        self.target = self.world.torus(self.pos() + v.round())

    def handle_broker_status(self, success: bool):
        self.state = MOVE_TO_TARGET
        if success:
            self.set_new_random_rel_target()
            self.ore_data = None
        else:
            self.target = self.base.pos()

    def step(self):
        super().before_step()

        if self.energy_low() or self.base_full:
            self.reactive_move_towards(self.base.pos())
        elif self.broker.step():
            pass  # broker is active
        elif self.state == ATTEMPT_DELEGATION:
            self.broker.attempt_ore_data_delegation(self.ore_data, self.handle_broker_status)
        elif self.state == MOVE_TO_TARGET:
            if self.reached_target():
                if self.at_base():
                    self.dir = Vec2D.random_dir()
                if self.ore_data:
                    self.state = ATTEMPT_DELEGATION
                else:
                    self.state = SCAN
            else:
                self.reactive_move_towards(self.target)

        elif self.state == SCAN:
            agents = self.box_scan(self.mp.P // 2)
            self.consume_energy(self.mp.P)
            ores = [a for a in agents if ORE in a.group_ids]
            explorers = [a for a in agents if EXPLORER in a.group_ids]
            transporters = [a for a in agents if TRANSPORTER in a.group_ids]

            if ores:
                ttl = 3
                data = [(o.idx, o.pos()) for o in ores]
                self.ore_data = (data, ttl)
                self.state = ATTEMPT_DELEGATION
                """
                rel_ore_pos = [self.vec_to(o.pos()) for o in ores]
                rel_ore_cog = sum(rel_ore_pos, Vec2D()) / len(ores)
                if rel_ore_cog.magnitude() > self.mp.P / 4:
                    # TODO: set max iterations
                    self.color = Colors.MAGENTA
                    self.target = self.world.torus(self.pos() + rel_ore_cog.round())
                    self.state = "MOVE_TO_TARGET"
                else:
                    rel_ore_pos = [self.vec_to(o.pos()) for o in ores]
                    tsm_idx = tsm.iterative_inf_norm_tsm(rel_ore_pos, n=1000)
                    ores = [ores[i] for i in tsm_idx]
                    ore_data = [(o.idx, o.pos()) for o in ores]
                    self.ore_data = (len(transporters), ore_data)
                """
            else:
                self.set_new_random_rel_target()
                self.state = MOVE_TO_TARGET

        self.broker.nearby_idle_transporters = 0
        super().after_step()

    def receive_event(self, event_type, data):
        self.broker.receive_event(event_type, data)
        if event_type == ORE_POSITIONS:
            ores, ttl = data
            self.ore_data = ores, ttl - 1
        if event_type == BASE_FULL:
            self.base_full = True
