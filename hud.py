"""
Gestion de l'affichage du HUD (Head-Up Display), incluant les indicateurs de position de la voiture, la santé du joueur, l'argent, et l'heure dans le jeu.
"""

import pyglet
import numpy as np
from worldsprite import WorldSprite


class CarIndicatorHud:
    """
    Classe pour gérer l'affichage de l'indicateur de position de la voiture sur le HUD.
    """
    def __init__(self, size_x, size_y, scale, batch):
        """
        Initialise l'indicateur de position de la voiture.

        Parameters
        ----------
        size_x : int
            Largeur de la fenêtre.
        size_y : int
            Hauteur de la fenêtre.
        scale : float
            Échelle de l'affichage.
        batch : pyglet.graphics.Batch
            Groupe de batch pyglet pour l'affichage.

        Returns
        -------
        None.
        """
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self.batch = batch
        self.SCALE = scale
        self.car_circle = pyglet.shapes.Circle(x=100, y=150, batch=batch, radius=8, color=(255, 41, 41))

    def get_relative_pos(self, x, y, cam_x, cam_y):
        """
        Calcule la position relative d'un point par rapport à la caméra.

        Parameters
        ----------
        x : int
            Position x du point.
        y : int
            Position y du point.
        cam_x : int
            Position x de la caméra.
        cam_y : int
            Position y de la caméra.

        Returns
        -------
        tuple
            La position relative (x, y) par rapport à la caméra.
        """
        return x - cam_x, y - cam_y

    def update(self, car_x, car_y, cam_x, cam_y):
        """
        Met à jour la position et la visibilité de l'indicateur de voiture.

        Parameters
        ----------
        car_x : int
            Position x de la voiture.
        car_y : int
            Position y de la voiture.
        cam_x : int
            Position x de la caméra.
        cam_y : int
            Position y de la caméra.

        Returns
        -------
        None.
        """
        rel_x, rel_y = self.get_relative_pos(car_x, car_y, cam_x, cam_y)
        if 0 <= rel_x < self._SIZE_X :
            if 0 <= rel_y < self._SIZE_Y :
                self.car_circle.visible = False
                return

        self.car_circle.visible = True
        self.car_circle.x = rel_x
        self.car_circle.y = rel_y
        if rel_x > self._SIZE_X:
            self.car_circle.x = self._SIZE_X - 8
        elif rel_x < 0:
            self.car_circle.x = 8
        if rel_y > self._SIZE_Y:
            self.car_circle.y = self._SIZE_Y - 8
        elif rel_y < 0:
            self.car_circle.y = 8


class Hud:
    """
    Classe pour gérer l'affichage du HUD du joueur.
    """
    def __init__(self, size_x, size_y, scale, batch):
        """
        Initialise le HUD du joueur.

        Parameters
        ----------
        size_x : int
            Largeur de la fenêtre.
        size_y : int
            Hauteur de la fenêtre.
        scale : float
            Échelle de l'affichage.
        batch : pyglet.graphics.Batch
            Groupe de batch pyglet pour l'affichage.

        Returns
        -------
        None.
        """
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self.group = pyglet.graphics.Group(1)
        self.car_indicator = CarIndicatorHud(size_x, size_y, scale, batch)
        self.death = pyglet.sprite.Sprite(img=pyglet.image.load("img/gui/mort.png"), x=0, y=0, batch=batch, group=self.group)
        self.life_label = pyglet.text.Label("", font_name='Times New Roman', font_size=16, x=0, y=344, color=(255, 0, 0, 255), batch=batch, group=self.group)
        self.money_label = pyglet.text.Label("", font_name='Times New Roman', font_size=16, x=0, y=324, color=(100, 255, 100, 255), batch=batch, group=self.group)
        self.time_label = pyglet.text.Label("", font_name='Times New Roman', font_size=16, x=0, y=304, color=(255, 255, 100, 255), batch=batch, group=self.group)
        self.map_circle = pyglet.shapes.Circle(x=100, y=150, batch=batch, radius=4, color=(255, 41, 41), group=self.group)
        self.map = pyglet.sprite.Sprite(img=pyglet.image.load("img/gui/hud_map.png"), x=0, y=0, batch=batch, group=self.group)
        self.map.opacity = 128
        self.death.visible = False
        self.map.visible = False
        self.map_circle.visible = False

    def pixel_pos_to_world(self, x, y):
        """
        Convertit une position en pixels à une position dans le monde.

        Parameters
        ----------
        x : int
            Position x en pixels.
        y : int
            Position y en pixels.

        Returns
        -------
        tuple
            La position (x, y) dans le monde.
        """
        return int((x+np.sin((y+self._SIZE_X)*0.0625)*8)/256), (-int(((y+self._SIZE_Y)+np.cos(x*0.0625)*8)/256))

    def update(self, inputo, player_health, player_money, time_of_day, car_x, car_y, cam_x, cam_y):
        """
        Met à jour les éléments affichés sur le HUD.

        Parameters
        ----------
        inputo : Input
            Objet contenant les entrées du joueur.
        player_health : float
            Santé actuelle du joueur.
        player_money : float
            Montant d'argent du joueur.
        time_of_day : float
            Temps actuel du jeu.
        car_x : int
            Position x de la voiture.
        car_y : int
            Position y de la voiture.
        cam_x : int
            Position x de la caméra.
        cam_y : int
            Position y de la caméra.

        Returns
        -------
        None.
        """
        self.car_indicator.update(car_x, car_y, cam_x, cam_y)
        if player_health < 0:
            player_health = 0
        self.life_label.text = str(int(player_health))
        self.money_label.text = str(int(player_money))+"€"
        hour = str((int(time_of_day)//60)+6)
        if len(hour) == 1:
            hour = "0"+hour
        minute = str(int(time_of_day)%60)
        if len(minute) == 1:
            minute = "0"+minute
        self.time_label.text = hour+":"+minute
        if inputo.map:
            self.map_circle.visible = True
            self.map.visible = True
            self.map_circle.x, self.map_circle.y = self.pixel_pos_to_world(cam_x, cam_y)
            self.map_circle.x = (self.map_circle.x/1248)*191 + 229
            self.map_circle.y = 360 - (self.map_circle.y/2352)*360
        else:
            self.map.visible = False
            self.map_circle.visible = False
        if player_health <= 0:
            self.death.visible = True
