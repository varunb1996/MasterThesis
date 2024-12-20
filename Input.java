package kupa_org;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

public class Input {
	protected String dateiname;
	public int n;
	public int breite;
	public int hoehe;
	public int tiefe;
	public double eps;
	protected String suf;
	public String suffix;
	public int testpkt;
	public boolean reachPorosity;
	public double zielporositaet;
	public int maxN;
	public double minRadius;
	public double maxRadius;
	public String distribution; 
	public double beta_p;
	public double beta_q;
	public double pOverlap;
	
	// Konstruktor
	public Input(String file) {
		dateiname = file;
		
		// Default-Belegung:
		n = 5;
		breite = 900;
		hoehe = 700;
		tiefe = 200;
		suf = "";
		suffix = "";
		testpkt = 500;
		reachPorosity = true;
		zielporositaet = 0.25;
		maxN = 50;
		minRadius = 7;
		maxRadius = 10;
		pOverlap = 0.1;
		distribution = "uniform";
		beta_p = 2;
		beta_q = 2;
		
		// Belegung mit Daten aus Input-Datei (falls vorhanden)
		try (Scanner sc = new Scanner(new File(dateiname))) {
			boolean def;
			String zeile;
			String [] input;
			while (sc.hasNextLine()) {
				def = false;
				zeile = sc.nextLine();
				try {	
					if (zeile.charAt(0) != '#') { // Ueberspringen der Kommentarzeilen
						input = zeile.split(": ");
						if (input[0].equals("n")) {
							try {
								n = Integer.parseInt(input[1]);
								if (n <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
									def = true;
							} finally {
								if (def) {
									System.out.println("Es wurde keine gueltige Anzahl Kugelpackungen uebergeben");
									System.out.println("Default-Belegung der Anzahl Kugelpackungen: " + n);
								}
							}
						} else if (input[0].equals("breite")) {
							try {
								breite = Integer.parseInt(input[1]);
								if (breite <= 0) {										
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde keine gueltige Raumbreite uebergeben");
									System.out.println("Default-Belegung der Breite: " + breite);
								}
							}	
						} else if (input[0].equals("hoehe")) {
							try {
								hoehe = Integer.parseInt(input[1]);
								if (hoehe <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde keine gueltige Raumhoehe uebergeben");
									System.out.println("Default-Belegung der Hoehe: " + hoehe);
								}
							}
						} else if (input[0].equals("tiefe")) {
							try {
								tiefe = Integer.parseInt(input[1]);
								if (tiefe <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde keine gueltige Raumtiefe uebergeben");
									System.out.println("Default-Belegung der Tiefe: " + tiefe);
								}
							}
						} else if (input[0].equals("minimaler Radius")) {
							try {
								minRadius = Double.parseDouble(input[1]);
								if (minRadius <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde kein gueltiger minimaler Radius uebergeben");
									System.out.println("Default-Belegung des minimalen Radius: " + minRadius);
								}
							}
						} else if (input[0].equals("maximaler Radius")) {
							try {
								maxRadius = Double.parseDouble(input[1]);
								if (maxRadius <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde kein gueltiger maximaler Radius uebergeben");
									System.out.println("Default-Belegung des maximalen Radius: " + maxRadius);
								}
							}
						} else if (input[0].equals("eps")) {
							try {
								eps = Double.parseDouble(input[1]);
								if (eps <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde kein gueltiger Abstand zwischen den Kugeln der untersten Ebende uebergeben");
									System.out.println("Default-Belegung des Abstandes: " + eps);
								}
							}
						} else if (input[0].equals("prozentualer Überlapp")) {
							try {
								pOverlap = Double.parseDouble(input[1]);
								if (pOverlap < 0 || pOverlap > 1) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde kein gueltiger prozentualer Überlapp für Kugeln angegeben");
									System.out.println("Default-Belegung des prozentualen Überlapps: " + pOverlap);
								}
							}
						} else if (input[0].equals("Verteilung")) {
							try {
								distribution = input[1];
							} catch (ArrayIndexOutOfBoundsException e) {
								// Verteilung hat bereits Default-Belegung
							}
						} else if (input[0].equals("Beta-Verteilung p")) {
							try {
								beta_p = Double.parseDouble(input[1]);
								if (beta_p <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde kein gueltiger prozentualer Überlapp für Kugeln angegeben");
									System.out.println("Default-Belegung des prozentualen Überlapps: " + pOverlap);
								}
							}
						} else if (input[0].equals("Beta-Verteilung q")) {
							try {
								beta_q = Double.parseDouble(input[1]);
								if (beta_q <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde kein gueltiger prozentualer Überlapp für Kugeln angegeben");
									System.out.println("Default-Belegung des prozentualen Überlapps: " + pOverlap);
								}
							}
						} else if (input[0].equals("suffix")) {
							try {
								suf = "_" + input[1];
								suffix = "_" + input[1];
							} catch (ArrayIndexOutOfBoundsException e) {
								// suffix hat bereits Default-Belegung
							}
						} else if (input[0].equals("testpkt")) {
							try {
								testpkt = Integer.parseInt(input[1]);
								if (testpkt <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde keine gueltige Anzahl Testpunkte fuer den Monte-Carlo-Algorithmus uebergeben");
									System.out.println("Default-Belegung der Anzahl Testpunkte: " + testpkt);
								}
							}
						} else if (input[0].equals("reachPorosity")) {
							try {
								reachPorosity = Boolean.parseBoolean(input[1]);
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								System.out.println("Es wurde keine gueltige Angabe gemacht, ob eine Zielporositaet erreicht werden soll");
								System.out.println("Default-Belegung: Kugeln werden vergrößert, sodass Zielporositaet erreicht wird ");
							}
						} else if (input[0].equals("zielporositaet")) {
							try {
								zielporositaet = Double.parseDouble(input[1]);
								if (zielporositaet <= 0 || zielporositaet > 1) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde keine gueltige Zielporositaet uebergeben");
									System.out.println("Default-Belegung der Zielporositaet: " + zielporositaet);
								}
							}
						} else if (input[0].equals("maxN")) {
							try {
								maxN = Integer.parseInt(input[1]);
								if (maxN <= 0) {
									def = true;
								}
							} catch (NumberFormatException | ArrayIndexOutOfBoundsException e) {
								def = true;
							} finally {
								if (def) { 
									System.out.println("Es wurde keine gueltige Anzahl max. Schleifendurchlaeufe uebergeben");
									System.out.println("Default-Belegung der max. Anzahl Schleifendurchlaeufe: " + maxN);
								}
							}
						}

					}
				} catch (StringIndexOutOfBoundsException e) {
					// bei Leerzeile soll Programm nicht abbrechen
				}
			}
		} catch (FileNotFoundException e) {
			System.out.println("Die Datei "+ dateiname +" konnte nicht gefunden werden.");
			System.out.println(e.getMessage());
			System.out.println("Alle Eingabedaten werden mit Default-Werten belegt");
		}
		//this.gebeBelegungAus();
	}
	
	public void setSuffix(int i) {
		if (this.suf.length() > 0) {
			this.suffix = String.format("_TC%02d%s", i, this.suf);
		} else {
			this.suffix = String.format("_TC%02d", i);
		}
	}
	
	public void gebeBelegungAus() {
		System.out.println("belegte Werte:");
		System.out.println("  Raumgroesse: ");
		System.out.println("    Breite: " + breite);
		System.out.println("    Hoehe: " + hoehe);
		System.out.println("    Tiefe: " + tiefe);
		System.out.println("  minmialer Kugelradius: " + minRadius);
		System.out.println("  maximaler Kugelradius: " + maxRadius);
		System.out.println("  prozentualer Überlapp: " + pOverlap);
		System.out.println("  Verteilung: " + distribution);
		System.out.println("  prozentualer Abstand Kugeln unterste Ebene (eps): " + eps);
		System.out.println("  Anzahl Testpunkte Monte-Carlo: " + testpkt);
		if (reachPorosity) {
			System.out.println("  Zielporositaet: " + zielporositaet);
			System.out.println("  max. Anzahl Schleifendurchlaeufe: " + maxN);
		}
	}

}
