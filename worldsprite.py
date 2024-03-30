import pyglet


class WorldSprite(pyglet.sprite.Sprite):
    def set_relative_pos(self, x, y, cam_x, cam_y):
        self.x = x - cam_x
        self.y = y - cam_y
