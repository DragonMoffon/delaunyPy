import random
from time import time
from math import floor

GRADIENT_CHOICES = ((0.70710678118, 0.70710678118), (0.70710678118, -0.70710678118), (1, 0), (0, 1),
                    (-0.70710678118, 0.70710678118), (-0.70710678118, -0.70710678118), (-1, 0), (0, -1))


def smoother_step(shift):
    return shift**3 * (shift * (6 * shift - 15) + 10)


def mix(s, e, f):
    return s * (1 - f) + f * e


def perlin1D(x: float, octaves=1, factor=2, seed=None):
    if seed is None:
        seed = time()
    random.seed(seed)
    octave_seeds = [random.random() for _ in range(octaves)]
    result = 0

    for octave in range(octaves):
        scaled_x = x*(factor**octave)
        base = int(scaled_x)
        shift = scaled_x - base
        random.seed(octave_seeds[octave] * 2**base/seed)
        grad_base = random.uniform(-1, 1) * shift
        value_base = random.uniform(-0.5, 0.5)
        random.seed(octave_seeds[octave] * 2**(1+base)/seed)
        grad_step = random.uniform(-1, 1) * (shift-1)
        value_step = random.uniform(-0.5, 0.5)
        f = smoother_step(shift)
        value = mix(grad_base, grad_step, f) + mix(value_base, value_step, f)
        result += value / (2**octave)

    return result


def perlin2D(x: float, y: float, octaves, factor, seed=None):
    if seed is None:
        seed = time()
    random.seed(seed)
    gradients_shuffled = list(GRADIENT_CHOICES)
    random.shuffle(gradients_shuffled)
    octave_seeds = [(random.random(), random.random()) for _ in range(octaves)]
    result = 0

    for octave in range(octaves):
        scaled_x, scaled_y = x*(factor**octave), y*(factor**octave)
        bases = (int(scaled_x), int(scaled_y))
        shifts = (scaled_x-bases[0], scaled_y-bases[1])
        f_x, f_y = smoother_step(shifts[0]), smoother_step(shifts[1])


def get_1D_distribution(detail=25, seed=time()):
    return list(perlin1D(2*i/detail, octaves=4, seed=seed) for i in range(detail))


