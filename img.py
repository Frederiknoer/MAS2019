import imageio
import numpy as np
from main import create_world
from masparams import MasParams

image_count = 300
cycles_per_image = 10


def to_img(world):
    w, h = world.w, world.h
    img = np.empty((h, w, 3), dtype=np.float)
    for y in range(h):
        for x in range(w):
            if world.m[y][x]:
                color = world.m[y][x][-1].color
            else:
                color = (0, 0, 0)
            img[y, x] = color
    return img


world = create_world(MasParams())
images = [to_img(world)]
for i in range(image_count):
    for j in range(cycles_per_image):
        world.step()
    images.append(to_img(world))

imageio.mimsave("my.gif", images, fps=30)
