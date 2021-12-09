from typing import List
from time import time
import random

import perlin


class Point:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def data(self):
        yield self.x
        yield self.y

    def __repr__(self):
        return f"x: {self.x}, y: {self.y}"


def insert_sort_points(values: List[Point]):
    result = []
    for point in values:
        for index, compare_point in enumerate(result):
            if point.x < compare_point.x:
                result.insert(index, point)
                break
        else:
            result.append(point)

    return result


def create_random_points(num_points: int, seed: float = None) -> List[Point]:
    if seed is None:
        seed = time()
    random.seed(seed)
    points: List[Point] = []

    for _ in range(num_points):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        point = Point(x, y)
        points.append(point)

    points.sort(key=lambda p: p.x)
    return points


def create_perlin1D_points(num_points: int, seed: float = None) -> List[Point]:
    if seed is None:
        seed = time()
    random.seed(seed)
    x_seed, y_seed = random.random(), random.random()
    points: List[Point] = []

    for _ in range(num_points):
        x = perlin.perlin1D(random.random()*8, seed=x_seed)
        random.seed(x)
        y = perlin.perlin1D(random.random()*8, seed=y_seed)
        random.seed(y)
        point = Point(x, y)
        points.append(point)

    points.sort(key=lambda p: p.x)
    return points


def create_perlin1D_points_squared(num_points: int, seed: float = None) -> List[Point]:
    if seed is None:
        seed = time()
    random.seed(seed)
    x_seed, y_seed = random.random(), random.random()
    points: List[Point] = []
    max_coord = 0

    for _ in range(num_points):
        x = perlin.perlin1D(random.random() * 40, seed=x_seed)
        random.seed(x)
        y = perlin.perlin1D(random.random() * 40, seed=y_seed)
        random.seed(y)
        point = Point(x, y)

        if abs(point.x) > max_coord:
            max_coord = abs(point.x)
        elif abs(point.y) > max_coord:
            max_coord = abs(point.y)

        points.append(point)

    sorted_points = insert_sort_points(points)

    return sorted_points


def create_grid_points(grid_width: int, grid_height: int, seed: float = None) -> List[Point]:
    if seed is None:
        seed = time()
    random.seed(seed)
    points = []
    for x in range(int(-grid_width/2), int(grid_width/2)):
        current_points = []
        for y in range(int(-grid_height/2), int(grid_height/2)):
            if y == int(-grid_height/2):
                point_y = y
            elif y == int(grid_height/2)-1:
                point_y = y+1
            else:
                point_y = y + random.random()

            if x == int(-grid_width/2):
                point_x = x
            elif x == int(grid_width/2)-1:
                point_x = x+1
            else:
                point_x = x + random.random()

            point = Point(point_x/grid_width, point_y/grid_height)
            for index, compare_point in enumerate(current_points):
                if point.x < compare_point.x:
                    current_points.insert(index, point)
                    break
            else:
                current_points.append(point)
        points.extend(current_points)

    return points
