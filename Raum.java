package kupa_org;
import java.awt.geom.Ellipse2D;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

import javax.imageio.ImageIO;

/**
 * Raum repraesentiert einen dreidimensionalen Raum, in der zu uebergebenen Ausdehung x, y, z.
 * Einheit der Raumgroesse: µm
 * Die z-Richtung steht für die Tiefe des Raumes, in der hintereinander gestaffelt in festen Abstaenden die einzelnen Bildebenen zu finden sind.
 * Jede Bildebene hat die gleiche Ausdehung in x- und y- Richtung, wie der uebergeordnete Raum.
 *
 * @author Karin Havemann
 * @version Mai 2020
 */

public class Raum {
  private Bildebene[] xyEbenen; // Array aus verschiedenen Bildebenen, die Querschnitte durch den Raum darstellen
  private int x;
  private int y;
  private int z; // Groesse des Raumes: hoehe*breite*tiefe in µm
  private final int schwarz = -16777216; // Farbwert von schwarzen Pixeln

  // Konstruktor
  public Raum(int breite, int hoehe, int tiefe) {
    this.x = (int) (breite);
    this.y = (int) (hoehe);
    this.z = (int) (tiefe);
  }

  // Getter-Methoden
  public int getX() {
    return x;
  }

  public int getY() {
    return y;
  }

  public int getZ() {
    return z;
  }

  public Bildebene[] getRaum() {
    return xyEbenen;
  }
  
  public long getVolumen() {
	  return x * y * z;
  }
  
  public void erzeugeBildebenen() {
	  // Array aus den verschiedenen Bildebenen erstellen
	  this.xyEbenen = new Bildebene[this.z + 1];
	  for (int i = 0; i < xyEbenen.length; i++) {
		  xyEbenen[i] = new Bildebene(this.x, this.y);
	  }
  }

  /**
   * Methode zum Zeichnen eines Kugelquerschnitts als gefuellten Kreis mit dem Mittelpunkt (x,y) und dem Radius radius in der Bildebene z des Bildebenenarrays xyEbenen.
   *
   * @param z       gibt an in welcher Bildebene des Arrays xyEbenen der Kugelquerschnitt gezeichnet werden soll
   * @param x, y    Mittelpunkt des Kreises
   * @param radius  Radius des Kreises
   */
  public void zeichneKreis (int z, double x, double y, double radius) {
    double kreisEckeX = x - radius;
    double kreisEckeY = y - radius;
    double durchmesser = 2 * radius;
    // in dem Rechteck mit dem oberen, linken Eckpunkt (kreisEckeX, kreisEckeY) und der Breite und Hoehe durchmesser wird ein groesstmoeglicher Kreis erzeugt
    Ellipse2D.Double kreis = new Ellipse2D.Double(kreisEckeX, kreisEckeY, durchmesser, durchmesser);
    xyEbenen[z].zeichneForm(kreis, true);
  }

  /**
   * Abspeichern der einzelnen Bildebenen als Bilddateien in einem gemeinsamen Ordner
   * @param praefix - ggf. Praefix fuer Ordnerbezeichnung 
   * @param suffix - ggf. Suffix fuer Ordnerbezeichnung 
   */
  public void generiereBildserie(String suffix, String distribution, int minRadius, int maxRadius) {
    String filename;
    String dirname;
    if (minRadius != maxRadius) {
    	dirname = "../resources/output/" + this.getX() + "x" + this.getY() + "x" + this.getZ() + "_" + distribution + "_" + minRadius + "_" + maxRadius + suffix + "_Bildserie";
    } else {
    	dirname = "../resources/output/" + this.getX() + "x" + this.getY() + "x" + this.getZ() + "_" + minRadius + "_" + maxRadius + suffix + "_Bildserie";
    }
    File directory = new File(dirname);
    directory.mkdir(); // Ordner anlegen
    for (int i = 0; i < xyEbenen.length; i++) {
      try {
        filename = "kugelEbene_" + i + ".png"; // Dateiname der i-ten Bildebene
        File output = new File (directory, filename);
        BufferedImage image = xyEbenen[i].getImage();
        ImageIO.write(image, "png", output);
      } catch (IOException e) {
        System.out.println(e.getMessage());
      }
    }
  }

  /**
   * Zaehlt die Anzahl freier Pixel und die Anzahl aller Pixel ueber alle Bildebenen im Raum
   * und berechnet daraus die Porositaet der nachgebildeten Mikrostruktur.
   * @return Porositaet der nachgebildeten Mikrostruktur (zwischen 0 und 1)
   */
  public double getPorositaet() {

	  long freiePixel = 0;
	  long gesamtPixel = 0;
	  for (int i = 0; i < xyEbenen.length; i++) {
		  freiePixel = freiePixel + xyEbenen[i].zaehleFreiePixel(schwarz); 
		  gesamtPixel = gesamtPixel + xyEbenen[i].zaehleGesamtPixel();
	  }
	  //System.out.println("Anzahl freie Pixel: "+freiePixel);
	  //System.out.println("Anzahl alle Pixel: "+gesamtPixel);
	  double porositaet = (double) (freiePixel)/gesamtPixel;
	  return porositaet;
  }
  
  /**
   * Berechnung der Porositaet des mit Kugeln gefuellten Raums
   * Methode liefert nur sinnvolles Ergebniss, wenn Kugeln sich nicht ueberlappen 
   * und alle den gleichen Radius haben
   * 
   * Dient als Kontrollmethode fuer das Pixelzaehlen bei Kugelpackungen mit sich nicht 
   * ueberlappenden Kugeln. 
   * 
   * @param anzahlKugeln: Anzahl Kugeln im Raum
   * @param radius: gleicher Radius aller Kugeln
   * @return
   */
  public double berechnePorositaet(int anzahlKugeln, double radius) {
	  double v_eine = Math.PI * Math.pow(radius, 3) * 4. / 3; // Volumen einer Kugel
	  double v_alle = v_eine * anzahlKugeln; // Volumen aller Kugeln
	  double porositaet = (this.getVolumen()-v_alle) / (this.getVolumen());
	  return porositaet;
  }
}
