"""
Gestion des différentes 'scènes' du jeu
"""

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
    """
    Classe abstraite pour représenter une scène dans le jeu.
    """
    @abstractmethod
    def draw(self):
        """
        Méthode abstraite pour dessiner la scène.
        """
        pass

    @abstractmethod
    def update(self, dt):
        """
        Méthode abstraite pour mettre à jour la scène.
        
        Parameters
        ----------
        dt : float
            Temps écoulé depuis la dernière mise à jour.
        """
        pass

class TitleScreen(Scene):
    """
    Classe pour représenter l'écran de titre du jeu.
    """
    def __init__(self, scale, size_x, size_y, inputo, window):
        """
        Initialise l'écran de titre du jeu.

        Parameters
        ----------
        scale : float
            Échelle de l'affichage.
        size_x : int
            Largeur de la fenêtre.
        size_y : int
            Hauteur de la fenêtre.
        inputo : InputObject
            Objet d'entrée pour la gestion des entrées utilisateur.
        window : Window
            Fenêtre principale du jeu.

        Returns
        -------
        None.
        """
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
        self.player.loop = True
        self.player.play()
        self.time = 0

        pyglet.clock.schedule_interval(self.update, 1/60)

    def draw(self):
        """
        Dessine l'écran de titre.
        """
        self.fbo.bind()
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self.batch.draw()
        glEnable(GL_BLEND)
        self.fbo.unbind()
        glEnable(GL_BLEND)
        self.overlay.blit(0, 0, width=self._SIZE_X*self._window_scale, height=self._SIZE_Y*self._window_scale)

    def update(self, dt):
        """
        Met à jour l'écran de titre.

        Parameters
        ----------
        dt : float
            Temps écoulé depuis la dernière mise à jour.
        """
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
    """
    Classe pour représenter la scène principale du jeu.
    """
    def __init__(self, scale, size_x, size_y, inputo, window, worldgen):
        """
        Initialise la scène principale du jeu.

        Parameters
        ----------
        scale : float
            Échelle de l'affichage.
        size_x : int
            Largeur de la fenêtre.
        size_y : int
            Hauteur de la fenêtre.
        inputo : InputObject
            Objet d'entrée pour la gestion des entrées utilisateur.
        window : Window
            Fenêtre principale du jeu.
        worldgen : WorldGen
            Générateur de monde pour créer le monde du jeu.

        Returns
        -------
        None.
        """
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
        self.npc_manager = NpcManager(self.sprite_batch)
        self.tilingmap = TilingMap(self.cam_x, self.cam_y, self._SIZE_X, self._SIZE_Y, self.npc_manager, self.sprite_batch)
        self.player = Player(self.sprite_batch, 100*256, -280*256, self._SIZE_X, self._SIZE_Y, self._window_scale, self.inventory)
        self.bullet_manager = BulletManager()
        self.overlay = pyglet.image.Texture.create(self._SIZE_X, self._SIZE_Y, internalformat=pyglet.gl.GL_RGBA8)
        self.fbo = pyglet.image.Framebuffer()
        self.fbo.attach_texture(self.overlay)

        self.prod = pyglet.media.load('snd/ambiance.mp3')
        self.prod_player = pyglet.media.Player()
        self.prod_player.queue(self.prod)
        self.prod_player.loop = True
        self.prod_player.play()

        self.time_of_day = 120

        pyglet.clock.schedule_interval(self.update, 1/60)

        weapon = Weapon(WEAPON_MODELS[5], 0, 0, 0, 0, 0)
        print(self.inventory.pickup(weapon))

        #self.inventory.pickup_item()

    def draw(self):
        """
        Dessine la scène principale du jeu.
        """
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
        """
        Met à jour la scène principale du jeu.

        Parameters
        ----------
        dt : float
            Temps écoulé depuis la dernière mise à jour.
        """
        self.time_of_day += dt
        self.time_of_day %= 1440
        bullet = self.player.update(self._inputo, dt, self.tilingmap.sprite_dict)
        if bullet != None:
            self.bullet_manager.add_bullet(bullet, True)
        if self.player.death_time > 4:
            self._window.switch_scene(0)
        self.player.money += self.npc_manager.update(\
            self.bullet_manager, self.item_manager, self.player.playerwalker.pos_x, self.player.playerwalker.pos_y,\
            self.player.heal, self.cam_x, self.cam_y, self.tilingmap.occupation_grid, self.bullet_manager.bullet_list_player,\
            self.bullet_manager.bullet_list_ennemy, dt\
        )
        self.item_manager.update(self.inventory, self.player.playerwalker.pos_x, self.player.playerwalker.pos_y, self.player.selection, self.cam_x, self.cam_y, dt)
        self.bullet_manager.update(dt, self.player, self.tilingmap.sprite_dict, self.cam_x, self.cam_y)
        self.cam_x = self.player.cam_x
        self.cam_y = self.player.cam_y
        self.hud.update(self._inputo, self.player.health, self.player.money, self.time_of_day, self.player.playercar.x, self.player.playercar.y, self.cam_x, self.cam_y)
        self.worldgen.group.update(self.time_of_day, self.cam_x, self.cam_y, self.player.playercar.x, self.player.playercar.y, -np.radians(self.player.playercar.sprite.rotation-90))
        self.tilingmap.update(self.cam_x, self.cam_y)
        if self._inputo.openinv:
            self._inputo.openinv = 0
            self.inventory.active = not self.inventory.active
        if self.inventory.active:
            self.inventory.update(self._inputo, self._window_scale, self.player.playerwalker.back_x, self.player.playerwalker.back_y)
