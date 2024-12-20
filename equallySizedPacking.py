
"""
@Author: Karin Havemann
@Date: 04.04.2022
"""
import numpy as np
from numba import jit # Just-In-Time-Compiler
from random import randrange
import time
import sys
import traceback
# eigene Module
from packing import *
from input import Input


np.seterr(all='raise')

class EquallySizedPacking(Packing):
    def __init__(self, input):
        """
        Konstruktor zum Erzeugen einer Kugelpackung mit Kugeln gleicher Größe, die einander berühren.

        Die Kugeln einer EquallySizedPacking haben alle denselben Radius self.radius. Jede Kugel kann entfernte
        Nachbarn haben, deren Indizes in self.distantNeighbors gespeichert werden. Entfernte Nachbarn sind Kugeln, deren
        Abstand (zwischen den Mittelpunkten) kleiner als 4 * self.radius ist.
        Eine Kugelpackung hat eine Liste self.pockets an möglichen Kugelpositionen (:= Pockets).

        :param input: Input - enthält alle Eingabedaten der Datei
        """
        self.radius = input._radius
        Packing.__init__(self, input)

        n = self.maxNumOfSpheres()
        # max. Anzahl entfernte Nachbarn pro Kugel
        self.maxNeighbors = 50 ##TODO: wie viele entfernte Nachbarn kann eine Kugel maximal haben?
        # Feld, das in Zeile i die Indizes der entfernten Nachbarkugeln zu Kugel i speichert
        self.distantNeighbors = np.full((n, self.maxNeighbors), -1., dtype=int)
        # max. Anzahl Pockets in einem Raum
        self._numOfPockets = int(2 * self.x * self.y / (np.pi * np.power(self.radius, 2))) ##TODO: wie viele Pockets max.?
        # Feld aus Pockets
        # jede Zeile: [x, y, z, r, k1, k2, k3]
        #   x-, y- und z-Koordinate des Mittelpunkts der Pocket und Radius r
        #   k1, k2, k3: 3 bereits platzierte Kugeln, aus denen die Pocket erzeugt wurde
        self.pockets = np.zeros((self._numOfPockets, 7), dtype=float)
        self.countPockets = 0 # Zähler, wie viele Pockets belegt sind

    # overriding abstract method
    def maxNumOfSpheres(self):
        """
        Berechnet max. Anzahl Kugeln in der Kugelpackung.

        Eine dichteste Kugelpackung gleichgroßer, sich berührender Kugeln hat eine Packungsdichte von ca. 74 %.
        Die Packungsdichte beschreibt das Verhältnis aus mit Kugeln ausgefülltem Volumen und Gesamtvolumen des Raums.
        Da in einer EquallySizedPacking Kugeln gleicher Größe so platziert werden, dass sie einander berühren,
        können sie max. die Packungsdichte einer dichtesten Kugelpackung erreichen, also 74 %.

        Das Raumvolumen beträgt in der Theorie x*y*z. In der Praxis werden aber Kugeln im Raum platziert solange ihr
        Mittelpunkt innerhalb des Raumes liegt. Das Raumvolumen beträgt daher an jeder Kantenlänge 2 zusätzöliche Radien.

        :return: int - max. Anzahl Kugeln in einer EquallySizedPacking
        """
        # Raumvolumen v_r:
        # bei Platzierung ist entscheidend, ob Mittelpunkt im Raum liegt
        # --> Raumvolumen praktisch um 2*radius in jeder Dimension (x, y, z) größer
        v_r = (self.x + 2 * self.radius) * (self.y + 2 * self.radius) * (self.z + 2 * self.radius)
        v_s = (4/3) * np.pi * np.power(self.radius, 3) # Volumen einer Kugel
        p = 0.74 # Packungsdichte dichteste Kugelpackung
        n = (p * v_r) / v_s # max. Anzahl Kugeln
        return int(n + 1)

    # def nextInNeighbors(self, i):
    #     """
    #     Gibt Index für nächstes freies Feld zum Abspeichern einer Nachbarkugel der Kugel i.
    #
    #     Für die Kugel mit Index i werden die Indizes der entfernten Nachbarn im Feld self.distantNeighbors gespeichert.
    #     Alle freien Felder, die kein Nachbarindex enthalten sind mit dem Wert -1 initialisiert.
    #     Die Methode gibt den Index des ersten freien Feldes (< 0) von self.distantNeighbors[i] zurück.
    #
    #     :param i: int - Kugel mit Index i aus der Kugelliste self.spheres
    #     :return: int - Index 1. Feld mit noch nicht belegter Nachbarkugel für Kugel i
    #     """
    #     # nächsten freien Platz in Nachbarsliste finden für die Kugel i
    #     for j in range(self.maxNeighbors):
    #         if self.distantNeighbors[i, j] < 0: # alle nicht freien Werte sind durch Werte >= 0 belegt
    #             return j
    #     raise ValueError("kein freies Feld für weitere Nachbarkugel")
    #     #return -1

    def pocketValid(self, pocket):
        """
        Prüft, ob die übergebene Pocket gültig ist.

        Eine Pocket ist gültig, wenn der Mittelpunkt innerhalb des Raumes mit den Seitenlängen x, y und z liegt
        und sich die Pocket nicht mit einer bereits existierenden Kugeln überschneidet.

        Eine
        :param pocket: np.array(7, dtype=float) - [x, y, z, r, nb1, nb2, nb3]
            x, y und z: Position Mittelpunkt Pocket
            r: Radius Pocket
            nb1, nb2, nb3: (int) Index Nachbarkugeln aus denen, die Pocket erzeugt wurde
        :return: bool - true, wenn Pocket gültig
        """
        if (pocket[0] < 0) or (pocket[0] > self.x) or (pocket[1] < 0) or (pocket[1] > self.y) or (pocket[2] < 0) or (pocket[2] > self.z):
            return False # Mittelpunkt der Pocket liegt nicht im Raum
        # Überprüfung: Überschneidung Pocket mit einer bereits platzierten Kugel
        # Entfernte Nachbarkugeln der 3 Erzeugendenkugeln durch gehen
        # Aus den 3 Erzeugendenkugeln wurde eine neue Pocket berechnet
        for i in range(4,7):
            index = int(pocket[i]) # Index der Erzeugendenkugel
            try:
                #last = self.nextInNeighbors(index)
                last = nextInNeighbors(self.distantNeighbors[index])
            except ValueError as ex:
                ex_type, ex_value, ex_traceback = sys.exc_info()
                print("Exception message : %s" % ex_value)
                print("Erhöhe self.maxNeighbors im Konstruktor von EquallySizedPacking")
                exit()
            for j in range(last):
                neighbor = self.distantNeighbors[index, j] # Index entfernte Nachbarkugel
                if sphereDistance(pocket[:4], self.spheres[neighbor]) < -0.0001:
                    return False
        return True

    def sortPocketList(self):
        """
        Sortieren der Pocketliste aufsteigend  nach der z-Koordinate.

        Alle Pockets werden aufsteigend nach ihrer z-Koordinate sortiert, sodass die Pocket mit der niedrigsten
        z-Koordinate an Position self.pockets[0] steht.
        Alle nicht belegten Pockets ([-1, -1, -1, -1, -1, -1, -1]) befinden sich am Ende des Feldes.

        :return: kein Rückgabewert
        """
        sortedPockets = self.pockets[:,2].argsort() # Indizes der sortierten Pockets
        numOfEmptyPockets = self._numOfPockets-self.countPockets # Anzahl nicht belegter Pockets in self.pockets
        emptyPockets = sortedPockets[:numOfEmptyPockets].copy() # Array der Indizes nicht belegten Pockets
        # Verschieben der Indizes der belegten Pockets an den Beginn von sortedPockets
        sortedPockets[:self.countPockets] = sortedPockets[numOfEmptyPockets:]
        sortedPockets[self.countPockets:] = emptyPockets
        self.pockets = self.pockets[sortedPockets] # Umsortierung

    def initPocketList(self):
        """
        Initialisierung der Pocketsliste.

        Anhand der Kugeln in der Initialisierungsebene werden alle möglichen Pockets berechnet und in self.pockets
        eingetragen.

        :return: kein Rückgabewert
        """
        # self.distantNeighbors initialisieren:
        # für jede Kugel aus der Initialisierungsebene werden entfernte Nachbarkugeln gespeichert
        for i in range(self.countSpheres):
            for j in range(i+1, self.countSpheres):
                if pointDistance(self.spheres[i,:3], self.spheres[j,:3]) <= 4 * self.radius:
                    try:
                        #free = self.nextInNeighbors(i)
                        free = nextInNeighbors(self.distantNeighbors[i])
                    except ValueError as ex:
                        ex_type, ex_value, ex_traceback = sys.exc_info()
                        print("Exception message : %s" % ex_value)
                        print("Erhöhe self.maxNeighbors im Konstruktor von EquallySizedPacking")
                        exit()
                    #free = self.nextInNeighbors(i)
                    self.distantNeighbors[i, free] = j
                    # Nachbarn symmetrisch abspeichern
                    #free = self.nextInNeighbors(j)
                    try:
                        #free = self.nextInNeighbors(j)
                        free = nextInNeighbors(self.distantNeighbors[j])
                    except ValueError as ex:
                        ex_type, ex_value, ex_traceback = sys.exc_info()
                        print("Exception message : %s" % ex_value)
                        print("Erhöhe self.maxNeighbors im Konstruktor von EquallySizedPacking")
                        exit()
                    self.distantNeighbors[j, free] = i

        # aus entfernten Nachbarkugeln Pockets berechnen
        for i in range(self.countSpheres):
            try:
                #last = self.nextInNeighbors(i)
                last = nextInNeighbors(self.distantNeighbors[i])
            except ValueError as ex:
                ex_type, ex_value, ex_traceback = sys.exc_info()
                print("Exception message : %s" % ex_value)
                print("Erhöhe self.maxNeighbors im Konstruktor von EquallySizedPacking")
                exit()
            #last = self.nextInNeighbors(i)
            for j in range(last):
                for k in range(j+1, last):
                    nb1 = self.distantNeighbors[i, j] # Index entfernter Nachbar 1 Kugel i
                    nb2 = self.distantNeighbors[i, k] # Index entfernter Nachbar 2 Kugel i
                    if (nb1 > i) and (nb2 > i): # sonst wurde Pocket bereits in frueherem Schleifendurchlauf berechnet
                        if pocketPossibleAlt(self.spheres[i], self.spheres[nb1], self.spheres[nb2]):
                            temp = calculatePocket(self.spheres[i], self.spheres[nb1], self.spheres[nb2])
                            pocket = np.full(7, -1.)
                            pocket[4:7] = np.array([i, nb1, nb2]) # Erzeugendenkugeln der Pocket
                            pocket[:4] = temp # Position und Radius der Pocket
                            if self.pocketValid(pocket):
                                self.pockets[self.countPockets] = pocket
                                self.countPockets += 1
        self.sortPocketList()
        #self.pockets = sortPocketList(self.pockets, self.countPockets, self._numOfPockets)

    def updatePocketList(self):
        """
        Pocketliste aktualisieren nachdem in der niedrigsten Pocket eine Kugel platziert wurde.

        Beim Aktualisieren der Pocketliste müssen alle Pockets gelöscht werden, die sich mit der gerade platzierten
        Kugel überschneiden. Zudem müssen alle neuen Pockets berechnet werden, die sich aus der geraden platzierten
        Kugel und ihren entfernten Nachbarkugeln ergeben.

        :return: kein Rückgabewert
        """
        kugelId = self.countSpheres - 1 # Index der neusten platzierten Kugel

        # überschneidende Pockets löschen
        n = self.countPockets
        for i in range(n):
            if sphereDistance(self.spheres[kugelId], self.pockets[i,:4]) < -0.0001:
                self.pockets[i] = np.full(7, -1)
                self.countPockets -= 1
        self.sortPocketList()
        #self.pockets = sortPocketList(self.pockets, self.countPockets, self._numOfPockets)

        # Nachbarn der neuen Kugel bestimmen (Variante 1: Teilliste durchgehen)
        # Bedingungen, die erfüllt sein müssen, damit Kugel entfernte Nachbarkugel der neuen Kugel sein kann
        dist = (self.spheres[kugelId,3] * 4) * 1.0001 # max. Abstand, damit Kugeln benachbart sein können
        con1 = (self.spheres[:,0] > self.spheres[kugelId,0] - dist) & (self.spheres[:,0] < self.spheres[kugelId,0] + dist)
        con2 = (self.spheres[:,1] > self.spheres[kugelId,1] - dist) & (self.spheres[:,1] < self.spheres[kugelId,1] + dist)
        con3 = (self.spheres[:,2] > self.spheres[kugelId,2] - dist) & (self.spheres[:,2] < self.spheres[kugelId,2] + dist)
        con4 = (self.spheres[:,0] > 0) & (self.spheres[:,1] > 0) & (self.spheres[:,2] > 0)
        # Anzahl Kugeln, die die Bedingungen (con1 - con3) (nicht) erfüllen
        n = (con1 & con2 & con3 & con4).sum()
        nr = len(self.spheres) - n  # (con1 & con2 & con3).sum() = Anzahl True in Array
        # Indizes der Kugeln, die die Bedingungen (con1 - con3) erfüllen
        indices = (con1 & con2 & con3 & con4).argsort()[nr:]

        # aus potentiellen Nachbarkugeln alle entfernten Nachbarkugeln berechnen
        for i in range(n):
            potNei = indices[i] # Index potentielle Nachbarkugel
            if (pointDistance(self.spheres[kugelId], self.spheres[potNei]) <= (4 * self.radius)) and (potNei != kugelId):

                # last = self.nextInNeighbors(kugelId)
                try:
                    #last = self.nextInNeighbors(kugelId)
                    last = nextInNeighbors(self.distantNeighbors[kugelId])
                except ValueError as ex:
                    ex_type, ex_value, ex_traceback = sys.exc_info()
                    print("Exception message : %s" % ex_value)
                    print("Erhöhe self.maxNeighbors im Konstruktor von EquallySizedPacking")
                    exit()
                self.distantNeighbors[kugelId, last] = potNei
                # Nachbarkugeln symmetrisch abspeichern
                # last = self.nextInNeighbors(potNei)
                try:
                    #last = self.nextInNeighbors(potNei)
                    last = nextInNeighbors(self.distantNeighbors[potNei])
                except ValueError as ex:
                    ex_type, ex_value, ex_traceback = sys.exc_info()
                    print("Exception message : %s" % ex_value)
                    print("Erhöhe self.maxNeighbors im Konstruktor von EquallySizedPacking")
                    exit()
                self.distantNeighbors[potNei, last] = kugelId

        # Nachbarn der neuen Kugel bestimmen (Variante 2: gesamte Liste durchgehen)
        # for i in range(kugelId): # gesamte Kugelliste (außer neue Kugel selbst) nach entfernten Nachbarn durchsuchen
        #     if pointDistance(self.spheres[kugelId], self.spheres[i]) <= (4 * self.radius):
        #         last = self.nextInNeighbors(kugelId)
        #         self.distantNeighbors[kugelId, last] = i
        #         # Nachbarkugeln symmetrisch abspeichern
        #         last = self.nextInNeighbors(i)
        #         self.distantNeighbors[i, last] = kugelId

        # neue Pockets aus Nachbarn der neuen Kugel berechnen
        # last = self.nextInNeighbors(kugelId)
        try:
            #last = self.nextInNeighbors(kugelId)
            last = nextInNeighbors(self.distantNeighbors[kugelId])
        except ValueError as ex:
            ex_type, ex_value, ex_traceback = sys.exc_info()
            print("Exception message : %s" % ex_value)
            print("Erhöhe self.maxNeighbors im Konstruktor von EquallySizedPacking")
            exit()
        for i in range(last):
            for j in range(i+1, last):
                nb1 = self.distantNeighbors[kugelId, i] # Index einer Nachbarkugeln
                nb2 = self.distantNeighbors[kugelId, j] # Index einer weiteren Nachbarkugeln
                if pocketPossibleAlt(self.spheres[kugelId], self.spheres[nb1], self.spheres[nb2]):
                    temp = calculatePocket(self.spheres[kugelId], self.spheres[nb1], self.spheres[nb2])
                    pocket = np.full(7, -1.)
                    pocket[4:7] = np.array([kugelId, nb1, nb2])  # Erzeugendenkugeln der Pocket
                    pocket[:4] = temp  # Position und Radius der Pocket
                    if self.pocketValid(pocket):
                        self.pockets[self.countPockets] = pocket
                        self.countPockets += 1
        self.sortPocketList()
        #self.pockets = sortPocketList(self.pockets, self.countPockets, self._numOfPockets)

    def generatePacking(self):
        """
        Generieren der Kugelpackung.

        Eine Kugelpackung wird generiert, indem die Kugeln der Initialisierungsebene aus einer Datei eingelesen werden
        und alle möglichen Pockets berechnet werden. Dann wird an der Stelle der niedrigsten Pocket eine Kugel
        platziert und die Pocketliste entsprechend aktualisiert. Dieser Vorgang wird solange wiederholt bis der gesamte
        Raum mit Kugeln gefüllt ist und es daher keine freien Pockets mehr gibt.

        :return: kein Rückgabewert
        """
        csvIn = f"../resources/output/{self.x}x{self.y}x{self.z}_{int(self.radius)}_{int(self.radius)}{self.suffix}_initialisierungsebene.csv"
        csvOut = f"../resources/output/{self.x}x{self.y}x{self.z}_{int(self.radius)}_{int(self.radius)}{self.suffix}_kupa.csv"
        self.initialize(csvIn) # Initialisierungsebene einlesen
        self.initPocketList()
        #print(len(self.pockets[(self.pockets[:,3] > 0)]))
        while self.pockets[0,2] > 0: # Solange freie Pockets vorhanden sind
            lowestPoc = self.pockets[0]
            self.spheres[self.countSpheres] = lowestPoc[:4]
            self.countSpheres += 1
            self.updatePocketList()
        self.writeCsvFile(csvOut)

@jit(nopython=True)
def calculatePocket(k1, k2, k3):
        """
        Berechnung Position einer möglichen Pocket aus 3 Kugelpositionen.

        :param k1: np.array([x, y, z, r], dtype=float) - Kugel 1 mit x-, y- und z-Koordinate sowie Radius r
        :param k2: np.array([x, y, z, r], dtype=float) - Kugel 2 mit x-, y- und z-Koordinate sowie Radius r
        :param k3: np.array([x, y, z, r], dtype=float) - Kugel 3 mit x-, y- und z-Koordinate sowie Radius r
        :return: np.array([x, y, z, r], dtype=float) - mögliche Pocket (Position und Radius)
        """
        p12 = (k1[0:3] + k2[0:3]) / 2  # Mittelpunkt zwischen K1 und K2
        p13 = (k1[0:3] + k3[0:3]) / 2  # Mittelpunkt zwischen K1 und K3
        p1p2 = k2[0:3] - k1[0:3]  # Richtungsvektor zwischen K1 und K2
        p1p3 = k3[0:3] - k1[0:3]  # Richtungsvektor zwischen K1 und K3

        r = k1[3]  # Radius aller Kugeln
        d_p1p13 = np.linalg.norm(p1p3) / 2  # Abstand zwischen K1 und P13
        h13 = np.sqrt((2 * r) ** 2 - d_p1p13 ** 2)  # Abstand zwischen P13 und K4

        n = np.cross(p1p2, p1p3)  # Normalenvektor der Ebene durch P1, P2, P3
        u = np.cross(p1p3, n)  # Richtungsvektor Gerade g1 durch P13 und P0
        v = np.cross(p1p2, n)  # Richtungsvektor Gerade g2 durch P12 und P0

        if lineDistance(u, p13, v, p12) < 0.00001:
            # Gleichungssystem zum Bestimmen der Punkte mit dem kürzesten Abstand zwischen g1 und g2
            A = np.array([[np.dot(u, v), (-1.) * np.dot(v, v)], [np.dot(u, u), (-1.) * np.dot(v, u)]])
            b = np.array([(-1.) * np.dot(p13 - p12, v), (-1.) * np.dot(p13 - p12, u)])
            x = np.linalg.solve(A, b)
            p0 = p13 + x[0] * u
            d_p0p13 = np.linalg.norm(p0 - p13)  # Abstand zwischen P0 und P13
            h = np.sqrt(h13 ** 2 - d_p0p13 ** 2)  # Abstand zwischen P0 und K4
            p41 = p0 + n * (h / np.linalg.norm(n))
            p42 = p0 - n * (h / np.linalg.norm(n))
            pocket = np.full(4, -1.)
            if p41[2] < p42[2]:
                pocket[:3] = p42
            else:
                pocket[:3] = p41
            radius = pointDistance(k1[:3], pocket[:3]) - k1[3]
            pocket[3] = radius
            return pocket

@jit(nopython=True)
def pocketPossibleAlt(k1, k2, k3):
    """
    Berechnet, ob die Pocketberechnung aus 3 Kugeln möglich ist.

    Berechnung, ob eine Kugel so platziert werden kann, dass sie die 3 übergebenen Kugeln berührt bei konstantem Radius.

    :param k1: np.array([x, y, z, r], dtype=float) - Kugel 1 mit x-, y- und z-Koordinate sowie Radius r
    :param k2: np.array([x, y, z, r], dtype=float) - Kugel 2 mit x-, y- und z-Koordinate sowie Radius r
    :param k3: np.array([x, y, z, r], dtype=float) - Kugel 3 mit x-, y- und z-Koordinate sowie Radius r
    :return: bool -
    """
    a = pointDistance(k1[:3], k2[:3])
    b = pointDistance(k2[:3], k3[:3])

    radius = k1[3]
    beta_hat = np.arccos(a / (4 * radius))
    sp = np.dot((k1[:3] - k2[:3]), (k3[:3] - k2[:3]))
    beta = np.arccos(sp / (a * b))

    h = np.sqrt(np.power(2 * radius, 2) - np.power(a / 2, 2))
    if h < radius:
        return False
    determinante = np.power(2 * radius, 2) + np.power(b, 2) - 4 * radius * b * np.cos(
        np.absolute(beta - beta_hat))
    # d = np.sqrt(np.power(2 * radius, 2) + np.power(b, 2) - 4 * radius * b * np.cos(np.absolute(beta - beta_hat)))
    if ((determinante > 0) and (np.sqrt(determinante) <= (2 * radius))):
        return True
    return False

@jit(nopython=True)
def nextInNeighbors(neighbors):
    """
    Gibt Index für nächstes freies Feld zum Abspeichern einer Nachbarkugel.

    Alle freien Felder, die kein Nachbarindex enthalten sind mit dem Wert -1 initialisiert.
    Die Methode gibt den Index des ersten freien Feldes (< 0) von neighbors zurück.

    :param neighbors: np.array(self.maxNeighbors, dtype=int) - Feld aus Indizes von Nachbarn einer Kugel
    :return: int - Index 1. Feld mit noch nicht belegter Nachbarkugel für Kugel i
    """
    # nächsten freien Platz in Nachbarsliste finden für die Kugel i
    for j in range(len(neighbors)):
        if neighbors[j] < 0:  # alle nicht freien Werte sind durch Werte >= 0 belegt
            return j
    raise ValueError("kein freies Feld für weitere Nachbarkugel")
    # return -1

# @jit(nopython=True)
# def sortPocketList(pockets, n, nmax):
#     sortedPockets = pockets[:,2].argsort()
#     numOfEmptyPockets = nmax-n
#     emptyPockets = sortedPockets[:numOfEmptyPockets].copy()
#     sortedPockets[:n] = sortedPockets[numOfEmptyPockets:]
#     sortedPockets[n:] = emptyPockets
#     return pockets[sortedPockets]
