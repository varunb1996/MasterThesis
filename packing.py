# Idee: objektorientiert

"""
@Author: Karin Havemann
@Date: 28.06.2022
"""

import numpy as np
from numba import jit # Just-In-Time-Compiler
import csv
from abc import ABC, abstractmethod

# eigene Module
from funktionen import *

class Packing(ABC):
    def __init__(self, input):
        """
        Konstruktor zum Erzeugen einer Kugelpackung.

        Eine Kugelpackung entsteht in einem Raum mit den Seiten x, y und z. Sie besteht aus maximal n Kugeln, die in
        einer Kugelliste self.spheres gespeichert werden. Die aktuelle Anzahl Kugeln in der Kugelpackung beträgt
        self.countSpheres. self.suffix ist ein (optionaler) Zusatz für die Bezeichnung aller Dateien, die im
        Zusammenhang mit dem Generieren der Kugelpackung erstellt werden.

        :param input: Input - enthält alle Eingabedaten der Datei
        """
        self.x = input._x
        self.y = input._y
        self.z = input._z
        self.suffix = input._suffix
        self.countSpheres = 0 # Zaehlt wie viele Kugeln bereits platziert wurden

        n = self.maxNumOfSpheres()
        self.spheres = np.full((n, 4), -1., dtype=float)

    @abstractmethod
    def maxNumOfSpheres(self):
        """
        Berechnung der max. Anzahl Kugeln in einer Kugelpackung.

        :return: int - max. Anzahl Kugeln in einer Kugelpackung
        """
        pass

    def readCsvFile(self, datei):
        """
        Einlesen einer Kugelliste als csv-Datei.
        Aus einer csv-Datei werden Kugeln (x-, y- und z-Koordinate, Radius) zeilenweise eingelesen.

        :param datei: string - Dateiname der csv-Datei
        :return: [] - Liste aus Kugelpositionen ([x, y, z, r])
        """
        list = []
        with open(datei, "r") as f:
            #f = open(datei, "r")
            reader = csv.reader(f)
            next(reader) # Titelzeile überlesen
            for row in reader:  # zeilenweise einlesen
                x = row[0]
                y = row[1]
                z = row[2]
                r = row[3]
                list.append([x, y, z, r])
        return list

    def writeCsvFile(self, datei):
        """
        Schreiben einer Kugelliste als csv-Datei.
        Alle Positionen (x, y, z) und Radien (r) von Kugeln einer Kugelliste werden zeilenweise in eine csv-Datei
        geschrieben.

        :param datei: string - Dateiname der csv-Datei
        :return: kein Rückgabewert
        """
        with open(datei, "w") as f:
            #f = open(datei, "w")
            writer = csv.writer(f)
            writer.writerow(['x', 'y', 'z', 'radius']) # Titelzeile
            #for row in self.spheres[(self.spheres[:,3] > 0)]: # alle Einträge mit Radius <= 0 sind keine gültigen Kugeln
            for row in self.spheres[:self.countSpheres]:
                writer.writerow(row)

    def initialize(self, datei):
        """
        Kugelpackung wird initialisiert, indem die Kugeln aus der Initialisierungsebene eingelesen und in self.spheres
        gespeichert werden.

        :param datei: string - Dateiname der csv-Datei, die die Kugeln der Initialisierungsebene enthält
        :return: kein Rückgabewert
        """
        list = self.readCsvFile(datei)
        self.countSpheres = len(list)
        self.spheres[:len(list)] = np.asarray(list)

# Hilfsmethoden
@jit(nopython=True)
def lineDistance(rv1, sv1, rv2, sv2):
    """
    Berechnung des Abstands zwischen 2 Geraden im R^3.
    Geraden:
    g1 : x = sv1 + a * rv1
    g2 : x = sv2 + b * rv2

    :param rv1: np.array([x, y, z], dtype=float) - Richtungsvektor Gerade 1
    :param sv1: np.array([x, y, z], dtype=float) - Stützvektor Gerade 1
    :param rv2: np.array([x, y, z], dtype=float) - Richtungsvektor Gerade 2
    :param sv2: np.array([x, y, z], dtype=float) - Stützvektor Gerade 2
    :return: float - Abstand zwischen g1 und g2
    """
    u = np.cross(rv1, rv2)
    a = np.linalg.norm(u)
    # TODO: Fehlerbehandlung: Kreuzprodukt ist Nullvektor --> Geraden parallel
    d = np.absolute(np.dot(sv1 - sv2, u)) / a
    return d

@jit(nopython=True)
def sphereDistance(sphere1, sphere2):
    """
    Berechnung des Abstands zwischen 2 Kugeln.
    Der Abstand zwischen 2 Kugeln ist der minimale Abstand ihrer Oberflächen.

    :param sphere1: np.array([x, y, z, r], dtype=float) - Kugel 1 mit x-, y-, z-Koordinate und Radius r
    :param sphere2: np.array([x, y, z, r], dtype=float) - Kugel 2 mit x-, y-, z-Koordinate und Radius r
    :return: Abstand zwischen Kugel 1 und 2
    """
    dist = np.linalg.norm(sphere1[:3] - sphere2[:3]) - (sphere1[3] + sphere2[3])
    return dist

@jit(nopython=True)
def pointDistance(point1, point2):
    """
    Berechnung Abstand zwischen 2 Punkten im R^3.

    :param point1: np.array([x, y, z], dtype=float) - Punkt 1
    :param point2: np.array([x, y, z], dtype=float) - Punkt 2
    :return: Abstand zwischen Punkt 1und 2
    """
    dist = np.linalg.norm(point1 - point2)
    return dist

@jit(nopython=True)
def pocketPossible(k1, k2, k3, r4_max, r4_min):
    """
    Ermittlung, ob die Berechnung einer neuen Kugelposition anhand der drei bereits platzierten Kugeln k1, k2, k3
    möglich ist.

    :param k1: np.array([x, y, z, r], dtype=float) - Kugel 1
    :param k2: np.array([x, y, z, r], dtype=float) - Kugel 2
    :param k3: np.array([x, y, z, r], dtype=float) - Kugel 3
    :param r4_max: float - minimaler Radius einer zu platzierenden Kugel
    :param r4_min: float - maximaler Radius einer zu platzierenden Kugel
    :return: Boolean - True, wenn Berechnung möglich, sonst false
    """
    paare = [(k1, k2), (k2, k3), (k1, k3)]
    n = np.cross(k1[:3] - k2[:3], k3[:3] - k2[:3])

    for paar in paare:
        k1 = paar[0]
        k2 = paar[1]
        d1 = np.linalg.norm(k2[:3] - k1[:3])
        d2 = k1[3] + r4_max
        d3 = k2[3] + r4_max

        #if d1 == 0 or d2 == 0:
        #    print(k1, k2, k3, r4_max)
        if (np.power(d1, 2) + np.power(d2, 2) - np.power(d3, 2)) / (2 * d1 * d2) > 1:
            return False
        a = np.linalg.norm(k1[:3] - k2[:3])
        b = np.linalg.norm(k2[:3] - k3[:3])
        c = np.linalg.norm(k1[:3] - k3[:3])
        success, x1, x2 = pqformel(a, b, c, k1[3], k2[3], k3[3])
        #if radikand(r4_max, a, b, c, k1[3], k2[3], k3[3]) < 0 and radikand(r4_min, a, b, c, k1[3], k2[3], k3[3]) < 0:
        #    return False
        r_mitte = (r4_max + r4_min) / 2
        radikand_mitte = radikand(r_mitte, a, b, c, k1[3], k2[3], k3[3])
        if success and ((x1 > 0 and x1 < r4_max) or (x2 > 0 and x2 < r4_max)) or radikand_mitte > 0:
            return True
        else:
            return False

