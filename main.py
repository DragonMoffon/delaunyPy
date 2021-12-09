from array import array

import arcade
import arcade.gl as gl

from triangulation import Triangulation
from point import *


class Window(arcade.Window):

    def __init__(self):
        super().__init__(800, 800,  title="triangulation")
        points = create_grid_points(16, 16)
        self.triangles = Triangulation(points)

        self.program = self.ctx.load_program(vertex_shader="shaders/first_test.vert",
                                             fragment_shader="shaders/first_test.frag")
        self.data = self.ctx.buffer(data=array('f', list(self.triangles.point_data())))
        self.indices = self.ctx.buffer(data=array('i', list(self.triangles.indices())))
        self.renderer = self.ctx.geometry([gl.BufferDescription(self.data, '2f', ['in_pos'])],
                                          index_buffer=self.indices, mode=self.ctx.LINES)

        self.current_triangle = 0

    def on_draw(self):
        arcade.start_render()
        self.renderer.render(self.program)

        for edge in self.triangles.triangles[self.current_triangle].edges:
            point_1 = self.triangles.points[edge.s]
            point_2 = self.triangles.points[edge.e]
            arcade.draw_line(point_1.x*80, point_1.y*80, point_2.x*80, point_2.y*80, arcade.color.WHITE, 4)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.E:
            self.current_triangle += 1
        elif symbol == arcade.key.Q:
            self.current_triangle -= 1
        elif symbol == arcade.key.R:
            points = create_grid_points(100, 100)
            self.triangles = Triangulation(points)
            data = array('f', list(self.triangles.point_data()))
            self.data.orphan(size=data.__sizeof__())
            self.data.write(data=data)
            data = array('i', list(self.triangles.indices()))
            self.indices.orphan(size=data.__sizeof__())
            self.indices.write(data=data)


def main():
    window = Window()
    window.run()


if __name__ == '__main__':
    main()
