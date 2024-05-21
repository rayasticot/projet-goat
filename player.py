import pyglet
import random as r
import numpy as np
from worldsprite import WorldSprite
import os


SENSI = np.pi/2
SPEED_ADD = 4
DECCEL_ADD = 1
BRAKE_ADD = 4
FRONT_SPEED_L = 12
BACK_SPEED_L = 2


class BulletManager:
    def __init__(self):
        self.bullet_list_player = []
        self.bullet_list_ennemy = []

    def add_bullet(self, bullet, btype):
        if btype:
            self.bullet_list_player.append(bullet)
        else:
            self.bullet_list_ennemy.append(bullet)

    def update(self, delta_t, player, obstacles, cam_x, cam_y):
        bullet_player_to_remove = []
        bullet_ennemy_to_remove = []
        for i in range(len(self.bullet_list_player)):
            if self.bullet_list_player[i].update(delta_t, obstacles, cam_x, cam_y):
                bullet_player_to_remove.append(i)
        for i in range(len(self.bullet_list_ennemy)):
            if self.bullet_list_ennemy[i].update(delta_t, obstacles, cam_x, cam_y):
                bullet_ennemy_to_remove.append(i)
            player.check_bullet_hit(self.bullet_list_ennemy[i])
        new_bullet_list_player = []
        new_bullet_list_ennemy = []
        for i in range(len(self.bullet_list_player)):
            if not i in bullet_player_to_remove:
                new_bullet_list_player.append(self.bullet_list_player[i])
        for i in range(len(self.bullet_list_ennemy)):
            if not i in bullet_ennemy_to_remove:
                new_bullet_list_ennemy.append(self.bullet_list_ennemy[i])
        self.bullet_list_player = new_bullet_list_player
        self.bullet_list_ennemy = new_bullet_list_ennemy


class Bullet:
    def __init__(self, pos_x, pos_y, dir_x, dir_y, reach, damage, accuracy, batch):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.og_x = pos_x
        self.og_y = pos_y
        angle = np.arctan2(dir_y, dir_x)
        self.dir_x = np.cos(angle+np.radians(r.uniform(accuracy, -accuracy)))
        self.dir_y = np.sin(angle+np.radians(r.uniform(accuracy, -accuracy)))
        dir_inten = np.sqrt(self.dir_x**2 + self.dir_y**2)
        self.dir_x /= dir_inten
        self.dir_y /= dir_inten
        self.line = pyglet.shapes.Line(0, 0, 100, 100, 1, (255, 255, 255, 200), batch=batch)
        self.destroy_time = reach/1860
        self.alive_time = 0.0
        self.damage = damage

    def find_x1_y1(self, dt):
        if self.alive_time < 0.1:
            return self.og_x, self.og_y
        return self.og_x + self.dir_x*(self.alive_time-0.1)*1860, self.og_y + self.dir_y*(self.alive_time-0.1)*1860

    def update(self, dt, obstacles, cam_x, cam_y):
        self.alive_time += dt
        self.pos_x += self.dir_x*dt*1860
        self.pos_y += self.dir_y*dt*1860
        self.line.x, self.line.y = self.find_x1_y1(dt)
        self.line.x2, self.line.y2 = self.pos_x, self.pos_y
        self.line.x = self.line.x - cam_x
        self.line.y = self.line.y - cam_y
        self.line.x2 = self.line.x2 - cam_x
        self.line.y2 = self.line.y2 - cam_y
        if self.alive_time >= self.destroy_time:
            return True
        for obstacle in obstacles.values():
            if obstacle.x <= self.line.x2 < obstacle.x+256 and obstacle.y <= self.line.y2 < obstacle.y+256:
                return True
        return False


class WeaponControl:
    def __init__(self, pos_x, pos_y, inventory, batch):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.inventory = inventory
        self.weapon = self.inventory.hand[0]
        self.last_shot = 0
        self.time_since_load = 0
        self.batch = batch

    def update(self, pos_x, pos_y, dir_x, dir_y, inputo, dt):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.last_shot += dt
        self.time_since_load += dt
        self.weapon = self.inventory.hand[0]
        if self.weapon == None:
            return None
        #print(self.weapon.loaded)
        if inputo.reload:
            inputo.reload = 0
            if self.weapon.loaded < self.weapon.capacity and self.time_since_load > self.weapon.loadtime:
                self.weapon.loaded = self.inventory.take_bullets(self.weapon.bullet_type, self.weapon.capacity)
                if self.weapon.loaded > 0:
                    self.time_since_load = 0
        if inputo.lclick:
            if self.weapon.loaded <= 0 or self.time_since_load < self.weapon.loadtime:
                return None
            if self.last_shot > 1/self.weapon.rate:
                self.last_shot = 0
                self.weapon.loaded -= 1
                return Bullet(pos_x, pos_y, dir_x, dir_y, self.weapon.reach, self.weapon.damage, self.weapon.accuracy, self.batch)
        return None


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
        self.dir_y = -1.0
        self.image = pyglet.image.load("img/van.png")
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.sprite = WorldSprite(batch=batch, img=self.image, x=(((self._SIZE_X)//2)), y=(((self._SIZE_Y)//2)), z=-100)
        self.sprite.scale_x = 1/4
        self.sprite.scale_y = 1/4
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

    def accelerate(self, inputo, delta_t, obstacles, cam_x, cam_y):
        self.decceletate(inputo, delta_t)
        accel_intensity = (inputo.up - inputo.dw*0.5)*delta_t*SPEED_ADD*(-1)
        self.speed_intensity = np.sqrt(self.speed_x**2 + self.speed_y**2)
        self.speed_x += (4/(self.speed_intensity+1))*self.dir_x*accel_intensity
        self.speed_y += (4/(self.speed_intensity+1))*self.dir_y*accel_intensity
        self.pos_x += self.speed_x
        self.pos_y += self.speed_y
        spr_x, spr_y = self.pos_x - cam_x, self.pos_y - cam_y
        touch = False
        for obstacle in obstacles.values():
            if obstacle.x <= spr_x < obstacle.x+256 and obstacle.y <= spr_y < obstacle.y+256:
                touch = True
                break
        if touch:
            self.pos_x -= self.speed_x
            self.pos_y -= self.speed_y
            self.speed_x = 0
            self.speed_y = 0
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

    def update(self, inputo, delta_t, obstacles, cam_x, cam_y):
        self.rotate(inputo, delta_t)
        self.accelerate(inputo, delta_t, obstacles, cam_x, cam_y)
        self.sprite.rotation = np.degrees(np.arctan2(self.dir_y, self.dir_x)*(-1) + (np.pi/2) + np.pi)
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
        self.back_x = pos_x
        self.back_y = pos_y
        self.speed_x = 0.0
        self.speed_y = 0.0
        self.x, self.y = int(pos_x), int(pos_y)
        self.image = pyglet.image.load("img/persoprinci.png")
        self.m_image = pyglet.image.load("img/persoprinci_m.png")
        self.image.anchor_x = self.image.width // 2
        self.image.anchor_y = self.image.height // 2
        self.sprite = WorldSprite(batch=batch, img=self.image, x=(((self._SIZE_X)//2)), y=(((self._SIZE_Y)//2)))

    def set_back(self, dir_x, dir_y):
        self.back_x = self.pos_x - dir_x*32
        self.back_y = self.pos_y - dir_y*32
    
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

    def update(self, inputo, delta_t, obstacles, cam_x, cam_y, acc_x_ow=None, acc_y_ow=None): # Attention multiplier acc_ow avec delta_t à l'avance
        dir_x = inputo.mx - ((self._SIZE_X*self._window_scale)//2)
        dir_y = inputo.my - ((self._SIZE_Y*self._window_scale)//2)
        dir_inten = np.sqrt(dir_x**2 + dir_y**2)
        dir_x, dir_y = dir_x/dir_inten, dir_y/dir_inten
        self.sprite.rotation = np.degrees(np.arctan2(dir_y, dir_x)*(-1) + (np.pi/2))
        if acc_x_ow == None or acc_y_ow == None:
            acc_x, acc_y = 0, 0
            if inputo.rg:
                acc_x = 8*delta_t
            if inputo.le:
                acc_x = -8*delta_t
            if inputo.up:
                acc_y = 8*delta_t
            if inputo.dw:
                acc_y = -8*delta_t
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
        spr_x, spr_y = self.pos_x - cam_x, self.pos_y - cam_y
        touch = False
        for obstacle in obstacles.values():
            if obstacle.x <= spr_x < obstacle.x+256 and obstacle.y <= spr_y < obstacle.y+256:
                touch = True
                break
        if touch:
            self.pos_x -= self.speed_x
            self.pos_y -= self.speed_y
            self.speed_x = 0
            self.speed_y = 0

        self.set_back(dir_x, dir_y)

        self.x, self.y = int(self.pos_x), int(self.pos_y)
    
    def update_sprite(self, cam_x, cam_y):
        self.sprite.set_relative_pos(self.x, self.y, cam_x, cam_y)


class Player:
    def __init__(self, batch, pos_x, pos_y, size_x, size_y, scale, inventory):
        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        self._window_scale = scale
        self.cam_x = int(pos_x) - (size_x//2)
        self.cam_y = int(pos_y) - (size_y//2)
        self.selection = 1
        self.health = 100
        self.death_time = 0
        self.playercar = PlayerCar(batch, pos_x, pos_y, size_x, size_y, scale)
        self.playerwalker = PlayerWalker(batch, pos_x, pos_y, size_x, size_y, scale)
        self.weaponcontrol = WeaponControl(pos_x, pos_y, inventory, batch)
        self.music_folder = "snd/radio-wc"
        self.mplayer = pyglet.media.Player()

    def check_bullet_hit(self, bullet):
        if self.playerwalker.x < bullet.pos_x < self.playerwalker.x+32:
            if self.playerwalker.y < bullet.pos_y < self.playerwalker.y+32:
                self.health -= bullet.damage/4

    def radio(self):
        # Get a list of music files in the folder
        music_files = [f for f in os.listdir(self.music_folder) if f.endswith('.mp3') or f.endswith('.wav')]
        if not music_files:
            print("No music files found in the folder.")
            return

        # Load music into the player
        playlist = [os.path.join(self.music_folder, f) for f in music_files]

        # Shuffle the playlist
        r.shuffle(playlist)

        # Add the music to the player's queue
        for music_file in playlist:
            self.mplayer.queue(pyglet.media.load(music_file))

        # Start playing
        self.mplayer.play()

    def update(self, inputo, delta_t, obstacles):
        if self.health <= 0:
            self.playerwalker.sprite.image = self.playerwalker.m_image
            self.playerwalker.update_sprite(self.cam_x, self.cam_y)
            self.playercar.update_sprite(self.cam_x, self.cam_y)
            self.death_time += delta_t
            return None
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
                    #self.radio()
                if car_dir_inten < 256:
                    car_dir_x, car_dir_y = (car_dir_x/car_dir_inten)*8*delta_t, (car_dir_y/car_dir_inten)*8*delta_t
                    self.playerwalker.update(inputo, delta_t, obstacles, self.cam_x, self.cam_y, car_dir_x, car_dir_y)
                else:
                    self.playerwalker.update(inputo, delta_t, obstacles, self.cam_x, self.cam_y)
            else:
                self.playerwalker.update(inputo, delta_t, obstacles, self.cam_x, self.cam_y)
            self.cam_x = self.playerwalker.x - (self._SIZE_X//2)
            self.cam_y = self.playerwalker.y - (self._SIZE_Y//2)
            if inputo.rclick:
                self.cam_x = self.playerwalker.x + (((inputo.mx//4)-(self._SIZE_X//2))*2) - 160
                self.cam_y = self.playerwalker.y + (((inputo.my//4)-(self._SIZE_Y//2))*2) - 96
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
                self.mplayer.pause()
                self.mplayer.next_source()
            else:
                self.playercar.update(inputo, delta_t, obstacles, self.cam_x, self.cam_y)
            self.cam_x = self.playercar.x - (self._SIZE_X//2)
            self.cam_y = self.playercar.y - (self._SIZE_Y//2)
            if inputo.rclick:
                self.cam_x = self.playercar.x + (((inputo.mx//4)-(self._SIZE_X//2))*2) - 160
                self.cam_y = self.playercar.y + (((inputo.my//4)-(self._SIZE_Y//2))*2) - 96
        self.playercar.update_sprite(self.cam_x, self.cam_y)
        self.playerwalker.update_sprite(self.cam_x, self.cam_y)

        dir_x = inputo.mx - ((self._SIZE_X*self._window_scale)//2)
        dir_y = inputo.my - ((self._SIZE_Y*self._window_scale)//2)

        return self.weaponcontrol.update(self.playerwalker.pos_x, self.playerwalker.pos_y, dir_x, dir_y, inputo, delta_t)
