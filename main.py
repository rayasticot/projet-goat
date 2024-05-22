"""
Module principal
"""

import argparse

import pyglet
from pyglet.gl import *
from scene import Scene, MainGameScene, TitleScreen
from world_gen import WorldGen
from keyinput import Input 
from keymap import Keymap


class Game(pyglet.window.Window):
    """
    Classe principale gérant le jeu.
    """
    def __init__(self, scale=3, keymap="qwerty"):
        """
        Initialise la fenêtre de jeu.

        Parameters
        ----------
        scale : int, optional
            Échelle de la fenêtre. The default is 3.
        keymap : str, optional
            Mappage des touches. The default is "qwerty".

        Returns
        -------
        None.
        """
        self._SIZE_X = 640
        self._SIZE_Y = 360
        self._window_scale = scale
        self.keymap = Keymap(keymap)
        self._inputo = Input()
        self._fps_display = pyglet.window.FPSDisplay(window=self)
        super().__init__(self._SIZE_X*self._window_scale, self._SIZE_Y*self._window_scale, caption="Trafficant d'armes simulator", fullscreen=False)
        self.worldgen = WorldGen(self._window_scale, self._SIZE_X, self._SIZE_Y)
        self.scene = TitleScreen(self._window_scale, self._SIZE_X, self._SIZE_Y, self._inputo, self)

    def switch_scene(self, new_scene):
        """
        Change la scène du jeu.

        Parameters
        ----------
        new_scene : int
            Nouvelle scène à afficher.

        Returns
        -------
        None.
        """
        pyglet.clock.unschedule(self.scene.update)
        match new_scene:
            case -1:
                self.close()
            case 0:
                self.scene = TitleScreen(self._window_scale, self._SIZE_X, self._SIZE_Y, self._inputo, self)
            case 1:
                self.scene = MainGameScene(self._window_scale, self._SIZE_X, self._SIZE_Y, self._inputo, self, self.worldgen)

    def on_draw(self):
        """
        Méthode appelée lors du dessin de la fenêtre.

        Returns
        -------
        None.
        """
        self.switch_to()
        self.clear()
        self.scene.draw()
        self._fps_display.draw()

    def on_key_press(self, symbol, modifiers):
        """
        Méthode appelée lorsqu'une touche est pressée.

        Parameters
        ----------
        symbol : int
            Code de la touche.
        modifiers : int
            Modificateurs.

        Returns
        -------
        None.
        """
        match(self.keymap.get_action(symbol)):
            case "UP":
                self._inputo.up = 1
            case "DOWN":
                self._inputo.dw = 1
            case "RIGHT":
                self._inputo.rg = 1
            case "LEFT":
                self._inputo.le = 1
            case "BRAKE":
                self._inputo.hbrake = 1
            case "INTERACT":
                self._inputo.getin = 1
            case "OPENINV":
                self._inputo.openinv = 1
            case "RELOAD":
                self._inputo.reload = 1
            case "MAP":
                self._inputo.map = 1

    def on_key_release(self, symbol, modifiers):
        """
        Méthode appelée lorsqu'une touche est relâchée.

        Parameters
        ----------
        symbol : int
            Code de la touche.
        modifiers : int
            Modificateurs.

        Returns
        -------
        None.
        """
        match(self.keymap.get_action(symbol)):
            case "UP":
                self._inputo.up = 0
            case "DOWN":
                self._inputo.dw = 0
            case "RIGHT":
                self._inputo.rg = 0
            case "LEFT":
                self._inputo.le = 0
            case "BRAKE":
                self._inputo.hbrake = 0
            case "INTERACT":
                self._inputo.getin = 0
            case "OPENINV":
                self._inputo.openinv = 0
            case "RELOAD":
                self._inputo.reload = 0
            case "MAP":
                self._inputo.map = 0

    def on_mouse_motion(self, x, y, dx, dy):
        """
        Méthode appelée lors du mouvement de la souris.

        Parameters
        ----------
        x : int
            Position x de la souris.
        y : int
            Position y de la souris.
        dx : int
            Déplacement en x de la souris.
        dy : int
            Déplacement en y de la souris.

        Returns
        -------
        None.
        """
        self._inputo.mx = x
        self._inputo.my = y

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Méthode appelée lorsqu'un bouton de la souris est encastré.

        Parameters
        ----------
        x : int
            Position x de la souris.
        y : int
            Position y de la souris.
        button : int
            Code du bouton de la souris.
        modifiers : int
            Modificateurs.

        Returns
        -------
        None.
        """

        if button == pyglet.window.mouse.LEFT:
            self._inputo.lclick = 1
        if button == pyglet.window.mouse.RIGHT:
            self._inputo.rclick = 1

    def on_mouse_release(self, x, y, button, modifiers):
        """
        Méthode appelée lorsqu'un bouton de la souris est relâché.

        Parameters
        ----------
        x : int
            Position x de la souris.
        y : int
            Position y de la souris.
        button : int
            Code du bouton de la souris.
        modifiers : int
            Modificateurs.

        Returns
        -------
        None.
        """
        if button == pyglet.window.mouse.LEFT:
            self._inputo.lclick = 0
        if button == pyglet.window.mouse.RIGHT:
            self._inputo.rclick = 0

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """
        Méthode appelée lors du déplacement de la souris en maintenant un bouton enfoncé.

        Parameters
        ----------
        x : int
            Position x de la souris.
        y : int
            Position y de la souris.
        dx : int
            Déplacement en x de la souris.
        dy : int
            Déplacement en y de la souris.
        buttons : int
            Boutons enfoncés.
        modifiers : int
            Modificateurs.

        Returns
        -------
        None.
        """
        self._inputo.mx = x
        self._inputo.my = y

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="Trafficant d'armes simulator")

    parser.add_argument('--scale',type=int, default=3)
    parser.add_argument('--keymap',type=str, default="qwerty")

    args = parser.parse_args()

    pyglet.image.Texture.default_min_filter = GL_NEAREST
    pyglet.image.Texture.default_mag_filter = GL_NEAREST
    window = Game(scale=args.scale,keymap=args.keymap)
    pyglet.app.run(1/60)
