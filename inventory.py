import pyglet
import numpy as np
from dataclasses import dataclass
import json


#BULLET_TYPE = ("9mm")

ITEM_SPRITES = (
    pyglet.image.load("img/items/ak.png")
)


@dataclass
class Item:
    sprite: pyglet.sprite.Sprite
    name: str
    desc: str
    weight: float
    equipable: bool


@dataclass
class WeaponModel:
    sprite_index: int
    name: str
    desc: str
    weight: float
    capacity: int
    bullet_type: int
    rate: float
    reach: int
    accuracy: float
    damage: float


@dataclass
class Weapon(Item):
    model: WeaponModel
    loaded: int
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


#WEAPON_MODELS = load_weapon_models("item/weapon_models.json")


class GridItem(pyglet.gui.WidgetBase):
    def __init__(self, x, y, empty, empty_t, filled, filled_t, inventory, item_index, i_type, batch, group=None):
        super().__init__(x, y, empty.width, empty.height)
        self._empty = empty
        self._empty_t = empty_t
        self._filled = filled
        self._filled_t = filled_t
        self._batch = batch
        self._user_group = group
        bg_group = pyglet.graphics.Group(order=0, parent=group)
        self._sprite = pyglet.sprite.Sprite(self._empty_t, x, y, batch=batch, group=bg_group)
        self._inventory = inventory
        self.item_index = item_index
        self.i_type = i_type
        self._enabled = False
        self.presence = False

    def mouse_press(self, x, y, buttons, modifiers):
        if not self._enabled or not self._check_hit(x, y):
            return
        self._inventory.item_pressed(self.item_index, self.i_type)

    def mouse_release(self, x, y, buttons, modifiers):
        if not self._enabled or not self._pressed:
            return
        self._inventory.item_released(self.item_index, self.i_type)

    def mouse_motion(self, x, y, dx, dy):
        if self._check_hit(x, y):
            if self.presence:
                self._sprite.image = self._filled
            else:
                self._sprite.image = self._empty
        else:
            if self.presence:
                self._sprite.image = self._filled_t
            else:
                self._sprite.image = self._empty_t

    def update(self, inputo, scale):
        self.mouse_motion(inputo.mx//scale, inputo.my//scale, 0, 0)

    def set_status(self, occupied):
        if occupied:
            self._sprite.image = self._filled
            self.presence = True
        else:
            self._sprite.image = self._empty
            self.presence = False
    
    def enable(self, value):
        self._enabled = value
        self._sprite.visible = value


class ArrowButton(pyglet.gui.WidgetBase):
    def __init__(self, x, y, image, image_t, batch, group=None):
        super().__init__(x, y, image.width, image.height)
        self.image = image
        self.image_t = image_t
        bg_group = pyglet.graphics.Group(order=0, parent=group)
        self._sprite = pyglet.sprite.Sprite(self.image_t, x, y, batch=batch, group=bg_group)
        self._batch = batch
        self._user_group = group
        self.enabled = True

    def mouse_press(self, x, y, buttons, modifiers):
        if not self.enabled or not self._check_hit(x, y):
            return False
        return True

    def mouse_motion(self, x, y, dx, dy):
        if self._check_hit(x, y):
            self._sprite.image = self.image
        else:
            self._sprite.image = self.image_t

    def update(self, inputo, scale):
        self.mouse_motion(inputo.mx//scale, inputo.my//scale, 0, 0)
        if inputo.lclick:
            if self.mouse_press(inputo.mx//scale, inputo.my//scale, 0, 0):
                inputo.lclick = 0
                return True
        return False


class Inventory:
    def __init__(self, size_x, size_y):
        self.batch = pyglet.graphics.Batch()

        self.arms = [None]*3
        self.equi = [None]*4
        self.cons = [None]*16
        self.keys = [None]*16
        self.bullets = {
            "9mm": 0,
            "7.62mm": 0
        }
        self.hand = [None]*4

        self.widget_arms = [None]*3
        self.widget_equi = [None]*4
        self.widget_cons = [None]*14
        self.widget_keys = [None]*14
        self.widget_bullets = [None]*len(self.bullets)
        self.widget_hand = [None]*4

        self.indicator_label = pyglet.text.Label("", font_name="Times New Roman", font_size=24, x=size_x/2, y=size_y-24, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))

        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        #self.cadre = pyglet.image.load("img/gui/cadre_item.png")
        #self.cadre_r = pyglet.image.load("img/gui/cadre_item_rempli.png")
        #self.g_cadre = pyglet.image.load("img/gui/gros_cadre.png")
        #self.g_cadre_r = pyglet.image.load("img/gui/gros_cadre_rempli.png")
        self.m_cadre = pyglet.image.load("img/gui/moyen_cadre.png")
        self.m_cadre_t = pyglet.image.load("img/gui/moyen_cadre_t.png")
        self.m_cadre_r = pyglet.image.load("img/gui/moyen_cadre_rempli.png")
        self.m_cadre_r_t = pyglet.image.load("img/gui/moyen_cadre_rempli_t.png")

        self.arrow_right = pyglet.image.load("img/gui/arrow_right.png")
        self.arrow_right_t = pyglet.image.load("img/gui/arrow_right_t.png")
        self.arrow_left = pyglet.image.load("img/gui/arrow_left.png")
        self.arrow_left_t = pyglet.image.load("img/gui/arrow_left_t.png")

        self.empty = pyglet.image.load("img/gui/empty.png")
        self.fond_img = pyglet.image.load("img/gui/fond.png")

        self.fond = pyglet.sprite.Sprite(img=self.fond_img, x=0, y=0, batch=self.batch)
        self.fond.opacity = 200

        self.active = False
        self.page = 0
        self.cursor_index = 0
        self.create_widgets()

    def switch_page(self, ammount):
        self.page += ammount
        self.page %= 4

    def create_widgets(self):
        center_x = self._SIZE_X/2
        center_y = self._SIZE_Y/2
        arms_be_x = center_x - 32*len(self.widget_arms)
        arms_be_y = center_y - 32
        for i in range(len(self.widget_arms)):
            self.widget_arms[i] = GridItem(arms_be_x+i*64, arms_be_y, self.m_cadre, self.m_cadre_t, self.m_cadre_r, self.m_cadre_r_t, self, i, 0, self.batch)

        equi_be_x = center_x - 32*len(self.widget_equi)
        equi_be_y = center_y - 32
        for i in range(len(self.widget_equi)):
            self.widget_equi[i] = GridItem(equi_be_x+i*64, equi_be_y, self.m_cadre, self.m_cadre_t, self.m_cadre_r, self.m_cadre_r_t, self, i, 1, self.batch)

        cons_be_x = center_x - 32*7
        cons_be_y = center_y - 32*2
        for i in range(len(self.widget_cons)):
            self.widget_cons[i] = GridItem(cons_be_x+(i%7)*64, cons_be_y+(i//7)*64, self.m_cadre, self.m_cadre_t, self.m_cadre_r, self.m_cadre_r_t, self, i, 2, self.batch)

        for i in range(len(self.widget_keys)):
            self.widget_keys[i] = GridItem(cons_be_x+(i%7)*64, cons_be_y+(i//7)*64, self.empty, self.empty, self.m_cadre_r, self.m_cadre_r_t, self, i, 3, self.batch)
        
        hand_be_x = center_x - 64*len(self.widget_equi) + 32
        for i in range(len(self.widget_hand)):
            self.widget_hand[i] = GridItem(hand_be_x+i*128, 8, self.m_cadre, self.m_cadre_t, self.m_cadre_r, self.m_cadre_r_t, self, i, 3, self.batch)
        
        self.hand_text0 = pyglet.text.Label("arme", font_name="Times New Roman", font_size=12, x=hand_be_x+32, y=84, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))
        self.hand_text1 = pyglet.text.Label("objet", font_name="Times New Roman", font_size=12, x=hand_be_x+128+31, y=84, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))
        self.hand_text2 = pyglet.text.Label("armure", font_name="Times New Roman", font_size=12, x=hand_be_x+256+31, y=84, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))
        self.hand_text3 = pyglet.text.Label("casque", font_name="Times New Roman", font_size=12, x=hand_be_x+384+31, y=84, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))

        self.arrow_button_r = ArrowButton(self._SIZE_X-68, center_y-32, self.arrow_right, self.arrow_right_t, self.batch)
        self.arrow_button_l = ArrowButton(4, center_y-32, self.arrow_left, self.arrow_left_t, self.batch)


    def update(self, inputo, scale):
        e_arms, e_equi, e_cons, e_keys, e_bull = False, False, False, False, False
        match self.page:
            case 0:
                e_arms = True
                self.indicator_label.text = "armes"
            case 1:
                e_equi = True
                self.indicator_label.text = "équipement"
            case 2:
                e_cons = True
                self.indicator_label.text = "objets"
            case 3:
                e_keys = True
                self.indicator_label.text = "objets clés"
            case 4:
                e_bull = True
                self.indicator_label.text = "munitions"
        for widget in self.widget_arms:
            widget.enable(e_arms)
            widget.update(inputo, scale)
        for widget in self.widget_equi:
            widget.enable(e_equi)
            widget.update(inputo, scale)
        for widget in self.widget_cons:
            widget.enable(e_cons)
            widget.update(inputo, scale)
        for widget in self.widget_keys:
            widget.enable(e_keys)
            widget.update(inputo, scale)
        for widget in self.widget_hand:
            widget.enable(True)
            widget.update(inputo, scale)
        if self.arrow_button_l.update(inputo, scale):
            self.switch_page(-1)
        if self.arrow_button_r.update(inputo, scale):
            self.switch_page(1)
