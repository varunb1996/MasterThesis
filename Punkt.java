package kupa_org;
/**
 * Klasse Punkt
 * Die Pixel einer Bilddatei werden durch die x- und y-Koordinate beschrieben.
 * In z-Richtung werden mehrere Bilddateien hintereinander gestaffelt.
 * Die Klasse Punkt beschreibt anhand von drei Koordinaten einen Punkt in einem dreidimensionalen Raum,
 * wobei x- und y-Koordinate in einer Ebene/Bilddatei liegen.
 * Die z-Koordinate gibt an, in welcher Bilddatei der Punkt liegt.
 *
 * @author Karin Havemann
 * @version Maerz 2020
 */

public class Punkt {
  private double x; // x-Koordinate
  private double y; // y-Koordinate
  private double z; // z-Koordinate

  // Konstruktor
  public Punkt (double x, double y, double z) {
    this.x = x;
    this.y = y;
    this.z = z;
  }

  // Getter-Methoden
  public double getX() {
    return x;
  }

  public double getY() {
    return y;
  }

  public double getZ() {
    return z;
  }
  
  // Verschieben des Punktes um jeweils in Richtung einer Koordinatenachse
  public void addX(double x) {
	  this.x += x;
  }

  public void addY(double y) {
	  this.y += y;
  }
  
  public void addZ(double z) {
	  this.z += z;
  }
  
  // toString-Methode
  @Override
  public String toString() {
	  return "(" + x + ", " + y + ", " + z + ")";
  }

  /**
   * Bestimmt den euklidischen Abstand zwischen dem aktuellen und dem uebergebenen Punkt
   * @param punkt
   * @return
   */
  public double abstand(Punkt punkt) {
	  return Math.sqrt(Math.pow(punkt.getX()-x,2)+Math.pow(punkt.getY()-y,2)+Math.pow(punkt.getZ()-z,2));
  }
  
  /**
   * Wandelt die Koordinaten des Punktes in ein zweidimensionales Array um.
   * @return
   */
  public double[][] toArray(){
	  double[][] arr = {{x}, {y}, {z}};
	  return arr;
  }

  @Override
  public boolean equals(Object obj) {
	  if (this == obj)
		  return true;
	  if (obj == null)
		  return false;
	  if (getClass() != obj.getClass())
		  return false;
	  Punkt other = (Punkt) obj;
	  if (x != other.x)
		  return false;
	  if (y != other.y)
		  return false;
	  if (z != other.z)
		  return false;
	  return true;
  }
}
