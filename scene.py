import pyglet
from pyglet.gl import *
import numpy as np
from abc import ABC, abstractmethod
from world_gen import WorldGen
from tileobject import TilingMap
from player import Player, BulletManager
from inventory import Inventory, Weapon, WEAPON_MODELS, GroundItemManager
from hud import Hud
from npc import NpcManager


class Scene(ABC):
    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def update(self, dt):
        pass

class TitleScreen(Scene):
    def __init__(self, scale, size_x, size_y, inputo, window):
        self._window = window
        self._window_scale = scale
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self._inputo = inputo
        self.overlay = pyglet.image.Texture.create(self._SIZE_X, self._SIZE_Y, internalformat=pyglet.gl.GL_RGBA8)
        self.fbo = pyglet.image.Framebuffer()
        self.fbo.attach_texture(self.overlay)
        self.batch = pyglet.graphics.Batch()
        self.bg = pyglet.sprite.Sprite(img=pyglet.image.load('img/titlescreen/titlescreen.png'), batch=self.batch)
        self.logo_image = pyglet.image.load('img/titlescreen/logo.png')
        self.logo_image.anchor_x = self.logo_image.width//2
        self.logo_image.anchor_y = self.logo_image.height//2
        self.logo = pyglet.sprite.Sprite(img=self.logo_image, batch=self.batch, x=self._SIZE_X//2, y=280)
        self.button = pyglet.sprite.Sprite(img=pyglet.image.load('img/titlescreen/button.png'), batch=self.batch, x=208, y=65)
        self.quit = pyglet.sprite.Sprite(img=pyglet.image.load_animation('img/titlescreen/music.gif'), batch=self.batch, x=500, y=30)
        self.prod = pyglet.media.load('snd/titre.wav')
        self.player = pyglet.media.Player()
        self.player.queue(self.prod)
        self.player.eos_action = 'loop'
        self.player.play()
        self.time = 0

        pyglet.clock.schedule_interval(self.update, 1/60)

    def draw(self):
        # afficher images
        self.fbo.bind()
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.batch.draw()
        glEnable(GL_BLEND)
        self.fbo.unbind()
        glEnable(GL_BLEND)
        self.overlay.blit(0, 0, width=self._SIZE_X*self._window_scale, height=self._SIZE_Y*self._window_scale)

    def update(self, dt):
        if self.button.x <= self._inputo.mx/self._window_scale < self.button.width + self.button.x and self.button.y <= self._inputo.my/self._window_scale < self.button.height + self.button.y:
            if self._inputo.lclick:
                self._window.switch_scene(1)
            self.button.color = (153, 0, 0)
        else:
            self.button.color = (255, 255, 255)
        if self.quit.x <= self._inputo.mx/self._window_scale < self.quit.width + self.quit.x and self.quit.y <= self._inputo.my/self._window_scale < self.quit.height + self.quit.y:
            if self._inputo.lclick:
                self._window.switch_scene(-1)
            self.quit.color = (153, 0, 0)
        else:
            self.quit.color = (255, 255, 255)
        self.time += dt
        self.time %= 10000
        self.logo.scale = 0.1 * np.sin(np.pi * self.time/2) + 1


class MainGameScene(Scene):
    def __init__(self, scale, size_x, size_y, inputo, window, worldgen):
        self._window = window
        self._window_scale = scale
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self._inputo = inputo
        self.worldgen = worldgen
        self.sprite_batch = pyglet.graphics.Batch()
        self.cam_x = 0
        self.cam_y = 0
        self.item_manager = GroundItemManager(self.sprite_batch)
        self.inventory = Inventory(self._SIZE_X, self._SIZE_Y, self.item_manager)
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

        #weapon = Weapon(WEAPON_MODELS[0], 0, 0, 0, 0, 0)
        #print(self.inventory.pickup(weapon))

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
        self.time_of_day += dt
        self.time_of_day %= 1440
        #print(self.time_of_day//60)
        #print(self.time_of_day%60)
        bullet = self.player.update(self._inputo, dt)
        if bullet != None:
            self.bullet_manager.add_bullet(bullet, True)
        if self.player.death_time > 4:
            self._window.switch_scene(0)
        self.npc_manager.update(\
            self.bullet_manager, self.item_manager, self.player.playerwalker.pos_x, self.player.playerwalker.pos_y,\
            self.cam_x, self.cam_y, self.tilingmap.occupation_grid, self.bullet_manager.bullet_list_player,\
            self.bullet_manager.bullet_list_ennemy, dt\
        )
        self.item_manager.update(self.inventory, self.player.playerwalker.pos_x, self.player.playerwalker.pos_y, self.player.selection, self.cam_x, self.cam_y, dt)
        self.bullet_manager.update(dt, self.player, self.cam_x, self.cam_y)
        self.cam_x = self.player.cam_x
        self.cam_y = self.player.cam_y
        self.hud.update(self.player.playercar.x, self.player.playercar.y, self.cam_x, self.cam_y)
        self.worldgen.group.update(self.time_of_day, self.cam_x, self.cam_y, self.player.playercar.x, self.player.playercar.y, -np.radians(self.player.playercar.sprite.rotation-90))
        self.tilingmap.update(self.cam_x, self.cam_y)
        if self._inputo.openinv:
            self._inputo.openinv = 0
            self.inventory.active = not self.inventory.active
        if self.inventory.active:
            self.inventory.update(self._inputo, self._window_scale, self.player.playerwalker.back_x, self.player.playerwalker.back_y)
