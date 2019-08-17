"""traveling sales man"""
from typing import List
from pygridmas import Vec2D
import random


def calc_travel_inf_dist(l: List[Vec2D]):
    dist = 0
    for i in range(1, len(l)):
        dist += (l[i] - l[i - 1]).inf_magnitude()
    return dist


def calc_local_inf_dist(l: List[Vec2D], i):
    if i == 0:
        return (l[0] - l[1]).inf_magnitude()
    elif i == len(l) - 1:
        return (l[-1] - l[-2]).inf_magnitude()
    else:
        return (l[i - 1] - l[i]).inf_magnitude() + (l[i + 1] - l[i]).inf_magnitude()


def iterative_inf_norm_tsm(orig_l: List[Vec2D], n=20):
    idx = list(range(len(orig_l)))
    if len(orig_l) <= 2:
        return idx
    l = list(orig_l)
    for _ in range(n):
        i, j = random.sample(idx, 2)
        old_dist = calc_local_inf_dist(l, i) + calc_local_inf_dist(l, j)
        l[i], l[j] = l[j], l[i]
        new_dist = calc_local_inf_dist(l, i) + calc_local_inf_dist(l, j)
        if old_dist < new_dist:
            l[i], l[j] = l[j], l[i]
        else:
            idx[i], idx[j] = idx[j], idx[i]
    return idx


def main():
    l = [Vec2D(0, 0), Vec2D(10, 10), Vec2D(0, 0), Vec2D(10, 10)]
    tsm_idx = iterative_inf_norm_tsm(l)
    ll = [l[i] for i in tsm_idx]

    old_dist = calc_travel_inf_dist(l)
    new_dist = calc_travel_inf_dist(ll)
    assert old_dist == 30
    assert new_dist == 10

    print('test succeeded')


if __name__ == '__main__':
    main()
