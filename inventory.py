import pyglet
import numpy as np
from dataclasses import dataclass
import json


BULLET_TYPE = {
    "9mm": 0
}

ITEM_SPRITES = (
    pyglet.image.load("img/items/ak.png")
)


@dataclass
class Item:
    sprite: pyglet.sprite.Sprite
    name: str
    desc: str
    weight: float
    size_x: int
    size_y: int
    equipable: bool


@dataclass
class WeaponModel:
    capacity: int
    bullet_type: int
    rate: float
    reach: int
    accuracy: float
    damage: float


@dataclass
class BulletBox(Item):
    bullet_type: int
    total: int

    def take(self, ammount):
        given = ammount
        if self.total < ammount:
            given = self.total
        self.total -= given

        return given


@dataclass
class Mag(Item):
    model: WeaponModel
    total: int

    def load(self, bullet_box):
        if self.model.bullet_type != bullet_box.bullet_type:
            return 1
        ammount_to_add = bullet_box.take(self.model.capacity - self.total)
        total += ammount_to_add

        return 0


@dataclass
class Weapon(Item):
    model: WeaponModel
    mag: Mag
    rate_damaged: float
    reach_damaged: float
    accuracy_damaged: float
    damage_damaged: float


def load_weapon_models(filename):
    models = ()
    with open(filename, "r") as fileread:
        fileloaded = json.load(fileread)
        for model in fileloaded["models"]:
            models = models + WeaponModel(pyglet.image.load(model["sprite"]), model["name"], model["desc"],\
                model["weight"], model["size_x"], model["size_y"], True, model["capacity"], model["bullet_type"],\
                model["rate"], model["reach"], model["accuracy"], model["damage"])
    return models


WEAPON_MODELS = load_weapon_models("item/weapon_models.json")


class GridItem(pyglet.gui.WidgetBase):
    def __init__(self, x, y, empty, filled, inventory, item_x, item_y, batch, group=None):
        super().__init__(x, y, empty.width, empty.height)
        self._empty = empty
        self._filled = filled
        self._batch = batch
        self._user_group = group
        bg_group = pyglet.graphics.Group(order=0, parent=group)
        self._sprite = pyglet.sprite.Sprite(self._empty, x, y, batch=batch, group=bg_group)
        self._inventory = inventory
        self.item_x = item_x
        self.item_y = item_y

    def on_mouse_press(self, x, y, buttons, modifiers):
        if not self.enabled or not self._check_hit(x, y):
            return
        self._inventory.item_pressed(self.item_x, self.item_y)

    def on_mouse_release(self, x, y, buttons, modifiers):
        if not self.enabled or not self._pressed:
            return
        self._inventory.item_released(self.item_x, self.item_y)

    def set_status(self, occupied):
        if occupied:
            self._sprite.image = self._filled
        else:
            self._sprite.image = self._empty


class Inventory:
    def __init__(self, window, size_x, size_y):
        self.frame = pyglet.gui.Frame(window)
        self.batch = pyglet.graphics.Batch()
        self.occupation_grid = np.zeros((10, 5))
        self.item_grid = [[None]*5]*10
        self.item_hand = [None, None]
        self.item_body = [None, None, None]
        self.inv_items = []
        self.hand_items = [None, None]
        self.body_item = [None, None, None]
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self.cadre = pyglet.image.load("img/gui/cadre_item.png")
        self.cadre_r = pyglet.image.load("img/gui/cadre_item_rempli.png")
        self.g_cadre = pyglet.image.load("img/gui/gros_cadre.png")
        self.g_cadre_r = pyglet.image.load("img/gui/gros_cadre_rempli.png")
        self.m_cadre = pyglet.image.load("img/gui/moyen_cadre.png")
        self.m_cadre_r = pyglet.image.load("img/gui/moyen_cadre_rempli.png")
        self.active = False
        self.create_widgets()

    def create_widgets(self):
        initial_add_x = (self._SIZE_X-(32*10))/2
        initial_add_y = (self._SIZE_Y-(32*8))/2
        for x in range(len(self.item_grid)):
            for y in range(len(self.item_grid[0])):
                self.item_grid[x][y] = GridItem(x*32 + initial_add_x, 32*(y+3) + initial_add_y, self.cadre, self.cadre_r, self, x, y, self.batch)
                self.frame.add_widget(self.item_grid[x][y])
        for i in range(len(self.item_hand)):
            self.item_hand[i] = GridItem(i*160 + initial_add_x, initial_add_y, self.g_cadre, self.g_cadre_r, self, -1, -1, self.batch)
        for i in range(len(self.item_body)):
            self.item_body[i] = GridItem(self._SIZE_X-64, i*64 + ((self._SIZE_Y-192)//2), self.m_cadre, self.m_cadre_r, self, -1, -1, self.batch)
