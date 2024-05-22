"""
Module pour la gestion des sprites dans le monde.
"""

import pyglet


class WorldSprite(pyglet.sprite.Sprite):
    """
    Classe pour représenter les sprites dans le monde.
    """
    def set_relative_pos(self, x, y, cam_x, cam_y):
        """
        Définit la position relative du sprite par rapport à la caméra.

        Parameters
        ----------
        x : float
            Position x absolue du sprite.
        y : float
            Position y absolue du sprite.
        cam_x : float
            Position x de la caméra.
        cam_y : float
            Position y de la caméra.

        Returns
        -------
        None.
        """
        self.x = x - cam_x
        self.y = y - cam_y
