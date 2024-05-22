"""
Module pour la gestion des mappings de touches du clavier.
"""

import json
from pyglet.window import key


class Keymap:
    """
    Classe pour gérer les mappings de touches du clavier.
    """
    def __init__(self, keymap):
        """
        Initialise les mappings de touches à partir d'un fichier JSON.

        Parameters
        ----------
        keymap : str
            Nom du fichier JSON contenant les mappings de touches.

        Returns
        -------
        None.
        """
        with open(f"keymap/{keymap}.json") as f:
            self.keymap = json.load(f)
    
    def get_action(self, symbol):
        """
        Récupère l'action associée à un symbole de touche.

        Parameters
        ----------
        symbol : int
            Symbole de la touche.

        Returns
        -------
        str or None
            L'action associée au symbole de la touche, ou None si aucune action n'est définie.
        """
        symbol = key.symbol_string(symbol)
        return self.keymap[symbol] if symbol in self.keymap else None