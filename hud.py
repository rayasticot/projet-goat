import pyglet
import numpy
from worldsprite import WorldSprite


class Hud:
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
        