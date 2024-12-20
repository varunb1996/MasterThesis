package kupa_org;

import java.util.ArrayList;

/**
 * Klasse Kugel
 * Die Klasse Kugel ermoeglicht die Darstellung einer gleichmaessigen Kugel im dreidimensionalen Raum.
 * Dabei wird eine Kugel definiert durch ihre Attribute mitte (Mittelpunkt der Kugel mit x-, y- und z-Koordinate)
 * und radius (Kugelradius).
 * 
 * Zudem erhaelt jede Kugel eine nachbarliste, die alle Kugeln im gleichen System/Raum umfasst,
 * für deren Abstand d zwischen den Mittelpunkten gilt: d < 4*radius 
 * Die Kugeln liegen also so nah beieinander, dass eine weitere Kugel platziert werden kann, 
 * sodass sie die aktuelle Kugel und ihre Nachbarkugel beruehrt. 
 * 
 * testpunkte: ist eine Liste von Punkten auf der Kugeloberfläche 
 *
 * @author Karin Havemann
 * @version Februar 2021
 */

public class Kugel {
  private Punkt mitte; // Mittelpunkt der Kugel
  private double radius; // Kugelradius in mikrometer
  private double rAussen; // ausserer Kugelradius
  private ArrayList<Punkt> testpunkte;
  private ArrayList<Kugel> nachbarliste;

  // Konstruktor
  public Kugel (Punkt mp, double r) {
    mitte = mp;
    radius = r;
    rAussen = radius;
    testpunkte = new ArrayList<>();
    nachbarliste = new ArrayList<>();
  }
  
  public Kugel (double x, double y, double z, double r) {
	    mitte = new Punkt(x, y, z);
	    radius = r;
	    rAussen = radius;
	    testpunkte = new ArrayList<>();
	    nachbarliste = new ArrayList<>();
	  }

  // Getter-Methode
  public Punkt getKugelmitte() {
    return mitte;
  }

  public double getKugelradius() {
    return radius;
  }
  
  public ArrayList<Punkt> getTestpunkte() {
	  return testpunkte;
  }
  
  public ArrayList<Kugel> getNachbarn() {
	  return nachbarliste;
  }
  
  public double getAussenradius() {
	  return rAussen;
  }
  
  public void setAussenradius(double r) {
	  rAussen = r;
  }

  // toString-Methode
  @Override
  public String toString() {
    return mitte + "\t r: " + radius;
  }
  
  /**
   * Fuegt die uebergebene Kugel zur Nachbarschaftsliste hinzu. 
   * Nachbarschaft von Kugeln ist symmetrisch:
   * Kugel a Nachbar von Kugel b <=> Kugel b Nachbar von Kugel a
   * @param nachbar
   */
  public void addNachbar(Kugel nachbar) {
	  this.nachbarliste.add(nachbar);
	  nachbar.getNachbarn().add(this);
  }
  
  /**
   * Verschiebt die Kugel in x, y und z Richtung um einen zufaelligen Wert abhaengig von eps
   * @param eps
   */
  public void randomMove(double eps) {
	  //TODO: Berechnung ueberpruefen (ggf. kuerzen)
	  double rand_x = (-1 + 2 * Math.random()) * eps * 0.5;
	  double rand_y = (-1 + 2 * Math.random()) * eps * 0.5;
	  double rand_z = (-1 + 2 * Math.random()) * eps * 0.5;
	  mitte.addX(rand_x);
	  mitte.addY(rand_y);
	  mitte.addZ(rand_z);  
  }
  
  /**
   * Gibt den Abstand zwischen den Oberflaechen der aktuellen und der uebergebenen Kugel zurueck
   * @param kugel
   * @return
   */
  public double abstand(Kugel kugel) {
	  return mitte.abstand(kugel.mitte) - radius - kugel.radius;
  }
  
  /**
   * Auf der Kugeloberflaeche werden anzTestpunkte im gleichmaessigen Abstand generiert. 
   * Jeder erzeugt Testpunkt wird in der testpunkt-Liste gespeichert
   * @param anzTestpunkte
   */
  public void generiereTestpunkte(int anzTestpunkte) {
	  double theta;
	  double phi;
	  
	  double a = 4 * Math.PI * Math.pow(radius, 2) / anzTestpunkte; // quadratische Flaeche fuer einen Testpunkt
	  double d = Math.sqrt(a); // Naehrung fuer die Seitenlaenge der Flaeche eines Testpunkts
	  
	  int M_theta = (int) (Math.PI * radius / d + 0.5); // vertikales Unterteilen der Kugeloberflaeche in Kreise mit gleichem Abstand d_theta
	  double d_theta = Math.PI * radius / M_theta;
	  
	  double d_phi = a/d_theta; // horizontaler Abstand zwischen den Testpunkten auf Kugeloberflaeche
	  
	  for (int m = 0; m < M_theta; m++) {
		  theta = Math.PI * (m + 0.5)/M_theta; // vertikaler Winkel der Position des Testpunkts auf der Kugeloberflaeche
		  
		  int M_phi = (int) (2 * Math.PI * Math.sin(theta) * radius / d_phi + 0.5); // horizontales Unterteilen der einzelnen Kreise in Positionen mit gleichem Abstand
		  
		  for (int n = 0; n < M_phi; n++) {
			  phi = 2 * Math.PI * n / M_phi; 
			  // Berechnung der Koordinaten eines Testpunkts
			  double x = radius * Math.sin(theta) * Math.cos(phi) + mitte.getX();
			  double y = radius * Math.sin(theta) * Math.sin(phi) + mitte.getY();
			  double z = radius * Math.cos(theta) + mitte.getZ();
			  testpunkte.add(new Punkt(x, y, z)); // Testpunkt zur Liste hinzufuegen
		  }
		  
	  }
  }
  
  /**
   * Leeren die testpunkt-Liste
   */
  public void loescheTestpunkte() {
	  testpunkte.clear();
  }
}
