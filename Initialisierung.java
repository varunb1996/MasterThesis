package kupa_org;

public class Initialisierung {

	public static void main(String[] args) {
		start();
	}
	
	public static void start() {
		// Kugeln in Initialisierungsebene erzeugen 
		System.out.println("Initialisierungsebene der Kugelpackung");
		Kugelpackung.initialisieren();
		// System.out.println("Initialisierung Ende\n");
		//System.out.println(String.format("%02d", 10));
	}

}
