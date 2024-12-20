#!/usr/bin/env python3

"""
@Author: Karin Havemann
@Date: 28.06.2022

Klasse Input:
Einlesen der Werte aus Eingabedatei.

Einzulesende Werte unterscheiden sich je nach Art der Kugelpackung
"""

from abc import ABC, abstractmethod

class Input(ABC):
    def __init__(self, filename):
        """
        Konstruktor der Input Klasse, die für das Einlesen der Eingabedaten zuständig ist.

        Die Eingabedaten werden der Datei filename entnommen. Alle einzulesenen Werte werden zunächst mit Default-Werten
        belegt, falls Fehler beim Einlesen auftreten. Anschließend werden die Eingabedaten eingelesen.

        :param filename: string - Name der Eingabedatei
        """
        self.filename = filename
        self.default()

    @abstractmethod
    def default(self):
        """
        Default-Belegung aller einzulesenen Werte.

        :return: kein Rückgabewert
        """
        pass

    def setSuffix(self, i):
        """
        Dateizusatzbezeichnung erweitert mit der Testcase-Nummer.

        :param i: Testcase-Nummer
        :return: kein Rückgabewert
        """
        self._suffix = f"_TC{i:02d}{self._suf}"
        #self._suffix = f"_TC{i:02d}"

    @abstractmethod
    def printAssignment(self):
        """
        Ausgabe der Belegung aller einzulesenen Werte.

        :return: kein Rückgabewert
        """
        pass

    @abstractmethod
    def readInput(self):
        """
        Einlesen aller einzulesenen Werte aus der Eingabedatei.

        :return: kein Rückgabewert
        """
        pass