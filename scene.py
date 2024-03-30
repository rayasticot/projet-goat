import pyglet
from pyglet.gl import *
from abc import ABC, abstractmethod
from world_gen import WorldGen
from player import Player


class Scene(ABC):
    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def update(self, dt):
        pass


class MainGameScene(Scene):
    def __init__(self, scale, size_x, size_y, inputo):
        self._window_scale = scale
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self._inputo = inputo
        self.worldgen = WorldGen(self._window_scale, self._SIZE_X, self._SIZE_Y)
        self.sprite_batch = pyglet.graphics.Batch()
        self.cam_x = 0
        self.cam_y = 0
        self.player = Player(self.sprite_batch, 0, 0, self._SIZE_X, self._SIZE_Y, self._window_scale)
        self.overlay = pyglet.image.Texture.create(self._SIZE_X, self._SIZE_Y, internalformat=pyglet.gl.GL_RGBA8)
        self.fbo = pyglet.image.Framebuffer()
        self.fbo.attach_texture(self.overlay)
        pyglet.clock.schedule_interval(self.update, 1/60)

    def draw(self):
        #self.backsprite.draw()
        self.fbo.bind()
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        self.worldgen.batch.draw()
        self.sprite_batch.draw()
        self.fbo.unbind()
        glEnable(GL_BLEND)
        self.overlay.blit(0, 0, width=self._SIZE_X*self._window_scale, height=self._SIZE_Y*self._window_scale)

    def update(self, dt):
        self.player.update(self._inputo, dt)
        self.cam_x = self.player.cam_x
        self.cam_y = self.player.cam_y
        self.worldgen.group.update(self.cam_x, self.cam_y)

    def __del__(self):
        pyglet.clock.unschedule(self.update)
