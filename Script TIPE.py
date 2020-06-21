## Bibliothèques


import numpy as np
import matplotlib.pyplot as plt
import time as t
import random as rd
import keyboard as kb


## Classes


class Sardine:
    def __init__(self, IA, position, trajectoire, vitesse, milieu):
        self.IA = IA("sardine")             #Fait appel à la classe IA concernée
        self.position = position            #Définition de la position
        self.trajectoire = trajectoire
        self.vitesse = vitesse
        self.vitesseEvolutive = vitesse
        self.milieu = milieu
        self.pression = [0,0,0,0]           #Pression initiale nulle
        self.visionPreda = []                    #Vision éventuelle de prédateurs (ne les voit pas au temps 0)
        self.visionSard = []
        self.vie = True                     #La sardine est initialement vivante
    
    def deplacement(self):
        self.position = self.IA.deplacement(self, self.position, self.trajectoire, self.vitesseEvolutive, self.pression, self.visionPreda, self.visionSard, self.milieu)
        self.milieu.Allpos[self.milieu.Sards.index(self)] = self.position
    
    def mort(self):                         #On désactive toutes les fonctionnalités de la sardine
       del self.milieu.Allpos[self.milieu.Allpos.index(self.position)]
       del self.milieu.Sards[self.milieu.Sards.index(self)]
       self.vie = False
       self.vision = None
       self.pression = None
       self.position = None
       self.IA = None
       def dep(self):
           pass
       self.deplacement = dep
    
    def creation(IA, vitesse, milieu):
        sardine = Sardine(IA,[rd.gauss(milieu.taille[0]/2,10),rd.gauss(milieu.taille[1]/2,10)],None,vitesse,milieu)        #position : répartition aléatoire en gaussienne autour du centre. 
        milieu.Allpos.append(sardine.position)
        milieu.Sards.append(sardine)
        return sardine
    
    def ActuVitesse(self):      # La vitesse dépend ici du nombre de voisins, à terme permet une valorisation du déplacement de groupe.
        self.vitesseEvolutive = self.vitesse*(1 + len(self.visionSard)*0.05)
    
    def ActuVision(self):       # Actualise les individus vus par la sardine (à 360°, pour une distance donnée)
        for preda in self.milieu.Predas :
            if distance(self,preda)<=10 and not preda in self.visionPreda :
                self.visionPreda.append(preda)
            elif distance(self,preda)>10 and preda in self.visionPreda :
                self.visionPreda.pop(self.visionPreda.index(preda))
        for sard in self.milieu.Sards :
            if distance(self,sard)<=10 and not sard in self.visionSard :
                self.visionSard.append(sard)
            elif distance(self,sard)>10 and sard in self.visionSard :
                self.visionSard.pop(self.visionSard.index(sard))


class Predateur:
    def __init__(self, IA, position, trajectoire, vitesse, milieu):
        self.IA = IA("predateur")           #Definition de l'IA
        self.position = position            #Definition de la position
        self.trajectoire = trajectoire      #Equation de la trajectoire
        self.vitesse = vitesse              #La vitesse sera en réalité la distance parcourue durant le temps TpsFrames
        self.milieu = milieu                
        self.victimes = 0                   #Initialement, aucune victime
        self.vision = []                    #Sardines dans son champ de vision
        self.vie = True                     #Initialement en vie
    
    def deplacement(self):                  #Appel à l'IA pour le déplacement
        pos = self.position
        self.position = self.IA.deplacement(self, self.position, self.trajectoire, self.vitesse, self.vision, self.milieu)
        self.trajectoire = [(self.position[0]-pos[0])/np.sqrt((self.position[0]-pos[0])**2 + (self.position[1]-pos[1])**2),(self.position[1]-pos[1])/np.sqrt((self.position[0]-pos[0])**2 + (self.position[1]-pos[1])**2)]
    
    def elimination(self, sardine):         #Elimination d'une sardine
        self.victimes += 1
        self.milieu.victimes += 1
        sardine.mort()
    
    def stop(self):                         #Arret du prédateur, generalement en sortie de zone (à voir pour satiété)
       self.vie = False
       self.vision = None
       self.position = None
       self.trajectoire = None
       self.IA = None
       def dep(self):
           pass
       self.deplacement = dep
       return self.victimes


class Milieu:
    def __init__(self, taille, Fpression):
        self.taille = taille[:]
        self.Fpression = Fpression[:]
        self.Allpos = []                    #Positions de toutes les sardines
        self.Sards = []                     #Liste des sardines
        self.Predas = []                    #Liste des prédateurs
        self.frames = []                    #Positions des sardines et du prédateur aux différents temps
        self.victimes = 0                   #Victimes initiales : 0
    
    def fin(self):
        for preda in self.Predas:
            if not (0 < preda.position[0] < self.taille[0] or 0 < preda.position[1] < self.taille[1]) :
                for sard in self.Sards :
                    sard.mort()
                for preda in self.Predas:
                    preda.stop()
    
    def boolFin(self):
        return False in [(0 <= preda.position[0] <= self.taille[0] or 0 <= preda.position[1] <= self.taille[1]) for preda in self.Predas]
    
    def frame(self) :
        L=[]
        for i in self.Predas:
            L.append(i.position)
        self.frames.append([self.Allpos[:],L,self.victimes])     #Définiton d'une frame


class IA1:      #Déplacement aléatoire, IA peu intéressante. 
    def __init__(self, type):
        self.type = type
        if type == 'sardine' :
            def deplacement(self, position, trajectoire, vitesse, pression, visionPreda, visionSard, milieu):
                return [int(rd.random()*milieu.taille[0]*1000)/1000,int(rd.random()*milieu.taille[1]*1000)/1000]        #Nombre aléatoire entre 0 et la taille du milieu, à 10^-3 près
            self.deplacement = deplacement
        else :
            def deplacement(self, position, trajectoire, vitesse, vision, milieu):
                return [int(rd.random()*milieu.taille[0]*1000)/1000,int(rd.random()*milieu.taille[1]*1000)/1000]
            self.deplacement = deplacement


class IA2:      #Principalement pour les prédateurs, déplacement linéaire.
    def __init__(self, type):
        self.type = type
        if type == 'sardine' :
            def deplacement(self, position, trajectoire, vitesse, pression, visionPreda, visionSard, milieu):
                return position
            self.deplacement = deplacement
        else :
            def deplacement(self, position, trajectoire, vitesse, vision, milieu):
                return [position[0]+vitesse*trajectoire[0],position[1]+vitesse*trajectoire[1]]
            self.deplacement = deplacement


class IA3:      #IA principalement pour debug, permet de déplacer l'individu (sardine ou prédateur) à l'aide des flèches du pavé numérique.
    def __init__(self, type):
        self.type = type
        if type == 'sardine' :
            def deplacement(self, position, trajectoire, vitesse, pression, visionPreda, visionSard, milieu):
                pos = position[:]
                if kb.is_pressed("haut") :
                    pos = [pos[0],pos[1] + vitesse]
                if kb.is_pressed("bas") :
                    pos = [pos[0],pos[1] - vitesse]
                if kb.is_pressed("droite") :
                    pos = [pos[0] + vitesse,pos[1]]
                if kb.is_pressed("gauche") :
                    pos = [pos[0] - vitesse,pos[1]]
                return pos
            self.deplacement = deplacement
        else :
            def deplacement(self, position, trajectoire, vitesse, vision, milieu):
                pos = position[:]
                if kb.is_pressed("haut") :
                    pos = [pos[0],pos[1] + vitesse]
                if kb.is_pressed("bas") :
                    pos = [pos[0],pos[1] - vitesse]
                if kb.is_pressed("droite") :
                    pos = [pos[0] + vitesse,pos[1]]
                if kb.is_pressed("gauche") :
                    pos = [pos[0] - vitesse,pos[1]]
                return pos
            self.deplacement = deplacement

class IA4 :     # IA au déplacement aléatoire mais physiquement réel (à l'inverse de l'IA1 qui se téléporte)
    def __init__(self,type):
        self.type = type
        if type == 'sardine' :
            def deplacement(self, position, trajectoire, vitesse, pression, visionPreda, visionSard, milieu):
                int = rd.randint(0,3)
                pos = position[:]
                if int == 0 and pos[1] < milieu.taille[1] - vitesse :
                    pos = [pos[0],pos[1] + vitesse]
                if int == 1 and pos[1] > vitesse :
                    pos = [pos[0],pos[1] - vitesse]
                if int == 2 and pos[0] < milieu.taille[0] - vitesse :
                    pos = [pos[0] + vitesse,pos[1]]
                if int == 3 and pos[0] > vitesse :
                    pos = [pos[0] - vitesse,pos[1]]
                return pos
            self.deplacement = deplacement
        else :
            def deplacement(self, position, trajectoire, vitesse, vision, milieu):
                int = rd.randint(0,3)
                pos = position[:]
                if int == 0 and pos[1] < milieu.taille[1] - vitesse :
                    pos = [pos[0],pos[1] + vitesse]
                if int == 1 and pos[1] > vitesse :
                    pos = [pos[0],pos[1] - vitesse]
                if int == 2 and pos[0] < milieu.taille[0] - vitesse :
                    pos = [pos[0] + vitesse,pos[1]]
                if int == 3 and pos[0] > vitesse :
                    pos = [pos[0] - vitesse,pos[1]]
                return pos
            self.deplacement = deplacement

class IA5 :     # IA la plus avancée avant la mise en pause du projet : fait la moyenne des vecteurs pointant les prédateurs dans son champ de vision et de déplace dans le sens inverse. Permet un éloignement optimal de l'individu dans une vision égoïste.
    def __init__(self,type):
        self.type = type
        if type == 'sardine' :
            def deplacement(self, position, trajectoire, vitesse, pression, visionPreda, visionSard, milieu):
                self.ActuVitesse()
                if visionPreda != [] :
                    self.trajectoire = trajectoire_moyenne(self,visionPreda)
                    trajectoire = self.trajectoire
                    if 0 <= position[0]+vitesse*trajectoire[0] <= milieu.taille[0] and 0 <= position[1]+vitesse*trajectoire[1] <= milieu.taille[1] :
                        return [position[0]+vitesse*trajectoire[0],position[1]+vitesse*trajectoire[1]]
                    elif 0 <= position[0]+vitesse*trajectoire[0] <= milieu.taille[0] :
                        return [position[0]+vitesse*trajectoire[0],position[1]]
                    elif 0 <= position[1]+vitesse*trajectoire[1] <= milieu.taille[1] :
                        return [position[0],position[1]+vitesse*trajectoire[1]]
                    else :
                        return position
                else :
                    self.trajectoire = [0,0]
                    return position
        else :
            def deplacement(self, position, trajectoire, vitesse, vision, milieu):
                if milieu.Sards != [] :
                    cible = plusproche(self,milieu.Sards)
                    self.trajectoire = [(cible.position[0]-position[0])/distance(self,cible),(cible.position[1]-position[1])/distance(self,cible)]
                    trajectoire = self.trajectoire
                    if 0 <= position[0]+vitesse*trajectoire[0] <= milieu.taille[0] and 0 <= position[1]+vitesse*trajectoire[1] <= milieu.taille[1] :
                        return [position[0]+vitesse*trajectoire[0],position[1]+vitesse*trajectoire[1]]
                    elif 0 <= position[0]+vitesse*trajectoire[0] <= milieu.taille[0] :
                        return [position[0]+vitesse*trajectoire[0],position[1]]
                    elif 0 <= position[1]+vitesse*trajectoire[1] <= milieu.taille[1] :
                        return [position[0],position[1]+vitesse*trajectoire[1]]
                    else :
                        return position
                else :
                    return position
        self.deplacement = deplacement

class Modelisation:
    def __init__(self,TpsFrames, milieu):
        self.frames = milieu.frames
        self.milieu = milieu
        self.TpsFrames = TpsFrames                  #Temps entre deux frames
    
    def affichage(self, n, plot=plt):
        self.lecture(self.frames[n],plot)           #Affiche la n-ième frame
    
    def affichage_remanant(self, n, plot=plt):
        self.lecture_remanante(self.frames[n-1],plot)
    
    def lecture(self, frame, plot):
        plot.plot([0,self.milieu.taille[0],self.milieu.taille[0],0,0], [0,0,self.milieu.taille[1],self.milieu.taille[1],0], c='black')
        plot.scatter([pos[0] for pos in frame[1]], [pos[1] for pos in frame[1]], c='red')
        plot.scatter([pos[0] for pos in frame[0]], [pos[1] for pos in frame[0]], c='blue')
    
    def lecture_remanante(self, frame, plot):
        plot.scatter([pos[0] for pos in frame[1]], [pos[1] for pos in frame[1]], c='red', alpha=0.5)
        plot.scatter([pos[0] for pos in frame[0]], [pos[1] for pos in frame[0]], c='blue', alpha=0.1)
    
    def film(self, circle):
        fig, ax = plt.subplots()
        temps = self.TpsFrames
        for i in range(len(self.frames)-1) :
            self.affichage(i,ax)
            if i!=0 :
                self.affichage_remanant(i,ax)
            if circle :
                for pos in self.frames[i][1] :
                    c = plt.Circle((pos[0],pos[1]),1,color='r',alpha=0.1)
                    ax.add_artist(c)
            ax.axis('equal')
            ax.text(0, 10.2, 'Nombre de victime : ' + str(self.frames[i][2]), horizontalalignment = 'left', verticalalignment = 'center')
            fig.show()
            plt.pause(temps)
            ax.cla()


## Main


NbSards = 20
taille = [100,100]
def distance(sard1,sard2):
    A,B = sard1.position,sard2.position
    return np.sqrt((A[0]-B[0])**2 + (A[1]-B[1])**2)
def plusproche(preda,sards):
    min = 0
    for i in range(len(sards)):
        if distance(preda,sards[min]) > distance(preda,sards[i]) :
            min = i
    return sards[min]
def trajectoire_moyenne(sard,predas):
    L = []
    for preda in predas :
        L.append([(preda.position[0]-sard.position[0])/distance(sard,preda),(preda.position[1]-sard.position[1])/distance(sard,preda)])
    traj = [0,0]
    for i in L :
        traj[0] -= i[0]
        traj[1] -= i[1]
    return [traj[0]/len(predas),traj[1]/len(predas)]
milieu1 = Milieu(taille,[])
VitPreda = 10
VitSard = 7
TpsFrame = 0.1                                                                  #Temps entre chaque frame lors du film
DistPreda = VitPreda*TpsFrame
DistSard = VitSard*TpsFrame
TrajPreda = [milieu1.taille[0]/np.sqrt(milieu1.taille[0]**2 + milieu1.taille[1]**2),milieu1.taille[0]/np.sqrt(milieu1.taille[0]**2 + milieu1.taille[1]**2)]  #expression barbare : vercteur unitaire de traj


plt.close()
sard = []
preda1 = Predateur(IA5,[0,0],TrajPreda,DistPreda,milieu1)
preda2 = Predateur(IA5,[100,100],TrajPreda,DistPreda,milieu1)
for i in range(NbSards):
    sard.append(Sardine.creation(IA5, DistSard, milieu1))
# Sardine.creation(IA5,0.2,milieu1)
milieu1.Predas = [preda1,preda2]
milieu1.frame()


while not milieu1.boolFin() and milieu1.Sards != [] :
    for preda in milieu1.Predas :
        preda.deplacement()
        for sard in milieu1.Sards :
            if distance(preda,sard) < 5 :
                preda.elimination(sard)
                print(milieu1.victimes)
    for sard in milieu1.Sards:
        sard.ActuVision()
        sard.deplacement()
    milieu1.frame()

plt.close()

modelisation = Modelisation(TpsFrame/10,milieu1)

t1 = t.time()
modelisation.film(True)
t2 = t.time()
plt.close()
L = [preda.victimes for preda in milieu1.Predas]
print(milieu1.victimes,L,t2-t1)