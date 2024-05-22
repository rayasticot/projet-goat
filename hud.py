import pyglet
import numpy as np
from worldsprite import WorldSprite


class CarIndicatorHud:
    def __init__(self, size_x, size_y, scale, batch):
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self.batch = batch
        self.SCALE = scale
        self.car_circle = pyglet.shapes.Circle(x=100, y=150, batch=batch, radius=8, color=(255, 41, 41))

    def get_relative_pos(self, x, y, cam_x, cam_y):
            return x - cam_x, y - cam_y

    def update(self, car_x, car_y, cam_x, cam_y):
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
    def __init__(self, size_x, size_y, scale, batch):
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
        return int((x+np.sin((y+self._SIZE_X)*0.0625)*8)/256), (-int(((y+self._SIZE_Y)+np.cos(x*0.0625)*8)/256))

    def update(self, inputo, player_health, player_money, time_of_day, car_x, car_y, cam_x, cam_y):
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
