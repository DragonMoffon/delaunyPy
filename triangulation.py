from typing import Tuple, List

from point import Point


class Edge:

    def __init__(self, s: int, e: int):
        self.s = s
        self.e = e

    def __eq__(self, other):
        return (self.s == other.s and self.e == other.e) or (self.s == other.e and self.e == other.s)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.s, self.e))

    def __repr__(self):
        return f"{self.s, self.e}"


def calc_circumcircle(vertices, points):
    point_1 = points[vertices[0]]
    point_2 = points[vertices[1]]
    point_3 = points[vertices[2]]

    if point_2.x == point_1.x:
        c_2 = (point_2.x ** 2 - point_3.x ** 2) + (point_2.y ** 2 - point_3.y ** 2)
        c_3 = (point_3.x ** 2 - point_1.x ** 2) + (point_3.y ** 2 - point_1.y ** 2)
        c_t = (c_2 * (point_1.x - point_3.x) / (point_3.x - point_2.x)) - c_3

        div = 2 * ((point_1.y - point_3.y) - ((point_3.y - point_2.y) / (point_3.x - point_2.x)) * (
                    point_1.x - point_3.x))
        center_y = c_t / div
        center_x = (c_2 + 2 * center_y * (point_3.y - point_2.y)) / (2 * (point_2.x - point_3.x))
    else:
        c_1 = (point_1.x ** 2 - point_2.x ** 2) + (point_1.y ** 2 - point_2.y ** 2)
        c_2 = (point_2.x ** 2 - point_3.x ** 2) + (point_2.y ** 2 - point_3.y ** 2)
        c_t = (c_1 * (point_3.x - point_2.x) / (point_2.x - point_1.x)) - c_2

        div = 2 * ((point_3.y - point_2.y) - ((point_2.y - point_1.y) / (point_2.x - point_1.x)) * (point_3.x - point_2.x))
        center_y = c_t / div
        center_x = (c_1 + 2 * center_y * (point_2.y - point_1.y)) / (2 * (point_1.x - point_2.x))

    center_radius = (center_x - point_1.x) ** 2 + (center_y - point_1.y) ** 2

    return center_x, center_y, center_radius


def calc_area(vertices, points):
    point_1 = points[vertices[0]]
    point_2 = points[vertices[1]]
    point_3 = points[vertices[2]]
    return 0.5*((point_2.x-point_1.x)(point_3.y-point_1.y) - (point_3.x-point_1.x)(point_2.y-point_1.y))


class Triangle:

    def __init__(self, vertices: Tuple[int, int, int], points):
        self.vertices = vertices
        self.area = calc_area(vertices, points)
        self.edges = (Edge(vertices[0], vertices[1]), Edge(vertices[1], vertices[2]), Edge(vertices[2], vertices[0]))
        self.circumcircle = calc_circumcircle(vertices, points)

    def __eq__(self, other):
        return self.vertices == other.vertices

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.vertices)

    def edge_data(self):
        for edge in self.edges:
            yield edge.s
            yield edge.e

    def vertex_data(self):
        for vertex in self.vertices:
            yield vertex

    def valid(self):
        return not any((self.edges[0].s < 0, self.edges[0].e < 0,
                        self.edges[1].s < 0, self.edges[1].e < 0,
                        self.edges[2].s < 0, self.edges[2].e < 0))


def in_circumcircle(triangle: Triangle, target: Point):
    center_x, center_y, center_radius = triangle.circumcircle

    center_dist = (center_x - target.x)**2 + (center_y - target.y)**2

    if center_dist <= center_radius:
        return True
    return False


class Triangulation:

    def __init__(self, points: List[Point]):
        self.points = points
        self.triangles: List[Triangle] = []

        self.calculate_triangulation()

    def calculate_triangulation(self):
        self.points.extend((Point(-2.5, -2.5), Point(0, 2.5), Point(2.5, 0)))
        calculation_triangles = [Triangle((-3, -2, -1), self.points)]
        valid_triangles = []
        for index, point in enumerate(self.points[:-3]):
            check_edges = []
            for triangle in calculation_triangles.copy():
                if triangle.circumcircle[2] < (point.x - triangle.circumcircle[0])**2:
                    calculation_triangles.remove(triangle)
                    if not (triangle.vertices[0] < 0 or triangle.vertices[1] < 0 or triangle.vertices[2] < 0):
                        valid_triangles.append(triangle)
                elif in_circumcircle(triangle, point):
                    calculation_triangles.remove(triangle)
                    check_edges.extend(triangle.edges)

            calculation_triangles.extend([Triangle((index, edge.s, edge.e), self.points)
                                          for edge in check_edges if check_edges.count(edge) <= 1])

        valid_triangles.extend((triangle for triangle in calculation_triangles if
                                not (triangle.vertices[0] < 0 or triangle.vertices[1] < 0 or triangle.vertices[2] < 0)))
        self.triangles = valid_triangles

    def point_data(self):
        for point in self.points:
            yield from point.data()

    def indices(self):
        for tri in self.triangles:
            yield from tri.edge_data()
