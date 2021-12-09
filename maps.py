import random
from time import time
from typing import List, Dict, Set, Tuple

import point
import triangulation
import perlin

LAND, SEA = 0, 1


class MapPoint:

    def __init__(self, pos: point.Point, index: int):
        self.pos = pos
        self.index = index
        self.child_triangles: Set[int] = set()
        self.neighbors: Set[int] = set()


class PointMap:

    def __init__(self, base_triangulation: triangulation.Triangulation):
        self.triangulation: triangulation.Triangulation = base_triangulation
        self.points: Tuple[MapPoint] = tuple()

        self.generate_map_points()

    def generate_map_points(self):
        self.points = tuple(MapPoint(p, index) for index, p in enumerate(self.triangulation.points))
        for index, triangle in enumerate(self.triangulation.triangles):
            for vertex in triangle.vertices:
                self.points[vertex].child_triangles.add(index)
                others = list(triangle.vertices[:])
                others.remove(vertex)
                self.points[vertex].neighbors.update(others)


class Plate:

    def __init__(self, points: Tuple[MapPoint], triangles: Tuple[triangulation.Triangle], area: float,
                 cont_type: int = LAND):
        self.points: Tuple[MapPoint] = points
        self.triangles: Tuple[triangulation.Triangle] = triangles
        self.area = 0
        self.type = cont_type

    def pick_triangle_by_area(self, value: float):
        scaled_value = value*self.area
        for triangle in self.triangles:
            scaled_value -= triangle.area
            if scaled_value <= 0:
                return triangle
        raise IndexError(f"{value} is greater than 1.0 which is invalid.")


class PlateGenData:

    def __init__(self, seed_point, plate_type: int):
        self.seed_point = seed_point
        self.points: Set[MapPoint] = {seed_point}

        self.type = plate_type

        self.triangles: Set[triangulation.Triangle] = set()
        self.area = 0

        self.shell_points: Set[MapPoint] = {seed_point}
        self.cost = 0

    def add(self, new_point):
        self.points.add(new_point)
        self.shell_points.add(new_point)

    def add_triangle(self, new_triangle):
        if new_triangle not in self.triangles:
            self.area += new_triangle.area
            self.triangles.add(new_triangle)


class PlateMap:

    def __init__(self, point_map, plates):
        self.map: PointMap = point_map
        self.plate: List[Plate] = plates

    def pick_continent_by_area(self, value):
        for plate in self.plate:
            value -= plate.area
            if value <= 0:
                return plate
        raise IndexError(f"{value} is greater than 1.0 which is invalid.")


def create_plate_map(map_width: int, map_height: int, plate_num, plate_dist: float = None, seed=None):
    if seed is None:
        seed = time()

    point_map = PointMap(triangulation.Triangulation(point.create_grid_points(map_width, map_height, seed**2)))
    available_points = set(point_map.points)
    available_triangles = set(point_map.triangulation.triangles)

    def add_triangle(current_plate: PlateGenData, triangle):
        if triangle in available_triangles:
            current_plate.add_triangle(triangle)
            available_triangles.remove(triangle)

    random.seed(seed)

    if plate_dist is None:
        plate_dist = random.uniform(0.3, 0.55)

    plate_data = []
    for plate in range(plate_num):
        type_check, plate_type = random.random(), SEA
        if type_check <= plate_dist:
            plate_type = LAND
        seed_point = random.choice(point_map.points)
        plate_data.append(PlateGenData(seed_point, plate_type))
        available_points.remove(seed_point)

    while len(available_points):
        for plate in plate_data:
            plate.cost += 0.707 + 0.707 * plate.type
            if plate.cost > 0:
                for map_point in plate.shell_points.copy():
                    for tri in map_point.child_triangles:
                        add_triangle(plate, tri)
                    plate.shell_points.remove(map_point)
                    for neighbor in map_point.neighbors:
                        neighbor_point = point_map.points[neighbor]
                        if neighbor_point not in plate.points and neighbor_point in available_points:
                            cost = ((map_point.pos.x - neighbor_point.pos.x)**2 +
                                    (map_point.pos.y - neighbor_point.pos.y)**2)
                            plate.cost -= cost
                            plate.shell_points.add(neighbor_point)
                            plate.points.add(neighbor_point)
                            available_points.remove(neighbor_point)

    plates = []
    for plate in plate_data:
        plates.append(Plate(tuple(plate.points), tuple(plate.triangles), plate.area, plate.type))

    return PlateMap(point_map, tuple(plates))
