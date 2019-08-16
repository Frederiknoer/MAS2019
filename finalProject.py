from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import random
import math

size = 300
world = World(w=size, h=size, torus_enabled=True)
worldCenter = (Vec2D(math.floor(size/2), math.floor(size/2)))
NrOfOres = 50
NrOfExplores = 10
NrOfTransporters = 10

class Ore(Agent):
    color = Colors.YELLOW
    group_ids = {1}

class Base(Agent):
    color = Colors.BLUE

class Explorer(Agent):
    color = Colors.GREEN
    start_target: Vec2D = None
    reached_target = False

    def initialize(self):
        self.start_target = Vec2D(
        random.randint(1,size-1),
        random.randint(1,size-1)
        )

    def step(self):
#        ores = self.box_scan(5, group_id=1)

#        if len(ores) > 0:
#            self.nearest_ore = ores[0]
#            self.start_target = nearest_ore.pos()

        if not self.reached_target:
            self.move_towards(self.start_target)
            self.reached_target = self.pos() == self.start_target
        else:
            self.start_target = Vec2D(
            random.randint(1,size-1),
            random.randint(1,size-1)
            )
            self.reached_target = self.pos() == self.start_target


class Transporter(Agent):
    color = Colors.RED
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
