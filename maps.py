import random
from time import time
from typing import List, Dict, Set, Tuple
from array import array

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

    def __init__(self, points: Tuple[MapPoint], cont_type: int = LAND):
        self.points: Tuple[MapPoint] = points
        self.triangles: Tuple[triangulation.Triangle] = tuple()
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

    def __init__(self, seed_point, plate_type: int, plate_index):
        self.index = plate_index

        self.seed_point = seed_point
        self.points: Set[MapPoint] = {seed_point}
        self.point_indices: Set[int] = {seed_point.index}

        self.type = plate_type

        self.shell_points: Set[MapPoint] = {seed_point}
        self.cost = 0

    def add(self, new_point):
        self.points.add(new_point)
        self.shell_points.add(new_point)


class PlateMap:

    def __init__(self, point_map, plates):
        self.map: PointMap = point_map
        self.plates: List[Plate] = plates

    def pick_continent_by_area(self, value):
        value *= 4  # 2 squared as the map goes from -1 to 1 on the x and y axis so this is always the area.
        for plate in self.plates:
            value -= plate.area
            if value <= 0:
                return plate
        raise IndexError(f"{value} is greater than 1.0 which is invalid.")

    def get_buffer_data(self):
        num_plates = len(self.plates)-1
        visited_points = set()
        new_points = []
        index_convert: Dict[Tuple[int, int], int] = {}
        for index, plate in enumerate(self.plates):
            normal_index = index/num_plates
            for triangle in plate.triangles:
                for vertex in triangle.vertices:
                    vertex_pos = self.map.triangulation.points[vertex]
                    new_point = (vertex_pos.x, vertex_pos.y, normal_index)
                    if new_point not in visited_points:
                        visited_points.add(new_point)
                        index_convert[(vertex, index)] = len(new_points)
                        new_points.append(new_point)
        vertices = []
        for point_data in new_points:
            vertices.extend(point_data)
        indices = []
        for index, plate in enumerate(self.plates):
            for triangle in plate.triangles:
                indices.extend((index_convert[vertex, index] for vertex in triangle.vertices))

        return (array('f', vertices),
                array('i', indices))


def create_plate_map(map_width: int, map_height: int, plate_num, plate_dist: float = None, seed=None):
    if seed is None:
        seed = time()

    point_map = PointMap(triangulation.Triangulation(point.create_grid_points(map_width, map_height, seed**2)))
    available_points = set(point_map.points)

    random.seed(seed)

    if plate_dist is None:
        plate_dist = random.uniform(0.4, 0.65)

    plate_data = []
    for plate in range(plate_num):
        type_check, plate_type = random.random(), SEA
        if type_check <= plate_dist:
            plate_type = LAND
        seed_point = random.choice(tuple(available_points))
        plate_data.append(PlateGenData(seed_point, plate_type, plate))
        available_points.remove(seed_point)

    print("start: ", time() % 10000)

    while len(available_points)-3 > 0:
        print(len(available_points)-3)
        for plate in plate_data:
            plate.cost += 0.001 + 0.001 * plate.type
            if plate.cost > 0:
                for map_point in plate.shell_points.copy():
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
    print("done: ", time() % 10000)

    plates = []
    for plate in plate_data:
        plates.append(Plate(tuple(plate.points), plate.type))

    return PlateMap(point_map, tuple(plates))


class PlateMapStepperInfo:

    def __init__(self, map_width: int, map_height: int, plate_num: int, plate_dist: float):
        self.plate_num = plate_num
        self.plate_dist = plate_dist

        self.point_map = PointMap(triangulation.Triangulation(point.create_grid_points(map_width, map_height)))
        self.available_points = set(self.point_map.points)
        self.available_triangles = set(self.point_map.triangulation.triangles)

        if plate_dist is None:
            plate_dist = random.uniform(0.3, 0.55)

        self.plate_data = []
        for plate in range(plate_num):
            type_check, plate_type = random.random(), SEA
            if type_check <= plate_dist:
                plate_type = LAND
            seed_point = random.choice(tuple(self.available_points))
            self.plate_data.append(PlateGenData(seed_point, plate_type, plate))
            self.available_points.remove(seed_point)

        self.triangles = []

    def step(self):
        if len(self.available_points) - 3 > 0:
            for plate in self.plate_data:
                print(plate, plate.type, plate.cost)
                plate.cost += 0.001 + 0.001 * plate.type
                if plate.cost > 0:
                    print("extending")
                    cost_mod = 1
                    if len(plate.shell_points) > 0:
                        cost_mod = (6) / (len(plate.shell_points)**2)
                    for map_point in plate.shell_points.copy():
                        plate.shell_points.remove(map_point)
                        for neighbor in map_point.neighbors:
                            neighbor_point = self.point_map.points[neighbor]
                            if neighbor_point not in plate.points and neighbor_point in self.available_points:
                                cost = ((map_point.pos.x - neighbor_point.pos.x) ** 2 +
                                        (map_point.pos.y - neighbor_point.pos.y) ** 2)
                                plate.cost -= cost * cost_mod
                                plate.shell_points.add(neighbor_point)
                                plate.points.add(neighbor_point)
                                plate.point_indices.add(neighbor)
                                self.available_points.remove(neighbor_point)
        elif not len(self.triangles):
            for tri in self.point_map.triangulation.triangles:
                for plate in self.plate_data:
                    check = (vertex in plate.point_indices for vertex in tri.vertices)
                    if any(check):
                        self.triangles.append((tri, plate.index))



