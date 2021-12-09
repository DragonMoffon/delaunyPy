import arcade

import samples


class Window(arcade.Window):

    def __init__(self):
        super().__init__(1920, 1080,  title="triangulation")
        self.sample = samples.StepperPlateExample(self.ctx)

    def on_draw(self):
        arcade.start_render()
        self.sample.draw()


def main():
    window = Window()
    window.run()


if __name__ == '__main__':
    main()
