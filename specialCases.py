"""
@Author: Karin Havemann
@Date: Juli 2022

Enum zum Unterscheiden verschiedener Sonderfälle, die bei Kugelpackungen aus Kugeln unterschiedlicher Größe auftreten
können
"""

from enum import Enum

class SpecialCase(Enum):
    DEFAULT = 0 # Normalfall
    STRAIGHT = 1 # Mittelpunkte M1, M2 und M3 liegen annähernd auf einer Geraden
    DISTANCE = 2 # zu weiter Abstand zwischen Kugeln
    HEIGHT = 3 # Höhe der Pyramide lässt sich nicht berechnen
    NEWRADIUS = 4 # neuer Radius für zu platzierende Kugel konnte gefunden werden
    OVERLAPCALCPOC = 5 # Zu großer Überlapp von K4 zu K1, K2 oder K3
    OVERLAPALLNEI = 6 # Zu großer Überlapp von K4 zu irgendeiner Nachbarkugel

def writeSpecialCase(counts, datei):
    """
    Methode zum Schreiben der Anzahl Sonderfälle in eine Datei.

    :param counts: [] - Anzahl der Sonderfälle für die verschiedenen Special Cases.
    :param datei: String - Name der Datei
    """
    n_cases = 8
    describtion = ['Anzahl Aufrufe CalcPocket', 'Kugeln auf einer Geraden', 'Abstand zwischen 2 Kugeln zu groß',
                   'Pyramidenhöhe kann nicht berechnet werden', 'mit neuem Radius kann Position berechnet werden',
                   'Überlapp in Pocketberechung', 'Überlapp aller Nachbarkugeln',
                   'Anzahl Kugeln, die mit größerem Radius platziert wurden, als die Position berechnet wurde']
    with open(datei, "w") as f:
        for i in range(n_cases):
            f.write(f"{describtion[i]}: {counts[i]}\n")

