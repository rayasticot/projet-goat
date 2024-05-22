import pyglet
import random
import numpy as np
from worldsprite import WorldSprite
from npc import NpcWalker
from inventory import Weapon, WEAPON_MODELS
from city import City, cities


MAP_SIZE = 30
OBJECTS = (
    pyglet.image.load("img/house.png"), pyglet.image.load("img/house2.png"), pyglet.image.load("img/house3.png"), pyglet.image.load("img/bldng_g1.png"),
    pyglet.image.load("img/bldng_g2.png"), pyglet.image.load("img/bldng_g3.png"), pyglet.image.load("img/bldng_r1.png"), pyglet.image.load("img/bldng_r2.png"),
    pyglet.image.load("img/bldng_r3.png"), pyglet.image.load("img/rochertest.png")
)


class TilingMap:
    def __init__(self, cam_x, cam_y, size_x, size_y, npc_manager, batch):
        self.cam_x = cam_x
        self.cam_y = cam_y
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self.occupation_grid = np.zeros((MAP_SIZE, MAP_SIZE))
        self.sprite_dict = {}
        self.npc_spawn = {}
        self.npc_manager = npc_manager
        self.batch = batch

    def noise_create(self, x, y, threshhold):
        pic = np.zeros((MAP_SIZE, MAP_SIZE))
        new_sprite_dict = {}
        new_npc_spawn = {}
        for i in range(MAP_SIZE):
            for j in range(MAP_SIZE):
                is_city = False
                for city in cities:
                    if city.x <= i+x < city.x+len(city.data[0]) and city.y <= j+y < city.y+len(city.data):
                        is_city = True
                        co_x, co_y = city.x-(i+x), city.y-(j+y)
                        pic[i][j] = city.data[co_y][co_x]
                        selected_key = (i+x, j+y)
                        if selected_key in self.sprite_dict.keys():
                            new_sprite_dict[selected_key] = self.sprite_dict[selected_key]
                        else:
                            if pic[i][j] != 0:
                                new_sprite_dict[selected_key] = WorldSprite(batch=self.batch, img=OBJECTS[int(pic[i][j])-1], x=self._SIZE_X, y=self._SIZE_Y)
                        if selected_key in self.npc_spawn.keys():
                            new_npc_spawn[selected_key] = self.npc_spawn[selected_key]
                        else:
                            if random.randint(0, 3) == 0:
                                new_npc_spawn[selected_key] = random.randint(0, 2)
                                if random.randint(0, 3) == 0:
                                    new_npc_spawn[selected_key] = 3
                                self.npc_manager.npcs.append(NpcWalker((i+x)*256, (j+y)*256, 100, new_npc_spawn[selected_key], None, False, self.batch))
                            else:
                                new_npc_spawn[selected_key] = -1
                if is_city:
                    continue
                if random.Random((i+x) + (j+y)*7321).uniform(0, 1) > threshhold:
                    chosen_obstacle = random.randint(0, 8)
                    pic[i][j] = chosen_obstacle
                    selected_key = (i+x, j+y)
                    if selected_key in self.sprite_dict.keys():
                        new_sprite_dict[selected_key] = self.sprite_dict[selected_key]
                    else:
                        new_sprite_dict[selected_key] = WorldSprite(batch=self.batch, img=OBJECTS[chosen_obstacle], x=self._SIZE_X, y=self._SIZE_Y)
                    if selected_key in self.npc_spawn.keys():
                        new_npc_spawn[selected_key] = self.npc_spawn[selected_key]
                    else:
                        if random.randint(0, 3) == 0:
                            new_npc_spawn[selected_key] = random.randint(0, 2)
                            self.npc_manager.npcs.append(NpcWalker((i+x)*256, (j+y)*256, 100, new_npc_spawn[selected_key], None, False, self.batch))
                        else:
                            new_npc_spawn[selected_key] = -1
        return pic, new_sprite_dict, new_npc_spawn

    def update_sprites(self):
        for key, value in self.sprite_dict.items():
            value.set_relative_pos(key[0]*256, key[1]*256, self.cam_x, self.cam_y)

    def update(self, cam_x, cam_y):
        self.cam_x = cam_x
        self.cam_y = cam_y
        x, y = (self.cam_x//256)-14, (self.cam_y//256)-15
        self.occupation_grid, self.sprite_dict, self.npc_spawn = self.noise_create(x, y, 0.99)
        self.update_sprites()
