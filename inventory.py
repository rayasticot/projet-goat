"""
Module contenant des classes et des fonctions pour gérer l'inventaire et les objets du jeu.
"""

import pyglet
import numpy as np
from dataclasses import dataclass
import json
from worldsprite import WorldSprite


ITEM_IMAGES = (
    pyglet.image.load("img/items/ak.png"),
    pyglet.image.load("img/items/9mm.png"),
    pyglet.image.load("img/items/7.62mm.png"),
    pyglet.image.load("img/items/Cyma.png"),
    pyglet.image.load("img/items/Famas.png"),
    pyglet.image.load("img/items/Glock17.png"),
    pyglet.image.load("img/items/M4A1.png"),
    pyglet.image.load("img/items/MP7.png"),
    pyglet.image.load("img/items/P229.png"),
    pyglet.image.load("img/items/20mm.png"),
)
BULLET_IMAGE = {
    "9mm": 1,
    "7.62mm": 2,
    "20mm": 9
}


class Item:
    """
    Classe représentant un objet dans l'inventaire
    """
    def __init__(self, iteminfo, itype, image_index, name, desc, weight):
        """
        Initialise un objet avec les informations fournies.
        
        Parameters
        ----------
        iteminfo : dict, optional
            Informations sur l'objet.
            Le format doit inclure les clés "itype" (type d'objet), 
            "image" (index de l'image), "name" (nom), "desc" (description)
            et "weight" (poids). Par défaut, None.
        itype : int
            Type d'objet.
        image_index : int
            Index de l'image de l'objet.
        name : str
            Nom de l'objet.
        desc : str
            Description de l'objet.
        weight : int
            Poids de l'objet.

        Returns
        -------
        None

        """

        if not iteminfo:
            self.itype = itype
            self.sprite = WorldSprite(img=ITEM_IMAGES[image_index])
            self.name = name
            self.desc = desc
            self.weight = weight
            return
        self.itype = iteminfo["itype"]
        self.sprite = WorldSprite(img=ITEM_IMAGES[iteminfo["image"]])
        self.name = iteminfo["name"]
        self.desc = iteminfo["desc"]
        self.weight = iteminfo["weight"]


class WeaponModel:
    """
    Classe représentant un modèle d'arme.
    """
    def __init__(self, modelinfo):
        """
        Initialise un modèle d'arme avec les informations fournies.

        Parameters
        ----------
        modelinfo : dict
            Informations sur le modèle de l'arme.

        Returns
        -------
        None

        """
        self.image_index = modelinfo["image"]
        self.name = modelinfo["name"]
        self.desc = modelinfo["desc"]
        self.weight = modelinfo["weight"]
        self.capacity = modelinfo["capacity"]
        self.loadtime = modelinfo["loadtime"]
        self.bullet_type = modelinfo["bullet_type"]
        self.rate = modelinfo["rate"]
        self.reach = modelinfo["reach"]
        self.accuracy = modelinfo["accuracy"]
        self.damage = modelinfo["damage"]
        self.price = modelinfo["price"]


class Weapon(Item):
    """
    Classe représentant une arme.
    """
    def __init__(self, model, loaded, rate_dmg, reach_dmg, accuracy_dmg, damage_dmg):
        """
        Initialise une arme avec les informations fournies.

        Parameters
        ----------
        model : WeaponModel
            Modèle de l'arme.
        loaded : bool
            Charge de l'arme.
        rate_dmg : float
            Dégâts de taux.
        reach_dmg : float
            Dégâts de portée.
        accuracy_dmg : float
            Dégâts de précision.
        damage_dmg : float
            Dégâts sur les dégâts.

        Returns
        -------
        None
    
        """
        super().__init__(None, 0, model.image_index, model.name, model.desc, model.weight)
        self.capacity = model.capacity
        self.loadtime = model.loadtime
        self.bullet_type = model.bullet_type
        self.rate = model.rate - model.rate*rate_dmg
        self.reach = model.reach - model.reach*reach_dmg
        self.accuracy = model.accuracy + model.accuracy*accuracy_dmg
        self.damage = model.damage - model.damage*damage_dmg
        self.loaded = loaded
        self.price = model.price


class BulletBox(Item):
    """
    Classe représentant une boîte de munitions.

    """
    def __init__(self, btype, ammount):
        """
        Initialise une boîte de munitions avec les informations fournies.

        Parameters
        ----------
        btype : str
            Type de munitions.
        ammount : int
            Quantité de munitions.

        Returns
        -------
        None

        """
        super().__init__(None, 4, BULLET_IMAGE[btype], btype, "", 0)
        self.btype = btype
        self.ammount = ammount
        self.price = 100


def load_weapons_models(filename):
    """
    Charge les modèles d'armes à partir d'un fichier JSON.

    Parameters
    ----------
    filename : str
        Nom du fichier JSON contenant les modèles d'armes.

    Returns
    -------
    tuple
        Tuple des modèles d'armes.

    """
    models = []
    with open(filename, "r") as file:
        data = json.load(file)
        for model in data["models"]:
            models.append(WeaponModel(model))
    return tuple(models)


WEAPON_MODELS = load_weapons_models("item/weapon_models.json")


class GridItem(pyglet.gui.WidgetBase):
    """
    Classe pour représenter un élément de grille d'objets.

    """
    def __init__(self, x, y, empty, empty_t, filled, filled_t, inventory, item_index, i_type, batch, group=None):
        """
        Initialise un élément de grille.

        Parameters
        ----------
        x : int
            Position x de l'élément de grille.
        y : int
            Position y de l'élément de grille.
        empty : pyglet.image.AbstractImage
            Image de l'élément vide.
        empty_t : pyglet.image.AbstractImage
            Image de l'élément vide en surbrillance.
        filled : pyglet.image.AbstractImage
            Image de l'élément rempli.
        filled_t : pyglet.image.AbstractImage
            Image de l'élément rempli en surbrillance.
        inventory : Inventory
            Instance de l'inventaire auquel appartient cet élément de grille.
        item_index : int
            Index de l'élément dans l'inventaire.
        i_type : int
            Type de l'élément.
        batch : pyglet.graphics.Batch
            Groupe de batch pyglet pour l'affichage.
        group : pyglet.graphics.Group, optional
            Groupe de rendu auquel cet élément appartient. Le default est None.

        Returns
        -------
        None.

        """
        super().__init__(x, y, empty.width, empty.height)
        self._empty = empty
        self._empty_t = empty_t
        self._filled = filled
        self._filled_t = filled_t
        self._batch = batch
        self._user_group = group
        bg_group = pyglet.graphics.Group(order=0, parent=group)
        self._sprite = pyglet.sprite.Sprite(self._empty_t, x, y, batch=batch, group=bg_group)
        self._inventory = inventory
        self.item_index = item_index
        self.i_type = i_type
        self._enabled = False
        self.presence = False

    def mouse_press(self, x, y, buttons, modifiers):
        """
        Méthode appelée lorsqu'un clic de souris est effectué.

        Parameters
        ----------
        x : int
            Position x du clic.
        y : int
            Position y du clic.
        buttons : int
            Boutons de souris pressés.
        modifiers : int
            Modificateurs de souris pressés.

        Returns
        -------
        bool
            Vrai si l'élément a été pressé avec succès, Faux sinon.

        """
        if not self._enabled or not self._check_hit(x, y):
            return
        self._inventory.item_pressed(self.item_index, self.i_type)

    def mouse_release(self, x, y, buttons, modifiers):
        """
        Méthode appelée lorsqu'un clic de souris est relâché.

        Parameters
        ----------
        x : int
            Position x du relâchement du clic.
        y : int
            Position y du relâchement du clic.
        buttons : int
            Boutons de souris relâchés.
        modifiers : int
            Modificateurs de souris relâchés.

        Returns
        -------
        bool
            Vrai si l'élément a été relâché avec succès, Faux sinon.

        """
        if not self._enabled or not self._check_hit(x, y):
            return False
        self._inventory.item_released(self.item_index, self.i_type)
        return True

    def mouse_motion(self, x, y, dx, dy):
        """
        Méthode appelée lorsqu'un mouvement de souris est détecté.

        Parameters
        ----------
        x : int
            Position x actuelle du curseur de la souris.
        y : int
            Position y actuelle du curseur de la souris.
        dx : int
            Déplacement en x du curseur de la souris.
        dy : int
            Déplacement en y du curseur de la souris.

        Returns
        -------
        None.

        """
        if self._check_hit(x, y):
            if self.presence:
                self._sprite.image = self._filled
            else:
                self._sprite.image = self._empty
        else:
            if self.presence:
                self._sprite.image = self._filled_t
            else:
                self._sprite.image = self._empty_t

    def update(self, inputo, scale, press, release):
        """
        Met à jour l'élément de grille.

        Parameters
        ----------
        inputo : InputObject
            Objet d'entrée contenant les informations sur l'entrée utilisateur.
        scale : float
            Échelle de l'affichage.
        press : bool
            Indique si un clic de souris a été pressé.
        release : bool
            Indique si un clic de souris a été relâché.

        Returns
        -------
        bool
            Vrai si un élément a été relâché avec succès, Faux sinon.

        """
        self.mouse_motion(inputo.mx//scale, inputo.my//scale, 0, 0)
        if press:
            self.mouse_press(inputo.mx//scale, inputo.my//scale, None, None)
        if release:
            return self.mouse_release(inputo.mx//scale, inputo.my//scale, None, None)
        return False
    
    def enable(self, value):
        """
        Active ou désactive l'élément de grille.

        Parameters
        ----------
        value : bool
            Valeur d'activation de l'élément.

        Returns
        -------
        None.

        """
        self._enabled = value
        self._sprite.visible = value


class ArrowButton(pyglet.gui.WidgetBase):
    """
    Classe pour représenter un bouton fléché.

    """
    def __init__(self, x, y, image, image_t, batch, group=None):
        """
        Initialise un bouton fléché.

        Parameters
        ----------
        x : int
            Position x du bouton.
        y : int
            Position y du bouton.
        image : pyglet.image.AbstractImage
            Image du bouton.
        image_t : pyglet.image.AbstractImage
            Image du bouton en surbrillance.
        batch : pyglet.graphics.Batch
            Groupe de batch pyglet pour l'affichage.
        group : pyglet.graphics.Group, optional
            Groupe de rendu auquel cet élément appartient. Le default est None.

        Returns
        -------
        None.

        """
        super().__init__(x, y, image.width, image.height)
        self.image = image
        self.image_t = image_t
        bg_group = pyglet.graphics.Group(order=0, parent=group)
        self._sprite = pyglet.sprite.Sprite(self.image_t, x, y, batch=batch, group=bg_group)
        self._batch = batch
        self._user_group = group
        self.enabled = True

    def mouse_press(self, x, y, buttons, modifiers):
        """
        Méthode appelée lorsqu'un clic de souris est pressé.

        Parameters
        ----------
        x : int
            Position x du clic.
        y : int
            Position y du clic.
        buttons : int
            Boutons de souris pressés.
        modifiers : int
            Modificateurs de souris pressés.

        Returns
        -------
        bool
            Vrai si le bouton a été pressé avec succès, Faux sinon.

        """
        if not self.enabled or not self._check_hit(x, y):
            return False
        return True

    def mouse_motion(self, x, y, dx, dy):
        """
        Méthode appelée lorsqu'un mouvement de souris est détecté.

        Parameters
        ----------
        x : int
            Position x actuelle du curseur de la souris.
        y : int
            Position y actuelle du curseur de la souris.
        dx : int
            Déplacement en x du curseur de la souris.
        dy : int
            Déplacement en y du curseur de la souris.

        Returns
        -------
        None.

        """
        if self._check_hit(x, y):
            self._sprite.image = self.image
        else:
            self._sprite.image = self.image_t

    def update(self, inputo, scale):
        """
        Met à jour le bouton fléché.

        Parameters
        ----------
        inputo : InputObject
            Objet d'entrée contenant les informations sur l'entrée utilisateur.
        scale : float
            Échelle de l'affichage.

        Returns
        -------
        bool
            Vrai si le bouton a été pressé avec succès, Faux sinon.

        """
        self.mouse_motion(inputo.mx//scale, inputo.my//scale, 0, 0)
        if inputo.lclick:
            if self.mouse_press(inputo.mx//scale, inputo.my//scale, 0, 0):
                inputo.lclick = 0
                return True
        return False


class Inventory:
    """
    Classe pour gérer l'inventaire du joueur.
    """
    def __init__(self, size_x, size_y, item_manager):
        """
        Initialise l'inventaire du joueur.

        Parameters
        ----------
        size_x : int
            Largeur de la fenêtre.
        size_y : int
            Hauteur de la fenêtre.
        item_manager : ItemManager
            Gestionnaire d'objets.

        Returns
        -------
        None.
        """
        self.batch = pyglet.graphics.Batch()

        self.arms = [None]*3
        self.equi = [None]*4
        self.cons = [None]*16
        self.keys = [None]*16
        self.bullets = {
            "9mm": 300,
            "7.62mm": 100,
            "20mm": 100
        }
        self.hand = [None]*4

        self.widget_arms = [None]*3
        self.widget_equi = [None]*4
        self.widget_cons = [None]*14
        self.widget_keys = [None]*14
        self.sprite_bullets = [None]*len(self.bullets)
        self.text_bullets = [None]*len(self.bullets)
        self.widget_hand = [None]*4

        self.indicator_label = pyglet.text.Label("", font_name="Times New Roman", font_size=24, x=size_x/2, y=size_y-24, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))

        self.item_manager = item_manager

        self._SIZE_X = size_x
        self._SIZE_Y = size_y
        #self.cadre = pyglet.image.load("img/gui/cadre_item.png")
        #self.cadre_r = pyglet.image.load("img/gui/cadre_item_rempli.png")
        #self.g_cadre = pyglet.image.load("img/gui/gros_cadre.png")
        #self.g_cadre_r = pyglet.image.load("img/gui/gros_cadre_rempli.png")
        self.m_cadre = pyglet.image.load("img/gui/moyen_cadre.png")
        self.m_cadre_t = pyglet.image.load("img/gui/moyen_cadre_t.png")
        self.m_cadre_r = pyglet.image.load("img/gui/moyen_cadre_rempli.png")
        self.m_cadre_r_t = pyglet.image.load("img/gui/moyen_cadre_rempli_t.png")

        self.arrow_right = pyglet.image.load("img/gui/arrow_right.png")
        self.arrow_right_t = pyglet.image.load("img/gui/arrow_right_t.png")
        self.arrow_left = pyglet.image.load("img/gui/arrow_left.png")
        self.arrow_left_t = pyglet.image.load("img/gui/arrow_left_t.png")

        self.empty = pyglet.image.load("img/gui/empty.png")
        self.fond_img = pyglet.image.load("img/gui/fond.png")

        self.fond = pyglet.sprite.Sprite(img=self.fond_img, x=0, y=0, batch=self.batch)
        self.fond.opacity = 200

        self.active = False
        self.page = 0
        self.cursor_index = 0
        self.last_lclick = 0
        self.pressed_item_type = None
        self.pressed_item_index = None
        self.release_item_type = None
        self.release_item_index = None
        self.create_widgets()

    def switch_page(self, ammount):
        """
        Change la page de l'inventaire.

        Parameters
        ----------
        ammount : int
            Quantité à ajouter ou soustraire à la page actuelle.

        Returns
        -------
        None.
        """

        self.page += ammount
        self.page %= 5

    def create_widgets(self):
        """
        Crée les widgets de l'inventaire.

        Returns
        -------
        None.
        """

        center_x = self._SIZE_X/2
        center_y = self._SIZE_Y/2
        self.ARMS_BE_X = center_x - 32*len(self.widget_arms)
        self.ARMS_BE_Y = center_y - 32
        for i in range(len(self.widget_arms)):
            self.widget_arms[i] = GridItem(self.ARMS_BE_X+i*64, self.ARMS_BE_Y, self.m_cadre, self.m_cadre_t, self.m_cadre_r, self.m_cadre_r_t, self, i, 0, self.batch)

        self.EQUI_BE_X = center_x - 32*len(self.widget_equi)
        self.EQUI_BE_Y = center_y - 32
        for i in range(len(self.widget_equi)):
            self.widget_equi[i] = GridItem(self.EQUI_BE_X+i*64, self.EQUI_BE_Y, self.m_cadre, self.m_cadre_t, self.m_cadre_r, self.m_cadre_r_t, self, i, 1, self.batch)

        self.CONS_BE_X = center_x - 32*7
        self.CONS_BE_Y = center_y - 32*2
        for i in range(len(self.widget_cons)):
            self.widget_cons[i] = GridItem(self.CONS_BE_X+(i%7)*64, self.CONS_BE_Y+(i//7)*64, self.m_cadre, self.m_cadre_t, self.m_cadre_r, self.m_cadre_r_t, self, i, 2, self.batch)

        for i in range(len(self.widget_keys)):
            self.widget_keys[i] = GridItem(self.CONS_BE_X+(i%7)*64, self.CONS_BE_Y+(i//7)*64, self.empty, self.empty, self.m_cadre_r, self.m_cadre_r_t, self, i, 3, self.batch)

        self.HAND_BE_X = center_x - 64*len(self.widget_equi) + 32
        for i in range(len(self.widget_hand)):
            self.widget_hand[i] = GridItem(self.HAND_BE_X+i*128, 8, self.m_cadre, self.m_cadre_t, self.m_cadre_r, self.m_cadre_r_t, self, i, 5, self.batch)

        self.hand_text0 = pyglet.text.Label("arme", font_name="Times New Roman", font_size=12, x=self.HAND_BE_X+32, y=84, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))
        self.hand_text1 = pyglet.text.Label("objet", font_name="Times New Roman", font_size=12, x=self.HAND_BE_X+128+31, y=84, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))
        self.hand_text2 = pyglet.text.Label("armure", font_name="Times New Roman", font_size=12, x=self.HAND_BE_X+256+31, y=84, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))
        self.hand_text3 = pyglet.text.Label("casque", font_name="Times New Roman", font_size=12, x=self.HAND_BE_X+384+31, y=84, anchor_x="center", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))

        self.arrow_button_r = ArrowButton(self._SIZE_X-68, center_y-32, self.arrow_right, self.arrow_right_t, self.batch)
        self.arrow_button_l = ArrowButton(4, center_y-32, self.arrow_left, self.arrow_left_t, self.batch)

        i = 0
        for key, value in self.bullets.items():
            self.text_bullets[i] = pyglet.text.Label(key+": "+str(value), font_name="Times New Roman", font_size=32, x=128, y=self._SIZE_Y-64-32*i, anchor_x="left", anchor_y="center", batch=self.batch, color=(142, 0, 58, 255))
            self.sprite_bullets[i] = pyglet.sprite.Sprite(img=ITEM_IMAGES[BULLET_IMAGE[key]], x=80, y=self._SIZE_Y-83-32*i, batch=self.batch)
            self.sprite_bullets[i].scale_x = 1/2
            self.sprite_bullets[i].scale_y = 1/2
            i += 1


    def find_free(self, inv):
        """
        Trouve le premier emplacement vide dans l'inventaire.

        Parameters
        ----------
        inv : list
            Liste représentant une catégorie d'objets dans l'inventaire.

        Returns
        -------
        int or None
            Index de l'emplacement vide trouvé, ou None s'il n'y a pas d'emplacement vide.
        """

        for i, item in enumerate(inv):
            if item == None:
                return i
        return None


    def list_from_type(self, i_type):
        """
        Renvoie la liste correspondant au type d'objet spécifié.

        Parameters
        ----------
        i_type : int
            Type d'objet (0: armes, 1: équipement, 2: objets de consommation, 3: clés, 5: objets tenus en main).

        Returns
        -------
        list
            Liste correspondant au type d'objet spécifié.
        """

        match i_type:
            case 0:
                return self.arms
            case 1:
                return self.equi
            case 2:
                return self.cons
            case 3:
                return self.keys
            case 5:
                return self.hand


    def pickup(self, item) -> bool: # Vrai si ramassé sans problème, Faux si pas ramassé
        """
        Ramasse un objet et l'ajoute à l'inventaire.

        Parameters
        ----------
        item : Item
            Objet à ramasser.

        Returns
        -------
        bool
            True si l'objet a été ramassé avec succès, False sinon.
        """
        if 0 <= item.itype <= 3:
            item_inv = None
            match item.itype:
                case 0:
                    item_inv = self.arms
                case 1:
                    item_inv = self.equi
                case 2:
                    item_inv = self.cons
                case 3:
                    item_inv = self.keys
            free = self.find_free(item_inv)
            if free == None:
                return False
            item_inv[free] = item
            item_inv[free].sprite.batch = self.batch
            return True
        if item.itype == 4:
            self.bullets[item.btype] += item.ammount
            #item_inv[free].sprite.batch = self.batch
            return True
        return False


    def throwaway(self, inv, index, manager, x, y):
        """
        Jette un objet de l'inventaire sur le sol.

        Parameters
        ----------
        inv : list
            Liste représentant une catégorie d'objets dans l'inventaire.
        index : int
            Index de l'objet à jeter.
        manager : ItemManager
            Gestionnaire d'objets au sol.
        x : int
            Position x où jeter l'objet.
        y : int
            Position y où jeter l'objet.

        Returns
        -------
        None.
        """

        if inv[index] == None:
            return None
        item = inv[index]
        inv[index] = None
        manager.add_item(item, x, y)


    def finalswitch(self, inv1, index1, inv2, index2):
        """
        Échange deux objets entre deux catégories d'objets de l'inventaire.

        Parameters
        ----------
        inv1 : list
            Liste représentant une catégorie d'objets dans l'inventaire.
        index1 : int
            Index de l'objet dans la première liste.
        inv2 : list
            Liste représentant une autre catégorie d'objets dans l'inventaire.
        index2 : int
            Index de l'objet dans la deuxième liste.

        Returns
        -------
        None.
        """

        item1 = inv1[index1]
        item2 = inv2[index2]
        inv1[index1] = item2
        inv2[index2] = item1


    def switchup(self, inv1, index1, inv2, index2):
        """
        Échange deux objets entre deux catégories d'objets de l'inventaire.

        Parameters
        ----------
        inv1 : list
            Liste représentant une catégorie d'objets dans l'inventaire.
        index1 : int
            Index de l'objet dans la première liste.
        inv2 : list
            Liste représentant une autre catégorie d'objets dans l'inventaire.
        index2 : int
            Index de l'objet dans la deuxième liste.

        Returns
        -------
        None.
        """

        if inv1 != inv2:
            if inv1 == self.hand:
                match inv2:
                    case self.arms:
                        if index1 == 0:
                            self.finalswitch(inv1, index1, inv2, index2)
                        return
                    case self.cons:
                        if index1 == 1:
                            self.finalswitch(inv1, index1, inv2, index2)
                        return
                    case self.equi:
                        if index1 == 2 or index1 == 3:
                            self.finalswitch(inv1, index1, inv2, index2)
                        return
                return
            if inv2 == self.hand:
                match inv1:
                    case self.arms:
                        if index2 == 0:
                            self.finalswitch(inv1, index1, inv2, index2)
                        return
                    case self.cons:
                        if index2 == 1:
                            self.finalswitch(inv1, index1, inv2, index2)
                        return
                    case self.equi:
                        if index2 == 2 or index2 == 3:
                            self.finalswitch(inv1, index1, inv2, index2)
                        return
                return
            return
        if inv1 == self.keys or inv1 == self.hand:
            return
        self.finalswitch(inv1, index1, inv2, index2)


    def take_bullets(self, btype, ammount):
        """
        Prend des munitions de l'inventaire.

        Parameters
        ----------
        btype : str
            Type de munitions.
        ammount : int
            Quantité de munitions à prendre.

        Returns
        -------
        int
            La quantité de munitions effectivement prises.
        """

        if self.bullets[btype] >= ammount:
            self.bullets[btype] -= ammount
            return ammount
        to_give = self.bullets[btype]
        self.bullets[btype] = 0
        return to_give


    def item_pressed(self, index, i_type):
        """
        Indique qu'un objet a été appuyé.

        Parameters
        ----------
        index : int
            Index de l'objet.
        i_type : int
            Type de l'objet.

        Returns
        -------
        None.
        """

        self.released_item_index = None
        self.released_item_type = None
        self.pressed_item_index = index
        self.pressed_item_type = i_type


    def item_released(self, index, i_type):
        """
        Indique qu'un objet a été relâché.

        Parameters
        ----------
        index : int
            Index de l'objet.
        i_type : int
            Type de l'objet.

        Returns
        -------
        None.
        """

        if self.pressed_item_index != None and self.pressed_item_type != None:
            self.switchup(self.list_from_type(self.pressed_item_type), self.pressed_item_index, self.list_from_type(i_type), index)


    def place_items(self, inputo, scale):
        """
        Place les objets dans l'inventaire en fonction de la page actuelle.

        Parameters
        ----------
        inputo : Input
            Entrées du joueur.
        scale : float
            Échelle d'affichage.

        Returns
        -------
        None.
        """

        e_arms, e_equi, e_cons, e_keys, e_bull = False, False, False, False, False
        match self.page:
            case 0:
                e_arms = True
            case 1:
                e_equi = True
            case 2:
                e_cons = True
            case 3:
                e_keys = True
            case 4:
                e_bull = True

        for i in range(len(self.arms)):
            if self.arms[i] == None:
                continue
            if i == self.pressed_item_index and self.pressed_item_type == 0:
                self.arms[i].sprite.x = (inputo.mx//scale)-32
                self.arms[i].sprite.y = (inputo.my//scale)-32
            else:
                self.arms[i].sprite.x = self.ARMS_BE_X+i*64
                self.arms[i].sprite.y = self.ARMS_BE_Y
            self.arms[i].sprite.visible = e_arms

        for i in range(len(self.equi)):
            if self.equi[i] == None:
                continue
            if i == self.pressed_item_index and self.pressed_item_type == 1:
                self.equi[i].sprite.x = (inputo.mx//scale)-32
                self.equi[i].sprite.y = (inputo.my//scale)-32
            else:
                self.equi[i].sprite.x = self.EQUI_BE_X+i*64
                self.equi[i].sprite.y = self.EQUI_BE_Y
            self.equi[i].sprite.visible = e_equi

        for i in range(len(self.cons)):
            if self.cons[i] == None:
                continue
            if i == self.pressed_item_index and self.pressed_item_type == 2:
                self.cons[i].sprite.x = (inputo.mx//scale)-32
                self.cons[i].sprite.y = (inputo.my//scale)-32
            else:
                self.cons[i].sprite.x = self.CONS_BE_X+(i%7)*64
                self.cons[i].sprite.y = self.CONS_BE_Y+(i//7)*64
            self.cons[i].sprite.visible = e_cons

        for i in range(len(self.keys)):
            if self.keys[i] == None:
                continue
            if i == self.pressed_item_index and self.pressed_item_type == 3:
                self.keys[i].sprite.x = (inputo.mx//scale)-32
                self.keys[i].sprite.y = (inputo.my//scale)-32
            else:
                self.keys[i].sprite.x = self.CONS_BE_X+(i%7)*64
                self.keys[i].sprite.y = self.CONS_BE_Y+(i//7)*64
            self.keys[i].sprite.visible = e_keys

        for i in range(len(self.hand)):
            if self.hand[i] == None:
                continue
            if i == self.pressed_item_index and self.pressed_item_type == 5:
                self.hand[i].sprite.x = (inputo.mx//scale)-32
                self.hand[i].sprite.y = (inputo.my//scale)-32
            else:
                self.hand[i].sprite.x = self.HAND_BE_X+i*128
                self.hand[i].sprite.y = 8
            self.hand[i].sprite.visible = True


    def update(self, inputo, scale, player_back_x, player_back_y):
        """
        Met à jour l'inventaire en fonction des entrées du joueur.

        Parameters
        ----------
        inputo : Input
            Entrées du joueur.
        scale : float
            Échelle d'affichage.
        player_back_x : int
            Position x du joueur.
        player_back_y : int
            Position y du joueur.

        Returns
        -------
        None.
        """

        press, release = 0, 0
        if self.last_lclick != inputo.lclick:
            if inputo.lclick:
                press = 1
                self.pressed_item_index = None
                self.pressed_item_type = None
            else:
                release = 1
                self.released_item_index = None
                self.released_item_type = None
            self.last_lclick = inputo.lclick
        e_arms, e_equi, e_cons, e_keys, e_bull = False, False, False, False, False
        match self.page:
            case 0:
                e_arms = True
                self.indicator_label.text = "armes"
            case 1:
                e_equi = True
                self.indicator_label.text = "équipement"
            case 2:
                e_cons = True
                self.indicator_label.text = "objets"
            case 3:
                e_keys = True
                self.indicator_label.text = "objets clés"
            case 4:
                e_bull = True
                self.indicator_label.text = "munitions"
        released_in_case = False
        for i, widget in enumerate(self.widget_arms):
            if self.arms[i]:
                widget.presence = True
            else:
                widget.presence = False
            widget.enable(e_arms)
            if not released_in_case:
                released_in_case = widget.update(inputo, scale, press, release)
        for i, widget in enumerate(self.widget_equi):
            if self.equi[i]:
                widget.presence = True
            else:
                widget.presence = False
            widget.enable(e_equi)
            if not released_in_case:
                released_in_case = widget.update(inputo, scale, press, release)
        for i, widget in enumerate(self.widget_cons):
            if self.cons[i]:
                widget.presence = True
            else:
                widget.presence = False
            widget.enable(e_cons)
            if not released_in_case:
                released_in_case = widget.update(inputo, scale, press, release)
        for i, widget in enumerate(self.widget_keys):
            if self.keys[i]:
                widget.presence = True
            else:
                widget.presence = False
            widget.enable(e_keys)
            if not released_in_case:
                released_in_case = widget.update(inputo, scale, press, release)
        for i, widget in enumerate(self.widget_hand):
            if self.hand[i]:
                widget.presence = True
            else:
                widget.presence = False
            widget.enable(True)
            if not released_in_case:
                released_in_case = widget.update(inputo, scale, press, release)
        if not released_in_case and release:
            if self.pressed_item_type != None and self.pressed_item_index != None:
                self.throwaway(self.list_from_type(self.pressed_item_type), self.pressed_item_index, self.item_manager, player_back_x, player_back_y)
        i = 0
        for key, value in self.bullets.items():
            self.sprite_bullets[i].visible = e_bull
            self.text_bullets[i].visible = e_bull
            self.text_bullets[i].text = key+": "+str(value)
            i += 1
        if self.arrow_button_l.update(inputo, scale):
            self.switch_page(-1)
        if self.arrow_button_r.update(inputo, scale):
            self.switch_page(1)
        
        if release:
            self.pressed_item_index = None
            self.pressed_item_type = None
        if press:
            self.released_item_index = None
            self.released_item_type = None
        
        self.place_items(inputo, scale)


class GroundItem:
    """
    Classe pour représenter un objet dans le monde.
    """

    def __init__(self, item, pos_x, pos_y):
        """
        Initialise un objet dans le monde.

        Parameters
        ----------
        item : Item
            Objet dans le monde.
        pos_x : int
            Position x de l'objet dans le monde.
        pos_y : int
            Position y de l'objet dans le monde.

        Returns
        -------
        None.
        """

        self.item = item
        self.pos_x = pos_x
        self.pos_y = pos_y


class GroundItemManager:
    """
    Classe pour gérer les objets dans le monde.
    """
    def __init__(self, batch):
        """
        Initialise le gestionnaire des objets dans le monde.

        Parameters
        ----------
        batch : pyglet.graphics.Batch
            Groupe de batch pyglet pour l'affichage des objets.

        Returns
        -------
        None.
        """

        self.batch = batch
        self.groud_item_list = []#[GroundItem(Weapon(WEAPON_MODELS[0], 0, 0, 0, 0, 0), 100*256, -300*256)]
        #self.groud_item_list[0].item.sprite.batch = self.batch
        self.pickup_sound = pyglet.media.load("snd/pickup.mp3", streaming=False)
        self.pickup_player = pyglet.media.Player()

    def add_item(self, item, x, y):
        """
        Ajoute un objet dans le monde.

        Parameters
        ----------
        item : objet
            L'objet à ajouter.
        x : int
            Position x de l'objet.
        y : int
            Position y de l'objet.

        Returns
        -------
        None.
        """

        if item == None:
            return
        self.groud_item_list.append(GroundItem(item, x, y))
        self.groud_item_list[-1].item.sprite.batch = self.batch

    def grid_cos_to_pixel(self, grid_x, grid_y, cam_x, cam_y):
        """
        Convertit les coordonnées de la grille en coordonnées de pixels.

        Parameters
        ----------
        grid_x : int
            Position x dans la grille.
        grid_y : int
            Position y dans la grille.
        cam_x : int
            Position x de la caméra.
        cam_y : int
            Position y de la caméra.

        Returns
        -------
        tuple
            La position convertie en pixels (x, y).
        """

        return (256*grid_x) + cam_x - (14*256), (256*grid_y) + cam_y - (15*256)

    def pixel_to_grid_cos(self, x, y, cam_x, cam_y):
        """
        Convertit les coordonnées de pixels en coordonnées de la grille.

        Parameters
        ----------
        x : int
            Position x en pixels.
        y : int
            Position y en pixels.
        cam_x : int
            Position x de la caméra.
        cam_y : int
            Position y de la caméra.

        Returns
        -------
        tuple
            La position convertie dans la grille (x, y).
        """

        return int((x//256) - (cam_x//256)) + 14, int((y//256) - (cam_y//256)) + 15

    def check_npc_seller(self, npc_x, npc_y, npc_health):
        """
        Vérifie les achats avec un PNJ.

        Parameters
        ----------
        npc_x : int
            Position x du PNJ.
        npc_y : int
            Position y du PNJ.
        npc_health : int
            Vie du PNJ.

        Returns
        -------
        int
            Le montant total de l'argent obtenu grâce aux achats du PNJ.
        """
        new_item_list = []
        total_money = 0
        for item in self.groud_item_list:
            if item.pos_x <= npc_x < item.pos_x+64 and item.pos_y <= npc_y < item.pos_y+64 and npc_health > 0:
                total_money += item.item.price
                item.item.sprite.delete()
                continue
            new_item_list.append(item)
        self.groud_item_list = new_item_list
        return total_money

    def update(self, inventory, player_x, player_y, player_selection, cam_x, cam_y, delta_t):
        """
        Met à jour les objets au sol.

        Parameters
        ----------
        inventory : Inventory
            L'inventaire du joueur.
        player_x : int
            Position x du joueur.
        player_y : int
            Position y du joueur.
        player_selection : bool
            Sélection du joueur.
        cam_x : int
            Position x de la caméra.
        cam_y : int
            Position y de la caméra.
        delta_t : float
            Temps écoulé depuis la dernière mise à jour.

        Returns
        -------
        None.
        """
        new_item_list = []
        for item in self.groud_item_list:
            grid_x, grid_y = self.pixel_to_grid_cos(item.pos_x, item.pos_y, cam_x, cam_y)
            if not 1 <= grid_x < 29 or not 1 <= grid_y < 29:
                continue
            item.item.sprite.set_relative_pos(item.pos_x, item.pos_y, cam_x, cam_y)
            if item.pos_x <= player_x < item.pos_x+64 and item.pos_y <= player_y < item.pos_y+64:
                self.pickup_player.queue(self.pickup_sound)
                self.pickup_player.play()
                if player_selection:
                    if inventory.pickup(item.item):
                        continue
            new_item_list.append(item)
        self.groud_item_list = new_item_list
