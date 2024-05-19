import pyglet
from pyglet.gl import *
import numpy as np
from abc import ABC, abstractmethod
from world_gen import WorldGen
from tileobject import TilingMap
from player import Player, BulletManager
from inventory import Inventory, Weapon, WEAPON_MODELS
from hud import Hud
from npc import NpcManager


class Scene(ABC):
    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def update(self, dt):
        pass


class MainGameScene(Scene):
    def __init__(self, scale, size_x, size_y, inputo, window):
        self._window_scale = scale
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self._inputo = inputo
        self.worldgen = WorldGen(self._window_scale, self._SIZE_X, self._SIZE_Y)
        self.sprite_batch = pyglet.graphics.Batch()
        self.cam_x = 0
        self.cam_y = 0
        self.inventory = Inventory(self._SIZE_X, self._SIZE_Y)
        self.hud = Hud(self._SIZE_X, self._SIZE_Y, self._window_scale, self.sprite_batch)
        self.tilingmap = TilingMap(self.cam_x, self.cam_y, self._SIZE_X, self._SIZE_Y, self.sprite_batch)
        self.player = Player(self.sprite_batch, 0, 0, self._SIZE_X, self._SIZE_Y, self._window_scale, self.inventory)
        self.bullet_manager = BulletManager()
        self.overlay = pyglet.image.Texture.create(self._SIZE_X, self._SIZE_Y, internalformat=pyglet.gl.GL_RGBA8)
        self.fbo = pyglet.image.Framebuffer()
        self.fbo.attach_texture(self.overlay)

        self.npc_manager = NpcManager(self.sprite_batch)

        self.time_of_day = 120

        pyglet.clock.schedule_interval(self.update, 1/60)

        weapon = Weapon(WEAPON_MODELS[0], 0, 0, 0, 0, 0)
        print(self.inventory.pickup(weapon))

        #self.inventory.pickup_item()

    def draw(self):
        #self.backsprite.draw()
        self.fbo.bind()
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_BLEND)
        self.worldgen.batch.draw()
        self.sprite_batch.draw()
        if self.inventory.active:
            self.inventory.batch.draw()
        self.fbo.unbind()
        glEnable(GL_BLEND)
        self.overlay.blit(0, 0, width=self._SIZE_X*self._window_scale, height=self._SIZE_Y*self._window_scale)

    def update(self, dt):
        self.time_of_day += dt*60
        self.time_of_day %= 1440
        print(self.time_of_day//60)
        print(self.time_of_day%60)
        bullet = self.player.update(self._inputo, dt)
        if bullet != None:
            self.bullet_manager.add_bullet(bullet, True)
        self.npc_manager.update(\
            self.bullet_manager, self.player.playerwalker.pos_x, self.player.playerwalker.pos_y,\
            self.cam_x, self.cam_y, self.tilingmap.occupation_grid, self.bullet_manager.bullet_list_player,\
            self.bullet_manager.bullet_list_ennemy, dt\
        )
        self.bullet_manager.update(dt, self.cam_x, self.cam_y)
        self.cam_x = self.player.cam_x
        self.cam_y = self.player.cam_y
        self.hud.update(self.player.playercar.x, self.player.playercar.y, self.cam_x, self.cam_y)
        self.worldgen.group.update(self.time_of_day, self.cam_x, self.cam_y, self.player.playercar.x, self.player.playercar.y, -np.radians(self.player.playercar.sprite.rotation-90))
        self.tilingmap.update(self.cam_x, self.cam_y)
        if self._inputo.openinv:
            self._inputo.openinv = 0
            self.inventory.active = not self.inventory.active
        if self.inventory.active:
            self.inventory.update(self._inputo, self._window_scale)

    def __del__(self):
        pyglet.clock.unschedule(self.update)
