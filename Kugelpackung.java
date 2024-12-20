package kupa_org;

import java.util.ArrayList;
import java.util.Scanner;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.lang.Math;
import org.apache.commons.math3.distribution.BetaDistribution;

/**
 * Klasse zur Erzeugung einer Kugelpackung. 
 * Ein Raum soll mit zufällig angeordneten Kugeln gleicher Größe gefüllt werden, die sich berühren.
 * 
 * Es wird in einem Raum der Boden mit Kugeln gefüllt und im Anschluss aus den vorhandenen Kugeln 
 * alle möglichen Position (Pockets) neuer Kugeln berechnet.
 * Nach der Reihe wird dann immer der untersten Pocket eine Kugel platziert. 
 * Aus der platzierten Kugel ergeben sich neue mögliche Positionen von Kugeln. 
 * Das Aussuchen und Füllen der niedrigsten Pocket wird so lange wiederholt bis keine Pockets mehr vorhanden sind.
 * 
 * @author Tobias Noppeney, Lucas Rhein, Karin Havemann
 * @version Februar 2021
 */
public class Kugelpackung {
	private ArrayList<Kugel> kugelliste; // Liste aller Kugeln in der Kugelpackung
	private double eps; // Abstand zwischen 2 Kugeln
	private Raum mikrostruktur;
	public final static String inputdatei = "../resources/Eingabedaten.txt";
	private Input input;
	protected double minRadius; // minimaler Radius einer Kugel
	protected double maxRadius; // maximaler Radius einer Kugel
	protected double expectedR;

	// Konstruktor
	public Kugelpackung(Input eingabe) {
		input = eingabe;
		kugelliste = new ArrayList<>();
		mikrostruktur = new Raum(input.breite, input.hoehe, input.tiefe);
		this.minRadius = input.minRadius;
		this.maxRadius = input.maxRadius;
		eps = input.eps;
		
		if (input.distribution.equals("uniform")) {
			this.expectedR = (maxRadius + minRadius) / 2;
			//System.out.println("Erwartungswert "+this.expectedR);
		} else { // input.distribution.equals("beta")
			double expectBeta = input.beta_p / (input.beta_p + input.beta_q);
			this.expectedR = (maxRadius - minRadius) * expectBeta + minRadius;
			//System.out.println("Erwartungswert "+this.expectedR);
		}
	}


	/**
	 * Ermittelt den durchschnittlichen Radius aller Kugeln. Berechnung anhand der
	 * Aussenradien.
	 * 
	 * @return
	 */
	public double durchschnittsradius() {
		double r = 0;
		for (Kugel k : kugelliste) {
			r += k.getAussenradius();
		}
		r /= kugelliste.size();
		return r;
	}

	public static void initialisieren() {
		Input eingabe = new Input(inputdatei);
		int n = eingabe.n; // Anzahl der zu erzeugenden Kugelpackungen
		Kugelpackung kupa;
		for (int i = 1; i <= n; i++) {
			eingabe.setSuffix(i);
			kupa = new Kugelpackung(eingabe);
			kupa.untersteEbeneFuellen();
			String bezeichnung = "initialisierungsebene";
			//String bezeichnung = "kupa_sameSize";
			kupa.erzeugeCsvDatei(bezeichnung);
			System.out.println("Initialisierungsebene Testcase " + i + " von " + eingabe.n + " erzeugt.");
		}
	}

	public static void postprocessing() {
		Input eingabe = new Input(inputdatei);
		Kugelpackung kupa = new Kugelpackung(eingabe);
		String csvdatei;
		
		for (int i = 1; i <= eingabe.n; i++) {
			eingabe.setSuffix(i);
			kupa = new Kugelpackung(eingabe);
			if (kupa.minRadius != kupa.maxRadius) {
				csvdatei = "../resources/output/" + kupa.mikrostruktur.getX() + "x" + kupa.mikrostruktur.getY() + "x"
					+ kupa.mikrostruktur.getZ() + "_" + eingabe.distribution + "_" + (int) kupa.minRadius + "_" + (int) kupa.maxRadius 
					+ kupa.input.suffix + "_kupa.csv";
			} else {
				csvdatei = "../resources/output/" + kupa.mikrostruktur.getX() + "x" + kupa.mikrostruktur.getY() + "x"
						+ kupa.mikrostruktur.getZ() + "_" + (int) kupa.minRadius + "_" + (int) kupa.maxRadius 
						+ kupa.input.suffix + "_kupa.csv";
			}
			kupa.leseCsvDatei(csvdatei);
			kupa.mikrostruktur.erzeugeBildebenen();

			kupa.erzeugeQuerschnitte(); // erzeugt aus den Kugeln Querschnitte in jeder Bildebene des Raumes

			double porositaet = kupa.mikrostruktur.getPorositaet();
			//long startTime_porosity = System.nanoTime();
			if (kupa.input.reachPorosity) { // Variante: Anpassen der Porositaet durch vergroessern der Kugeln
				porositaet = kupa.erreicheZielporositaet(kupa.expectedR, porositaet);
			}
			//long endTime_porosity = System.nanoTime();
			//double time_porosity = (double) (endTime_porosity - startTime_porosity) / 1000000000.0;
			//System.out.println("Laufzeit Porosität: " + time_porosity);

			// new Kontaktverteilung(this.mikrostruktur);

			double spezOberflaeche = kupa.spezOberflaecheMonteCarlo(kupa.input.testpkt);

			//long startTime_bildserie = System.nanoTime();
			kupa.mikrostruktur.generiereBildserie(kupa.input.suffix, eingabe.distribution, (int) kupa.minRadius, (int) kupa.maxRadius); 
			// Bildebenen des Raumes als Bilddateien speichern
			//long endTime_bildserie = System.nanoTime();
			//double time_bildserie = (double) (endTime_bildserie - startTime_bildserie) / 1000000000.0;
			//System.out.println("Laufzeit Bildserie: " + time_bildserie);
			kupa.erzeugeVtkDatei(); // vtk-Datei erstellen
			kupa.erzeugeTxtDatei(porositaet, spezOberflaeche); // Porositaet abspeichern
			String bezeichnung = "kupa_postprocessing";
			if (kupa.input.reachPorosity) { // Kugelliste der vergrößerten Kugeln neu abspeichern
				kupa.erzeugeCsvDatei(bezeichnung);
			}
			System.out.println("Ausgabedateien Testcase " + i + " von " + eingabe.n + " erzeugt.");
		}
	}

	/**
	 * In der untersten Ebene werden die Kugeln erst alle geordnet mit einem
	 * konstant Abstand (eps) in Reihen angeordnet Kugeln aufeinanderfolgender
	 * Reihen werden versetzt platziert. Im Anschluss wird jede Kugeln in x-, y- und
	 * z-Richtung um einen zufaelligen Wert im Intervall [0 ; 0.5*eps] verschoben
	 */
	protected void untersteEbeneFuellen() {
		Kugel kugel;
		int i = 0; // zum pruefen ob es sich um eine gerade oder ungerade Reihe handelt
		BetaDistribution beta = new BetaDistribution(input.beta_p, input.beta_q);
		
		// durchlaufen der Ebene reihenweise mit bestimmten Faktorn (abhängig vom radius und eps)
		double radius;
		for (double x = maxRadius * eps; x <= mikrostruktur.getX() - maxRadius * eps; 
				x += 2 * this.expectedR * Math.sin(Math.toRadians(60)) + eps * maxRadius) {
			for (double y = maxRadius * eps; y <= mikrostruktur.getY() - maxRadius * eps; y += 2 * this.expectedR + eps * maxRadius) {
				// bei jeder zweiten Reihe wird die erste Kugel etwas um y verschoben platziert
				if (i % 2 == 1 && y <= maxRadius * eps * 1.0001) {
					y = minRadius + eps * maxRadius;
				}
				
				if (input.distribution.equals("uniform")) {
					radius = Math.random() * (maxRadius-minRadius) + minRadius;
				} else { // input.distribution.equals("beta")
					radius = beta.sample() * (maxRadius-minRadius) + minRadius;
				}

				// Kugel wird erzeugt, zufällig um einen kleinen Faktor verschoben und der
				// Kugelliste hinzugefügt
				kugel = new Kugel(new Punkt(x, y, radius), radius);
				kugel.randomMove(this.maxRadius * 2 * eps); //TODO: evtl. anderer Übergabewert
				kugelliste.add(kugel);
			}
			i++;
		}
	}

	/**
	 * Berechnung der spezifischen Oberflaeche mithilfe des Monte-Carlo-Algorithmus
	 * 
	 * @param anzTestpunkte Anzahl Testpunkte pro Kugel
	 * @return
	 */
	private double spezOberflaecheMonteCarlo(int anzTestpunkte) {
		long akzept_tp = 0;
		boolean akzeptieren;

		for (Kugel kugel : kugelliste) {
			kugel.generiereTestpunkte(anzTestpunkte);
			for (Punkt testpunkt : kugel.getTestpunkte()) {
				akzeptieren = true;
				for (Kugel nachbar : kugel.getNachbarn()) {
					// for (Kugel nachbar: kugelliste) {
					if (testpunkt.abstand(nachbar.getKugelmitte()) < nachbar.getKugelradius()) {
						akzeptieren = false;
					}
				}

				if (akzeptieren) {
					akzept_tp++;
				}
			}
			kugel.loescheTestpunkte();
		}

		long n = kugelliste.size(); // Anzahl Kugeln im System
		double rho = (double) n / (mikrostruktur.getX() * mikrostruktur.getY() * mikrostruktur.getZ()); // Anzahldichte

		// spezifische Oberflaeche
		double sv = 4 * Math.PI * rho * Math.pow(this.durchschnittsradius(), 2) * akzept_tp / (n * (anzTestpunkte - 1));
		return sv;
	}

	/**
	 * Es wird eine csv-Datei erzeugt, die alle Kugeln mit ihrem Mittelpunkt und
	 * Radius beinhaltet
	 * 
	 * @param praefix
	 */
	private void erzeugeCsvDatei(String bezeichnung) {
		String datei;
		if (this.minRadius != this.maxRadius) {
			datei = "../resources/output/" + mikrostruktur.getX() + "x" + mikrostruktur.getY() + "x" 
				+ mikrostruktur.getZ() + "_" + input.distribution + "_" + (int) minRadius + "_" + (int) maxRadius 
				+ input.suffix + "_" + bezeichnung + ".csv";
		} else {
			datei = "../resources/output/" + mikrostruktur.getX() + "x" + mikrostruktur.getY() + "x" 
				+ mikrostruktur.getZ() + "_" + (int) minRadius + "_" + (int) maxRadius + input.suffix + "_" 
				+ bezeichnung + ".csv";
		}
		try (PrintWriter pw = new PrintWriter(new File(datei))) {
			pw.println("x, y, z, r");
			for (Kugel k : kugelliste) {
				Punkt p = k.getKugelmitte();
				pw.println(p.getX() + ", " + p.getY() + ", " + p.getZ() + ", " + k.getAussenradius());
			}
		} catch (FileNotFoundException e) {
			System.out.println("Datei " + datei + " konnte nicht geschrieben werden.");
		}
	}

	private void leseCsvDatei(String datei) {
		try (Scanner sc = new Scanner(new File(datei))) {
			String zeile;
			String[] input;
			zeile = sc.nextLine(); // erste Zeile überlesen
			while (sc.hasNextLine()) {
				zeile = sc.nextLine();
				input = zeile.split(",");
				double x = Double.parseDouble(input[0]);
				double y = Double.parseDouble(input[1]);
				double z = Double.parseDouble(input[2]);
				double r = Double.parseDouble(input[3]);
				kugelliste.add(new Kugel(x, y, z, r));
			}

		} catch (FileNotFoundException e) {
			System.out.println("Die Datei " + datei + " konnte nicht gefunden werden.");
			System.out.println(e.getMessage());
		}
	}

	/**
	 * Erzeugt aus den Kugeln der Kugelliste Querschnitte der Kugeln in den
	 * verschiedenen xy-Ebenen(Bildebenen) des Raumes.
	 * 
	 * @throws SpherePositioningException
	 */
	private void erzeugeQuerschnitte() throws SpherePositioningException {
		if (kugelliste.size() == 0) {
			throw new SpherePositioningException("Die Kugelliste ist leer");
		} else {
			for (Kugel k : kugelliste) {
				double x = k.getKugelmitte().getX();
				double y = k.getKugelmitte().getY();
				double z = k.getKugelmitte().getZ();
				double r = k.getAussenradius();

				// Querschnitte unterhalb des Mittelpunktes
				int ebene = (int) z;
				double hoehe = z - ebene; // Abstand in zRichtung vom Mittelpunkt
				for (int i = ebene; i >= ebene - r; i--) {
					// keine Querschnitte ausserhalb des Raumes generieren (i>=0) und keine
					// Querschnitte ausserhalb der Kugel bestimmen (hoehe<=r)
					if (i >= 0 && hoehe <= r) {
						double kreisRadius = Math.sqrt((r * r) - (hoehe * hoehe));
						hoehe++;
						if (x >= 0 && x <= this.mikrostruktur.getX() && y >= 0 && y <= this.mikrostruktur.getY()
								&& i >= 0 && i <= this.mikrostruktur.getZ()) {
							mikrostruktur.zeichneKreis(i, x, y, kreisRadius);
						}
					}
				}

				// Querschnitte oberhalb des Mittelpunktes
				ebene = (int) (z + 1);
				hoehe = ebene - z; // Abstand in zRichtung vom Mittelpunkt
				for (int i = ebene; i <= ebene + r; i++) {
					// keine Querschnitte ausserhalb des Raumes generieren (i<=mikrostruktur.getZ())
					// und keine Querschnitte ausserhalb des Kugelradius
					if (i <= mikrostruktur.getZ() && hoehe <= r) {
						double kreisRadius = Math.sqrt((r * r) - (hoehe * hoehe));
						hoehe++;
						if (x >= 0 && x <= this.mikrostruktur.getX() && y >= 0 && y <= this.mikrostruktur.getY()
								&& i >= 0 && i <= this.mikrostruktur.getZ()) {
							mikrostruktur.zeichneKreis(i, x, y, kreisRadius);
						}
					}
				}
			}
		}
	}

	/**
	 * Erzeugt eine vtk-Datei in der alle Kugelpositionen (x-, y- und z-Koordinate)
	 * und der Kugeldurchmesser abgespeichert werden.
	 * 
	 * @param praefix - Praefix fuer Dateibezeichnung
	 */
	private void erzeugeVtkDatei() {
		String datei;
		if (this.minRadius != this.maxRadius) {
			datei = "../resources/output/" + this.mikrostruktur.getX() + "x" + this.mikrostruktur.getY() + "x"
					+ this.mikrostruktur.getZ() + "_" + input.distribution + "_" + (int) minRadius + "_" + (int) maxRadius 
					+ input.suffix + "_kugelliste.vtk";
		} else {
			datei = "../resources/output/" + this.mikrostruktur.getX() + "x" + this.mikrostruktur.getY() + "x"
					+ this.mikrostruktur.getZ() + "_" + (int) minRadius + "_" + (int) maxRadius 
					+ input.suffix + "_kugelliste.vtk";
		}
		try (PrintWriter pw = new PrintWriter(new File(datei))) {
			// Kopf der vtk-Datei
			pw.println("# vtk DataFile Version 3.0");
			pw.println("3D-Darstellung Kugelpackung");
			pw.println("ASCII");
			pw.println("DATASET POLYDATA");
			int size = kugelliste.size();
			pw.println("POINTS " + size + " double");
			for (Kugel k : kugelliste) { // Liste der Kugelpositionen
				Punkt p = k.getKugelmitte();
				pw.println(p.getX() + " " + p.getY() + " " + p.getZ());
			}
			pw.println();
			pw.println("POINT_DATA " + size);
			pw.println("SCALARS diameters double");
			pw.println("LOOKUP_TABLE default");
			for (Kugel k : kugelliste) { // Liste der Kugelradien
				pw.println(k.getAussenradius() * 2);
			}
		} catch (FileNotFoundException e) {
			System.out.println("Datei " + datei + " konnte nicht geschrieben werden.");
		}
	}

	/**
	 * Erzeugt eine txt-Datei mit den Daten zu der erzeugten Kugelpackung
	 * 
	 * @param praefix
	 * @param porositaet           - Porositaet ueber Pixel zaehlen
	 * @param porositaet_berechnet - Porositaet berechnet (nur bei sich nicht überlappenden Kugeln!)
	 * @param sv_mc                - spezifische Oberfläche ueber Monte-Carlo
	 * @param sv_b                 - spezifische Oberfläche berechnet (nur bei sich nicht überlappenden Kugeln!)
	 */
	private void erzeugeTxtDatei(double porositaet, double spezOberflaeche) {
		String datei;
		if (this.minRadius != this.maxRadius) {
			datei = "../resources/output/" + this.mikrostruktur.getX() + "x" + this.mikrostruktur.getY() + "x"
				+ this.mikrostruktur.getZ() + "_" + input.distribution + "_" + (int) minRadius + "_" + (int) maxRadius 
				+ input.suffix + "_daten.txt";
		} else {
			datei = "../resources/output/" + this.mikrostruktur.getX() + "x" + this.mikrostruktur.getY() + "x"
					+ this.mikrostruktur.getZ() + "_" + (int) minRadius + "_" + (int) maxRadius 
					+ input.suffix + "_daten.txt";
		}
		try (PrintWriter pw = new PrintWriter(new File(datei))) {
			pw.println("Kugelpackung");
			pw.println("Raumgroesse: " + this.mikrostruktur.getX() + "x" + this.mikrostruktur.getY() + "x"
					+ this.mikrostruktur.getZ());
			pw.println("Anzahl Kugeln: " + kugelliste.size());
			if (input.reachPorosity) {
				pw.println("Porositaet vor dem Vergrößern der Kugeln: " + this.mikrostruktur.getPorositaet());
			}
			pw.println("Porositaet (Pixel zaehlen): " + porositaet);

			pw.println("spezifische Oberflaeche (Monte-Carlo): " + spezOberflaeche);
		} catch (FileNotFoundException e) {
			System.out.println("Datei " + datei + " konnte nicht geschrieben werden.");
		}
	}

	/**
	 * Jeweils 10 % der Kugeln der kugelliste solange vergroessern bis die
	 * Zielporositaet zielporositaet erreicht/erstmalig ueberschritten wurde. Nur
	 * bei gleich großen Radien!
	 * 
	 * @param radius   : Groesse des inneren Radius aller Kugeln (identisch)
	 * @param porosity : aktuelle Porositaet der Kugelpackung
	 * @return
	 */
	private double erreicheZielporositaet(double radius, double porosity) {
		int maxN = this.input.maxN; // maximale Anzahl Schleifendurchlaeufe
		int i = 0; // counter

		String praefix = "";

		int n = kugelliste.size();
		long vol = this.mikrostruktur.getVolumen();
		double volBelegt_z = vol * (1 - input.zielporositaet); // angestrebtes Volumen, dass durch Kugeln belegt ist
		// double volBelegt_a = vol * (1 - porosity); // aktuelles Volumen, dass durch Kugeln belegt ist
		double a = (3 * volBelegt_z) / (4 * Math.PI * n);
		double rNeu = Math.pow(a, 1.0 / 3);
		double faktor = rNeu / radius;

		System.out.println("Porosität = " + porosity);
		while (porosity > input.zielporositaet && i < maxN) {
			for (int j = 0; j < (int) (n / 4); j++) {
				// eine zufaellige Kugel aus der Liste bestimmen:
				int k = (int) (Math.random() * n);
				double x = kugelliste.get(k).getAussenradius();
				// Berechne neuen Aussenradius der Kugel:
				// Zufallszahl im Intervall [x; faktor*x] (Kugeln vergroessern) bzw.
				double r = x * (1 + Math.random() * (faktor - 1));
				// <=> r = x + Math.random() * (y-x);
				kugelliste.get(k).setAussenradius(r);

			}
			erzeugeQuerschnitte();
			porosity = this.mikrostruktur.getPorositaet();
			System.out.println("Porositaet = " + porosity);
			i++;
		}

		if (i == maxN) {
			System.out.println("Abbruch: max. Anzahl Iterationen wurde erreicht, ohne die Zielporosität zu erhalten");
		}
		return porosity;

	}
}
