from pygridmas import World, Agent, Vec2D, Colors, Visualizer
import random
import math

size = 300
world = World(w=size, h=size, torus_enabled=True)

class Prey(Agent):
    color = Colors.YELLOW
    start_target: Vec2D = None
    reached_target = False
    counter = 0
    group_ids = {0}

    def initialize(self):
        self.start_target = Vec2D(
        random.randint(1,size-1),
        random.randint(1,size-1)
        )

    def step(self):
        self.counter = (self.counter + 1) % 3
        if self.counter != 0:
            return

        if not self.reached_target:
            self.move_towards(self.start_target)
            self.reached_target = self.pos() == self.start_target
        else:
            self.start_target = Vec2D(
            random.randint(1,size-1),
            random.randint(1,size-1)
            )
            self.reached_target = self.pos() == self.start_target

class Predator(Agent):
    color = Colors.RED
    start_target: Vec2D = None
    reached_target = False
    group_ids = {1}

    def initialize(self):
        self.start_target = Vec2D(
        random.randint(1,size-1),
        random.randint(1,size-1)
        )
        self.predatorState = "Move"


    def step(self):

        if self.predatorState == "Move":
            near_agents = self.box_scan(10, group_id=0)

            if len(near_agents) > 0:
                for prey in near_agents:
                    self.nearestPrey = prey
                    continue

                self.start_target = Agent.pos
                self.predatorState = "Stalk"
            else:
                if not self.reached_target:
                    self.move_towards(self.start_target)
                    self.reached_target = self.pos() == self.start_target
                else:
                    self.start_target = Vec2D(
                    random.randint(1,size-1),
                    random.randint(1,size-1)
                    )
                    self.reached_target = self.pos() == self.start_target

        elif self.predatorState == "Stalk":
            self.start_target = self.nearestPrey.pos()
            self.reached_target = self.pos() == self.start_target
            if self.reached_target:
                self.predatorState = "Attack"
            else:
                self.move_towards(self.start_target)

        elif self.predatorState == "Attack":
            world.remove_agent(idx=self.nearestPrey.idx)
            self.nearestPrey = None
            self.predatorState = "Move"


# Add a number of Repulsers to the world
for i in range(50):
    world.add_agent(Prey())
    if i % 10 == 0:
        world.add_agent(Predator())

# Visualize the world. The visualizer will call world.step(),
# trying to maintain a certain target speed (steps per second)
vis = Visualizer(world, scale=2, target_speed=40)
vis.start()
