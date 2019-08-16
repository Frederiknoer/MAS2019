from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import random
import math

size = 300
world = World(w=size, h=size, torus_enabled=True)
worldCenter = (Vec2D(math.floor(size/2), math.floor(size/2)))
NrOfOres = 50
NrOfExplores = 10
NrOfTransporters = 10

BASE = "BASE"
ORE = "ORE"
EXPLORER = "EXPLORER"
TRANSPORTER = "TRANSPORTER"


class Ore(Agent):
    color = Colors.YELLOW
    group_ids = {ORE}

class Base(Agent):
    color = Colors.BLUE
    group_ids = {BASE}

class Explorer(Agent):
    color = Colors.GREEN
    group_ids = {EXPLORER}
    start_target: Vec2D = None
    reached_target = False
    moveType = ""
    explorerState = "MOVE_RANDOM"


    def initialize(self):
        self.start_target = Vec2D(
        random.randint(self.pos().x - 20, self.pos().x + 20),
        random.randint(self.pos().y - 20, self.pos().y + 20)
        )

    def step(self):
        #print("Agent ", self.idx, " is in state: ", self.explorerState)
        if self.explorerState == "MOVE_RANDOM":
            if not self.reached_target:
                self.move_towards(self.start_target)
                self.reached_target = self.pos() == self.start_target
            else:
                self.explorerState = "SCAN"

        elif self.explorerState == "MOVE_REPULSE":
            if not self.reached_target:
                self.move_towards(self.repulse_target)
                self.reached_target = self.pos() == self.repulse_target
            else:
                self.explorerState = "SCAN"

        elif self.explorerState == "SCAN":
            agents = self.box_scan(10)

            if len(agents) > 0:
                self.ores = [agent for agent in agents if ORE in agent.group_ids]
                self.explores = [agent for agent in agents if EXPLORER in agent.group_ids]

                if len(self.explores) > 0:
                    other_agent = random.choice(self.explores)
                    dir = self.world.shortest_way(other_agent.pos(), self.pos())
                    if dir.magnitude() == 0:
                        self.start_target = Vec2D(
                        random.randint(self.pos().x - 20, self.pos().x + 20),
                        random.randint(self.pos().y - 20, self.pos().y + 20)
                        )
                        self.reached_target = self.pos() == self.start_target
                        self.moveType = "MOVE_RANDOM"
                    else:
                        normdir = dir/dir.magnitude()
                        self.repulse_target = other_agent.pos() + (normdir * random.randint(18,22)).round()
                        self.reached_target = self.pos() == self.repulse_target
                        self.moveType = "MOVE_REPULSE"
                else:
                    self.start_target = Vec2D(
                    random.randint(self.pos().x - 20, self.pos().x + 20),
                    random.randint(self.pos().y - 20, self.pos().y + 20)
                    )
                    self.reached_target = self.pos() == self.start_target
                    self.moveType = "MOVE_RANDOM"

                if len(self.ores) > 0:
                    self.explorerState = "EMIT_EVENT_ORE_POS"
                else:
                    self.explorerState = self.moveType
            else:
                self.start_target = Vec2D(
                random.randint(self.pos().x - 20, self.pos().x + 20),
                random.randint(self.pos().y - 20, self.pos().y + 20)
                )
                self.reached_target = self.pos() == self.start_target
                self.explorerState = "MOVE_RANDOM"

        elif self.explorerState == "EMIT_EVENT_ORE_POS":
            self.emit_event(rng=25, data=self.ores, group_id=TRANSPORTER)
            self.explorerState = self.moveType


class Transporter(Agent):
    color = Colors.RED
    group_ids = {TRANSPORTER}
    start_target: Vec2D = None
    reached_target = False



# Add a number of Repulsers to the world
for i in range(NrOfOres):
    world.add_agent(Ore())

for i in range(NrOfExplores):
    world.add_agent(Explorer(), pos=worldCenter)

for i in range(NrOfTransporters):
    world.add_agent(Transporter(), pos=worldCenter)

world.add_agent(Base(), pos=worldCenter)

# Visualize the world. The visualizer will call world.step(),
# trying to maintain a certain target speed (steps per second)
vis = Visualizer(world, scale=2, target_speed=40)
vis.start()
