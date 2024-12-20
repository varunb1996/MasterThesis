#!/usr/bin/env python3

#TODO: Kommentare
"""
@Author: Karin Havemann
@Date: 28.06.2022

Klasse Input:
Einlesen der Werte aus Eingabedatei.

einzulesene Werte aus Eingabedatei:
- self._n: int - Anzahl Kugelpackungen/Testcases, die erstellt werden sollen
- self._x: int - x-Dimension des Raumes
- self._y: int - y-Dimension des Raumes
- self._z: int - z-Dimension des Raumes
- self._radius: float - Radius der Kugeln
- self._suf: string - Zusatz zur Dateibezeichnung (optional)
"""

from input import *

class VariableSizedInput(Input):
    def __init__(self, filename):
        """
        Konstruktor der Input Klasse, die für das Einlesen der Eingabedaten zuständig ist.

        Die Eingabedaten werden der Datei filename entnommen. Alle einzulesenen Werte werden zunächst mit Default-Werten
        belegt, falls Fehler beim Einlesen auftreten. Anschließend werden die Eingabedaten eingelesen.

        :param filename: string - Name der Eingabedatei
        """
        Input.__init__(self, filename)
        self.default()
        self.readInput()


    def default(self):
        """
        Default-Belegung aller einzulesenen Werte.

        :return: kein Rückgabewert
        """
        self._n = 1
        self._x = 200
        self._y = 200
        self._z = 100
        self._minRadius = 7.0
        self._maxRadius = 10.0
        self._distribution = 'uniform'
        self._beta_p = 2
        self._beta_q = 2
        self._pOverlap = 0.05
        self._methodOverlap = 'single'
        #self.eps = 5.0
        self._suf = ''
        self._suffix = ''
        #self.testpoints = 500
        #self.reachPorosity = True
        #self.targetPorosity = 0.25
        #self.maxN = 50

    def printAssignment(self):
        """
        Ausgabe der Belegung aller einzulesenen Werte.

        :return: kein Rückgabewert
        """
        #print("Eingelesene Werte:")
        print(f"Anzahl Kugelpackungen: n = {self._n}")
        print("Raumgröße:")
        print(f"\tx: {self._x}")
        print(f"\ty: {self._y}")
        print(f"\tz: {self._z}")
        print(f"Kugelradius: {self._minRadius} - {self._maxRadius}")
        print(f"prozentualer Überlapp: {self._pOverlap}")
        print(f"Verteilung: {self._distribution}")

    def readInput(self):
        """
        Einlesen aller einzulesenen Werte aus der Eingabedatei.

        :return: kein Rückgabewert
        """
        defined = True
        with open(self.filename) as f:
            for line in f:
                if not line.startswith('#'):
                    if line.startswith('n'):
                        try:
                            temp = int(line.split(':')[1])
                            if temp > 0:
                                self._n = temp
                            else:
                                defined = False # Default
                        except ValueError:
                            defined = False # Default
                    elif line.startswith('breite'):
                        try:
                            temp = int(line.split(':')[1])
                            if temp > 0:
                                self._x = temp
                            else:
                                defined = False # Default
                        except ValueError:
                            defined = False # Default
                    elif line.startswith('hoehe'):
                        try:
                            temp = int(line.split(':')[1])
                            if temp > 0:
                                self._y = temp
                            else:
                                defined = False # Default
                        except ValueError:
                            defined = False # Default
                    elif line.startswith('tiefe'):
                        try:
                            temp = int(line.split(':')[1])
                            if temp > 0:
                                self._z = temp
                            else:
                                defined = False # Default
                        except ValueError:
                            defined = False # Default
                    elif line.startswith('minimaler Radius'):
                        try:
                            temp = float(line.split(':')[1])
                            if temp > 0:
                                self._minRadius = temp
                            else:
                                defined = False # Default
                        except ValueError:
                            defined = False # Default
                    elif line.startswith('maximaler Radius'):
                        try:
                            temp = float(line.split(':')[1])
                            if temp > 0:
                                self._maxRadius = temp
                            else:
                                defined = False # Default
                        except ValueError:
                            defined = False # Default
                    elif line.startswith('prozentualer Überlapp'):
                        try:
                            temp = float(line.split(':')[1])
                            if temp >=0 and temp <= 1:
                                self._pOverlap = temp
                            else:
                                defined = False # Default
                        except ValueError:
                            defined = False # Default
                    elif line.startswith('Verteilung'):
                        self._distribution = line.split(':')[1].strip() # Leerzeichen entfernen
                        if not (len(self._distribution) > 0):
                            self._distribution = 'uniform' # Default
                    elif line.startswith('Beta-Verteilung p'):
                        try:
                            temp = float(line.split(':')[1])
                            if temp > 0:
                                self._beta_p = temp
                            else:
                                defined = False  # Default
                        except ValueError:
                            defined = False # Default
                    elif line.startswith('Beta-Verteilung q'):
                        try:
                            temp = float(line.split(':')[1])
                            if temp > 0:
                                self._beta_q = temp
                            else:
                                defined = False  # Default
                        except ValueError:
                            defined = False # Default
                    elif line.startswith('suffix'):
                        self._suffix = line.split(':')[1].strip() # Leerzeichen entfernen
                        if len(self._suffix) > 0:
                            self._suf = '_' + self._suffix
                            self._suffix = '_' + self._suffix

        if defined == False:
            print("Es konnten nicht alle Eingabewerte eingelesen werden.")
            print("Min. ein Eingabewert wurde mit einem Default-Wert belegt")
        else:
            print("Alle Eingabedaten eingelesen.")
        self.printAssignment()
