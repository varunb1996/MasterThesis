"""
Testen einzelner Funktionen
"""

import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter, AutoMinorLocator)
#import unittest

# eigene Module:
from positioningExceptions import StraightException, OverlapException, SpacingException, UnknownError
import funktionen as funk
from specialCases import SpecialCase

class TestPocketBerechnung:#(unittest.TestCase):
    # @classmethod
    # def setUpClass(cls) -> None:
    #     #load_test_data()
    #     print('Set up Class')

    def __init__(self):
        self.data = self.load_test_data()
        #print(list(self.data.index))
        self.test_pockets()
        #self.test_optimization()
        #self.drawRadikand()
        #self.testRadikand()

    def load_test_data(self):
        datentyp = {"test": str, "x1": str, "y1": str, "z1": str, "r1": str, "x2": str, "y2": str, "z2": str, "r2": str,
                    "x3": str, "y3": str, "z3": str, "r3": str, "r4": str}
        kugeln = pd.read_excel('../resources/testdata.xlsx', dtype=datentyp, engine='openpyxl', skipfooter=0)
        #kugeln = pd.read_excel('../resources/testdata.xlsx', dtype=datentyp)
        for col in list(kugeln.columns)[1:]:
            kugeln[col] = kugeln[col].apply(eval)
        return kugeln

    def test_pockets(self):
        p1 = np.array([5, 0, 0, 1])
        p2 = np.array([0, 0, 0, 1])
        p3 = np.array([0, 2, 0, 1])
        #success, p4 = funk.calcPocket_optOverlap(p1, p2, p3, 1, 0.01, 'relativeVolume')
        #success, p41 = funk.calcPocket(p1, p2, p3, 1, 0.01)  # , 'relativeVolume')
        start = time.time()
        kugeln = []
        for i in range(1):
            if i == 1:
                start = time.time()
            for index, row in self.data.iterrows():
                print(f"{row['test']}: ")
                p1 = np.array([row['x1'], row['y1'], row['z1'], row['r1']])
                p2 = np.array([row['x2'], row['y2'], row['z2'], row['r2']])
                p3 = np.array([row['x3'], row['y3'], row['z3'], row['r3']])
                try:
                    success, p41, case = funk.calcPocket(p1, p2, p3, row['r4'], 0.01, 'average')
                    print(success, p41, case)
                    #success, p41 = funk.calcPocket_optOverlap(p1, p2, p3, row['r4'], 0.01, 'relativeVolume')
                except OverlapException as e:
                    #print(f"\t{e}")
                    pass
                except StraightException as e:
                    #print(f"\t{e}")
                    pass
                except SpacingException as e: # nur bei calcPocket_v2
                    pass
                else:
                    if success:
                        funk.testDistance(p1, p2, p3, p41, row['test'])
                        spheres = [p1, p2, p3, p41]
                        #funk.generateVTK(spheres, row['test'])
                        #kugeln.append({"test": row['test'], "x": p1[0], "y": p1[1], "z": p1[2], "r": p1[3]})
                        #kugeln.append({"test": row['test'], "x": p2[0], "y": p2[1], "z": p2[2], "r": p2[3]})
                        #kugeln.append({"test": row['test'], "x": p3[0], "y": p3[1], "z": p3[2], "r": p3[3]})
                        #kugeln.append({"test": row['test'], "x": p41[0], "y": p41[1], "z": p41[2], "r": p41[3]})
                    #else:
                        #print("\tAbstand zu groß. Keine Pocket mit diesem Radius möglich")
                #funk.generateCSV(kugeln, "geometrisch_opt")
        print("Zeit", time.time() - start)

    def test_optimization(self):
        start = time.time()
        kugeln = []
        for i in range (1):
            for index, row in self.data.iterrows():
                if row['test']=='F4c':
                    x0 = np.array([67.5, -32.9, 0])
                else:
                    x0 = np.array([1, 1, 1])
                #print('\n', row['test'])
                p1 = np.array([row['x1'], row['y1'], row['z1'], row['r1']])
                p2 = np.array([row['x2'], row['y2'], row['z2'], row['r2']])
                p3 = np.array([row['x3'], row['y3'], row['z3'], row['r3']])
                res = funk.optimizeOverlap(p1, p2, p3, row['r4'], x0, method='absoluteVolume')
                #print(np.asarray(x).shape)#, np.array([row['r4']]).shape)
                if (res.success):
                    p4 = np.concatenate([np.asarray(res.x), np.array([row['r4']])])
                    spheres = [p1, p2, p3, p4]
                    kugeln.append({"test": row['test'], "x": p1[0], "y": p1[1], "z": p1[2], "r": p1[3]})
                    kugeln.append({"test": row['test'], "x": p2[0], "y": p2[1], "z": p2[2], "r": p2[3]})
                    kugeln.append({"test": row['test'], "x": p3[0], "y": p3[1], "z": p3[2], "r": p3[3]})
                    kugeln.append({"test": row['test'], "x": p4[0], "y": p4[1], "z": p4[2], "r": p4[3]})
                    #funk.generateVTK(spheres, f"Opt_trust-constr{row['test']}")
            #funk.generateCSV(kugeln, "opt_trust-constr")
        print(time.time()-start)

    def drawRadikand(self):
        #test_list = ['N1a', 'F3a', 'F3b', 'F4b', 'F4d', 'F5a']
        test_list = ['F5b']#, 'F4d', 'F5a']
        name = 'C2'
        name_list = ['A1', 'A2']
        counter = 0
        X = np.linspace(-5, 20, 1001, endpoint=True)
        plt.rc('font', size=14)
        plt.figure(dpi=400)
        fig, ax = plt.subplots(constrained_layout=True)
        for index, row in self.data.iterrows():
            if row['test'] in test_list:
                k1 = np.array([row['x1'], row['y1'], row['z1'], row['r1']])
                k2 = np.array([row['x2'], row['y2'], row['z2'], row['r2']])
                k3 = np.array([row['x3'], row['y3'], row['z3'], row['r3']])
                a = np.linalg.norm(k1[:3]-k2[:3])
                b = np.linalg.norm(k2[:3]-k3[:3])
                c = np.linalg.norm(k1[:3]-k3[:3])
                r1 = k1[3]
                r2 = k2[3]
                r3 = k3[3]
                F = funk.radikand(X, a, b, c, r1, r2, r3)
                ax.plot(X, F, label=name_list[counter])
                counter += 1
        plt.axhline(y=0, c='black')
        # F3a - A1
        #plt.axvline(x=1.309401076758503, c="black")
        #plt.axvline(x=-3.309401076758503, c="black")
        # F3b - A2
        #plt.axvline(x=1.0000000024998748, c="black")
        #plt.axvline(x=-3.000000002499875, c="black")
        # F4b - B1
        #plt.axvline(x=2.507082990014199, c="black")
        #plt.axvline(x=0.5377895551041239, c="black")
        # F4d - B2
        #plt.axvline(x=15.681259459804837, c="black")
        #plt.axvline(x=-7.137066401318831, c="black")
        # F4e - B3
        #plt.axvline(x=-12.004747203910494, c="black")
        #plt.axvline(x=-73.15654311867014, c="black")
        # F5a - C1
        #plt.axvline(x=1.5, c="black")
        #plt.axvline(x=-3.499999999999999, c="black")
        # F5b - C2
        plt.axvline(x=16.475237400926964, c="black")
        plt.axvline(x=-4.9616780788930415, c="black")
        #ax.xaxis.set_major_locator(MultipleLocator(2))
        #ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        #ax.xaxis.set_minor_locator(MultipleLocator(0.5))
        #plt.xticks(np.arange(0, 20, step=0.5))

        #plt.legend()
        plt.xlabel("x", loc='right', size=18)
        #plt.xlabel("x", size=18)
        plt.ylabel("w(x)", loc='top', size=18)
        #plt.ylabel("w(x)", size=18)
        plt.savefig(f'../resources/figures/w_von_x_Fall_{name}')
        plt.show()

    def testRadikand(self):
        for index, row in self.data.iterrows():
            print(f"{row['test']}: ")
            k1 = np.array([row['x1'], row['y1'], row['z1'], row['r1']])
            k2 = np.array([row['x2'], row['y2'], row['z2'], row['r2']])
            k3 = np.array([row['x3'], row['y3'], row['z3'], row['r3']])
            a = np.linalg.norm(k1[:3] - k2[:3])
            b = np.linalg.norm(k2[:3] - k3[:3])
            c = np.linalg.norm(k1[:3] - k3[:3])
            r1 = k1[3]
            r2 = k2[3]
            r3 = k3[3]
            r4 = row['r4']
            #print(funk.radikand(r4, a, b, c, r1, r2, r3), funk.radikand_v2(r4, a, b, c, r1, r2, r3))
            #print(np.abs(funk.radikand(r4, a, b, c, r1, r2, r3)-funk.radikand_v2(r4, a, b, c, r1, r2, r3)) < 1e-6)
            #print(np.abs(funk.radikand_strich(r4, a, b, c, r1, r2, r3) - funk.radikand_strich_v3(r4, a, b, c, r1, r2, r3)) < 1e-6)
            #print(np.abs(funk.radikand_strich_v3(r4, a, b, c, r1, r2, r3) - funk.radikand_strich_v2(r4, a, b, c, r1, r2, r3)) < 1e-6)
            f = funk.radikand(r4, a, b, c, r1, r2, r3)
            f1 = funk.radikand_strich(r4, a, b, c, r1, r2, r3)
            f2 = funk.radikand_strich_strich(r4, a, b, c, r1, r2, r3)
            m = np.abs((f * f2) / np.power(f1, 2))
            print(m < 1, m)

def main():
    test = TestPocketBerechnung()

if __name__ == '__main__':
    main()

