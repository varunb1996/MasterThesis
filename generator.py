
"""
@Author: Karin Havemann
@Date: 04.07.2022

Klasse zum Erzeugen einer Kugelpackung aus Kugeln gleicher oder unterschiedlicher Größe
"""

import time

# Importieren eigener Module
from equallySizedPacking import *
from equallySizedInput import *
from variableSizedPacking import *
from variableSizedInput import *

class Generator:
    def __init__(self):
        eingabe = "../resources/Eingabedaten.txt"
        #self.inp = EquallySizedInput(eingabe)
        self.inp = VariableSizedInput(eingabe)
        if (self.inp._minRadius == self.inp._maxRadius):
            self.inp = EquallySizedInput(eingabe)
            self.generateEquallySizedPacking()
        else:
            self.generateVariableSizedPacking()

    def generateEquallySizedPacking(self):
        """
        Kugelpackung aus Kugeln gleicher Größe wird erzeugt.

        :return:
        """
        print("Erzeuge Kugelpackung")
        for i in range(self.inp._n): # insgesamt werden inp._n Kugelpackungen erzeugt
            self.inp.setSuffix(i+1)
            self.kupa = EquallySizedPacking(self.inp)
            self.kupa.generatePacking()
            print(f"Kugelpackung Testcase {i+1} von {self.inp._n} erzeugt.")

    def generateVariableSizedPacking(self):
        """
        Kugelpackung aus Kugeln unterschiedlicher Größe wird erzeugt.

        :return:
        """
        print("Erzeuge Kugelpackung")
        for i in range(self.inp._n):  # insgesamt werden inp._n Kugelpackungen erzeugt
            self.inp.setSuffix(i + 1)
            self.kupa = VariableSizedPacking(self.inp)
            start = time.time()
            self.kupa.generatePacking()
            print("benötigte Zeit:", time.time() - start)
            print(f"Kugelpackung Testcase {i + 1} von {self.inp._n} erzeugt.")

def main():
    gen = Generator()
    #gen.generateEquallySizedPacking()
    #gen.generateVariableSizedPacking()

if __name__ == "__main__":
    main()