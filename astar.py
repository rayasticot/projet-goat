"""
Module pour le calcul de chemin dans une grille en utilisant l'algorithme A*.
"""

import numpy as np


def calculate_h(x, y, goal_x, goal_y):
    """
    Calcule la distance heuristique entre deux points.

    Parameters
    ----------
    x : int
        Position x du point actuel.
    y : int
        Position y du point actuel.
    goal_x : int
        Position x du point de destination.
    goal_y : int
        Position y du point de destination.

    Returns
    -------
    float
        La distance heuristique entre les deux points.
    """

    return np.sqrt((x - goal_x)**2 + (y - goal_y)**2)


class Cell:
    """
    Classe représentant une cellule dans la grille pour l'algorithme A*.
    """

    def __init__(self, x, y, g, goal_x, goal_y, parent, h=None):
        """
        Initialise une cellule dans la grille.

        Parameters
        ----------
        x : int
            Position x de la cellule.
        y : int
            Position y de la cellule.
        g : int
            Coût du chemin du point de départ à cette cellule.
        goal_x : int
            Position x du point de destination.
        goal_y : int
            Position y du point de destination.
        parent : Cell
            Cellule parente de cette cellule.
        h : float, optional
            Distance heuristique entre cette cellule et la destination. 
            The default is None.

        Returns
        -------
        None.
        """

        self.x = x
        self.y = y
        self.g = g
        self.h = h
        if h == None:
            self.h = calculate_h(x, y, goal_x, goal_y)
        self.f = self.g+self.h
        self.parent = parent

    def __repr__(self):
        """
        Représentation textuelle de la cellule.

        Returns
        -------
        str
            La position de la cellule suivie de sa cellule parente.
        """

        return str(self.x)+", "+str(self.y)+"\n"+str(self.parent)


def get_last_two_cells(cell):
    """
    Renvoie les deux dernières cellules dans le chemin de la cellule donnée.

    Parameters
    ----------
    cell : Cell
        Cellule à partir de laquelle remonter pour trouver les deux dernières cellules.

    Returns
    -------
    tuple
        Un tuple contenant les deux dernières cellules dans le chemin.
    """

    try:
        cell0 = cell
        while 1:
            cell1 = cell0.parent
            cell2 = cell1.parent
            if cell2 == None:
                return cell0, cell1
            cell0 = cell0.parent
    except TypeError:
        return None


def find_smallest(liste):
    """
    Trouve l'indice du plus petit élément dans une liste de cellules.

    Parameters
    ----------
    liste : list
        Liste de cellules.

    Returns
    -------
    int
        L'indice du plus petit élément dans la liste.
    """

    smallest = 0
    for i, cell in enumerate(liste):
        if cell.f < liste[smallest].f:
            smallest = i
    return smallest


def inside(grid, x, y):
    """
    Vérifie si les coordonnées spécifiées sont à l'intérieur de la grille.

    Parameters
    ----------
    grid : numpy.ndarray
        Grille de la carte.
    x : int
        Coordonnée x.
    y : int
        Coordonnée y.

    Returns
    -------
    bool
        True si les coordonnées sont à l'intérieur de la grille, False sinon.
    """

    if 0 <= x < len(grid):
        if 0 <= y < len(grid[0]):
            return True
    return False


def find_path(grid, x1, y1, x2, y2):
    """
    Trouve le chemin optimal entre deux points dans la grille.

    Parameters
    ----------
    grid : numpy.ndarray
        Grille représentant la carte.
    x1 : int
        Position x du point de départ.
    y1 : int
        Position y du point de départ.
    x2 : int
        Position x du point de destination.
    y2 : int
        Position y du point de destination.

    Returns
    -------
    Cell or bool
        La cellule représentant le chemin optimal s'il est trouvé, False sinon.
    """

    closedl = np.zeros((len(grid), len(grid[0])))
    openl = [Cell(x1, y1, 0, None, None, None, 0)]
    opena = np.full((len(grid), len(grid[0])), float('inf'))

    while len(openl) > 0:
        q = openl.pop(find_smallest(openl))
        closedl[q.x][q.y] = True
        nexts = (
            Cell(q.x, q.y-1, q.g+1, x2, y2, q), Cell(q.x+1, q.y, q.g+1, x2, y2, q),
            Cell(q.x, q.y-1, q.g+1, x2, y2, q), Cell(q.x-1, q.y, q.g+1, x2, y2, q),
            Cell(q.x+1, q.y-1, q.g+1.4142135623730951, x2, y2, q), Cell(q.x+1, q.y+1, q.g+1.4142135623730951, x2, y2, q),
            Cell(q.x-1, q.y+1, q.g+1.4142135623730951, x2, y2, q), Cell(q.x-1, q.y-1, q.g+1.4142135623730951, x2, y2, q)
        )
        for cell in nexts:
            #print(cell)
            if cell.x == x2 and cell.y == y2:
                return cell
            if inside(grid, cell.x, cell.y) and not grid[cell.x][cell.y] and not closedl[cell.x][cell.y]:
                if opena[cell.x][cell.y] == float('inf') or opena[cell.x][cell.y] > cell.f:
                    #print("b")
                    opena[cell.x][cell.y] = cell.f
                    openl.append(cell)
            #print("a")
    return False


if __name__ == "__main__":
    # TEST
    grid = np.zeros((5, 4))
    grid[0][2] = 1
    grid[1][2] = 1
    grid[2][2] = 1
    grid[2][1] = 1
    grid[4][3] = 1
    """
    grid = np.array((
            (0, 0, 0, 0, 0),
            (0, 0, 1, 0, 0),
            (1, 1, 1, 0, 0),
            (0, 0, 0, 0, 1)
        )
    )
    """
    #print(grid[2][0])
    print(find_path(grid, 0, 0, 0, 3))
