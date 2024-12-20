
"""
@Author: Karin Havemann
@Date: 28.06.22

Klasse zum Erzeugen von Kugelpackungen aus Kugeln unterschiedlicher Größe.
"""

# Module importieren
import scipy.stats
from scipy.stats import uniform, beta

# eigene Module importieren
from packing import *
from funktionen import *
from specialCases import SpecialCase, writeSpecialCase

class VariableSizedPacking(Packing):
    def __init__(self, input):
        """
        Konstruktor zum Erzeugen einer Kugelpackung mit Kugeln unterschiedlicher Größe, die einander berühren oder
        überlappen.

        Die Kugeln einer VariableSizedPacking haben einen Radius zwischen self.minRadius und self.maxRadius.

        :param input: Input - enthält alle Eingabedaten der Datei
        """
        self.minRadius = input._minRadius
        self.maxRadius = input._maxRadius
        self.distribution = input._distribution
        self.beta_p = input._beta_p
        self.beta_q = input._beta_q
        self.pOverlap = input._pOverlap
        self.methodOverlap = input._methodOverlap
        Packing.__init__(self, input)

        self.loopLimit = 1/16 * (self.x * self.y * self.z) / np.power(self.maxRadius, 3)
        n = self.maxNumOfSpheres()
        # max. Anzahl Pockets in einem Raum
        self._numOfPockets = int(self.x * self.y)
            #10 * self.x * self.y / (np.pi * np.power(self.minRadius, 2)))  ##TODO: wie viele Pockets max.?
        # Feld aus Pockets
        # jede Zeile: [i1, i2, i3]
        #   Index der Kugeln 1 bis 3, die eine mögliche Pocket darstellen
        self.pockets = np.full((self._numOfPockets, 3), -1, dtype=int)
        self.countPockets = 0  # Zähler, wie viele Pockets belegt sind
        self.countCalcPockets = 0

    def maxNumOfSpheres(self):
        """
        Berechnet max. Anzahl Kugeln in der Kugelpackung.

        Eine dichteste Kugelpackung gleichgroßer, sich berührender Kugeln hat eine Packungsdichte von ca. 74 %.
        Die Packungsdichte beschreibt das Verhältnis aus mit Kugeln ausgefülltem Volumen und Gesamtvolumen des Raums.
        Da in einer EquallySizedPacking Kugeln gleicher Größe so platziert werden, dass sie einander berühren,
        können sie max. die Packungsdichte einer dichtesten Kugelpackung erreichen, also 74 %.

        Das Raumvolumen beträgt in der Theorie x*y*z. In der Praxis werden aber Kugeln im Raum platziert solange ihr
        Mittelpunkt innerhalb des Raumes liegt. Das Raumvolumen beträgt daher an jeder Kantenlänge 2 zusätzöliche Radien.

        :return: int - max. Anzahl Kugeln in einer VariableSizedPacking
        """
        if self.minRadius == self.maxRadius:
            expectedRadius = self.maxRadius
        elif self.distribution == 'uniform':
            expectedRadius = uniform(loc=self.minRadius, scale=self.maxRadius-self.minRadius).mean()
        else: # self.distribution == 'beta'
            expectedRadius = beta(self.beta_p, self.beta_q).expect(lambda x: (self.maxRadius - self.minRadius) * x + self.minRadius)

        # Raumvolumen v_r:
        # bei Platzierung ist entscheidend, ob Mittelpunkt im Raum liegt
        # --> Raumvolumen praktisch um 2*radius in jeder Dimension (x, y, z) größer
        v_r = (self.x + 2 * expectedRadius) * (self.y + 2 * expectedRadius) * (self.z + 2 * expectedRadius)
        v_s = (4 / 3) * np.pi * np.power(expectedRadius, 3) * (1 - self.pOverlap)  # Volumen einer Kugel
        p = 0.74  # Packungsdichte dichteste Kugelpackung
        n = (p * v_r) / v_s  # max. Anzahl Kugeln
        return int(n + 1)

    def pocketValid(self, pocket):
        """
        Prüft, ob die übergebene Pocket gültig ist.

        Eine Pocket ist gültig, wenn der Mittelpunkt innerhalb des Raumes mit den Seitenlängen x, y und z liegt
        und die Überlappung einer Pocket mit einer bereits existierenden Kugeln nicht zu groß ist.

        Eine
        :param pocket: np.array(4, dtype=float) - [x, y, z, r]
            x, y und z: Position Mittelpunkt Pocket
            r: Radius Pocket
        :return: bool - true, wenn Pocket gültig
        """
        if (pocket[0] < 0) or (pocket[0] > self.x) or (pocket[1] < 0) or (pocket[1] > self.y) or (pocket[2] < 0) \
                or (pocket[2] > self.z):
            #print("außerhalb Raum")
            return False, 0 # Mittelpunkt der Pocket liegt nicht im Raum
        # Überprüfung: Überschneidung Pocket mit einer bereits platzierten Kugel
        dist = pocket[3] + self.maxRadius # max. Abstand, damit Kugeln benachbart sein können
        # Bedingungen, die erfüllt sein müssen, damit Kugel entfernte Nachbarkugel der neuen Kugel sein kann
        con1 = (self.spheres[:, 0] > pocket[0] - (self.spheres[:, 3] + pocket[3])) \
               & (self.spheres[:, 0] < pocket[0] + (self.spheres[:, 3] + pocket[3]))
        con2 = (self.spheres[:, 1] > pocket[1] - (self.spheres[:, 3] + pocket[3])) \
               & (self.spheres[:, 1] < pocket[1] + (self.spheres[:, 3] + pocket[3]))
        con3 = (self.spheres[:, 2] > pocket[2] - (self.spheres[:, 3] + pocket[3])) \
               & (self.spheres[:, 2] < pocket[2] + (self.spheres[:, 3] + pocket[3]))
        con4 = (self.spheres[:, 0] >= 0) & (self.spheres[:, 1] >= 0) & (self.spheres[:, 2] >= 0)
        # Anzahl Kugeln, die die Bedingungen (con1 - con4) (nicht) erfüllen
        n = (con1 & con2 & con3 & con4).sum()
        nr = len(self.spheres) - n  # (con1 & con2 & con3 & con4).sum() = Anzahl True in Array
        # Indizes der Kugeln, die die Bedingungen (con1 - con4) erfüllen
        indices = (con1 & con2 & con3 & con4).argsort()[nr:]

        ovl = 0
        vol = 0
        for ind in indices:
            if sphereDistance(self.spheres[ind], pocket) < 0:
                if self.methodOverlap == 'average':
                    ovl += calcOverlap(self.spheres[ind], pocket)
                    vol += sphereVolume(self.spheres[ind, 3])
                else: ## self.methodOverlap == 'single'
                    ovl = calcOverlap(self.spheres[ind], pocket)
                    if ovl / sphereVolume(self.spheres[ind, 3]) > self.pOverlap or ovl / sphereVolume(pocket[3]) > self.pOverlap:
                        return False, 1
        if self.methodOverlap == 'average' and ovl / vol > self.pOverlap:
            return False, 1
        return True, 0

    def initPocketList(self):
        """
        Initialisierung der Pocketsliste.

        Anhand der Kugeln in der Initialisierungsebene werden alle möglichen Pockets (Kombinationen aus 3 entfernten
        Nachbarkugeln) berechnet und in self.pockets eingetragen.

        :return: kein Rückgabewert
        """
        for i in range(self.countSpheres):
            dist = (self.spheres[:, 3] + self.spheres[i, 3] + 2 * self.maxRadius)
            con1 = (self.spheres[:, 0] > self.spheres[i, 0] - dist) \
                   & (self.spheres[:, 0] < self.spheres[i, 0] + dist)
            con2 = (self.spheres[:, 1] > self.spheres[i, 1] - dist) \
                   & (self.spheres[:, 1] < self.spheres[i, 1] + dist)
            con3 = (self.spheres[:, 2] > self.spheres[i, 2] - dist) \
                   & (self.spheres[:, 2] < self.spheres[i, 2] + dist)
            con4 = (self.spheres[:, 0] >= 0) & (self.spheres[:, 1] >= 0) & (self.spheres[:, 2] >= 0)
            # Anzahl Kugeln, die die Bedingungen (con1 - con4) (nicht) erfüllen
            n = (con1 & con2 & con3 & con4).sum()
            nr = len(self.spheres) - n  # (con1 & con2 & con3 & con4).sum() = Anzahl True in Array
            # Indizes der Kugeln, die die Bedingungen (con1 - con4) erfüllen
            indices = (con1 & con2 & con3 & con4).argsort()[nr:]
            indices = indices[indices > i]

            # mögliche dreier Kombinationen an Kugeln durchgehen
            for ind1 in range(len(indices)):
                for ind2 in range(ind1+1, len(indices)):
                    idx1 = indices[ind1]
                    idx2 = indices[ind2]
                    if pocketPossible(self.spheres[i], self.spheres[idx1], self.spheres[idx2], self.maxRadius,
                                              self.minRadius):
                        self.pockets[self.countPockets] = np.array([i, idx1, idx2])
                        self.countPockets += 1

    def updatePocketList(self):
        """
        Pocketliste aktualisieren nachdem eine neue Kugel platziert wurde.

        Es müssen alle neuen Pockets (mögliche dreier Kombinationen an entfernten Nachbarkugeln) berechnet werden,
        die sich aus der geraden platzierten Kugel und ihren entfernten Nachbarkugeln ergeben.

        :return: kein Rückgabewert
        """
        # Nachbarn der neuen Kugel bestimmen
        kugelId = self.countSpheres - 1 # Index der neusten platzierten Kugel
        dist = (self.spheres[:kugelId, 3] + self.spheres[kugelId, 3] + 2 * self.maxRadius)
        con1 = (self.spheres[:kugelId, 0] > self.spheres[kugelId, 0] - dist) \
               & (self.spheres[:kugelId, 0] < self.spheres[kugelId, 0] + dist)
        con2 = (self.spheres[:kugelId, 1] > self.spheres[kugelId, 1] - dist) \
               & (self.spheres[:kugelId, 1] < self.spheres[kugelId, 1] + dist)
        con3 = (self.spheres[:kugelId, 2] > self.spheres[kugelId, 2] - dist) \
               & (self.spheres[:kugelId, 2] < self.spheres[kugelId, 2] + dist)
        con4 = (self.spheres[:kugelId, 0] >= 0) & (self.spheres[:kugelId, 1] >= 0) & (self.spheres[:kugelId, 2] >= 0)
        # Anzahl Kugeln, die die Bedingungen (con1 - con3) (nicht) erfüllen
        n = (con1 & con2 & con3 & con4).sum()
        #nr = len(self.spheres) - n  # (con1 & con2 & con3).sum() = Anzahl True in Array
        nr = kugelId - n
        # Indizes der Kugeln, die die Bedingungen (con1 - con3) erfüllen
        indices = (con1 & con2 & con3 & con4).argsort()[nr:]

        # mögliche dreier Kombinationen an Kugeln durchgehen
        sum = 0
        vorher = self.countPockets
        for ind1 in range(len(indices)):
            for ind2 in range(ind1 + 1, len(indices)):
                idx1 = indices[ind1]
                idx2 = indices[ind2]
                if pocketPossible(self.spheres[kugelId], self.spheres[idx1], self.spheres[idx2], self.maxRadius,
                                           self.minRadius):
                    self.pockets[self.countPockets] = np.array([idx1, idx2, kugelId])
                    self.countPockets += 1
                    sum += 1
        print("updatePocketList: ", self.countPockets, "davon neu: ", sum)

    def deletePockets(self, pocList):
        """
        Löschen aller Pockets an den Positionen, die in pocList gespeichert sind.

        :param pocList: Liste aus Pocketindices, die gelöscht werden sollen
        :return: kein Rückgabewert
        """
        print("deletePockets", self.countPockets, "davon löschen: ", len(pocList))
        for idx in pocList:
            a = self.spheres[self.pockets[idx, 0]]
            b = self.spheres[self.pockets[idx, 1]]
            c = self.spheres[self.pockets[idx, 2]]
            #print("\t", self.pockets[idx], np.linalg.norm(a-b), np.linalg.norm(a-c), np.linalg.norm(b-c))
            self.pockets[idx] = np.full((3), -1)
            self.countPockets -= 1
        self.pockets = self.pockets[self.pockets[:,0].argsort()][::-1]
        # Ausgabe aller Pockets:
        #for i in range(self.pockets.shape[0]):
        #    print(self.pockets[i])

    def generatePacking(self):
        """
        Generieren der Kugelpackung.

        Eine Kugelpackung wird generiert, indem die Kugeln der Initialisierungsebene aus einer Datei eingelesen werden
        und alle möglichen Pockets berechnet werden. Dann wird in einer Schleife ein neuer Radius vorgegeben.
        Mit diesem Radius wird eine neue Kugel an der niedrigsten möglichen Pocket platziert. Dafür werden für alle
        dreier Kombinationen an Nachbarkugeln, falls möglich, Kugelpositionen berechnet. Nachdem eine Kugel platziert
        wurde, wird die Pocketliste aktualisiert. Dieser Vorgang wird solange wiederholt bis der gesamte Raum mit
        Kugeln gefüllt ist und es daher keine freien Pockets mehr gibt.

        :return: kein Rückgabewert
        """
        csvIn = f"../resources/output/{self.x}x{self.y}x{self.z}_{self.distribution}_{int(self.minRadius)}_{int(self.maxRadius)}{self.suffix}_initialisierungsebene.csv"
        csvOut = f"../resources/output/{self.x}x{self.y}x{self.z}_{self.distribution}_{int(self.minRadius)}_{int(self.maxRadius)}{self.suffix}_kupa.csv"
        fileOut = f"../resources/output/{self.x}x{self.y}x{self.z}_{self.distribution}_{int(self.minRadius)}_{int(self.maxRadius)}{self.suffix}_anzahl_sonderfaelle.txt"
        self.initialize(csvIn) # Initialisierungsebene einlesen
        self.initPocketList()

        count_sf1 = 0  # 3 Kugeln auf einer Geraden
        count_sf2 = 0  # Abstand zwischen 2 Kugeln zu groß
        count_sf3 = 0  # Fehler bei Berechnung Pyramidenhöhe
        count_sf4 = 0  # Anzahl Fälle, die überlappend berechnet werden (pq-Formel) liefert passende Lösung
        count_sf5 = 0  # Überlapp-Exception in calcPocket
        count_sf6 = 0  # Überlapp unter allen Nachbarkugeln zu groß
        count_overlappedSpheres = 0

        loopCounter = 0
        while self.countPockets > 0 and loopCounter < self.loopLimit:
            loopCounter += 1
            pocDetected = False
            pocIdx = -1
            lowestPoc = np.zeros(4)
            delPockets = []
            if self.minRadius == self.maxRadius:
                radius = self.minRadius
            elif self.distribution == 'uniform':
                radius = uniform.rvs(loc=self.minRadius, scale=self.maxRadius-self.minRadius)
            else: # self.distribution == 'beta':
                radius = beta.rvs(self.beta_p, self.beta_q, loc=self.minRadius, scale=(self.maxRadius - self.minRadius))
            print("Radius: ", radius)
            # alle möglichen Pockets durchgehen
            normalPocket = True
            for i in range(self.countPockets):
                p1 = self.spheres[self.pockets[i, 0]]
                p2 = self.spheres[self.pockets[i, 1]]
                p3 = self.spheres[self.pockets[i, 2]]

                try:
                    self.countCalcPockets += 1
                    success, p4, case = calcPocket(p1, p2, p3, radius, self.pOverlap, self.methodOverlap)
                except OverlapException:
                    count_sf5 += 1
                    delPockets.append(i)
                except StraightException:
                    count_sf1 += 1
                    delPockets.append(i)
                except SpacingException: # TODO: nur bei calcPocket_v2
                    pass
                else:
                    # Sonderfälle zählen
                    if case == SpecialCase.DISTANCE:
                        count_sf2 += 1
                    elif case == SpecialCase.HEIGHT:
                        count_sf3 += 1
                    elif case == SpecialCase.NEWRADIUS:
                        count_sf3 += 1
                        count_sf4 += 1
                    if success and (not pocDetected or (pocDetected and p4[2] < lowestPoc[2])):
                        valid, plus = self.pocketValid(p4)
                        count_sf6 += plus
                        if valid:
                            pocDetected = True
                            lowestPoc = p4
                            pocIdx = i # Index der aktuell niedrigsten Pocket, die gefüllt werden soll
                            if case == SpecialCase.NEWRADIUS:
                                normalPocket = False
                            else:
                                normalPocket = True
                        else:
                            delPockets.append(i)
            if pocDetected:
                self.spheres[self.countSpheres] = lowestPoc
                self.countSpheres += 1
                delPockets.append(pocIdx)
                self.deletePockets(delPockets)
                self.updatePocketList()
                print("neu:", lowestPoc)
                loopCounter = 0
                if normalPocket == False:
                    count_overlappedSpheres += 1
            else:
                self.deletePockets(delPockets)
        print("Anzahl Aufrufe calcPocket:", self.countCalcPockets)
        self.writeCsvFile(csvOut)
        counts = [self.countCalcPockets, count_sf1, count_sf2, count_sf3, count_sf4, count_sf5, count_sf6, count_overlappedSpheres]
        writeSpecialCase(counts, fileOut)

