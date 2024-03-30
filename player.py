import pyglet
from worldsprite import WorldSprite
import numpy as np


SENSI = np.pi/2
SPEED_ADD = 4
DECCEL_ADD = 1
BRAKE_ADD = 4
FRONT_SPEED_L = 12
BACK_SPEED_L = 2


class PlayerCar:
    def __init__(self, batch, pos_x, pos_y, size_x, size_y, scale):
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self._window_scale = scale
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.x, self.y = int(pos_x), int(pos_y)
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.speed_intensity = 0.0
        self.dir_x = 0.0
        self.dir_y = 1.0
        self.image = pyglet.image.load("img/car.png")
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.sprite = WorldSprite(batch=batch, img=self.image, x=(((self._SIZE_X)//2)), y=(((self._SIZE_Y)//2)))
        #self.sprite.scale = self._window_scale

    def hbrake_func(self, x):
        if x <= 0:
            return 0
        if x < 0.755:
            return 4*(x**2)
        return 4/(x+1)

    def rotate(self, inputo, delta_t):
        rotate_intensity = (inputo.le - inputo.rg)*delta_t*self.hbrake_func(self.speed_intensity)
        angle = SENSI*rotate_intensity
        self.dir_x = np.cos(angle)*self.dir_x - np.sin(angle)*self.dir_y
        self.dir_y = np.sin(angle)*self.dir_x + np.cos(angle)*self.dir_y
        dir_inten = np.sqrt(self.dir_x**2 + self.dir_y**2)
        self.dir_x /= dir_inten
        self.dir_y /= dir_inten
        if inputo.hbrake == 0:
            self.speed_x = np.cos(angle)*self.speed_x - np.sin(angle)*self.speed_y
            self.speed_y = np.sin(angle)*self.speed_x + np.cos(angle)*self.speed_y

    def deccel_vec(self, speed_x, speed_y, inten):
        deccel_x = speed_x
        deccel_y = speed_y
        deccel_inten = np.sqrt(deccel_x**2 + deccel_y**2)
        if deccel_inten <= 0:
            return 0, 0
        deccel_x /= deccel_inten
        deccel_y /= deccel_inten
        return deccel_x*inten*DECCEL_ADD, deccel_y*inten*DECCEL_ADD

    def decceletate(self, inputo, delta_t):
        brake_ammount = 0
        if inputo.dw:
            brake_ammount = 0.5
        if inputo.hbrake:
            brake_ammount = 1
        deccel_x, deccel_y = self.deccel_vec(self.speed_x, self.speed_y, delta_t*brake_ammount*BRAKE_ADD + delta_t)
        if self.speed_x > 0:
            self.speed_x -= deccel_x
            if self.speed_x < 0:
                self.speed_x = 0
        elif self.speed_x < 0:
            self.speed_x -= deccel_x
            if self.speed_x > 0:
                self.speed_x = 0
        if self.speed_y > 0:
            self.speed_y -= deccel_y
            if self.speed_y < 0:
                self.speed_y = 0
        elif self.speed_y < 0:
            self.speed_y -= deccel_y
            if self.speed_y > 0:
                self.speed_y = 0

    def limit_speed(self, inputo):
        self.speed_intensity = np.sqrt(self.speed_x**2 + self.speed_y**2)
        speed_to_change = None
        if self.speed_intensity > FRONT_SPEED_L and inputo.up == 1:
            speed_to_change = FRONT_SPEED_L
        """
        if self.speed_intensity > BACK_SPEED_L and inputo.dw == 1 and inputo.up == 0:
            speed_to_change = BACK_SPEED_L
        """
        if speed_to_change != None:
            self.speed_x /= self.speed_intensity
            self.speed_y /= self.speed_intensity
            self.speed_x *= speed_to_change
            self.speed_y *= speed_to_change
        self.speed_intensity = np.sqrt(self.speed_x**2 + self.speed_y**2)

    def accelerate(self, inputo, delta_t):
        self.decceletate(inputo, delta_t)
        accel_intensity = (inputo.up - inputo.dw*0.5)*delta_t*SPEED_ADD*(-1)
        self.speed_intensity = np.sqrt(self.speed_x**2 + self.speed_y**2)
        self.speed_x += (4/(self.speed_intensity+1))*self.dir_x*accel_intensity
        self.speed_y += (4/(self.speed_intensity+1))*self.dir_y*accel_intensity
        self.pos_x += self.speed_x
        self.pos_y += self.speed_y
        self.limit_speed(inputo)

    """
    def push_to_dir_fix(self, delta_t):
        self.speed_intensity = np.sqrt(self.speed_x**2 + self.speed_y**2)
        if self.speed_intensity == 0:
            return
        angle_dif = np.arccos((self.speed_x*self.dir_x + self.speed_y*self.dir_y)/self.speed_intensity)
        angle_to_change = (1/12)*np.pi*delta_t*np.sign(angle_dif)
        if np.abs(angle_to_change) > np.abs(angle_dif):
            angle_to_change = angle_dif
        self.speed_x = np.cos(angle_to_change)*self.speed_x - np.sin(angle_to_change)*self.speed_y
        self.speed_y = np.sin(angle_to_change)*self.speed_x + np.cos(angle_to_change)*self.speed_y
    """

    """
    def render(self):
        self.sprite = rot_center(self.sprite_loaded, np.degrees(np.arctan2(self.dir_y, self.dir_x)*(-1) + (np.pi/2)))
    """

    def stop(self):
        self.speed_x = 0
        self.speed_y = 0
        self.speed_intensity = 0

    def update(self, inputo, delta_t):
        self.rotate(inputo, delta_t)
        self.accelerate(inputo, delta_t)
        self.sprite.rotation = np.degrees(np.arctan2(self.dir_y, self.dir_x)*(-1) + (np.pi/2))
        self.x, self.y = int(self.pos_x), int(self.pos_y)

    def update_sprite(self, cam_x, cam_y):
        self.sprite.set_relative_pos(self.x, self.y, cam_x, cam_y)


class PlayerWalker:
    def __init__(self, batch, pos_x, pos_y, size_x, size_y, scale):
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self._window_scale = scale
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.x, self.y = int(pos_x), int(pos_y)
        self.image = pyglet.image.load("img/mec.png")
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.sprite = WorldSprite(batch=batch, img=self.image, x=(((self._SIZE_X)//2)), y=(((self._SIZE_Y)//2)))
    
    def deccelerate(self, delta_t):
        if self.speed_x > 0:
            self.speed_x -= 8*delta_t
            if self.speed_x < 0:
                self.speed_x = 0
        if self.speed_x < 0:
            self.speed_x += 8*delta_t
            if self.speed_x > 0:
                self.speed_x = 0
        if self.speed_y > 0:
            self.speed_y -= 8*delta_t
            if self.speed_y < 0:
                self.speed_y = 0
        if self.speed_y < 0:
            self.speed_y += 8*delta_t
            if self.speed_y > 0:
                self.speed_y = 0

    def stop(self):
        self.speed_x = 0
        self.speed_y = 0

    def update(self, inputo, delta_t, acc_x_ow=None, acc_y_ow=None): # Attention multiplier acc_ow avec delta_t à l'avance
        dir_x = inputo.mx - ((self._SIZE_X*self._window_scale)//2)
        dir_y = inputo.my - ((self._SIZE_Y*self._window_scale)//2)
        dir_inten = np.sqrt(dir_x**2 + dir_y**2)
        dir_x, dir_y = dir_x/dir_inten, dir_y/dir_inten
        self.sprite.rotation = np.degrees(np.arctan2(dir_y, dir_x)*(-1) + (np.pi/2))
        if acc_x_ow == None or acc_y_ow == None:
            acc_x, acc_y = 0, 0
            if inputo.rg:
                acc_x = 32*delta_t
            if inputo.le:
                acc_x = -32*delta_t
            if inputo.up:
                acc_y = 32*delta_t
            if inputo.dw:
                acc_y = -32*delta_t
        else:
            acc_x, acc_y = acc_x_ow, acc_y_ow
        acc_inten = np.sqrt(acc_x**2 + acc_y**2)
        if acc_inten > 0:
            acc_x, acc_y = acc_x/acc_inten, acc_y/acc_inten
            self.speed_x += acc_x
            self.speed_y += acc_y
        self.deccelerate(delta_t)
        speed_inten = np.sqrt(self.speed_x**2 + self.speed_y**2)
        if speed_inten > 3:
            self.speed_x /= speed_inten
            self.speed_y /= speed_inten
            self.speed_x *= 3
            self.speed_y *= 3
        self.pos_x += self.speed_x
        self.pos_y += self.speed_y

        self.x, self.y = int(self.pos_x), int(self.pos_y)
    
    def update_sprite(self, cam_x, cam_y):
        self.sprite.set_relative_pos(self.x, self.y, cam_x, cam_y)


class Player:
    def __init__(self, batch, pos_x, pos_y, size_x, size_y, scale):
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self._window_scale = scale
        self.cam_x = int(pos_x) - (size_x//2)
        self.cam_y = int(pos_y) - (size_y//2)
        self.selection = 1
        self.playercar = PlayerCar(batch, pos_x, pos_y, size_x, size_y, scale)
        self.playerwalker = PlayerWalker(batch, pos_x, pos_y, size_x, size_y, scale)

    def update(self, inputo, delta_t):
        if self.selection:
            if inputo.getin:
                car_dir_x = self.playercar.pos_x - self.playerwalker.pos_x
                car_dir_y = self.playercar.pos_y - self.playerwalker.pos_y
                car_dir_inten = np.sqrt(car_dir_x**2 + car_dir_y**2)
                if car_dir_inten < 8:
                    self.selection = 0
                    inputo.getin = 0
                    self.playercar.stop()
                    self.playerwalker.sprite.visible = False
                if car_dir_inten < 256:
                    car_dir_x, car_dir_y = (car_dir_x/car_dir_inten)*32*delta_t, (car_dir_y/car_dir_inten)*32*delta_t
                    self.playerwalker.update(inputo, delta_t, car_dir_x, car_dir_y)
                else:
                    self.playerwalker.update(inputo, delta_t)
            else:
                self.playerwalker.update(inputo, delta_t)
            self.cam_x = self.playerwalker.x - (self._SIZE_X//2)
            self.cam_y = self.playerwalker.y - (self._SIZE_Y//2)
        else:
            self.playerwalker.pos_x = self.playercar.pos_x
            self.playerwalker.pos_y = self.playercar.pos_y
            self.playerwalker.x = self.playercar.x
            self.playerwalker.y = self.playercar.y
            if inputo.getin and self.playercar.speed_intensity < 1:
                self.selection = 1
                inputo.getin = 0
                self.playerwalker.stop()
                self.playerwalker.sprite.visible = True
            else:
                self.playercar.update(inputo, delta_t)
            self.cam_x = self.playercar.x - (self._SIZE_X//2)
            self.cam_y = self.playercar.y - (self._SIZE_Y//2)
        self.playercar.update_sprite(self.cam_x, self.cam_y)
        self.playerwalker.update_sprite(self.cam_x, self.cam_y)
