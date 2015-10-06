import cv2
import time
import numpy
import os
import fil_IO as io
import tkMessageBox
import ttk
from Tkinter import *
from PIL import Image
import threading

class HoGTrening:
    global antallPos
    global antallNeg
    global param

    def __init__(self,confParametere):
        self.param = confParametere
        self.progressBar = 0
        if self.param.getParam(2) < len(next(os.walk(self.param.getParam(1)+"\pos"))[2]) and self.param.getParam(2) > 0:
            self.antallPos = self.param.getParam(2)
        else:
            self.antallPos = len(next(os.walk(self.param.getParam(1)+"\pos"))[2])

        if self.param.getParam(3) < len(next(os.walk(self.param.getParam(1)+"\\neg"))[2]) and self.param.getParam(3) > 0:
            self.antallNeg = self.param.getParam(3)
        else:
            self.antallNeg = len(next(os.walk(self.param.getParam(1)+"\\neg"))[2])

        # Initierer HoG variabler. Initierer parameterisering av HoG.
        self.HOGde = cv2.HOGDescriptor((48, 64), (32,32), (16,16), (8,8), 6)
        return


    def genererNyHoGDatabase(self,progressbar):
        # Maksimum treningsdata er 687 positive og 836 negative. Utforer HoG og samler i matriser
        # Treningsdata har default vindusstorrelse paa bilder: 32x64.
        # Anvender HoG blokkstorrelse paa 4x4 og cellestorrelse 8x8.
        # Tilsvarer 432 features per bilde
        self.progressBar = progressbar
        if self.param.getParam(2) < len(next(os.walk(self.param.getParam(1)+"\pos"))[2]) and self.param.getParam(2) > 0:
            self.antallPos = self.param.getParam(2)
        else:
            self.antallPos = len(next(os.walk(self.param.getParam(1)+"\pos"))[2])

        if self.param.getParam(3) < len(next(os.walk(self.param.getParam(1)+"\\neg"))[2]) and self.param.getParam(3) > 0:
            self.antallNeg = self.param.getParam(3)
        else:
            self.antallNeg = len(next(os.walk(self.param.getParam(1)+"\\neg"))[2])

        self.progressBar.settMaxMin(self.antallPos,0,self.antallNeg,0)
        self.progressBar.oppdaterProgressbar( 0, 0)
        t = threading.Thread(target=self.Thread_finnHoG)
        t.start()

    def hentPosHoGVektor(self):
        vektor = self.lastHoGVector("posHoGVect.txt",self.antallPos)
        if type(vektor) != type(False):
            return vektor
        else:
            return False

    def hentNegHoGVektor(self):
        vektor = self.lastHoGVector("negHoGVect.txt",self.antallNeg)
        if type(vektor) != type(False):
            return vektor
        else:
            return False

    def lastHoGVector(self, filnavn, antall):
        dataArray = numpy.empty(((antall - 1),576))

        kolonne = 0
        rad = 0
        try:
            file = open( filnavn , 'r')
            confdatalines = file.readlines()
            print(len(confdatalines))
            for i in range(0,len(confdatalines)):

                start = int(str(confdatalines[i]).find('[', 0,len(confdatalines)  ))
                slutt = int(str(confdatalines[i]).find(']', 0,len(confdatalines)  ))

                streng = str(confdatalines[i])[start+2:slutt]
                dataArray[rad, kolonne] = float(streng)

                kolonne = kolonne + 1
                #Sjekker om linjen er siste element i radvektoren
                if int(str(confdatalines[i]).find(']]', 0,len(confdatalines)  )) != -1:
                    rad = rad +1
                    kolonne = 0

            return dataArray

        except:
            tkMessageBox.showinfo("Info","Greide ikke behandle fila "+str(filnavn)+", . Bygg database pa ny")
            return False
    pass

    def Thread_finnHoG(self):
        file = open( "posHoGVect.txt" , 'w')
        for pos in range(1,self.antallPos):
            # Laster inn bilder med fjes og utforer HoG. Endrer storrelse med resize(bredde,hoyde)
            try:
                bildePos = Image.open( self.param.getParam(1) + "\pos" + "\PosTrening (" + str(pos) + ").jpg" )
                bildePosSkalert = bildePos.resize((48,64), Image.ANTIALIAS)
                bildePosMat = numpy.asarray(bildePosSkalert)
            except:
                tkMessageBox.showinfo("Info","Feil med lasting av " +  str(self.param.getParam(1))+ "\pos" + "\PosTrening (" + str(pos) + ").jpg" )
                pass

            try:
                file.write(str(self.HOGde.compute(bildePosMat, padding=(0,0)))+'\n')

            except:
                tkMessageBox.showinfo("Info","Greier ikke a lagre fila posHoGVect.txt" )
                pass
            self.progressBar.oppdaterProgressbar( pos, 0)

        file.close()

        file = open( "negHoGVect.txt" , 'w')
        for neg in range(1,self.antallNeg):
            # Laster inn bilder med fjes og utforer HoG. Endrer storrelse med resize(bredde,hoyde)
            try:
                bildeNeg = Image.open( self.param.getParam(1) + "\\neg" + "\NegTrening (" + str(neg) + ").jpg" )
                bildeNegSkalert = bildeNeg.resize((48,64), Image.ANTIALIAS)
                bildeNegMat = numpy.asarray(bildeNegSkalert)
            except:
                tkMessageBox.showinfo("Info","Feil med lasting av " + str(self.param.getParam(1))+ "\\neg" + "\NegTrening (" + str(neg) + ").jpg" )
                pass

            try:
                file.write(str(self.HOGde.compute(bildeNegMat, padding=(0,0)))+'\n')
            except:
                tkMessageBox.showinfo("Info","Greier ikke a lagre fila negHoGVect.txt" )
                pass
            self.progressBar.oppdaterProgressbar( pos, neg)

        file.close()
    pass


class ProgressBar:
    global overskrift
    global master

    def __init__(self, tittel, guiRef, maxPos, maxNeg):
        self.overskrift = tittel
        self.master = guiRef
        self.maxpos = maxPos
        self.maxneg = maxNeg

        self.master.title(tittel)
        self.lblPos = Label( self.master, text= "Positive Bilder" )
        self.progPos = ttk.Progressbar(self.master,orient ="horizontal",length = 500, mode ="determinate")
        self.lblNeg = Label( self.master, text= "Negative Bilder" )
        self.progNeg = ttk.Progressbar(self.master,orient ="horizontal",length = 500, mode ="determinate")

        self.lblPos.pack()
        self.progPos.pack()
        self.lblNeg.pack()
        self.progNeg.pack()

        self.progNeg["maximum"] = self.maxneg
        self.progPos["maximum"] = self.maxpos
        self.progNeg["value"] = 0
        self.progPos["value"] = 0
        return

    def settMaxMin(self, maxPos,minPos,maxNeg,minNeg):
        self.maxpos = maxPos-1
        self.maxneg = maxNeg-1
        self.progNeg["maximum"] = self.maxneg
        self.progPos["maximum"] = self.maxpos
        self.progNeg["value"] = minNeg
        self.progPos["value"] = minPos
        return

    def oppdaterProgressbar(self, pos, neg):

        self.progNeg["value"] = neg
        self.progPos["value"] = pos
        return
