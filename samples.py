from array import array
from time import time

from arcade import ArcadeContext, draw_point
import arcade.gl as gl

from triangulation import Triangulation
import maps
from point import *


class GridTriangulationExample:

    def __init__(self, ctx: ArcadeContext):
        self.triangles = Triangulation(create_grid_points(16, 16))
        self.ctx: ArcadeContext = ctx
        self.program = self.ctx.load_program(vertex_shader="shaders/first_test.vert",
                                             fragment_shader="shaders/first_test.frag")
        self.data = self.ctx.buffer(data=array('f', list(self.triangles.point_data())))
        self.indices = self.ctx.buffer(data=array('i', list(self.triangles.indices())))
        self.renderer = self.ctx.geometry([gl.BufferDescription(self.data, '2f', ['in_pos'])],
                                          index_buffer=self.indices, mode=self.ctx.LINES)

    def draw(self):
        self.renderer.render(self.program)


class BasicPlateExample:

    def __init__(self, ctx):
        self.ctx: ArcadeContext = ctx
        self.plate_map: maps.PlateMap = maps.create_plate_map(16, 16, 12, 0.4)
        self.program = self.ctx.load_program(vertex_shader="shaders/plate_test.vert",
                                             fragment_shader="shaders/plate_test.frag")
        data, indices = self.plate_map.get_buffer_data()
        self.data = self.ctx.buffer(data=data)
        self.indices = self.ctx.buffer(data=indices)

        self.renderer = self.ctx.geometry([gl.BufferDescription(self.data, '2f 1f', ['in_pos', 'plate'])],
                                          index_buffer=self.indices, mode=self.ctx.TRIANGLES)

    def draw(self):
        self.renderer.render(self.program)


class StepperPlateExample:

    def __init__(self, ctx):
        self.ctx: ArcadeContext = ctx
        self.stepper = maps.PlateMapStepperInfo(100, 100, 24, 0.55)
        self.last_step = time()

        self.program = self.ctx.load_program(vertex_shader="shaders/first_test.vert",
                                             fragment_shader="shaders/first_test.frag")
        self.data = self.ctx.buffer(data=array('f', list(self.stepper.point_map.triangulation.point_data())))
        self.indices = self.ctx.buffer(data=array('i', list(self.stepper.point_map.triangulation.indices())))
        self.renderer = self.ctx.geometry([gl.BufferDescription(self.data, '2f', ['in_pos'])],
                                          index_buffer=self.indices, mode=self.ctx.LINES)

    def draw(self):
        self.renderer.render(self.program)

        for plate in self.stepper.plate_data:
            color = 50 + int(plate.index/(self.stepper.plate_num-1)*125)
            for point in plate.points:
                pos = point.pos
                draw_point((pos.x + 0.5) * 1920, (pos.y + 0.5) * 1080, (125*plate.type, color, color), 15)

        for triangle, plate in self.stepper.triangles:
            color = 50 + int(plate/(self.stepper.plate_num-1)*125)
            pos_x = 0
            pos_y = 0
            for vertex in triangle.vertices:
                pos = self.stepper.point_map.triangulation.points[vertex]
                pos_x += pos.x
                pos_y += pos.y

            pos_x /= 3
            pos_y /= 3

            draw_point((pos_x + 0.5) * 1920, (pos_y + 0.5) * 1080,
                       (self.stepper.plate_data[plate].type*125, color, color), 9)

        if time() > self.last_step + 0.1:
            self.stepper.step()
            self.last_step = time()
