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
    ores = None
    dir: Vec2D = None
    broker: Broker = None
    counter = 0

    def initialize(self):
        super().initialize()
        self.group_ids.add(EXPLORER)
        self.group_ids.add('{}{}'.format(EXPLORER, self.company_id))
        self.target = self.closest_base().pos()
        self.broker = Broker(self)
        self.ores = []

    def set_new_dir_target(self):
        self.target = self.world.torus(self.pos() + (self.dir * self.mp.P).round())

    def handle_broker_status(self, success: bool):
        self.state = MOVE_TO_TARGET
        if success:
            self.set_new_dir_target()
            self.ore_data = None
            self.ores = []
        else:
            base = self.closest_base()
            dir = self.vec_to(base.pos())
            if dir.inf_magnitude() <= self.mp.I:
                self.target = self.closest_base().pos()
            else:
                self.target = self.world.torus(self.pos() + (dir.inf_normalize() * self.mp.I).round())

    def prepare_ore_data(self):
        ttl = 10
        self.ore_data = (self.ores, ttl, [self.idx])

    def step(self):
        super().before_step()
        self.color = Colors.GREEN

        if self.energy_low() or self.base_full:
            self.reactive_move_towards(self.closest_base().pos())
        elif self.broker.step():
            self.color = Colors.WHITE
            pass  # broker is active
        elif self.state == ATTEMPT_DELEGATION:
            self.broker.attempt_ore_data_delegation(self.ore_data, self.handle_broker_status)
        elif self.state == MOVE_TO_TARGET:
            if self.reached_target():
                if self.at_base():
                    self.dir = Vec2D.random_dir().inf_normalize()
                if self.ore_data:
                    self.state = ATTEMPT_DELEGATION
                else:
                    self.state = SCAN
            else:
                self.reactive_move_towards(self.target)

        elif self.state == SCAN:
            self.color = Colors.MAGENTA
            agents = self.box_scan(self.mp.P // 2)
            self.consume_energy(self.mp.P)
            ores = [a for a in agents if ORE in a.group_ids]
            explorers = [a for a in agents if EXPLORER in a.group_ids]
            transporters = [a for a in agents if TRANSPORTER in a.group_ids]
            robots = explorers + transporters

            ores = [(o.idx, o.pos()) for o in ores]
            ores = [o for o in ores if not o in self.ores]
            already_found_ores = bool(self.ores)
            self.ores += ores
            self.ores = self.ores[:self.mp.S]
            if len(self.ores) >= self.mp.S or already_found_ores and self.counter > 10:
                self.prepare_ore_data()
                self.state = ATTEMPT_DELEGATION
            elif robots:
                rel_r_pos = [self.vec_to(r.pos()) for r in robots]
                cog_dir = sum(rel_r_pos, Vec2D())
                cog = self.pos() + cog_dir
                cog_dir = cog_dir.inf_normalize() if not cog_dir.is_zero_vec() else Vec2D.random_dir().inf_normalize()
                self.target = self.world.torus((cog - cog_dir * self.mp.P).round())
                self.dir = -cog_dir
                self.state = MOVE_TO_TARGET
            elif ores:
                self.counter = 0
                rel_ore_pos = [self.vec_to(o[1]) for o in ores]
                cog_dir = sum(rel_ore_pos, Vec2D())
                cog_dir = cog_dir.inf_normalize() if not cog_dir.is_zero_vec() else Vec2D.random_dir().inf_normalize()
                self.target = self.world.torus(self.pos() + (cog_dir * self.mp.P).round())
                self.state = MOVE_TO_TARGET
            else:
                self.set_new_dir_target()
                self.state = MOVE_TO_TARGET
        self.broker.nearby_idle_transporters = 0
        super().after_step()

    def receive_event(self, event_type, data):
        self.broker.receive_event(event_type, data)
        if event_type == ORE_POSITIONS:
            ores, ttl, idxs = data
            idxs.append(self.idx)
            self.ore_data = ores, ttl - 1, idxs
        if event_type == BASE_FULL:
            self.base_full = True
