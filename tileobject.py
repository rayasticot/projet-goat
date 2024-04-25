import pyglet
import numpy as np


class TilingMap:
    def __init__(self, cam_x, cam_y, batch):
        self.cam_x = cam_x
        self.cam_y = cam_y
        self.rocher = pyglet.image.load("img/rochertest.png")
        self.occupation_grid = np.zeros((8, 8))
        self.batch = batch

    def update(self, cam_x, cam_y):
        self.cam_x = cam_x
        self.cam_y = cam_y
        self.grid_x = 
