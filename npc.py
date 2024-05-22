"""
Module de gestion des personnages non-joueurs (NPC) comprenant les marcheurs et les véhicules.
"""

import pyglet
import random
import numpy as np
from worldsprite import WorldSprite
from player import Bullet
from inventory import Weapon, WEAPON_MODELS
from city import City, cities
from inventory import GroundItemManager, BulletBox
import astar


NPC_IMAGES = [pyglet.image.load("img/npc0.png"), pyglet.image.load("img/npc1.png"), pyglet.image.load("img/npc2.png"), pyglet.image.load("img/npc3.png"), pyglet.image.load("img/vendeur.png")]
for image in NPC_IMAGES:
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
NPC_IMAGES = tuple(NPC_IMAGES)

NPC_MORT_IMAGES = [pyglet.image.load("img/npc0_m.png"), pyglet.image.load("img/npc1_m.png"), pyglet.image.load("img/npc2_m.png"), pyglet.image.load("img/npc3_m.png"), pyglet.image.load("img/vendeur_m.png")]
for image in NPC_MORT_IMAGES:
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
NPC_MORT_IMAGES = tuple(NPC_MORT_IMAGES)

NPC_CARS = [pyglet.image.load("img/van.png"),]
for image in NPC_CARS:
    image.anchor_x = image.width // 2
    image.anchor_y = image.height // 2
NPC_CARS = tuple(NPC_CARS)


BULLETS_TYPES = ("9mm", "7.62mm", "20mm")


class NpcWalker:
    """
    Classe pour gérer les personnages non-joueurs (NPC) marcheurs.
    """
    def __init__(self, x, y, health, npctype, weapon, incar, batch):
        """
        Initialise un NPC marcheur.

        Parameters
        ----------
        x : float
            Position horizontale du NPC.
        y : float
            Position verticale du NPC.
        health : int
            Points de vie du NPC.
        npctype : int
            Type du NPC.
        weapon : Weapon
            Arme du NPC.
        incar : bool
            Indique si le NPC est dans un véhicule.
        batch : pyglet.graphics.Batch
            Groupe de batch pyglet pour l'affichage.

        Returns
        -------
        None.
        """
        self.x = x
        self.y = y
        self.npctype = npctype
        self.chosen_image = random.randint(0, 3)
        if self.npctype == 3:
            self.chosen_image = 4
        self.sprite = WorldSprite(batch=batch, img=NPC_IMAGES[self.chosen_image], x=0, y=0)
        self.stress = 0
        self.speed_objective = 90
        self.health = health
        if weapon != None:
            self.weapon = weapon
        else:
            self.weapon = self.choose_weapon()
        self.incar = incar
        self.last_shot = 0
        self.time_since_load = 0
        self.ideal_objective = self.choose_objective()
        self.objective = self.ideal_objective
        self.dead = False
        self.batch = batch
        self.shot_sound = pyglet.media.load("snd/gun.mp3", streaming=False)

    def choose_weapon(self):
        """
        Choisis aléatoirement une arme pour le NPC.

        Returns
        -------
        Weapon
            Arme choisie.
        """
        if self.npctype == 0 or self.npctype == 3:
            return None
        return Weapon(WEAPON_MODELS[random.randint(0, len(WEAPON_MODELS)-1)], 0, 0, 0, 0, 0)

    def choose_objective(self):
        """
        Choisis aléatoirement un objectif pour le NPC.

        Returns
        -------
        tuple
            Coordonnées de l'objectif (x, y).
        """
        distances = []
        for city in cities:
            distances.append(np.sqrt((self.x-(city.x*256))**2 + (self.y-(city.y*256))**2))
        min_city = distances.index(min(distances))
        return cities[min_city].x*256 + random.uniform(-1, 1)*256, cities[min_city].y*256 + random.uniform(-1, 1)*256

    def check_bullet_hit(self, bullet):
        """
        Vérifie si le NPC a été touché par une balle.

        Parameters
        ----------
        bullet : Bullet
            Balle tirée.

        Returns
        -------
        None.
        """
        if self.x < bullet.pos_x < self.x+32:
            if self.y < bullet.pos_y < self.y+32:
                self.health -= bullet.damage
                self.stress += 1

    def grid_cos_to_pixel(self, grid_x, grid_y, cam_x, cam_y):
        """
        Convertit les coordonnées de la grille en coordonnées pixel.

        Parameters
        ----------
        grid_x : int
            Coordonnée x dans la grille.
        grid_y : int
            Coordonnée y dans la grille.
        cam_x : float
            Position x de la caméra.
        cam_y : float
            Position y de la caméra.

        Returns
        -------
        tuple
            Coordonnées pixel converties (x, y).
        """
        return (256*grid_x) + cam_x - (14*256), (256*grid_y) + cam_y - (15*256)

    def pixel_to_grid_cos(self, x, y, cam_x, cam_y):
        """
        Convertit les coordonnées pixel en coordonnées de la grille.

        Parameters
        ----------
        x : float
            Coordonnée x en pixels.
        y : float
            Coordonnée y en pixels.
        cam_x : float
            Position x de la caméra.
        cam_y : float
            Position y de la caméra.

        Returns
        -------
        tuple
            Coordonnées de la grille (grid_x, grid_y).
        """
        return int((x//256) - (cam_x//256)) + 14, int((y//256) - (cam_y//256)) + 15

    def find_grid_side_from_dir(self, x, y, cam_x, cam_y, dir_x, dir_y):
        """
        Trouve le côté de la grille à partir de la direction donnée.

        Parameters
        ----------
        x : float
            Position x du NPC.
        y : float
            Position y du NPC.
        cam_x : float
            Position x de la caméra.
        cam_y : float
            Position y de la caméra.
        dir_x : float
            Direction x.
        dir_y : float
            Direction y.

        Returns
        -------
        tuple
            Coordonnées de la grille (grid_x, grid_y).
        """
        pos_x, pos_y = x+dir_x, y+dir_y
        while 1:
            pos_x += dir_x
            pos_y += dir_y
            grid_x, grid_y = self.pixel_to_grid_cos(pos_x, pos_y, cam_x, cam_y)
            if 0 <= grid_x < 30 and 0 <= grid_y < 30:
                continue
            else:
                return self.pixel_to_grid_cos(pos_x-dir_x, pos_y-dir_y, cam_x, cam_y)
        return None

    def get_mov_from_dir(self, dir_x, dir_y, delta_t):
        """
        Obtient le mouvement à partir de la direction donnée.

        Parameters
        ----------
        dir_x : float
            Direction x.
        dir_y : float
            Direction y.
        delta_t : float
            Temps écoulé depuis la dernière mise à jour.

        Returns
        -------
        tuple
            Mouvement (mov_x, mov_y).
        """
        mov_x, mov_y = dir_x, dir_y
        self.speed_objective = 90
        if self.stress > 1:
            self.speed_objective = 180
        mov_x *= self.speed_objective*delta_t
        mov_y *= self.speed_objective*delta_t
        return mov_x, mov_y

    def get_mov_to_point(self, x2, y2, obstacle_map, cam_x, cam_y, delta_t):
        """
        Obtient le mouvement vers un point donné.

        Parameters
        ----------
        x2 : float
            Coordonnée x de la destination.
        y2 : float
            Coordonnée y de la destination.
        obstacle_map : array
            Carte des obstacles.
        cam_x : float
            Position x de la caméra.
        cam_y : float
            Position y de la caméra.
        delta_t : float
            Temps écoulé depuis la dernière mise à jour.

        Returns
        -------
        tuple
            Mouvement (mov_x, mov_y).
        """
        dir_x, dir_y = x2-self.x, y2-self.y
        dir_inten = np.sqrt(dir_x**2+dir_y**2)
        dir_x, dir_y = dir_x/dir_inten, dir_y/dir_inten
        mov_x, mov_y = self.get_mov_from_dir(dir_x, dir_y, delta_t)
        grid_x, grid_y = self.pixel_to_grid_cos(self.x+mov_x, self.y+mov_y, cam_x, cam_y)
        #print(grid_x, grid_y)
        if not obstacle_map[grid_x][grid_y]:
            return mov_x, mov_y
        grid_x2, grid_y2 = self.find_grid_side_from_dir(self.x, self.y, cam_x, cam_y, dir_x, dir_y)
        cell0, cell1 = astar.get_last_two_cells(astar.find_path(obstacle_map, grid_x, grid_y, grid_x2, grid_y2))
        dest_x1, dest_y1 = self.pixel_to_grid_cos(cell0.x, cell0.y, cam_x, cam_y)
        dest_x2, dest_y2 = self.pixel_to_grid_cos(cell1.x, cell1.y, cam_x, cam_y)
        dir_x, dir_y = dest_x2-dest_x1, dest_y2
        dir_inten = np.sqrt(dir_x**2+dir_y**2)
        dir_x, dir_y = dir_x/dir_inten, dir_y/dir_inten
        mov_x, mov_y = self.get_mov_from_dir(dir_x, dir_y, delta_t)
        return mov_x, mov_y

    def update_sprite(self, cam_x, cam_y):
        """
        Met à jour le sprite du NPC.

        Parameters
        ----------
        cam_x : float
            Position x de la caméra.
        cam_y : float
            Position y de la caméra.

        Returns
        -------
        None.
        """
        self.sprite.rotation = np.degrees(np.arctan2(self.mov_y, self.mov_x)*(-1) + (np.pi/2))
        self.sprite.set_relative_pos(self.x, self.y, cam_x, cam_y)
    
    def get_distance_to_player(self, player_x, player_y):
        """
        Obtient la distance jusqu'au joueur.

        Parameters
        ----------
        player_x : float
            Position x du joueur.
        player_y : float
            Position y du joueur.

        Returns
        -------
        float
            Distance jusqu'au joueur.
        """
        dist_x = self.x-player_x
        dist_y = self.y-player_y
        return np.sqrt(dist_x**2 + dist_y**2)

    def weapon_update(self, player_x, player_y, delta_t):
        """
        Met à jour l'agissement au niveau des armes du NPC.

        Parameters
        ----------
        player_x : float
            Position x du joueur.
        player_y : float
            Position y du joueur.
        delta_t : float
            Temps écoulé depuis la dernière mise à jour.

        Returns
        -------
        Bullet or None
            Balle tirée ou None.
        """
        self.last_shot += delta_t
        self.time_since_load += delta_t
        if self.weapon == None:
            return None
        if self.weapon.loaded <= 0:
            if self.time_since_load > self.weapon.loadtime:
                self.weapon.loaded = self.weapon.capacity
                if self.weapon.loaded > 0:
                    self.time_since_load = 0
            return None
        if self.time_since_load < self.weapon.loadtime:
            return None
        if self.last_shot > 1/self.weapon.rate:
            self.shot_sound.play()
            self.last_shot = 0
            self.weapon.loaded -= 1
            dir_x, dir_y = player_x-self.x, player_y-self.y
            dir_inten = np.sqrt(dir_x**2+dir_y**2)
            dir_x, dir_y = dir_x/dir_inten, dir_y/dir_inten
            return Bullet(self.x, self.y, dir_x, dir_y, self.weapon.reach, self.weapon.damage, self.weapon.accuracy, self.batch)
        return None

    def update(self, player_x, player_y, cam_x, cam_y, obstacle_map, delta_t):
        """
        Met à jour le NPC.

        Parameters
        ----------
        player_x : float
            Position x du joueur.
        player_y : float
            Position y du joueur.
        cam_x : float
            Position x de la caméra.
        cam_y : float
            Position y de la caméra.
        obstacle_map : array
            Carte des obstacles.
        delta_t : float
            Temps écoulé depuis la dernière mise à jour.

        Returns
        -------
        Bullet or None
            Balle tirée ou None.
        """
        if self.health <= 0:
            self.sprite.image = NPC_MORT_IMAGES[self.chosen_image]
            self.update_sprite(cam_x, cam_y)
            return None
        match(self.npctype):
            case 1:
                if self.health < 25 or self.stress == 0:
                    self.objective = self.ideal_objective
                else:
                    if self.get_distance_to_player(player_x, player_y) > 200:
                        self.objective = (player_x, player_y)
                    else:
                        self.objective = self.ideal_objective
            case 2:
                if self.health < 25:
                    self.objective = self.ideal_objective
                else:
                    if self.get_distance_to_player(player_x, player_y) > 200:
                        self.objective = (player_x, player_y)
                    else:
                        self.objective = self.ideal_objective
            case 3:
                if self.get_distance_to_player(player_x, player_y) > 200:
                    self.objective = (player_x, player_y)
                else:
                    self.objective = self.ideal_objective
        self.mov_x, self.mov_y = self.get_mov_to_point(self.objective[0], self.objective[1], obstacle_map, cam_x, cam_y, delta_t)
        self.x += self.mov_x
        self.y += self.mov_y
        self.update_sprite(cam_x, cam_y)
        if self.npctype == 1 and self.stress > 0:
            return self.weapon_update(player_x, player_y, delta_t)
        if self.npctype == 2:
            return self.weapon_update(player_x, player_y, delta_t)
        return None


class NpcManager:
    """
    Classe pour gérer les NPC.
    """
    def __init__(self, batch):
        """
        Initialise le gestionnaire de NPC.

        Parameters
        ----------
        batch : pyglet.graphics.Batch
            Groupe de batch pyglet pour l'affichage.

        Returns
        -------
        None.
        """
        self.batch = batch
        self.npcs = [NpcWalker(0, 0, 100, 0, Weapon(WEAPON_MODELS[0], 0, 0, 0, 0, 0), False, self.batch)]
        #self.npcs_cars = []
        self.scream_sound = pyglet.media.load("snd/scream.mp3", streaming=False)
        self.scream_player = pyglet.media.Player()
    
    def update(self, bullet_manager, item_manager, player_x, player_y, heal_player, cam_x, cam_y, obstacle_map, bullet_list_player, bullet_list_ennemy, delta_t):
        """
        Met à jour le gestionnaire de NPC.

        Parameters
        ----------
        bullet_manager : BulletManager
            Gestionnaire de balles.
        item_manager : ItemManager
            Gestionnaire d'objets.
        player_x : float
            Position x du joueur.
        player_y : float
            Position y du joueur.
        cam_x : float
            Position x de la caméra.
        cam_y : float
            Position y de la caméra.
        obstacle_map : array
            Carte des obstacles.
        bullet_list_player : list
            Liste des balles du joueur.
        bullet_list_ennemy : list
            Liste des balles ennemies.
        delta_t : float
            Temps écoulé depuis la dernière mise à jour.

        Returns
        -------
        float
            Argent total collecté.
        """
        new_npcs = []
        total_money = 0
        for npc in self.npcs:
            grid_x, grid_y = npc.pixel_to_grid_cos(npc.x, npc.y, cam_x, cam_y)
            if not 0 <= grid_x < 30 or not 0 <= grid_y < 30:
                continue
            new_npcs.append(npc)
            if npc.npctype == 3:
                total_money += item_manager.check_npc_seller(npc.x, npc.y, npc.health)
            for bullet in bullet_list_player:
                npc.check_bullet_hit(bullet)
                if npc.health <= 0 and not npc.dead:
                    self.scream_player.queue(self.scream_sound)
                    self.scream_player.play()
                    npc.dead = True
                    heal_player(20)
                    item_manager.add_item(npc.weapon, npc.x, npc.y)
                    if npc.npctype == 3:
                        item_manager.add_item(BulletBox(BULLETS_TYPES[random.randint(0, 2)], random.randint(1, 20)), npc.x, npc.y)
            bullet = npc.update(player_x, player_y, cam_x, cam_y, obstacle_map, delta_t)
            if bullet != None:
                bullet_manager.add_bullet(bullet, False)
        self.npcs = new_npcs
        return total_money
