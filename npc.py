import pyglet
import numpy
from worldsprite import WorldSprite
from player import Bullet


NPC_IMAGES = (pyglet.image.load("img/mec.png"),)
NPC_CARS = (pyglet.image.load("img/van.png"),)


class NpcWalker:
    def __init__(self, x, y, health, npctype, incar, batch):
        self.x = x
        self.y = y
        self.npctype = npctype
        self.sprite = WorldSprite(batch=batch, img=NPC_IMAGES[0], x=0, y=0)
        self.objective = self.get_objective() # INTEGRER COORDONNÉES D'UNE VILLE SUR LA MAP
        self.stress = 0
        self.speed_objective = 1.5
        self.health = health
        self.incar = incar

    def get_objective(self):
        return (0, 0)

    def check_bullet_hit(self, bullet):
        if self.x < bullet.pos_x < self.x+32:
            if self.y < bullet.pos_y < self.y+32:
                self.health -= bullet.damage
                self.stress += 1

    def get_dir_to_point(self, x2, y2, obstacle_map):
        return (0.7071067811865476, 0.7071067811865476)

    def update_sprite(self, cam_x, cam_y):
        self.sprite.set_relative_pos(self.x, self.y, cam_x, cam_y)

    def update(self, player_x, player_y, cam_x, cam_y, obstacle_map, delta_t):
        match(self.npctype):
            case 0:
                self.dir_x, self.dir_y = self.get_dir_to_point(self.objective[0], self.objective[1], obstacle_map)
                self.speed_objective = 1.5
                if self.stress > 1:
                    self.speed_objective = 3
                self.x += self.dir_x*self.speed_objective
                self.y += self.dir_y*self.speed_objective
        self.update_sprite(cam_x, cam_y)


class NpcCar:
    def __init__(self, x, y, occupant, batch):
        self.x = x
        self.y = y
        self.npctype = npctype
        self.occupant = occupant
        self.sprite = WorldSprite(batch=batch, img=NPC_CARS[0], x=0, y=0)

    def update_sprite(self, cam_x, cam_y):
        self.sprite.set_relative_pos(self.x, self.y, cam_x, cam_y)

    def update(self, cam_x, cam_y, obstacle_map):
        if occupant != None:
            match(self.occupant.npctype):
                case 0:
                    pass
        self.update_sprite(cam_x, cam_y)

class NpcManager:
    def __init__(self, batch):
        self.batch = batch
        self.npcs = [NpcWalker(0, 0, 100, 0, False, self.batch)]
        self.npcs_cars = []
    
    def update(self, player_x, player_y, cam_x, cam_y, obstacle_map, bullet_list_player, bullet_list_ennemy, delta_t):
        for npc in self.npcs:
            for bullet in bullet_list_player:
                npc.check_bullet_hit(bullet)
            for bullet in bullet_list_ennemy:
                npc.check_bullet_hit(bullet)
            npc.update(player_x, player_y, cam_x, cam_y, obstacle_map, delta_t)
