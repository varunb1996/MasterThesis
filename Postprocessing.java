package kupa_org;

public class Postprocessing {
	public static void main(String[] args) {
		start();
	}
	
	public static void start() {
		// Kugeln in Initialisierungsebene erzeugen 
		System.out.println("Ausgabedateien der Kugelpackung");
		Kugelpackung.postprocessing();
		System.out.println("Programm Ende");
	}
}
