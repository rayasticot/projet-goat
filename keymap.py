import json
from pyglet.window import key


class Keymap:
    def __init__(self, keymap):
        with open(f"keymap/{keymap}.json") as f:
            self.keymap = json.load(f)
    
    def get_action(self, symbol):
        symbol = key.symbol_string(symbol)
        return self.keymap[symbol] if symbol in self.keymap else None