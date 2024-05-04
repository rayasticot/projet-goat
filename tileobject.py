import pyglet
import random
import numpy as np
from worldsprite import WorldSprite

MAP_SIZE = 30


class TilingMap:
    def __init__(self, cam_x, cam_y, size_x, size_y, batch):
        self.cam_x = cam_x
        self.cam_y = cam_y
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self.rocher = pyglet.image.load("img/rochertest.png")
        self.occupation_grid = np.zeros((MAP_SIZE, MAP_SIZE))
        self.sprite_dict = {}
        self.batch = batch

    def noise_create(self, x, y, threshhold):
        pic = np.zeros((MAP_SIZE, MAP_SIZE))
        new_sprite_dict = {}
        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                if random.Random((i+x) + (j+y)*7321).uniform(0, 1) > threshhold:
                    pic[i][j] = 1
                    selected_key = (i+x, j+y)
                    if selected_key in self.sprite_dict.keys():
                        new_sprite_dict[selected_key] = self.sprite_dict[selected_key]
                    else:
                        new_sprite_dict[selected_key] = WorldSprite(batch=self.batch, img=self.rocher, x=self._SIZE_X, y=self._SIZE_Y)
        return pic, new_sprite_dict
    
    def update_sprites(self):
        for key, value in self.sprite_dict.items():
            value.set_relative_pos(key[0]*256, key[1]*256, self.cam_x, self.cam_y)

    def update(self, cam_x, cam_y):
        self.cam_x = cam_x
        self.cam_y = cam_y
        x, y = (self.cam_x//256)-14, (self.cam_y//256)-15
        self.occupation_grid, self.sprite_dict = self.noise_create(x, y, 0.99)
        self.update_sprites()
