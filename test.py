
"""
@Author: Karin Havemann
@Date: 25.03.2022

Testen von Klassen und Methoden aus packing.py, equallySizedPacking.py, input.py
"""

from packing import *
from equallySizedPacking import *
from input import Input

class Test:
    def __init__(self):
        eingabe = "../resources/Eingabedaten.txt"
        self.inp = Input(eingabe)

    def testReadWriteCsv(self):
        self.kupa = EquallySizedPacking(self.inp)
        dateiIn = "../resources/output/100x100x100_suffix_initialisierungsebene.csv"
        self.kupa.initialize(dateiIn)
        print(self.kupa.spheres)
        print(self.kupa.countSpheres)
        self.kupa.writeCsvFile("test_output.csv")

    def testSortPocketList(self):
        self.kupa = EquallySizedPacking(self.inp)
        for i in range(10):
            self.kupa.pockets = np.full((self.kupa._numOfPockets, 4), -1.)
            self.kupa.countPockets = 0
            j = 0
            while j <= i:
                r = randrange(10)
                if self.kupa.pockets[r, 2] < 0:
                    j += 1
                    self.kupa.pockets[r, 2] = randrange(100)
                    self.kupa.countPockets += 1
            print(self.kupa.pockets)
            self.kupa.sortPocketList()
            print(self.kupa.pockets)
            print()

    def testDistRekursiv(self):
        self.kupa = EquallySizedPacking(self.inp)
        sphere = np.array([0, 0, 0, 10.])
        print(sphereDistance(sphere, sphere))

    def testRuntime(self):
        for i in range(self.inp._n):
            self.inp.setSuffix(i+1)
            self.kupa = EquallySizedPacking(self.inp)
            start = time.time()
            self.kupa.generatePacking()
            elapsed_time = time.time() - start
            print(elapsed_time)
        # self.inp._suffix = "_TC03" + self.inp._suffix
        # start = time.time()
        # self.kupa.generatePacking()
        # elapsed_time = time.time() - start
        # print(elapsed_time)

    def test(self):
        self.testRuntime()

t = Test()
t.test()