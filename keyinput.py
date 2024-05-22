"""
Module pour la gestion des entrées utilisateur dans le jeu.
"""

import pyglet


class Input:
    """
    Classe pour gérer les entrées utilisateur dans le jeu.
    """
    def __init__(self):
        """
        Initialise les états des différentes entrées utilisateur.

        Returns
        -------
        None.
        """

        self.up = 0
        self.dw = 0
        self.rg = 0
        self.le = 0
        self.mx = 0
        self.my = 0
        self.getin = 0
        self.openinv = 0
        self.hbrake = 0
        self.lclick = 0
        self.rclick = 0
        self.reload = 0
        self.map = 0
