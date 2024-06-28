"""
Jeu basé sur l'univers de l'Attaque des Titans par IMBERT Violette et BIHET Lucie
Réalisé sous Python 3.9
"""

import pygame
from pygame.locals import *
import math
import random
import os
os.chdir(os.path.dirname(__file__))                                             # Change le répertoire courant pour se déplacer dans le répertoire du programme

pygame.init()
pygame.font.init()
pygame.mixer.init()


SOL = 400

"""Varibales globales du main"""
FPS = 60
ECRAN_X = 1280
ECRAN_Y = 720


"""Varibales globales de la classe Caillou"""
VITESSE_CAILLOU_MIN = 10
VITESSE_CAILLOU_MAX = 25
X_DEPART_CAILLOU_MIN = 20
X_DEPART_CAILLOU_MAX = 1200
Y_DEPART_CAILLOU_MIN = 0
Y_DEPART_CAILLOU_MAX = 250
TAILLE_CAILLOU = 100
Y_CHUTE_MAX = 600
DEGAT_CAILLOU = 10

"""Varibales globales de la classe CaillouTombant"""
POSITION_BARRE = 10
EPAISSEUR_BARRE = 10

"""Varibales globales de la classe Score"""
NOIR = (0, 0, 0)
BLANC = (255, 255, 255)

"""Varibales globales de la classe Jeu"""
INDICE_TITAN = 8
VITESSE_CHUTE_RAPIDE = 20
VITESSE_CHUTE_LENTE = 100
DECLENCHEUR_CHUTE_RAPIDE = 10

"""Varibales globales de la classe Joueur"""
VIE_JOUEUR = 150
ATTAQUE_JOUEUR = 20
VITESSE_JOUEUR = 30
TAILLE_JOUEUR = 150
POSITION_JOUEUR_X = 250
POSITION_JOUEUR_Y = 520
GRIS = (60, 63, 60)
VERT = (111, 210, 46)
BARRE_DE_VIE_X = 0
BARRE_DE_VIE_Y = 0
EPAISSEUR_BARRE_JOUEUR = 5

"""Varibales globales de la classe Titans"""
VIE_TITANS = 100
VITESSE_TITANS_MIN = 2
VITESSE_TITANS_MAX = 8
ATTAQUE_TITANS = 0.5
POSITION_TITAN_X_MIN = 1400
POSITION_TITAN_X_MAX = 1800
VERT_BLEU = (43, 135, 98)
ROUGE = (230, 76, 0)
TYPE_TITAN = ['images/titan_normal.png', 'images/titan_normal2.png']
EPAISSEUR_BARRE_TITANS = 7


#####


class Titan(pygame.sprite.Sprite):
    def __init__(self, jeu):
        """Permet d'initialiser les paramètres de la classe Titan"""
        super().__init__()
        self.vie = VIE_TITANS
        self.max_vie = VIE_TITANS
        self.vitesse = random.randint(VITESSE_TITANS_MIN, VITESSE_TITANS_MAX)
        self.attaque = ATTAQUE_TITANS
        self.image = pygame.image.load(TYPE_TITAN[random.randint(0, 1)])
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(POSITION_TITAN_X_MIN, POSITION_TITAN_X_MAX)
        self.rect.y = SOL
        self.jeu = jeu

    def deplacement_titan(self):
        """Permet le déplacement des titans vers la gauche"""
        if not self.jeu.check_collision(self, self.jeu.tous_les_joueurs):
            self.rect.x -= self.vitesse

        if self.jeu.check_collision(self, self.jeu.tous_les_joueurs) and not self.jeu.pressed.get(pygame.K_SPACE):
            self.jeu.joueur.degats(ATTAQUE_TITANS)

    def degats(self, montant_dgt):
        """Gestion des dégats du titan"""
        if self.vie - montant_dgt > 0:
            self.vie -= montant_dgt
        elif self.vie - montant_dgt <= 0 and self.jeu.indice_titan < INDICE_TITAN:
            self.jeu.indice_titan += 1
            self.jeu.indice_chute_rapide += 1
            self.rect.x = random.randint(POSITION_TITAN_X_MIN, POSITION_TITAN_X_MAX)
            self.vitesse = random.randint(VITESSE_TITANS_MIN, VITESSE_TITANS_MAX)
            self.vie = VIE_TITANS
            self.image = pygame.image.load(TYPE_TITAN[random.randint(0, 1)])
            self.jeu.score.update_score()
        elif self.vie - montant_dgt <= 0 and self.jeu.indice_titan == INDICE_TITAN:
            self.jeu.indice_chute_rapide += 1
            self.jeu.all_titans.remove(self)
            self.jeu.score.update_score()

    def barre_de_vie(self, surface):
        """Crée la barre de vie du titan (visuel)"""
        pygame.draw.rect(surface, GRIS, [self.rect.x + 20, self.rect.y - 20, self.max_vie, EPAISSEUR_BARRE_TITANS])
        pygame.draw.rect(surface, VERT_BLEU, [self.rect.x + 20, self.rect.y - 20, self.vie, EPAISSEUR_BARRE_TITANS])



class Caillou(pygame.sprite.Sprite):
    def __init__(self, CaillouTombant):
        """Permet d'initialiser les paramètres de la classe Caillou"""
        super().__init__()
        self.image = pygame.image.load('images/caillou.png')
        self.image = pygame.transform.scale(self.image, (TAILLE_CAILLOU, TAILLE_CAILLOU))
        self.rect = self.image.get_rect()
        self.vitesse = random.randint(VITESSE_CAILLOU_MIN, VITESSE_CAILLOU_MAX)
        self.rect.x = random.randint(X_DEPART_CAILLOU_MIN, X_DEPART_CAILLOU_MAX)
        self.rect.y = -random.randint(Y_DEPART_CAILLOU_MIN, Y_DEPART_CAILLOU_MAX)
        self.caillou_tombant = CaillouTombant

    def supprimer_caillou(self):
        """Permet de supprimer les cailloux lorsqu'ils touchent le bas de la zone de jeu"""
        self.caillou_tombant.all_caillou.remove(self)

    def chute(self):
        """Permet le déplacements des cailloux pendant leurs chutes
        (mouvement rectiligne vertical vers le bas)"""
        self.rect.y += self.vitesse

        if self.rect.y >= Y_CHUTE_MAX:
            self.supprimer_caillou()

        if self.caillou_tombant.jeu.check_collision(self, self.caillou_tombant.jeu.tous_les_joueurs):
            self.supprimer_caillou()
            self.caillou_tombant.jeu.joueur.degats(DEGAT_CAILLOU)



class CaillouTombant:
    def __init__(self, Jeu):
        """Permet d'initialiser les paramètres de la classe CaillouTombant"""
        self.all_caillou = pygame.sprite.Group()
        self.jeu = Jeu

    def pluie_de_cailloux(self):
        """Ajoute les cailloux qui apparaissent au groupe de sprite"""
        self.all_caillou.add(Caillou(self))

    def barre_evenement_chute_rapide(self, surface):
        pygame.draw.rect(surface, GRIS, [POSITION_BARRE, POSITION_BARRE, ECRAN_X - 20, EPAISSEUR_BARRE])
        pygame.draw.rect(surface, ROUGE, [POSITION_BARRE, POSITION_BARRE, self.jeu.temps_de_chute_rapide, EPAISSEUR_BARRE])




class Joueur(pygame.sprite.Sprite):
    def __init__(self, jeu):
        """Permet d'initialiser les paramètres de la classe Joueur"""
        super().__init__()
        self.vie = VIE_JOUEUR
        self.max_vie = VIE_JOUEUR
        self.attaque = ATTAQUE_JOUEUR
        self.vitesse = VITESSE_JOUEUR
        self.image = pygame.image.load("images/levi.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TAILLE_JOUEUR, TAILLE_JOUEUR))
        self.rect = self.image.get_rect()
        self.rect.x = POSITION_JOUEUR_X
        self.rect.y = POSITION_JOUEUR_Y
        self.jeu = jeu

    def droite(self):
        """Permet le déplacement à droite du joueur selon sa vitesse"""
        if not self.jeu.check_collision(self, self.jeu.all_titans):
            self.rect.x += self.vitesse

    def gauche(self):
        """Permet le déplacement à gauche du joueur selon sa vitesse"""
        self.rect.x -= self.vitesse

    def barre_de_vie(self, surface):
        """Crée la barre de vie du joueur (visuel)"""
        pygame.draw.rect(surface, GRIS, [self.rect.x + 10, self.rect.y - 20, self.max_vie, EPAISSEUR_BARRE_JOUEUR])
        pygame.draw.rect(surface, VERT, [self.rect.x + 10, self.rect.y - 20, self.vie, EPAISSEUR_BARRE_JOUEUR])

    def degats(self, montant_dgt):
        """Inflige les dégats au joueur"""
        if self.vie - montant_dgt > montant_dgt:
            self.vie -= montant_dgt
        else:
            self.jeu.game_over()


class Son:
    def __init__(self):
        """Permet d'initialiser les paramètres de la classe Son"""
        self.sons = {
            'début': pygame.mixer.Sound("son/erwin_sound.ogg"),
            'mort': pygame.mixer.Sound("son/mikasa_sound.ogg")
        }
    def play_son(self, nom):
        """Jou le son entré en paramètre lors de l'appel de la fonction"""
        self.sons[nom].set_volume(0.2)
        self.sons[nom].play()



class Score:
    def __init__(self, jeu):
        """Permet d'initialiser les paramètres de la classe Score"""
        self.jeu = jeu
        self.score_joueur = 0

    def lire_fichier(self, fichier):
        """Permet de lire ce qu'il y a déjà d'écrit dans le fichier"""
        with open(fichier, 'r') as fichier2:
            self.jeu.liste_score = fichier2.read().splitlines()

    def sauvegarder_fichier(self, fichier):
        """Permet d'enregistrer dans le fichier toutes les modifications effectuées"""
        with open(fichier, 'w') as fichier2:
            fichier2.write(str(self.score_joueur))

    def afficher_meilleur_score(self):
        """Affiche sur l'accueil le meilleur score"""
        myfont = pygame.font.SysFont('Times New Roman', 25)
        texte_meilleure_score = myfont.render('Meilleur score : ' + str(self.jeu.liste_score[0]), False, NOIR)
        texte_meilleure_score_rect = texte_meilleure_score.get_rect()
        texte_meilleure_score_rect = (15, 5)
        self.jeu.fenetre.blit(texte_meilleure_score, texte_meilleure_score_rect)

    def update_score(self):
        """Met à jour le score au cours du jeu"""
        self.score_joueur += 1

    def afficher_score(self):
        """Affiche le score du joueur à l'écran"""
        myfont = pygame.font.SysFont('Times New Roman', 25)
        texte_score_joueur = myfont.render('Score actuel : ' + str(self.score_joueur), False, BLANC)
        texte_score_joueur_rect = texte_score_joueur.get_rect()
        texte_score_joueur_rect.center = (1100, 40)
        self.jeu.fenetre.blit(texte_score_joueur, texte_score_joueur_rect)



class Jeu:
    def __init__(self, liste_score, fenetre):
        """Permet d'initialiser les paramètres de la classe Jeu"""
        self.fenetre = fenetre
        self.liste_score = liste_score

        self.score = Score(self)
        self.joueur = Joueur(self)
        self.caillou_tombant = CaillouTombant(self)

        self.en_jeu = False
        self.en_regles = False
        self.info_icon = pygame.image.load("images/info.png")
        self.info_icon = pygame.transform.scale(self.info_icon, (50, 50))
        self.info_icon_rect = self.info_icon.get_rect()
        self.info_icon_rect.center = (1220, 40)

        self.all_titans = pygame.sprite.Group()                                 #crée un groupe de sprites vide

        self.tous_les_joueurs = pygame.sprite.Group()                           #crée un groupe de sprites vide
        self.tous_les_joueurs.add(self.joueur)

        self.indice_chute = 0
        self.indice_titan = 0
        self.vitesse_chute = VITESSE_CHUTE_LENTE
        self.indice_chute_rapide = 0
        self.temps_de_chute_rapide = ECRAN_X - 20

        self.pressed = {}


        self.son = Son()

    def apparition_titan(self):
        """Permet la création d'un titan à l'écran"""
        titan = Titan(self)
        self.all_titans.add(titan)

    def check_collision(self, sprite, groupe):
        """Vérifie la collision entre deux éléments (peut être utilisé pour plusieurs éléments"""
        return pygame.sprite.spritecollide(sprite, groupe, False, pygame.sprite.collide_mask)

    def start(self):
        """Permet de lancer la phase des titans à chaque fin de phase d'esquive de caillou"""
        self.en_jeu = True
        self.apparition_titan()
        self.apparition_titan()

    def remise_a_zero(self):
        """Réinitialise toutes les variables quand le joueur perd ou que la phase de la grosse chute de caillou se termine"""
        self.all_titans = pygame.sprite.Group()
        self.indice_chute = 0
        self.indice_titan = 0
        self.vitesse_chute = VITESSE_CHUTE_LENTE
        self.indice_chute_rapide = 0
        self.temps_de_chute_rapide = ECRAN_X - 20

    def game_over(self):
        """Arrête le jeu lorsque le joueur n'a plus de vie
        Revient au menu d'accueil
        Gère le meilleur score et remet le score à 0
        """
        print('Perdu')
        self.son.play_son('mort')
        self.en_jeu = False
        self.joueur.vie = self.joueur.max_vie
        self.caillou_tombant.all_caillou = pygame.sprite.Group()            #remplace l'ancien groupe par groupe de sprites vide, donc supprime les entités
        self.joueur.rect.x = POSITION_JOUEUR_X
        self.remise_a_zero()
        if int(self.score.score_joueur) > int(self.liste_score[0]):
            self.liste_score[0] = self.score.score_joueur
            self.score.sauvegarder_fichier('meilleur_score.txt')
        self.score.score_joueur = 0

    def afficher_regles(self):
        """Afficher les règles du jeu"""
        self.en_regles = True
        fond_regles = pygame.image.load("images/background_regles.png")
        self.fenetre.blit(fond_regles, (0, 0))
        self.fenetre.blit(self.info_icon, self.info_icon_rect)


    def gestion_chute_caillou(self):
        """Gère tous les éléments liés à la chute des cailloux"""
        if self.indice_chute_rapide == DECLENCHEUR_CHUTE_RAPIDE:                #déclenche la phase d'esquive de caillou quand 10 titans sont tués
            self.vitesse_chute = VITESSE_CHUTE_RAPIDE
            self.indice_chute = 0
            self.indice_chute_rapide = 0

        if self.indice_chute == self.vitesse_chute:                             #fait apparaitre un caillou tous les x passages dans la boucle principale
            self.caillou_tombant.pluie_de_cailloux()
            self.indice_chute = 0
        self.caillou_tombant.all_caillou.draw(self.fenetre)

        if self.vitesse_chute == VITESSE_CHUTE_RAPIDE:                          #fait baisser la barre de durée de la grosse chute de caillou
            self.temps_de_chute_rapide -= 2

        if self.temps_de_chute_rapide == 0:                                     #relance la vague de titan à la fin de la grosse chute de caillou
            self.remise_a_zero()
            self.start()



    def update(self):
        """Fonction qui permet de mettre à jour le jeu à chaque tour de la boucle principale pour afficher les nouveaux éléments, initilaiser les mouvements, etc..."""
        self.fenetre.blit(self.joueur.image, self.joueur.rect)
        self.score.afficher_score()
        self.indice_chute += 1

        for titan in self.all_titans:                                           #applique les fonctions liées aux titans à chaque titan indépendamment
            titan.deplacement_titan()
            titan.barre_de_vie(self.fenetre)

        self.joueur.barre_de_vie(self.fenetre)
        self.caillou_tombant.barre_evenement_chute_rapide(self.fenetre)
        self.all_titans.draw(self.fenetre)

        for caillou in self.caillou_tombant.all_caillou:
            caillou.chute()

        self.gestion_chute_caillou()

        if self.pressed.get(pygame.K_RIGHT) and self.joueur.rect.x < self.fenetre.get_width() - self.joueur.rect.width:
            self.joueur.droite()
        elif self.pressed.get(pygame.K_LEFT) and self.joueur.rect.x > 0:
            self.joueur.gauche()



def lancement_jeu(jeu, fenetre, score):
    """Importe les images nécessaires pour la 'décoration'"""
    pygame.display.set_caption('Attack on Titan - The Game')
    icon = pygame.image.load("images/bataillon.png")
    pygame.display.set_icon(icon)

    fond = pygame.image.load("images/background.jpg")

    fond_acceuil = pygame.image.load("images/background_accueil.jpg")

    banniere = pygame.image.load("images/banner_snk.png")
    banniere_rect = banniere.get_rect()
    banniere_rect.center = (640, 150)

    info_icon = pygame.image.load("images/info.png")
    info_icon = pygame.transform.scale(info_icon, (50, 50))
    info_icon_rect = info_icon.get_rect()
    info_icon_rect.center = (1220, 40)

    mikasa_icon = pygame.image.load("images/mikasa_icon.jpg")
    mikasa_icon = pygame.transform.scale(mikasa_icon, (200, 200))
    mikasa_icon_rect = mikasa_icon.get_rect()
    mikasa_icon_rect.center = (235, 550)

    jean_icon = pygame.image.load("images/jean_icon.jpg")
    jean_icon = pygame.transform.scale(jean_icon, (200, 200))
    jean_icon_rect = jean_icon.get_rect()
    jean_icon_rect.center = (505, 550)

    levi_icon = pygame.image.load("images/levi_icon.jpg")
    levi_icon = pygame.transform.scale(levi_icon, (200, 200))
    levi_icon_rect = levi_icon.get_rect()
    levi_icon_rect.center = (775, 550)

    hange_icon = pygame.image.load("images/hange_icon.jpg")
    hange_icon = pygame.transform.scale(hange_icon, (200, 200))
    hange_icon_rect = hange_icon.get_rect()
    hange_icon_rect.center = (1045, 550)

    myfont = pygame.font.SysFont('Times New Roman', 35)
    texte_accueil = myfont.render('Choisissez votre personnage pour lancer la partie', False, BLANC)
    texte_accueil_rect = texte_accueil.get_rect()
    texte_accueil_rect.center = (640, 360)

    pygame.key.set_repeat(400, 30)

    clock = pygame.time.Clock()

    continuer = 1
    while continuer:
        fenetre.blit(fond, (0, 0))
        if jeu.en_jeu and not jeu.en_regles:
            jeu.update()
        else:
            fenetre.blit(fond_acceuil, (0, 0))
            fenetre.blit(banniere, banniere_rect)
            fenetre.blit(info_icon, info_icon_rect)
            fenetre.blit(mikasa_icon, mikasa_icon_rect)
            fenetre.blit(jean_icon, jean_icon_rect)
            fenetre.blit(levi_icon, levi_icon_rect)
            fenetre.blit(hange_icon, hange_icon_rect)
            fenetre.blit(texte_accueil, texte_accueil_rect)
            score.afficher_meilleur_score()

        if jeu.en_regles:
            jeu.afficher_regles()
        for event in pygame.event.get():
            if event.type == QUIT:
                continuer = 0                                                   #Arrête la boucle si le joueur quitte le jeu
                pygame.quit()
                exit(0)
            elif event.type == KEYDOWN:
                jeu.pressed[event.key] = True
                for titan in jeu.all_titans:
                    if event.key == pygame.K_SPACE and jeu.check_collision(titan, jeu.tous_les_joueurs):
                        titan.degats(ATTAQUE_JOUEUR)
            elif event.type == pygame.KEYUP:
                jeu.pressed[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mikasa_icon_rect.collidepoint(event.pos) and not jeu.en_regles:
                    jeu.joueur.image = pygame.image.load("images/mikasa.png")
                    jeu.joueur.image = pygame.transform.scale(jeu.joueur.image, (TAILLE_JOUEUR, TAILLE_JOUEUR))
                    jeu.start()
                    jeu.son.play_son('début')
                elif jean_icon_rect.collidepoint(event.pos) and not jeu.en_regles:
                    jeu.joueur.image = pygame.image.load("images/jean.png")
                    jeu.joueur.image = pygame.transform.scale(jeu.joueur.image, (TAILLE_JOUEUR, TAILLE_JOUEUR))
                    jeu.start()
                    jeu.son.play_son('début')
                elif levi_icon_rect.collidepoint(event.pos) and not jeu.en_regles:
                    jeu.joueur.image = pygame.image.load("images/levi.png")
                    jeu.joueur.image = pygame.transform.scale(jeu.joueur.image, (TAILLE_JOUEUR, TAILLE_JOUEUR))
                    jeu.start()
                    jeu.son.play_son('début')
                elif hange_icon_rect.collidepoint(event.pos) and not jeu.en_regles:
                    jeu.joueur.image = pygame.image.load("images/hange.png")
                    jeu.joueur.image = pygame.transform.scale(jeu.joueur.image, (TAILLE_JOUEUR, TAILLE_JOUEUR))
                    jeu.start()
                    jeu.son.play_son('début')
                elif info_icon_rect.collidepoint(event.pos) and not jeu.en_regles:
                    jeu.afficher_regles()
                elif jeu.en_regles and jeu.info_icon_rect.collidepoint(event.pos):
                    jeu.en_regles = False


        pygame.display.flip()
        clock.tick(FPS)



def main():
    """Fonction qui permet de faire tourner le jeu
    Initialise la taille de la fenêtre et de certaines images (immobiles)
    Permet la gestion des fps
    Contient la boucle infinie pour faire tourner pygame
    """
    fenetre = pygame.display.set_mode((ECRAN_X, ECRAN_Y))
    musique = pygame.mixer.Sound('son/musique.ogg')
    musique.set_volume(0.1)
    musique.play(-1)
    liste_score = []
    jeu = Jeu(liste_score, fenetre)
    score = Score(jeu)
    score.lire_fichier('meilleur_score.txt')
    lancement_jeu(jeu, fenetre, score)


main()
