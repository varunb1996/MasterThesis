package kupa_org;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
//import java.awt.Color;
import java.util.ArrayList;

import javax.imageio.ImageIO;

public class Kontaktverteilung {
    private BufferedImage image;
    private Raum mikrostruktur;
    private int[][][] pixel;
    private ArrayList<Integer[]> pos = new ArrayList<>();
    private int anzahlDiff;
    private final int black = -16777216;
    private final int white = -1;
    private final int diff = 20000; //ist Unterschied der farbe je nach Kontaktverteilung
    // private final int diff = 10;

    public Kontaktverteilung(Raum r){
        mikrostruktur = r;
        image = new BufferedImage(r.getX(), r.getY(), BufferedImage.TYPE_INT_RGB);
        berechneL1NormAbstand();
        posSuchen();
        generiereBildserieKontaktverteilung();
    }

    public void berechneL1NormAbstand(){
        Bildebene[] xyEbene = new Bildebene[mikrostruktur.getRaum().length];
        for(int i=0; i<xyEbene.length; i++){
            xyEbene[i] = mikrostruktur.getRaum()[i];
        }
        //setzt pixel gleich den xyEbenen
        pixel = new int[xyEbene.length][xyEbene[0].getWidth()][xyEbene[0].getHeight()];
        for(int i=0; i<xyEbene.length; i++){
            int[] pixelxyEbene = xyEbene[i].getPixelArray();
            for(int j=0; j<xyEbene[i].getWidth(); j++){ 
                for(int k=0; k<xyEbene[i].getHeight(); k++){
                    pixel[i][j][k] = pixelxyEbene[j+k*xyEbene[i].getWidth()];
                    /*if(pixelxyEbene[j+k*xyEbene[i].getWidth()] == white){
                        pixel[i][j][k] = new Color(255, 255, 255).getRGB();
                    }else if(pixelxyEbene[j+k*xyEbene[i].getWidth()] == black){
                        pixel[i][j][k] = new Color(0, 0, 0).getRGB();
                    }*/
                }
            }
        }
        anzahlDiff = 0;
        while(blackpixel()){
            for(int i=0; i<pixel.length; i++){
                for(int j=0; j<pixel[i].length; j++){
                    for(int k=0; k<pixel[i][j].length; k++){
                        int c = white - anzahlDiff*diff;
                        int nc = white - (anzahlDiff+1)*diff;
                        //int c = new Color(255-anzahlDiff*diff, 255-anzahlDiff*diff, 255-anzahlDiff*diff).getRGB();
                        //int nc = new Color(255-(anzahlDiff+1)*diff, 255-(anzahlDiff+1)*diff, 255-(anzahlDiff+1)*diff).getRGB();
                        if(pixel[i][j][k] == c){
                            if(k<pixel[i][j].length-1){
                                if(pixel[i][j][k+1] < c){
                                    pixel[i][j][k+1] = nc;
                                }
                            }
                            if(k>0){
                                if(pixel[i][j][k-1] < c){
                                    pixel[i][j][k-1] = nc;
                                }
                            }
                            if(j<pixel[i].length-1){
                                if(pixel[i][j+1][k] < c){
                                    pixel[i][j+1][k] = nc;
                                }
                            }
                            if(j>0){
                                if(pixel[i][j-1][k] < c){
                                    pixel[i][j-1][k] = nc;
                                }
                            }
                            if(i<pixel.length-1){
                                if(pixel[i+1][j][k] < c){
                                    pixel[i+1][j][k] = nc;
                                }
                            }
                            if(i>0){
                                if(pixel[i-1][j][k] < c){
                                    pixel[i-1][j][k] = nc;
                                }
                            }
                        }
                    }
                }
            }
            anzahlDiff++;
        }
        System.out.println(anzahlDiff+"");
    }

    public boolean blackpixel(){
        for(int i=0; i<pixel.length; i++){
            for(int j=0; j<pixel[i].length; j++){
                for(int k=0; k<pixel[i][j].length; k++){
                    if(pixel[i][j][k] == black){
                    //if(pixel[i][j][k] == new Color(0, 0, 0).getRGB()){
                        return true;
                    }
                }
            }
        }
        return false;
    }

    public void posSuchen(){
        for(int i=1; i<pixel.length-1; i++){//weiss nicht ob man die unterste und oberste Ebene mit betrachten soll, da hier ja eigentlich kein neuer Mittelpunkt einer Kugel angelegt werden kann
            for(int j=0; j<pixel[i].length; j++){
                for(int k=0; k<pixel[i][j].length; k++){
                    if(pixel[i][j][k] != white){
                        if(k<pixel[i][j].length-1){
                            if(pixel[i][j][k+1] <= pixel[i][j][k] || pixel[i][j][k+1] == white){
                                continue;
                            }
                            if(j<pixel[i].length-1){
                                if(pixel[i][j+1][k+1] <= pixel[i][j][k] || pixel[i][j+1][k+1] == white){
                                    continue;
                                }
                                if(i<pixel.length-1){
                                    if(pixel[i+1][j+1][k+1] <= pixel[i][j][k] || pixel[i+1][j+1][k+1] == white){
                                        continue;
                                    } 
                                }
                                if(i>0){
                                    if(pixel[i-1][j+1][k+1] <= pixel[i][j][k] || pixel[i-1][j+1][k+1] == white){
                                        continue;
                                    }
                                }
                            }
                            if(j>0){
                                if(pixel[i][j-1][k+1] <= pixel[i][j][k] || pixel[i][j-1][k+1] == white){
                                    continue;
                                }
                                if(i<pixel.length-1){
                                    if(pixel[i+1][j-1][k+1] <= pixel[i][j][k] || pixel[i+1][j-1][k+1] == white){
                                        continue;
                                    } 
                                }
                                if(i>0){
                                    if(pixel[i-1][j-1][k+1] <= pixel[i][j][k] || pixel[i-1][j-1][k+1] == white){
                                        continue;
                                    }
                                }
                            }
                        }
                        if(k>0){
                            if(pixel[i][j][k-1] <= pixel[i][j][k] || pixel[i][j][k-1] == white){
                                continue;
                            }
                            if(j<pixel[i].length-1){
                                if(pixel[i][j+1][k-1] <= pixel[i][j][k] || pixel[i][j+1][k-1] == white){
                                    continue;
                                }
                                if(i<pixel.length-1){
                                    if(pixel[i+1][j+1][k-1] <= pixel[i][j][k] || pixel[i+1][j+1][k-1] == white){
                                        continue;
                                    } 
                                }
                                if(i>0){
                                    if(pixel[i-1][j+1][k-1] <= pixel[i][j][k] || pixel[i-1][j+1][k-1] == white){
                                        continue;
                                    }
                                }
                            }
                            if(j>0){
                                if(pixel[i][j-1][k-1] <= pixel[i][j][k] || pixel[i][j-1][k-1] == white){
                                    continue;
                                }
                                if(i<pixel.length-1){
                                    if(pixel[i+1][j-1][k-1] <= pixel[i][j][k] || pixel[i+1][j-1][k-1] == white){
                                        continue;
                                    } 
                                }
                                if(i>0){
                                    if(pixel[i-1][j-1][k-1] <= pixel[i][j][k] || pixel[i-1][j-1][k-1] == white){
                                        continue;
                                    }
                                }
                            }
                        }
                        if(j<pixel[i].length-1){
                            if(pixel[i][j+1][k] <= pixel[i][j][k] || pixel[i][j+1][k] == white){
                                continue;
                            }
                            if(i<pixel.length-1){
                                if(pixel[i+1][j+1][k] <= pixel[i][j][k] || pixel[i+1][j+1][k] == white){
                                    continue;
                                } 
                            }
                            if(i>0){
                                if(pixel[i-1][j+1][k] <= pixel[i][j][k] || pixel[i-1][j+1][k] == white){
                                    continue;
                                }
                            }
                        }
                        if(j>0){
                            if(pixel[i][j-1][k] <= pixel[i][j][k] || pixel[i][j-1][k] == white){
                                continue;
                            }
                            if(i<pixel.length-1){
                                if(pixel[i+1][j-1][k] <= pixel[i][j][k] || pixel[i+1][j-1][k] == white){
                                    continue;
                                } 
                            }
                            if(i>0){
                                if(pixel[i-1][j-1][k] <= pixel[i][j][k] || pixel[i-1][j-1][k] == white){
                                    continue;
                                }
                            }
                        }
                        if(i<pixel.length-1){
                            if(pixel[i+1][j][k] <= pixel[i][j][k] || pixel[i+1][j][k] == white){
                                continue;
                            }
                            if(k<pixel[i][j].length-1){
                                if(pixel[i+1][j][k+1] <= pixel[i][j][k] || pixel[i+1][j][k+1] == white){
                                    continue;
                                } 
                            }
                            if(k>0){
                                if(pixel[i+1][j][k-1] <= pixel[i][j][k] || pixel[i+1][j][k-1] == white){
                                    continue;
                                }
                            }
                        }
                        if(i>0){
                            if(pixel[i-1][j][k] <=  pixel[i][j][k] || pixel[i-1][j][k] == white){
                                continue;
                            }
                            if(k<pixel[i][j].length-1){
                                if(pixel[i-1][j][k+1] <= pixel[i][j][k] || pixel[i-1][j][k+1] == white){
                                    continue;
                                } 
                            }
                            if(k>0){
                                if(pixel[i-1][j][k-1] <= pixel[i][j][k] || pixel[i-1][j][k-1] == white){
                                    continue;
                                }
                            }
                        }
                        Integer[] temp = {j, k, i};
                        pos.add(temp);
                        pixel[i][j][k] = black;
                    }
                }
            }
        }
    }
    
    public void generiereBildserieKontaktverteilung() {
    String filename;
    String dirname = "Bildserie_kontaktverteilung_" + mikrostruktur.getX() + "x" + mikrostruktur.getY() + "x" + mikrostruktur.getZ();
    File directory = new File(dirname);
    directory.mkdir(); // Ordner anlegen
    for (int i = 0; i < pixel.length; i++) {
      try {
        filename = "kugelEbene_" + i + ".png"; // Dateiname der i-ten Bildebene
        File output = new File (directory, filename);
        BufferedImage image = new BufferedImage(this.image.getWidth(), this.image.getHeight(), BufferedImage.TYPE_INT_RGB);
        for(int k=0; k<this.image.getHeight(); k++){
            for(int j=0; j<this.image.getWidth(); j++){
                image.setRGB(j, k, pixel[i][j][k]);
            }
        }
        ImageIO.write(image, "png", output);
      } catch (IOException e) {
        System.out.println(e.getMessage());
      }
    }
    try(PrintWriter pw = new PrintWriter(new File(directory, "kugelEbenen_NeuePunkte.txt"))){
        pw.println("Neue Punkte");
        pw.println("Anzahl: " + pos.size());
        for(int i=0; i<pos.size(); i++){
            StringBuilder sb = new StringBuilder();
            sb.append(pos.get(i)[0]).append(", ").append(pos.get(i)[1]).append(", ").append(pos.get(i)[2]);
            pw.println(sb.toString());
        }
    }catch(FileNotFoundException e){
        System.out.println(e.getMessage());
    } 
  }
}