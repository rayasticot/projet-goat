import pyglet
from pyglet.gl import *
from pyglet.window import key
from scene import Scene, MainGameScene
from keyinput import Input 


class Game(pyglet.window.Window):
    def __init__(self):
        self._SIZE_X = 640
        self._SIZE_Y = 360
        self._window_scale = 3
        self._inputo = Input()
        self._fps_display = pyglet.window.FPSDisplay(window=self)
        super().__init__(self._SIZE_X*self._window_scale, self._SIZE_Y*self._window_scale, caption="AAA", fullscreen=False)
        self.scene = MainGameScene(self._window_scale, self._SIZE_X, self._SIZE_Y, self._inputo)

    def on_draw(self):
        self.switch_to()
        self.clear()
        self.scene.draw()
        self._fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        match(symbol):
            case key.W:
                self._inputo.up = 1
            case key.S:
                self._inputo.dw = 1
            case key.D:
                self._inputo.rg = 1
            case key.A:
                self._inputo.le = 1
            case key.SPACE:
                self._inputo.hbrake = 1
            case key.F:
                self._inputo.getin = 1

    def on_key_release(self, symbol, modifiers):
        match(symbol):
            case key.W:
                self._inputo.up = 0
            case key.S:
                self._inputo.dw = 0
            case key.D:
                self._inputo.rg = 0
            case key.A:
                self._inputo.le = 0
            case key.SPACE:
                self._inputo.hbrake = 0
            case key.F:
                self._inputo.getin = 0

    def on_mouse_motion(self, x, y, dx, dy):
        self._inputo.mx = x
        self._inputo.my = y


if __name__ == "__main__":
    pyglet.image.Texture.default_min_filter = GL_NEAREST
    pyglet.image.Texture.default_mag_filter = GL_NEAREST
    window = Game()
    pyglet.app.run(1/200)
