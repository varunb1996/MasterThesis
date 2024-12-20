package kupa_org;
import java.awt.Frame;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Shape;
import java.awt.event.WindowAdapter;
import java.awt.event.WindowEvent;
import java.awt.image.BufferedImage;

/**
 * Klasse Bildebene
 * Eine Bildebene ist ein Fenster auf dem grafische Objekte (z. B. Kreise) angezeigt werden koennen.
 * Der Ausgabe der grafischen Objekte liegt ein zweidimensionales Koordinatensystem zu Grunde,
 * dessen Ursprung in der linken oberen Ecke der Bildebene liegt.
 * Die positiven x-Werte erstrecken sich horizontal in Richtung rechts.
 * Die positiven y-Werte erstrecken sich vertikal in Richtung unten.
 *
 * Eine Bildebene kann als Bilddatei gespeichert werden.
 *
 * @author Karin Havemann
 * @version Juli 2020
 */

public class Bildebene extends Frame {
  private int xRichtung; // positive xAchse verlauft von der oberen linken Ecke horizontal nach rechts
  private int yRichtung; // positive yAchse verlauft von der oberen linken Ecke senkrecht nach unten

  private BufferedImage image;
  private Graphics2D grafik;  // Grafikkontext der Bildebene, ueber den sich das Bild "bemalen" laesst

  // Konstruktor
  public Bildebene (int breite, int hoehe) {
    xRichtung = breite;
    yRichtung = hoehe;
    setSize(xRichtung, yRichtung); // Groesse der Bildebene in Pixeln
    setVisible(false); // Sichtbarkeit des Fensters
    /**
     * ermoeglicht schliessen der sich oeffnenden Fenster
     * (WindowAdapter als anonyme innere Klasse, alternativ eine
     * neue Klasse, die von WindowAdapter erbt)
     * 
     * TODO: Test, ob WindowListener uebrhaupt noetig (da Fenstersichtbarkeit = false)
     */
    addWindowListener(new WindowAdapter() {
        public void windowClosing(WindowEvent e) {
          System.exit(0);
        }
      } );
    // Grafikkontext erzeugen
    image = new BufferedImage(xRichtung, yRichtung, BufferedImage.TYPE_INT_RGB);
    grafik = image.createGraphics();
  }

  // Getter-Methode
  public BufferedImage getImage() {
    return this.image;
  }

  // wird aufgerufen, wenn Fenster neu aufgebaut wird
  @Override
  public void paint(Graphics g) {
    g.drawImage(image, 0, 0, this); // zeichnen der Grafik
  }

  /**
   * Zeichnen einer Form s im Grafikkontext der Bildebene.
   * Es kann nur der Umriss der uebergebenen Form oder eine gefuellte Form gezeichnet werden.
   * @param s           Form, die gezeichnet werden soll
   * @param gefuellt    bei true wird eine ausgefuellte Form gezeichnet, sonst nur der Umriss
   */
  public void zeichneForm(Shape s, boolean gefuellt) {
    if (gefuellt == true) {
      grafik.fill(s); // gefuellte Form zeichnen 
    } else {
      grafik.draw(s); // Umriss der Form zeichnen
    }
    repaint(); // neuzeichnen durch Aufruf der paint-Methode
  }

  /**
   * Zaehlt die Anzahl freier Pixel (Pixel ohne Kugeln) in einer Bildebene.
   * Hierfuer werden die Farbwerte einer Bildebene als int-Werte in einem Array gespeichert
   * Fuer jeden Wert im Array, der dem uebergebenen Referenzwert farbwert entspricht,
   * wird ein Pixelzaehler um eins erhoeht.
   * @param farbwert    als Referenzwert fuer die Farbe freier Pixel
   * @return Anzahl     Zahl an freien Pixeln in einer Bildebene
   */
  public long zaehleFreiePixel(int farbwert) {
	  long anzahl = 0; // Pixelzaehler

	  int w = image.getWidth();
	  int h = image.getHeight();
	  int[] pixel = new int [w * h];
	  image.getRGB(0, 0, w, h, pixel, 0, w); // Bild in Array transformieren
	  for (int i = 0; i < pixel.length; i++) {
		  if (pixel[i] == farbwert) { // Abgleich mit Referenzwert
			  anzahl++;
		  }
	  }
	  return anzahl;
  }

  /**
   * Errechnet die gesamte Anzahl an Pixeln in einer Bildebene
   * @return
   */
  public long zaehleGesamtPixel() {
	  return image.getWidth() * image.getHeight();
  }

  public int[] getPixelArray(){
    int w = image.getWidth();
    int h = image.getHeight();
    int[] pixel = new int[w * h];
    image.getRGB(0, 0, w, h, pixel, 0, w);
    return pixel;
  }

}
