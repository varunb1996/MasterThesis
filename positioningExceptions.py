

"""
3 benachbarte Punkte liegen auf einer Geraden, daher kann keine Pocket berechnet werden
"""
class StraightException(Exception):
    # def __init__(self, p1, p2, p3):
    #     self.p1 = p1
    #     self.p2 = p2
    #     self.p3 = p3

    def __str__(self):
        #return f"Die Punkte {self.p1}, {self.p2}, {self.p3} liegen auf einer Geraden."
        return "Die 3 Punkte zur Pocketberechnung liegen auf einer Geraden."

"""
Der maximal erlaubte prozentuale Überlapp ist überschritten
"""
class OverlapException(Exception):
    def __init__(self, p_o, kind="relative"):
        self.p = p_o
        self.kind = kind

    def __int__(self):
        self.p = -1

    def __str__(self):
        if (self.p >= 0):
            return f"Der {self.kind} Überlapp ist größer {self.p * 100} %."
        else:
            return "Der Überlapp ist zu groß."


"""
Kugeln sind zu weit entfernt, um eine neue Kugel mit gegebenen Radius r4 zu platzieren
"""
class SpacingException(Exception):
    def __init__(self, radius):
        self.r4 = radius

    def __init__(self):
        self.r4 = -1

    def __str__(self):
        if self.r4 >= 0:
            return f"Abstand zwischen den 3 Kugeln zu groß zum Platzieren einer neue Kugel mit Radius {self.r4}."
        else:
            return f"Abstand zwischen den 3 Kugeln zu groß zum Platzieren einer neue Kugel."

"""
Für unbekannte Fehlermeldungen (Ursache muss ermittelt werden)
"""
class UnknownError(Exception):
    def __init__(self, method):
        self.method_name = method

    def __str__(self):
        return f"Es ist ein unbekannter Fehler in der Methode {self.method_name} aufgetreten."