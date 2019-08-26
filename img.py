import imageio
import numpy as np


def to_img(world, scale=1):
    w, h = world.w, world.h
    img = np.empty((h, w, 3), dtype=np.float)
    for y in range(h):
        yy = h - y - 1
        for x in range(w):
            if world.m[y][x]:
                color = world.m[y][x][-1].color
            else:
                color = (0, 0, 0)
            img[yy, x] = color
    return np.kron(img, np.ones((scale, scale, 1)))


def create_gif(filename, world, frames, fps=1, scale=3, include_blanc=True):
    images = []
    for i in frames:
        while world.time < i:
            world.step()
        images.append(to_img(world, scale))
    if include_blanc:
        images.append(np.zeros_like(images[0]))
    imageio.mimsave("{}.gif".format(filename), images, fps=fps)
