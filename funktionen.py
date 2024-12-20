# Module importieren
import numpy as np
import scipy.optimize
import pandas as pd
from numba import jit # Just-In-Time-Compiler

# eigene Module:
from positioningExceptions import StraightException, OverlapException, SpacingException, UnknownError
from specialCases import SpecialCase

@jit(nopython=True)
def heightTetraeder(p1, p2, p3, r4):
    """
    Berechnet aus den 3 Kugelpositionen p1, p2 und p3 sowie dem Radius r4 die 4 Kantenlängen des allgemeinen Tetraeders.
    Die vier Eckpunkte des allgemeinen Tetraeders werden durch die 4 Kugelmittelpunkte bestimmt.Wenn die Positionierung
    einer neuen Kugel mit Radius r4 möglich ist, wird aus Volumen und Grundfläche des allgmeinen Tetraeders die Höhe
    berechnet und zurückgegeben. Sonst wird eine SpacingException geworfen.
    :param p1: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 1
    :param p2: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 2
    :param p3: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 3
    :param r4: float - Radius der zu zu platzierenden 4. Kugel
    :return: Höhe des allgemeinen Tetraeders, der durch die Mittelpunkte der 4 Kugeln gebildet wird
    """
    a = np.linalg.norm(p1[:3] - p2[:3])
    b = np.linalg.norm(p2[:3] - p3[:3])
    c = np.linalg.norm(p1[:3] - p3[:3])
    aHat = p3[3] + r4
    bHat = p1[3] + r4
    cHat = p2[3] + r4
    f_a = np.power(b, 2) + np.power(bHat, 2) + np.power(c, 2) + np.power(cHat, 2) - np.power(a, 2) - np.power(aHat, 2)
    f_b = np.power(a, 2) + np.power(aHat, 2) + np.power(c, 2) + np.power(cHat, 2) - np.power(b, 2) - np.power(bHat, 2)
    f_c = np.power(a, 2) + np.power(aHat, 2) + np.power(b, 2) + np.power(bHat, 2) - np.power(c, 2) - np.power(cHat, 2)
    delta = np.power(a, 2) * np.power(b, 2) * np.power(c, 2) + np.power(a, 2) * np.power(bHat, 2) * np.power(cHat, 2) \
            + np.power(aHat, 2) * np.power(b, 2) * np.power(cHat, 2) \
            + np.power(aHat, 2) * np.power(bHat, 2) * np.power(c, 2)
    determinante = np.power(a, 2) * np.power(aHat, 2) * f_a + np.power(b, 2) * np.power(bHat, 2) * f_b \
                   + np.power(c, 2) * np.power(cHat, 2) * f_c - delta
    if determinante < 0:
        # negative Determinante abfangen
        # raise ValueError(f"neue Kugel kann nicht alle 3 Kugeln gleichzeitig berühren: ({determinante}, {f_a}, {f_b}, {f_c}, {delta})")
        #raise SpacingException(r4)
        raise SpacingException()
    # Volumen
    V = 1 / 12 * np.sqrt(determinante)
    # Fläche Grundfläche
    A = 1 / 4 * np.sqrt((a + b + c) * (-a + b + c) * (a - b + c) * (a + b - c))
    # Höhe Tetraeder
    h = 3 * V / A
    return h

@jit(nopython=True)
def lineDistance(rv1, sv1, rv2, sv2, eps=1e-9):
    """
    Berechnung des Abstands zwischen 2 Geraden im R^3. Bei zwei parallelen Geraden wird eine StraightException
    geworfen.
    Geraden:
    g1 : x = sv1 + a * rv1
    g2 : x = sv2 + b * rv2

    :param rv1: np.array([x, y, z], dtype=float) - Richtungsvektor Gerade 1
    :param sv1: np.array([x, y, z], dtype=float) - Stützvektor Gerade 1
    :param rv2: np.array([x, y, z], dtype=float) - Richtungsvektor Gerade 2
    :param sv2: np.array([x, y, z], dtype=float) - Stützvektor Gerade 2
    :param eps: float - Kriterium zum Überprüfen der Parallelität der beiden Geraden
    :return: float - Abstand zwischen g1 und g2
    """
    u = np.cross(rv1, rv2)
    a = np.linalg.norm(u)
    if np.linalg.norm(u) < eps:  # Kreuzprodukt ist Nullvektor
        # raise ValueError("Kreuzprodukt ist Nullvektor. Die beiden Geraden sind parallel.")
        raise StraightException()
    d = np.absolute(np.dot(sv1 - sv2, u)) / a
    return d

@jit(nopython=True)
def calcIntersectionPoint(g1, g2):
    """
    Berechnung des Lotfußpunktes zweier (windschiefer) Geraden g1 und g2.
    :param g1: (s=[x, y, z], v=[x, y, z]) - Tupel aus 2 Vektoren mit je drei Einträgen. s ist der Ortsvektor der Geraden
        g1 und v der Richtungsvektor
    :param g2: (s=[x, y, z], v=[x, y, z]) - Tupel aus 2 Vektoren mit je drei Einträgen. s ist der Ortsvektor der Geraden
        g2 und v der Richtungsvektor
    :return: Lotfußpunkt der Geraden g1 und g2
    """
    # eig. wird Lotfußpunkt berechnet (Floating-Point Arithmetik)??
    # Gleichungssystem zum Bestimmen der Punkte mit dem kürzesten Abstand zwischen g1 und g2
    A = np.array(
        [[np.dot(g1[1], g2[1]), (-1.) * np.dot(g2[1], g2[1])], [np.dot(g1[1], g1[1]), (-1.) * np.dot(g2[1], g1[1])]])
    b = np.array([(-1.) * np.dot(g1[0] - g2[0], g2[1]), (-1.) * np.dot(g1[0] - g2[0], g1[1])])
    x = np.linalg.solve(A, b)
    hs = g1[0] + x[0] * g1[1]
    return hs

@jit(nopython=True)
def testDistance(p1, p2, p3, p4, testcase=''):
    """
    Testet, ob der Abstand zwischen p4 zu den Punkten p1, p2 und p3 den addierten Radien entspricht.
    :param p1: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 1
    :param p2: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 2
    :param p3: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 3
    :param p4: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 4
    :param testcase: string - Beschreibung des Testcases
    :return:
    """
    points = [p1, p2, p3]
    count = 0
    for p in points:
        count += 1
        if (np.linalg.norm(p4[:3] - p[:3]) - (p4[3] + p[3])) > 0.0001:
            print(f"\tzu großer Abstand zwischen P4 = {p4[:3]} und P{count} = {p[:3]} in Testcase {testcase}: "
                  f"{np.linalg.norm(p4[:3] - p[:3])} statt {p4[3] + p[3]}")

@jit(nopython=True)
def calcSLines(p1, p2, p3, r4):
    """
    Berechnung der Geraden durch S1 (liegt auf der Geraden p1p2) und H_s, S2 (liegt auf der Geraden p2p3) und H_s
    sowie S3 (liegt auf der Geraden p1p3) und H_s.
    :param p1: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 1
    :param p2: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 2
    :param p3: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 3
    :param r4: float - Radius der Kugel 4
    :return: Liste der drei Geraden aus Tupeln, die jeweils den Stütz- und den Richtungsvektor enthalten
    """
    paare = [(p1, p2), (p2, p3), (p3, p1)]
    n = np.cross(p1[:3] - p2[:3], p3[:3] - p2[:3])
    geraden = []

    for paar in paare:
        k1 = paar[0]
        k2 = paar[1]
        d1 = np.linalg.norm(k2[:3] - k1[:3])
        d2 = k1[3] + r4
        d3 = k2[3] + r4

        if d1 < 0 or d2 < 0 or d3 < 0:
            print(d1, d2, d3)
            print(p1, p2, p3, r4)
        alpha_quer = (np.power(d1, 2) + np.power(d2, 2) - np.power(d3, 2)) / (2 * d1 * d2)
        if np.abs(alpha_quer) > 1:
            raise SpacingException()
        alpha = np.arccos(np.abs(alpha_quer))

        ps = np.cos(alpha) * (k1[3] + r4)
        if alpha_quer > 0:
            s = k1[:3] + (ps / np.linalg.norm(k2[:3] - k1[:3])) * (k2[:3] - k1[:3])
        else:
            s = k1[:3] - (ps / np.linalg.norm(k2[:3] - k1[:3])) * (k2[:3] - k1[:3])
        v = np.cross(k2[:3] - k1[:3], n)
        geraden.append((s, v))
    return geraden

@jit(nopython=True)
def radikand(x, a, b, c, r1, r2, r3):
    """
    Berechnung des Radikanden aus der Berechnung des Volumens eines allgemeinen Tetraeders von Euler.

    :param x: float - Radius zu platzierende Kugel 4
    :param a: float - Abstand zwischen den platzierten Kugeln 1 und 2
    :param b: float - Abstand zwischen den platzierten Kugeln 2 und 3
    :param c: float - Abstand zwischen den platzierten Kugeln 1 und 3
    :param r1: float - Radius platzierte Kugel 1
    :param r2: float - Radius platzierte Kugel 2
    :param r3: float - Radius platzierte Kugel 3
    :return: Radikand an der Stelle x = r4
    """
    # a = np.linalg.norm(k1[:3]-k2[:3])
    # b = np.linalg.norm(k2[:3]-k3[:3])
    # c = np.linalg.norm(k1[:3]-k3[:3])
    # r1 = k1[3]
    # r2 = k2[3]
    # r3 = k3[3]
    s1 = np.power(a,2) * np.power((r3+x),2) * (np.power(b,2) + np.power((r1+x), 2) + np.power(c,2) + np.power((r2+x),2)
                                               - np.power(a,2) - np.power((r3+x),2))
    s2 = np.power(b, 2) * np.power((r1 + x), 2) * (np.power(a, 2) + np.power((r3 + x), 2) + np.power(c, 2)
                                                   + np.power((r2 + x), 2) - np.power(b, 2) - np.power((r1 + x), 2))
    s3 = np.power(c, 2) * np.power((r2 + x), 2) * (np.power(a, 2) + np.power((r3 + x), 2) + np.power(b, 2)
                                                   + np.power((r1 + x), 2) - np.power(c, 2) - np.power((r2 + x), 2))
    delta = np.power(a, 2) * np.power(b, 2) * np.power(c, 2) \
            + np.power(a, 2) * np.power((r1 + x), 2) * np.power((r2 + x), 2) \
            + np.power(b, 2) * np.power((r3 + x), 2) * np.power((r2 + x), 2) \
            + np.power(c, 2) * np.power((r3 + x), 2) * np.power((r1 + x), 2)

    return s1 + s2 + s3 - delta

@jit(nopython=True)
def radikand_strich(x, a, b, c, r1, r2, r3):
    """
    Ableitung des Radikanden aus der Berechnung des Volumens eines allgemeinen Tetraeders von Euler nach x (Radius der
    zu platzierenden 4. Kugel).

    :param x: float - Radius zu platzierende Kugel 4
    :param a: float - Abstand zwischen den platzierten Kugeln 1 und 2
    :param b: float - Abstand zwischen den platzierten Kugeln 2 und 3
    :param c: float - Abstand zwischen den platzierten Kugeln 1 und 3
    :param r1: float - Radius platzierte Kugel 1
    :param r2: float - Radius platzierte Kugel 2
    :param r3: float - Radius platzierte Kugel 3
    :return: Ableitung des Radikanden an der Stelle x = r4
    """
    s1 = np.power(x, 3) * 4 * np.power(a, 2) + np.power(x, 2) * 3 * (np.power(a, 2) * 2 * (r1 + r2)) \
         + x * 2 * np.power(a, 2) * (np.power(b, 2) + np.power(c, 2) - np.power(a, 2) + np.power(r1, 2)
                                     + np.power(r2, 2) + 4 * r3 * (r1 + r2 - r3)) \
         + np.power(a, 2) * 2 * r3 * (np.power(b, 2) + np.power(c, 2) - np.power(a, 2) + np.power(r1, 2)
                                      + np.power(r2, 2) - np.power(r3, 2) + r3 * (r1 + r2 - r3))
    s2 = np.power(x, 3) * 4 * np.power(b, 2) + np.power(x, 2) * 3 * (np.power(b, 2) * 2 * (r3 + r2)) \
         + x * 2 * np.power(b, 2) * (np.power(a, 2) + np.power(c, 2) - np.power(b, 2) + np.power(r3, 2)
                                     + np.power(r2, 2) + 4 * r1 * (r3 + r2 - r1)) \
         + np.power(b, 2) * 2 * r1 * (np.power(a, 2) + np.power(c, 2) - np.power(b, 2) + np.power(r3, 2)
                                      + np.power(r2, 2) - np.power(r1, 2) + r1 * (r3 + r2 - r1))
    s3 = np.power(x, 3) * 4 * np.power(c, 2) + np.power(x, 2) * 3 * (np.power(c, 2) * 2 * (r3 + r1)) \
         + x * 2 * np.power(c, 2) * (np.power(a, 2) + np.power(b, 2) - np.power(c, 2) + np.power(r3, 2)
                                     + np.power(r1, 2) + 4 * r2 * (r3 + r1 - r2)) \
         + np.power(c, 2) * 2 * r2 * (np.power(a, 2) + np.power(b, 2) - np.power(c, 2) + np.power(r3, 2)
                                      + np.power(r1, 2) - np.power(r2, 2) + r2 * (r3 + r1 - r2))
    delta = np.power(x, 3) * 4 * (np.power(a, 2) + np.power(b, 2) + np.power(c, 2)) \
            + np.power(x, 2) * 6 *(np.power(a, 2) * (r1 + r2) + np.power(b, 2) * (r3 + r2) + np.power(c, 2) * (r3 + r1)) \
            + x * 2 * (np.power(a, 2) * (np.power(r1, 2) + 4 * r1 * r2 + np.power(r2, 2))
                       + np.power(b, 2) * (np.power(r3, 2) + 4 * r2 * r3 + np.power(r2, 2))
                       + np.power(c, 2) * (np.power(r3, 2) +  4 * r1 * r3 + np.power(r1, 2))) \
            + 2 * (np.power(a, 2) * r1 * r2 * (r1 + r2) + np.power(b, 2) * r2 * r3 * (r2 + r3)
                   + np.power(c, 2) * r1 * r3 * (r1 + r3))
    return s1 + s2 + s3 - delta

def radikand_strich_strich(x, a, b, c, r1, r2, r3):
    """
    2. Ableitung des Radikanden aus der Berechnung des Volumens eines allgemeinen Tetraeders von Euler nach x (Radius
    der zu platzierenden 4. Kugel).

    :param x: float - Radius zu platzierende Kugel 4
    :param a: float - Abstand zwischen den platzierten Kugeln 1 und 2
    :param b: float - Abstand zwischen den platzierten Kugeln 2 und 3
    :param c: float - Abstand zwischen den platzierten Kugeln 1 und 3
    :param r1: float - Radius platzierte Kugel 1
    :param r2: float - Radius platzierte Kugel 2
    :param r3: float - Radius platzierte Kugel 3
    :return: 2. Ableitung des Radikanden an der Stelle x = r4
    """
    s1 = 2 * (np.power(a, 2) * (b ** 2 + c ** 2 - a ** 2 + r1 ** 2 + r2 ** 2 + 4 * r3 * (r1 + r2 - r3))
                  + b ** 2 * (a ** 2 + c ** 2 - b ** 2 + r3 ** 2 + r2 ** 2 + 4 * r1 * (r3 + r2 - r1))
                  + c ** 2 * (a ** 2 + b ** 2 - c ** 2 + r3 ** 2 + r1 ** 2 + 4 * r2 * (r3 + r1 - r2))
                  - a ** 2 * (r1 ** 2 + 4 * r1 * r2 + r2 ** 2) - b ** 2 * (r3 ** 2 + 4 * r2 * r3 + r2 ** 2)
                  - c ** 2 * (r3 ** 2 + 4 * r1 * r3 + r1 ** 2))
    return s1

def calcPocket_v3(p1, p2, p3, r4, eps=1e-9):
    """
    Berechnung Mittelpunkt Pocket aus p1, p2, p3 und r4, sodass p4 in der gleichen Ebene wie p1, p2 und p3 liegt.
    p4 entspricht daher Hs. Bei p1, p2, p3 annähernd auf einer Geraden wird eine StraightException geworfen, bei einem
    unbekanntem Fehler ein UnknownError.

    :param p1: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 1
    :param p2: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 2
    :param p3: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 3
    :param r4: float - Radius Kugel 4
    :param eps: float - Kriterium zum Überprüfen der Parallelität der beiden Geraden
    :return: Boolean, np.array([x, y, z, r], dtype=float) - True und Pocketposition und -radius, wenn Pocketberechnung
        erfolgreich, sonst False und Dummy Pocketposition und -radius.
    """
    n = np.cross(p1[:3] - p2[:3], p3[:3] - p2[:3])
    if np.linalg.norm(n) < eps:  # Kreuzprodukt ist Nullvektor
        raise StraightException()
    try:
        geraden = calcSLines(p1, p2, p3, r4)
    except SpacingException:
        return False, np.zeros(4)  # Dummy-Pocket zurückgeben
    else: # Höhe Tetraeder h = 0
        g1 = geraden[0]
        g2 = geraden[1]
        if lineDistance(g1[1], g1[0], g2[1], g2[0]) < 0.00001:
            # Aufruf von lineDistance kann StraightException werfen
            hs = calcIntersectionPoint(g1, g2)
            p4 = np.concatenate([hs, np.array([r4])])
            return True, p4
    raise UnknownError('calcPocket')

@jit(nopython=True)
def a_pqformel(a, b, c, r1, r2, r3):
    """
    Bestimmung des Faktors a_pq zur Anwendung in der pq-Formel zur Berechnung der Nullstellen des Radikanden aus der
    Berechnung des Volumens eines allgemeinen Tetraeders von Euler.

    :param a: float - Abstand zwischen den platzierten Kugeln 1 und 2
    :param b: float - Abstand zwischen den platzierten Kugeln 2 und 3
    :param c: float - Abstand zwischen den platzierten Kugeln 1 und 3
    :param r1: float - Radius platzierte Kugel 1
    :param r2: float - Radius platzierte Kugel 2
    :param r3: float - Radius platzierte Kugel 3
    :return: float - Faktor a_pq
    """
    a = np.power(a, 2) * (np.power(b, 2) + np.power(c, 2) - np.power(a, 2) + np.power(r1, 2) + np.power(r2, 2)
                          + 4*r3 * (r1 + r2 - r3))\
        + np.power(b, 2) * (np.power(a, 2) + np.power(c, 2) - np.power(b, 2) + np.power(r3, 2) + np.power(r2, 2)
                            + 4*r1 * (r3 + r2 - r1))\
        + np.power(c, 2) * (np.power(a, 2) + np.power(b, 2) - np.power(c, 2) + np.power(r3, 2) + np.power(r1, 2)
                            + 4*r2 * (r3 + r1 - r2))\
        - np.power(a, 2) * (np.power(r1, 2) + 4*r1*r2 + np.power(r2, 2)) \
        - np.power(b, 2) * (np.power(r3, 2) + 4*r2*r3 + np.power(r2, 2))\
        - np.power(c, 2) * (np.power(r3, 2) + 4*r1*r3 + np.power(r1, 2))
    return a

@jit(nopython=True)
def b_pqformel(a, b, c, r1, r2, r3):
    """
    Bestimmung des Faktors b_pq zur Anwendung in der pq-Formel zur Berechnung der Nullstellen des Radikanden aus der
    Berechnung des Volumens eines allgemeinen Tetraeders von Euler.

    :param a: float - Abstand zwischen den platzierten Kugeln 1 und 2
    :param b: float - Abstand zwischen den platzierten Kugeln 2 und 3
    :param c: float - Abstand zwischen den platzierten Kugeln 1 und 3
    :param r1: float - Radius platzierte Kugel 1
    :param r2: float - Radius platzierte Kugel 2
    :param r3: float - Radius platzierte Kugel 3
    :return: float - Faktor b_pq
    """
    b = np.power(a, 2) * r3 * (np.power(b, 2) + np.power(c, 2) - np.power(a, 2) + np.power(r1, 2) + np.power(r2, 2)
                               - np.power(r3, 2) + r3 * (r1 + r2 - r3))\
        + np.power(b, 2) * r1 * (np.power(a, 2) + np.power(c, 2) - np.power(b, 2) + np.power(r3, 2) + np.power(r2, 2)
                                 - np.power(r1, 2) + r1 * (r3 + r2 - r1))\
        + np.power(c, 2) * r2 * (np.power(a, 2) + np.power(b, 2) - np.power(c, 2) + np.power(r3, 2) + np.power(r1, 2)
                                 - np.power(r2, 2) + r2 * (r3 + r1 - r2))\
        - np.power(a, 2) * (np.power(r1, 2) * r2 + r1 * np.power(r2, 2)) \
        - np.power(b, 2) * (np.power(r3, 2) * r2 + r3 * np.power(r2, 2)) \
        - np.power(c, 2) * (r1 * np.power(r3, 2) + np.power(r1, 2) * r3)
    return 2 * b

@jit(nopython=True)
def c_pqformel(a, b, c, r1, r2, r3):
    """
    Bestimmung des Faktors c_pq zur Anwendung in der pq-Formel zur Berechnung der Nullstellen des Radikanden aus der
    Berechnung des Volumens eines allgemeinen Tetraeders von Euler.

    :param a: float - Abstand zwischen den platzierten Kugeln 1 und 2
    :param b: float - Abstand zwischen den platzierten Kugeln 2 und 3
    :param c: float - Abstand zwischen den platzierten Kugeln 1 und 3
    :param r1: float - Radius platzierte Kugel 1
    :param r2: float - Radius platzierte Kugel 2
    :param r3: float - Radius platzierte Kugel 3
    :return: float - Faktor c_pq
    """
    c = np.power(a, 2) * np.power(r3, 2) * (np.power(b, 2) + np.power(c, 2) - np.power(a, 2) + np.power(r1, 2)
                                            + np.power(r2, 2) - np.power(r3, 2)) \
        + np.power(b, 2) * np.power(r1, 2) * (np.power(a, 2) + np.power(c, 2) - np.power(b, 2) + np.power(r3, 2)
                                              + np.power(r2, 2) - np.power(r1, 2))\
        + np.power(c, 2) * np.power(r2, 2) * (np.power(a, 2) + np.power(b, 2) - np.power(c, 2) + np.power(r3, 2)
                                              + np.power(r1, 2) - np.power(r2, 2)) \
        - np.power(a, 2) * np.power(b, 2) * np.power(c, 2) - np.power(a, 2) * np.power(r1, 2) * np.power(r2, 2) \
        - np.power(b, 2) * np.power(r2, 2) * np.power(r3, 2) - np.power(c, 2) * np.power(r1, 2) * np.power(r3, 2)
    return c

@jit(nopython=True)
def pqformel(a, b, c, r1, r2, r3):
    """
    Anwendung der pq-Formel zur Berechnung der Nullstellen des Radikanden (Polynom vom Grad 2) aus der Berechnung des
    Volumens eines allgemeinen Tetraeders von Euler.

    :param a: float - Abstand zwischen den platzierten Kugeln 1 und 2
    :param b: float - Abstand zwischen den platzierten Kugeln 2 und 3
    :param c: float - Abstand zwischen den platzierten Kugeln 1 und 3
    :param r1: float - Radius platzierte Kugel 1
    :param r2: float - Radius platzierte Kugel 2
    :param r3: float - Radius platzierte Kugel 3
    :return: Boolean, float, float - Boolsche Variable, die angibt, ob mindestens eine Nullstelle gefunden wurde, und
        die bestimmten Nullstellen
    """
    a_pq = a_pqformel(a, b, c, r1, r2, r3)
    b_pq = b_pqformel(a, b, c, r1, r2, r3)
    c_pq = c_pqformel(a, b, c, r1, r2, r3)
    p = b_pq / a_pq
    q = c_pq / a_pq
    D = np.power((p/2), 2) - q
    if D < 0:
        return False, 0, 0 # 2 Dummy-Nullstellen zurückgeben
    elif D == 0:
        x1 = - (p/2)
        return True, x1, x1 # 1 Dummy-Nullstelle zurückgeben
    else: # D > 0:
        x1 = - (p/2) + np.sqrt(D)
        x2 = - (p / 2) - np.sqrt(D)
        return True, x1, x2

def calcPocket(p1, p2, p3, r4, pOverlap, methodOverlap='single'):
    """
    Berechnung Mittelpunkt Pocket als berührende bzw. überlappende Position aus p1, p2, p3 und r4, falls möglich.
    Sonst StraightException (p1, p2 und p3 liegen auf einer Geraden), OverlapException (max. erlaubte Überlappung
    überschritten), UnknownError (unbekannter Fehler). Überlappende Position wird über Nullstellensuche des Radikanden
    berechnet.

    :param p1: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 1
    :param p2: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 2
    :param p3: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 3
    :param r4: float - Radius Kugel 4
    :param pOverlap: float - maximal erlaubter relativer Überlapp
    :param methodOverlap: string - Methode, wie der Überlapp berechnet wird
        single: als Verhältnis aus überlappendem Volumen zum Volumen genau einer Kugel
        average: als Mittel zwischen allen benachbarten Kugeln
    :return: Boolean, np.array([x, y, z, r], dtype=float), case - True und Pocketposition und -radius, wenn
        Pocketberechnung erfolgreich, sonst False und Dummy Pocketposition und -radius. case ist ein Enum-Wert aus
        specialCases.py und gibt an, welcher Gruppe von Sonder- und Fehlerfällen die Pocketberechnung ggf. zugeordnet
        wird.
    """
    case = SpecialCase.DEFAULT
    n = np.cross(p1[:3] - p2[:3], p3[:3] - p2[:3])
    try:
        geraden = calcSLines(p1, p2, p3, r4)
    except SpacingException:
        case = SpecialCase.DISTANCE
        return False, np.zeros(4), case  # Dummy-Pocket zurückgeben
    else:
        g1 = geraden[0]
        g2 = geraden[1]
        if lineDistance(g1[1], g1[0], g2[1], g2[0]) < 0.00001:  # Aufruf von lineDistance kann StraightException werfen
            hs = calcIntersectionPoint(g1, g2)
            try: # Höhe Tetraeder
                h = heightTetraeder(p1, p2, p3, r4)
            except SpacingException:
                case = SpecialCase.HEIGHT
                a = np.linalg.norm(p1[:3]-p2[:3])
                b = np.linalg.norm(p2[:3]-p3[:3])
                c = np.linalg.norm(p1[:3]-p3[:3])
                r1 = p1[3]
                r2 = p2[3]
                r3 = p3[3]
                success, x1, x2 = pqformel(a, b, c, r1, r2, r3)
                if success == False:
                    raise SpacingException()
                elif ((x1 <= 0 or x1 > r4) and (x2 <= 0 or x2 > r4)):
                    return False, np.zeros(4), case
                elif (x1 > 0 and x1 <= r4) and (x2 > 0 and x2 <= r4):
                    h = 0
                    if x1 >= x2:
                        res = x1
                    else:
                        res = x2
                elif x1 > 0 and x1 <= r4:
                    h = 0
                    res = x1
                else: # x2 > 0 and x2 <= r4 * 1.005
                    h = 0
                    res = x2
                case = SpecialCase.NEWRADIUS
                print('--------------------------------------------------------------------------')
                #print("\tneuer Radius: ", res)

                #res = scipy.optimize.newton(radikand, r4, radikand_strich, args=(a, b, c, r1, r2, r3), full_output=True)
                #print(radikand(res[0], a, b, c, r1, r2, r3))
                #if (res[0] <= 0) or (res[0] > r4 * 1.025) or res[1].converged == False:
                #    return False, np.zeros(4)
                #else:
                    #r4 = res[0]
                success, p4 = calcPocket_v3(p1, p2, p3, res) # Kugelposition mit r_neu mit h=0 berechnen
                if methodOverlap == 'average':
                    relOverlap = absoluteOverlap(p4[:3], r4, p1, p2, p3) / \
                                 (sphereVolume(p1[3]) + sphereVolume(p2[3]) + sphereVolume(p3[3]))
                    if success == True and relOverlap > pOverlap:
                        raise OverlapException(pOverlap)
                    else:
                        p4[3] = r4
                        return success, p4, case
                else : # methodOverlap == 'single'
                    ovl1 = calcOverlap(p1, p4)
                    ovl11 = ovl1 / sphereVolume(p1[3])
                    ovl12 = ovl1 / sphereVolume(r4)
                    ovl2 = calcOverlap(p2, p4)
                    ovl21 = ovl2 / sphereVolume(p2[3])
                    ovl22 = ovl2 / sphereVolume(r4)
                    ovl3 = calcOverlap(p3, p4)
                    ovl31 = ovl3 / sphereVolume(p3[3])
                    ovl32 = ovl3 / sphereVolume(r4)
                    if success == True and (ovl11 > pOverlap or ovl12 > pOverlap or ovl21 > pOverlap or ovl22 > pOverlap or ovl31 > pOverlap or ovl32 > pOverlap):
                        raise OverlapException(pOverlap)
                    else:
                        p4[3] = r4
                        return success, p4, case
            else:
                p41 = hs + (h / np.linalg.norm(n)) * n
                p42 = hs - (h / np.linalg.norm(n)) * n
                if p41[2] >= p42[2]:
                    p4 = np.concatenate([p41, np.array([r4])])
                else:
                    p4 = np.concatenate([p42, np.array([r4])])
                return True, p4, case
    raise UnknownError('calcPocket')

def calcPocket_optOverlap(p1, p2, p3, r4, pOverlap, methodOverlap):
    """
    Berechnung Mittelpunkt Pocket als berührende bzw. überlappende Position aus p1, p2, p3 und r4, falls möglich.
    Sonst StraightException (p1, p2 und p3 liegen auf einer Geraden), OverlapException (max. erlaubte Überlappung
    überschritten), UnknownError (unbekannter Fehler). Überlappende Position wird über ein Optimierungsverfahren zum
    Finden einer minimalen Überlappung berechnet.

    :param p1: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 1
    :param p2: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 2
    :param p3: np.array([x, y, z, r], dtype=float) - Kugelposition und Radius Kugel 3
    :param r4: float - Radius Kugel 4
    :param pOverlap: float - maximal erlaubter relativer Überlapp
    :param methodOverlap: string - Methode, wie der Überlapp berechnet wird
        single: als Verhältnis aus überlappendem Volumen zum Volumen genau einer Kugel
        average: als Mittel zwischen allen benachbarten Kugeln
    :return: Boolean, np.array([x, y, z, r], dtype=float), case - True und Pocketposition und -radius, wenn
        Pocketberechnung erfolgreich, sonst False und Dummy Pocketposition und -radius. case ist ein Enum-Wert aus
        specialCases.py und gibt an, welcher Gruppe von Sonder- und Fehlerfällen die Pocketberechnung ggf. zugeordnet
        wird.
    """
    n = np.cross(p1[:3] - p2[:3], p3[:3] - p2[:3])
    try:
        geraden = calcSLines(p1, p2, p3, r4)
    except SpacingException:
        return False, np.zeros(4)  # Dummy-Pocket zurückgeben
    else:
        g1 = geraden[0]
        g2 = geraden[1]
        if lineDistance(g1[1], g1[0], g2[1], g2[0]) < 0.00001:  # Aufruf von lineDistance kann StraightException werfen
            hs = calcIntersectionPoint(g1, g2)
            #print("\tx0:", hs)
            # Höhe Tetraeder
            try:
                h = heightTetraeder(p1, p2, p3, r4)
            except SpacingException:
                x0 = hs.copy()
                x0[2] += min([p1[3], p2[3], p3[3], r4])  # Optimierung soll den höheren der beiden Punkte finden
                #x0[2] += 0.1
                #print("\tx0:", x0)
                #if np.linalg.norm(x0-p1[:3])*1.001 > p1[3]+r4 or np.linalg.norm(x0-p2[:3])*1.001 > p2[3]+r4 or np.linalg.norm(x0-p3[:3])*1.001 > p3[3]+r4:
                #    print("\tif")
                #    x0 = (p1[:3] + p2[:3] + p3[:3]) / 3
                #    x0[2] += min([p1[3], p2[3], p3[3], r4])
                if methodOverlap == 'absoluteVolume':
                    res = optimizeOverlap(p1, p2, p3, r4, x0, method='absoluteVolume')
                    kind = 'absolute'
                else:  # methodOverlap == 'relativeVolume'
                    res = optimizeOverlap(p1, p2, p3, r4, x0, method='relativeVolume')
                    kind = 'relative'
                relOverlap = absoluteOverlap(res.x, r4, p1, p2, p3) / \
                             (sphereVolume(p1[3]) + sphereVolume(p2[3]) + sphereVolume(p3[3]))
                if res.success == True and relOverlap > pOverlap: # TODO: was ist der prozentuale Überlapp?
                    #print("\t", relOverlap)
                    raise OverlapException(pOverlap, kind)
                else:
                    return res.success, np.concatenate([res.x, np.array([r4])])
            else:
                p41 = hs + (h / np.linalg.norm(n)) * n
                p42 = hs - (h / np.linalg.norm(n)) * n
                if p41[2] >= p42[2]:
                    p4 = np.concatenate([p41, np.array([r4])])
                else:
                    p4 = np.concatenate([p42, np.array([r4])])
                #print(f"\treguläres Ergebnis: {p4}")
                return True, p4
    raise UnknownError('calcPocket')

@jit(nopython=True)
def sphereSegmentVol(radius, h):
    """
    Berechnung des Volumens eines Kugelsegments einer Kugel mit Radius radius in der Höhe h.

    :param radius: float - Radius der Kugel
    :param h: float - Höhe des Kugelsegmente ausgehend von der Kugeloberfläche
    :return: float - Volumen Kugelsegment
    """
    return np.pi / 3 * np.power(h, 2) * (3 * radius - h)

@jit(nopython=True)
def sphereVolume(radius):
    """
    Berechnung des Volumens der Kugel mit dem Radius radius.

    :param radius: float - Kugelradius
    :return: float - Kugelvolumen
    """
    return 4 / 3 * np.pi * np.power(radius, 3)

@jit(nopython=True)
def calcOverlap(k1, k2):
    """
    Berechnung des überlappenden Volumens zweier sich schneidender Kugeln.

    :param k1: np.array(4,) - Kugel 1 mit Mittelpunkt M1 (k1[:3]) und Radius r1 (k1[3])
    :param k2: np.array(4,) - Kugel 2 mit Mittelpunkt M2 (k2[:3]) und Radius r2 (k2[3])
    :return: float - sich überlappendes Volumen
    """
    # Schnittbedingung
    if np.linalg.norm(k1[:3] - k2[:3]) >= k1[3] + k2[3]:
        return 0
    elif np.linalg.norm(k1[:3] - k2[:3]) <= np.abs(k1[3] - k2[3]):
        if k1[3] < k2[3]:
            return sphereVolume(k1[3])
        else:
            return sphereVolume(k2[3])
    # ||n|| = sqrt(4 * (x1-x2)² + 4 * (y1-y2)² + 4 * (z1-z2)²)
    norm_n = np.sqrt(4 * np.power(k1[0] - k2[0], 2) + 4 * np.power(k1[1] - k2[1], 2) + 4 * np.power(k1[2] - k2[2], 2))
    # Abstand M1 zu Schnittebene der beiden Kugeln:
    d = np.sum(np.power(k2[:3], 2)) - np.sum(np.power(k1[:3], 2)) + np.power(k1[3], 2) - np.power(k2[3], 2)
    dE1 = np.abs((2 * k1[0] * (k1[0] - k2[0]) + 2 * k1[1] * (k1[1] - k2[1]) + 2 * k1[2] * (k1[2] - k2[2]) + d) / norm_n)
    dE2 = np.abs((2 * k2[0] * (k1[0] - k2[0]) + 2 * k2[1] * (k1[1] - k2[1]) + 2 * k2[2] * (k1[2] - k2[2]) + d) / norm_n)
    dist = np.linalg.norm(k1 - k2)
    h1 = k1[3] - dE1
    h2 = k2[3] - dE2
    if dE1 <= dist and dE2 <= dist:
        volOverlap = sphereSegmentVol(k1[3], h1) + sphereSegmentVol(k2[3], h2)
    elif dE1 > dist:
        volOverlap = sphereSegmentVol(k1[3], h1) + (sphereVolume(k2[3]) - sphereSegmentVol(k2[3], h2))
    elif dE2 > dist:
        volOverlap = (sphereVolume(k1[3]) - sphereSegmentVol(k1[3], h1)) + sphereSegmentVol(k2[3], h2)
    return volOverlap

@jit(nopython=True)
def absoluteOverlap(x, r4, p1, p2, p3):
    """
    Berechnung des Volumens durch Überlappung von Kugel 4 mit den Kugeln in sphereList.

    :param x: np.array([x, y, z], dtype=float) - Mittelpunkt Kugel 4
    :param r4: float - Radius Kugel 4
    :param sphereList: list - Liste aus Kugeln (np.array([x, y, z, r], dtype=float))
    :return: Summe des absoluten Überlapps zwischen Kugel 4 und allen Kugeln in der Liste
    """
    #k4 = np.concatenate([x, np.array([r4])])
    k4 = np.zeros(4)
    k4[:3] = x
    k4[3] = r4
    sphereList = [p1, p2, p3]
    ovl = 0
    for sphere in sphereList:
        ovl += calcOverlap(sphere, k4)
    return ovl

@jit(nopython=True)
def relativeOverlap(x, r4, p1, p2, p3):
    """
    Berechnung des Volumens durch Überlappung von Kugel 4 mit den Kugeln in sphereList im Verhältnis zum Volumen der
    Kugeln in sphereList.

    :param x: np.array([x, y, z], dtype=float) - Mittelpunkt Kugel 4
    :param r4: float - Radius Kugel 4
    :param sphereList: list - Liste aus Kugeln (np.array([x, y, z, r], dtype=float))
    :return: Summe des absoluten Überlapps zwischen Kugel 4 und allen Kugeln in der Liste
    """
    k4 = np.zeros(4)
    k4[:3] = x
    k4[3] = r4
    sphereList = [p1, p2, p3]
    ovl = 0
    for sphere in sphereList:
        ovl += (calcOverlap(sphere, k4) / sphereVolume(sphere[3]))
    return ovl


def optimizeOverlap(k1, k2, k3, r4, x0, method="relativeVolume"):
    """
    Ruft ein iteratives Optimierungsverfahren zur Bestimmung der Kugel 4 mit möglichst geringem Überlapp auf. Wenn
    die Optimierung erfolgreich war, wird die ermittelte Position zurückgegeben, sonst eine TetrahedronException.
    :param k1: np.array([x, y, z, r], dtype=float) - Kugel 1 mit Mittelpunkt M1 (k1[:3]) und Radius r1 (k1[3])
    :param k2: np.array([x, y, z, r], dtype=float) - Kugel 2 mit Mittelpunkt M2 (k2[:3]) und Radius r2 (k2[3])
    :param k3: np.array([x, y, z, r], dtype=float) - Kugel 3 mit Mittelpunkt M3 (k3[:3]) und Radius r3 (k3[3])
    :param r4: float - Radius der Kugel 4
    :param x0: np.array([x, y, z], dtype=float) - Startposition der Kugel 4 (x, y, z)
    :param method: string - Methode wie der Überlapp ermittelt werden soll
    :return: Ergebnis der Optimierungsmethode von scipy
    """
    cons = ({'type': 'ineq', 'fun': lambda x: k1[3] + r4 - np.linalg.norm(x - k1[:3])},
            {'type': 'ineq', 'fun': lambda x: k2[3] + r4 - np.linalg.norm(x - k2[:3])},
            {'type': 'ineq', 'fun': lambda x: k3[3] + r4 - np.linalg.norm(x - k3[:3])})
    #nlc1 = scipy.optimize.NonlinearConstraint(lambda x: np.linalg.norm(k1[:3] - x), 0, k1[3] + r4)
    #nlc2 = scipy.optimize.NonlinearConstraint(lambda x: np.linalg.norm(k2[:3] - x), 0, k2[3] + r4)
    #nlc3 = scipy.optimize.NonlinearConstraint(lambda x: np.linalg.norm(k3[:3] - x), 0, k3[3] + r4)
    if method == "relativeVolume":
        res = scipy.optimize.minimize(relativeOverlap, x0, args=(r4, k1, k2, k3), method='COBYLA', constraints=cons)
        ovl = relativeOverlap(res.x, r4, k1, k2, k3)
    elif method == "absoluteVolume":
        res = scipy.optimize.minimize(absoluteOverlap, x0, args=(r4, k1, k2, k3), method='COBYLA', constraints=cons)
        #res = scipy.optimize.minimize(absoluteOverlap, x0, args=(r4, k1, k2, k3), method='SLSQP', constraints=cons)
        #res = scipy.optimize.minimize(absoluteOverlap, x0, args=(r4, k1, k2, k3), method='trust-constr', constraints=[nlc1, nlc2, nlc3])
        ovl = absoluteOverlap(res.x, r4, k1, k2, k3)
    #if res.success == True:
    #print("\n",res)
        #print(f"\tÜberlappendes Ergebnis gefunden: {res.x}")
        #print('\tAbstände neue Kugel zu andern Kugeln', np.abs(np.linalg.norm(res.x - k1[:3]) - (r4 + k1[3])),
        #      np.abs(np.linalg.norm(res.x - k2[:3]) - (r4 + k2[3])),
        #      np.abs(np.linalg.norm(res.x - k3[:3]) - (r4 + k3[3])))
        #print(f"\t{method}: {ovl}")
    #else:
    #    print("\tKein überlappendes Ergebnis gefunden.")
    return res

def generateVTK(spheres, test):
    """
    Testmethode zum Erstellen von VTK-Dateien.

    :param spheres:
    :param test:
    :return:
    """
    datei = "../resources/" + test + ".vtk"
    file1 = open(datei, "w")
    lines = ["# vtk DataFile Version 3.0\n", "3D-Darstellung Kugelpackung\n", "ASCII\n", "DATASET POLYDATA\n",
             f"POINTS {len(spheres)} double\n"]
    # file1.writelines(lines)
    for sp in spheres:
        lines.append(f"{sp[0]} {sp[1]} {sp[2]}\n")
    # lines = [f"{p1[0]} {p1[1]} {p1[2]}\n", f"{p2[0]} {p2[1]} {p2[2]}\n", f"{p3[0]} {p3[1]} {p3[2]}\n", f"{p41[0]} {p41[1]} {p41[2]}\n", f"{p42[0]} {p42[1]} {p42[2]}\n"]
    file1.writelines(lines)
    lines = ["\n", f"POINT_DATA {len(spheres)}\n", "SCALARS diameters double\n", "LOOKUP_TABLE default\n"]
    # file1.writelines(lines)
    for sp in spheres:
        lines.append(f"{sp[3] * 2}\n")
    # lines = [f"{p1[3] * 2}\n", f"{p2[3] * 2}\n", f"{p3[3] * 2}\n", f"{p41[3] * 2}\n", f"{p42[3] * 2}\n"]
    file1.writelines(lines)
    file1.close()


def generateCSV(testdata, datei):
    """
    Testdatei zum Erstellen einer csv-Datei.

    :param testdata:
    :param datei:
    :return:
    """
    datei = "../resources/" + datei + ".csv"
    df = pd.DataFrame(testdata)
    df.to_csv(datei)