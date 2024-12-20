package kupa_org;
/**
 * Klasse SpherePositioningexception
 * Exception, die geworfen wird, wenn korrekte Erzeugung der Kugelliste nicht gelungen ist.
 *
 * @author Karin Havemann
 * @version Maerz 2020
 */

public class SpherePositioningException extends RuntimeException {
  public SpherePositioningException() {
    super("Es gab einen Fehler beim Erzeugen der Kugelliste");
  }

  public SpherePositioningException(String s) {
    super(s);
  }
}
