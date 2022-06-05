import time
import copy
import pygame
import sys
import math
import statistics

ADANCIME_MAX = 0
nr_mutari = 0


class Joc:
    """
    Clasa care defineste jocul. Se va schimba de la un joc la altul.
    """

    JMIN = None
    JMAX = None
    GOL = "x"
    CAPTURI = 0
    lista_adiacenta = {}
    coordonate_noduri = []

    def __init__(self, tabla=None):

        self.buton = None

        if tabla:
            # tabla s-a modificat
            self.matr = tabla
        else:
            # inceputul jocului
            self.matr = [["@" for x in range(5)] for y in range(3)]  # @ = simbolul pentru caine
            self.matr[2][2] = "J"  # J = simbolul pentru jaguar

            tabla_2 = [[Joc.GOL for x in range(5)] for y in range(4)]

            tabla_2[2][0] = " "
            tabla_2[2][4] = " "
            tabla_2[3][1] = " "
            tabla_2[3][3] = " "

            self.matr = self.matr + tabla_2
            Joc.initializeaza()

    @classmethod
    def initializeaza(cls):
        """
        Initializaeaza lista coordonate_noduri(coordonatele tuturor nodurilor de pe tabla) si
        dictionarul lista_adiacenta, unde key = coordonatele unui nod si value = lista cu coordonatele
        tuturor nodurilor in care se poate ajunge.
        :return: nimic
        """

        # partea patratica a tablei
        cls.coordonate_noduri = [(i, j) for i in [0, 1, 2, 3, 4] for j in [0, 1, 2, 3, 4]]

        # nod a = (x,y), nod b = (z,t)
        # daca x,y sunt pare iar z,t impare sau invers, este posibila deplasarea pe diagonala
        mutari = [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        for i in range(5):
            for j in range(5):
                aux = []
                # daca au aceeasi paritate
                if i % 2 == j % 2:
                    for el in mutari:
                        x = i + el[0]
                        y = j + el[1]

                        if (x, y) in cls.coordonate_noduri:
                            aux.append((x, y))
                else:
                    for el in mutari[:4]:
                        x = i + el[0]
                        y = j + el[1]

                        if (x, y) in cls.coordonate_noduri:
                            aux.append((x, y))

                cls.lista_adiacenta[(i, j)] = aux

        # adaug partea triunghiulara
        cls.coordonate_noduri += [(5, 1), (5, 2), (5, 3), (6, 0), (6, 2), (6, 4)]
        cls.lista_adiacenta[(4, 2)] += [(5, 1), (5, 2), (5, 3)]
        cls.lista_adiacenta[(5, 1)] = [(4, 2), (5, 2), (6, 0)]
        cls.lista_adiacenta[(5, 2)] = [(4, 2), (5, 1), (5, 3), (6, 2)]
        cls.lista_adiacenta[(5, 3)] = [(4, 2), (5, 2), (6, 4)]
        cls.lista_adiacenta[(6, 0)] = [(5, 1), (6, 2)]
        cls.lista_adiacenta[(6, 2)] = [(6, 0), (6, 4), (5, 2)]
        cls.lista_adiacenta[(6, 4)] = [(5, 3), (6, 2)]

    @classmethod
    def jucator_opus(cls, jucator):
        if jucator == cls.JMIN:
            return cls.JMAX
        else:
            return cls.JMIN

    def coordonate_jaguar(self):
        """
        :return: Linia si coloana pe care se afla jaguarul
        """
        for i in range(len(self.matr)):
            for j in range(len(self.matr[i])):
                if (i, j) in Joc.coordonate_noduri:
                    if self.matr[i][j] == "J":
                        return i, j

    def locuri_libere_tabla(self):
        """
        :return: Lista cu coordonatele tuturor locurilor libere de pe tabla de joc din starea curenta.
        """

        l_locuri = []
        for i, j in Joc.coordonate_noduri:
            if self.matr[i][j] == Joc.GOL:
                l_locuri.append([j * Graph.scalare + Graph.translatie, i * Graph.scalare + Graph.translatie])
        return l_locuri

    def pozitii_caini_tabla(self):
        """
        :return: Lista cu coordonatele locatiilor tuturor cainilor de pe tabla curenta de joc.
        """

        l_caini = []
        for i, j in Joc.coordonate_noduri:
            if self.matr[i][j] == "@":
                l_caini.append([j * Graph.scalare + Graph.translatie, i * Graph.scalare + Graph.translatie])
        return l_caini

    def pozitie_jaguar_tabla(self):
        """
        :return: Lista cu pozitia pe tabla de joc a jaguarului, coordonatele din lista sunt de forma celor desenate.
        """

        l_jaguar = []
        for i, j in Joc.coordonate_noduri:
            if self.matr[i][j] == "J":
                l_jaguar.append([j * Graph.scalare + Graph.translatie, i * Graph.scalare + Graph.translatie])
        return l_jaguar

    def pozitii_caini_vecini(self, i, j):
        """

        :param i: Linia la care se afla piesa careia ii caut vecinii
        :param j: Coloana la care se afla piesa careia ii caut vecinii
        :return: Lista cu pozitiile tuturor cainilor vecini piesei cu locatia (i,j)
        """

        l_vecini = []
        for x, y in Joc.lista_adiacenta[(i, j)]:
            if self.matr[x][y] == "@":
                l_vecini.append((x, y))
        return l_vecini

    def pozitii_sarituri_posibile_tabla(self):
        """
        :return: Lista cu toate pozitiile de pe tabla de joc pe care jaguarul poate ajunge in urma unei singure sarituri
        """

        x_j, y_j = self.coordonate_jaguar()
        pozitii_caini_vecini = self.pozitii_caini_vecini(x_j, y_j)

        l_sarituri = []
        for x_c, y_c in pozitii_caini_vecini:
            if self.matr[x_c][y_c] == "@":
                x = x_j - x_c
                y = y_j - y_c

                x_s = x_j - 2 * x
                y_s = y_j - 2 * y

                if (x_s, y_s) in Joc.coordonate_noduri and self.matr[x_s][y_s] == Joc.GOL:
                    l_sarituri.append([y_s * Graph.scalare + Graph.translatie, x_s * Graph.scalare + Graph.translatie])

        return l_sarituri

    def deseneaza_ecran_joc(self):
        pieseAlbe = self.pozitii_caini_tabla()
        pieseNegre = self.pozitie_jaguar_tabla()

        ecran.fill((255, 255, 255))
        for nod in coordonateNoduri:
            pygame.draw.circle(surface=ecran, color=(0, 0, 0), center=nod, radius=Graph.razaPct,
                               width=0)  # width=0 face un cerc plin

        for muchie in Graph.muchii:
            p0 = coordonateNoduri[muchie[0]]
            p1 = coordonateNoduri[muchie[1]]
            pygame.draw.line(surface=ecran, color=(0, 0, 0), start_pos=p0, end_pos=p1, width=5)
        for nod in pieseAlbe:
            ecran.blit(piesaAlba, (nod[0] - Graph.razaPiesa, nod[1] - Graph.razaPiesa))
        for nod in pieseNegre:
            ecran.blit(piesaNeagra, (nod[0] - Graph.razaPiesa, nod[1] - Graph.razaPiesa))
        if nodPiesaSelectata:
            ecran.blit(piesaSelectata, (nodPiesaSelectata[0] - Graph.razaPiesa, nodPiesaSelectata[1] - Graph.razaPiesa))

        self.buton = Buton(display=ecran, top=450, left=15, w=30, h=30, text="Gata", culoareFundal=(105, 100, 105))
        self.buton.deseneaza()

        pygame.display.update()

    def pozitii_locuri_libere_vecine(self, x, y):
        """
        Returneaza toate locatiile vecine punctului (x,y) care sunt libere.
        :param a: Linia pe care se afla piesa
        :param b: Coloana pe care se afla piesa
        :return: Lista cu toate locatiile libere vecine punctului cu coordonatele (x,y)
        """

        l_vecini = []
        for i, j in Joc.lista_adiacenta[(x, y)]:
            if self.matr[i][j] == Joc.GOL:
                l_vecini.append((i, j))
        return l_vecini

    def salturi_posibile(self, a, b, matrice):
        """
        Returneaza o lista cu toate sariturile posibile din punctul de coordonate (a,b), fara sa efectueze saltul.
        :param a: Linia pe care se afla jaguarul.
        :param b: Coloana pe care se afla jaguarul.
        :param matrice: Matricea dupa efectuarea saltului (pentru apelul recursiv).
        :return: Lista cu toate sariturile posibile din locatia jaguarului
        """
        '''
           
            OBS:
            in urma acestei secvente de cod, rezultatul ramane intr-un format mai "greu/ciudat":
            pe fiecare pozitie para se afla o miscare M, iar pe pozitia impara imediat urmatoare se afla o lista
            care contine toate miscarile noi posibile din M (acest lucru se repeta si pentru listele mai mici din interior)
            [(2, 0), [(4, 0), [(2, 2), [(2, 4), []]], (4, 2), []], (2, 4), [], (4, 0), [(2, 0), [(2, 2), [(2, 4), []]]]]
              => [[(2, 0), (4, 0), (2, 2), (2, 4)], [(2, 0), (4, 2)], [(2, 4)], [(4, 0), (2, 0), (2, 2), (2, 4)]]
        '''
        l_sarituri = []
        for x_c, y_c in self.pozitii_caini_vecini(a, b):
            if matrice[x_c][y_c] == "@":
                x = a - x_c
                y = b - y_c

                salt_x = a - 2 * x
                salt_y = b - 2 * y

                # locatia in care va ajunge jaguarul dupa saritura trebuie sa:
                # i) sa aiba coordonate care se afla pe tabla
                # ii) sa fie goala
                if (salt_x, salt_y) in Joc.coordonate_noduri and (self.matr[salt_x][salt_y] == Joc.GOL):
                    matrice[x_c][y_c] = Joc.GOL

                    # se pot manca dupa si alti caini
                    l_sarituri_rec = self.salturi_posibile(salt_x, salt_y, matrice)
                    matrice[x_c][y_c] = "@"  # trebuie pus la loc pe tabla pentru ca nu este "mancat" efectiv

                    l_sarituri.append((salt_x, salt_y))
                    l_sarituri.append(l_sarituri_rec)

        return l_sarituri

    @staticmethod
    def modifica_lista(l_sarituri, l_secventa, l_noua):
        """
        Modifica formatul listei date ca parametru astfel incat fiecare succesiune de salturi sa fie o lista
        :param l_sarituri: Lista originala cu toate salturile posibile
        :param secventa: Lista care contine salturile consecutive dintr-o mutare
        :param l_noua: Lista modificata
        :return:
        """

        if not l_sarituri:
            l_noua.append(l_secventa.copy())

        for i in range(0, len(l_sarituri), 2):
            l_secventa.append(l_sarituri[i])
            Joc.modifica_lista(l_sarituri[i + 1], l_secventa, l_noua)
            l_secventa.pop(-1)

        return l_noua

    def mutari(self, jucator):
        """
        :param jucator: Numele jucatorului curent
        :return: Lista cu toate mutarile pe care le poate face jucatorul dat
        """

        l_mutari = []
        if jucator == "caini":
            for i, j in Joc.coordonate_noduri:
                # daca pe o anumita pozitie am un caine, acesta poate fi mutat in oricare loc liber vecin
                if self.matr[i][j] == "@":
                    for x, y in self.pozitii_locuri_libere_vecine(i, j):
                        matrice_tabla_noua = copy.deepcopy(self.matr)
                        matrice_tabla_noua[x][y] = "@"
                        matrice_tabla_noua[i][j] = Joc.GOL
                        joc_nou = Joc(matrice_tabla_noua)
                        l_mutari.append(joc_nou)

        else:
            i, j = self.coordonate_jaguar()
            # cazurile in care doar mut jaguarul pe tabla, fara salturi
            for x, y in self.pozitii_locuri_libere_vecine(i, j):
                matrice_tabla_noua = copy.deepcopy(self.matr)
                matrice_tabla_noua[x][y] = "J"
                matrice_tabla_noua[i][j] = Joc.GOL
                joc_nou = Joc(matrice_tabla_noua)
                l_mutari.append(joc_nou)

            for sarituri in self.modifica_lista(self.salturi_posibile(i, j, self.matr), [], []):
                matrice_tabla_noua = copy.deepcopy(self.matr)
                x_j, y_j = i, j

                # pentru fiecare pozitie in care poate ajunge jaguarul in aceasta secventa de sarituri
                for x, y in sarituri:
                    matrice_tabla_noua[(x_j + x) // 2][(y_j + y) // 2] = Joc.GOL
                    x_j = x
                    y_j = y

                matrice_tabla_noua[i][j] = Joc.GOL
                matrice_tabla_noua[x_j][y_j] = "J"

                joc_nou = Joc(matrice_tabla_noua)
                if joc_nou not in l_mutari and joc_nou != self:
                    l_mutari.append(joc_nou)

        return l_mutari

    def saritura_posibila(self, a, b):
        """
        Functia verifica daca se poate efectua un salt din punctul a in punctul b.
        :param a: Coordonatele unui punct de pe tabla
        :param b: Coordonatele unui alt punct de pe tabla
        :return: True daca se poate, False daca nu
        """
        x_a, y_a = a[0], a[1]
        x_b, y_b = b[0], b[1]

        if self.matr[(x_a + x_b) // 2][(y_a + y_b) // 2] == "@" and self.matr[x_b][y_b] == Joc.GOL and \
                (x_b, y_b) in Joc.coordonate_noduri:
            return True
        else:
            return False

    def final(self):
        """
        Jocul a ajuns intr-o stare finala daca au fost capturati minim 5 caini (castiga jaguarul) sau daca
        jaguarul este inconjurat de caini si nu poate sa "manance" niciunul (castiga cainii)
        :return: Numele castigatorului sau False daca nu este stare finala.
        """

        if self.CAPTURI >= 5:
            nod = self.coordonate_jaguar()
            return "jaguar"

        x_j, y_j = self.coordonate_jaguar()
        if self.pozitii_locuri_libere_vecine(x_j, y_j) == [] and self.salturi_posibile(x_j, y_j, self.matr) == []:
            return "caini"

        return False

    def estimeaza_scor(self, adancime):
        """
        Returneaza estimarea scorului starii curente.
        :param adancime: Reprezinta adancimea la care se afla starea, cu cat e mai aproape de final, cu atat e mai bun scorul
        :return: scorul estimat

        Au fost folosite doua moduri de estimare a scorului, utilizatorul alegandu-si pe care o va folosi.

        Estimarea 1: Scorul este dat de numarul de locuri in care se poate deplasa jaguarul din starea curenta.
        Jaguarul pierde daca este inconjurat de caini, deci un scor favorabil pentru el ar fi sa aiba cat mai multe mutari posibile.
        Cu cat jaguarul are mai putine miscari posibile pe tabla, cu atat scorul este mai bun pentru jucatorul cu cainii.

        Estimarea 2: Scorul este dat de numarul de caini ramasi pe tabla de joc.
        Cainii pierd daca jaguarul a capturat minim 5, deci un scor favorabil pentru ei ar fi sa fie cat mai multi pe tabla.
        Scorul este mai bun pentru jaguar daca numarul cainilor ramasi este mic, deoarece este mai aproape de castig.

        """
        if ESTIMARE == 1:
            castigator = self.final()
            if castigator == Joc.JMAX:
                return 99 + adancime  # un scor foarte mare, in loc de +infinit
            elif castigator == Joc.JMIN:
                return -99 - adancime
            else:
                x_j, y_j = self.coordonate_jaguar()
                vecini = self.pozitii_locuri_libere_vecine(x_j, y_j)
                sarituri = self.salturi_posibile(x_j, y_j, self.matr)

                if Joc.JMAX == "jaguar":
                    return len(vecini) + len(sarituri)
                else:
                    return - (len(vecini) + len(sarituri))
        else:
            castigator = self.final()
            if castigator == Joc.JMAX:
                return 999 + adancime
            elif castigator == Joc.JMIN:
                return -999 - adancime
            else:
                if Joc.JMAX == "caini":
                    return 14 - self.CAPTURI
                else:
                    return -14 + self.CAPTURI

    def __eq__(self, other):
        for i, j in Joc.coordonate_noduri:
            if self.matr[i][j] != other.matr[i][j]:
                return False
        return True

    def __str__(self):
        sir = ''
        for i in self.matr:
            sir += ' '.join(i)
            sir += '\n'
        return sir


class Stare:
    """
    Clasa folosita de algoritmii minimax si alpha-beta
    Are ca proprietate tabla de joc
    Functioneaza cu conditia ca in cadrul clasei Joc sa fie definiti JMIN si JMAX (cei doi jucatori posibili)
    De asemenea cere ca in clasa Joc sa fie definita si o metoda numita mutari() care ofera lista cu configuratiile posibile in urma mutarii unui jucator
    """

    def __init__(self, tabla_joc, j_curent, adancime, scor=None):
        self.tabla_joc = tabla_joc
        self.j_curent = j_curent
        self.adancime = adancime
        self.scor = scor
        self.mutari_posibile = []
        self.stare_aleasa = None

    def mutari(self):
        l_mutari = self.tabla_joc.mutari(self.j_curent)
        j_opus = Joc.jucator_opus(self.j_curent)
        l_stari_mutari = [Stare(mutare, j_opus, self.adancime - 1) for mutare in l_mutari]
        return l_stari_mutari

    def __str__(self):
        sir = str(self.tabla_joc) + "(Jucator curent:" + self.j_curent + ")\n"
        return sir

    def __repr__(self):
        sir = str(self.tabla_joc) + "(Jucator curent:" + self.j_curent + ")\n"
        return sir

    def __lt__(self, other):
        return self.tabla_joc.estimeaza_scor(self.adancime) < other.tabla_joc.estimeaza_scor(self.adancime)


""" Algoritmul MinMax """


def min_max(stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    # calculez toate mutarile posibile din starea curenta
    stare.mutari_posibile = stare.mutari()

    global nr_mutari
    nr_mutari += len(stare.mutari_posibile)

    # aplic algoritmul minimax pe toate mutarile posibile (calculand astfel subarborii lor)
    mutari_scor = [min_max(mutare) for mutare in stare.mutari_posibile]

    if stare.j_curent == Joc.JMAX:
        stare.stare_aleasa = max(mutari_scor, key=lambda x: x.scor)
    else:
        stare.stare_aleasa = min(mutari_scor, key=lambda x: x.scor)
    stare.scor = stare.stare_aleasa.scor
    return stare


""" Algoritmul Alpha-Beta"""


def alpha_beta(alpha, beta, stare):
    if stare.adancime == 0 or stare.tabla_joc.final():
        stare.scor = stare.tabla_joc.estimeaza_scor(stare.adancime)
        return stare

    if alpha > beta:
        return stare  # interval invalid

    stare.mutari_posibile = stare.mutari()

    # sortarea se face crescator in functie de estimarea scorului
    sorted(stare.mutari_posibile)

    # cate noduri au fost generate
    global nr_mutari
    nr_mutari += len(stare.mutari_posibile)

    if stare.j_curent == Joc.JMAX:
        scor_curent = float("-inf")

        for mutare in stare.mutari_posibile:
            # calculeaza scorul
            stare_noua = alpha_beta(alpha, beta, mutare)

            if scor_curent < stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor
            if alpha < stare_noua.scor:
                alpha = stare_noua.scor
                if alpha >= beta:
                    break

    elif stare.j_curent == Joc.JMIN:
        scor_curent = float("inf")

        for mutare in stare.mutari_posibile:

            stare_noua = alpha_beta(alpha, beta, mutare)

            if scor_curent > stare_noua.scor:
                stare.stare_aleasa = stare_noua
                scor_curent = stare_noua.scor

            if beta > stare_noua.scor:
                beta = stare_noua.scor
                if alpha >= beta:
                    break
    stare.scor = stare.stare_aleasa.scor

    return stare


def afis_daca_final(stare_curenta):
    final = stare_curenta.tabla_joc.final()
    if final:
        print("Castigator: " + final)
        return True

    return False


class Buton:
    def __init__(self, display=None, left=0, top=0, w=0, h=0, culoareFundal=(105, 100, 105),
                 culoareFundalSel=(200, 130, 200), text="", font="dejavuserif", fontDimensiune=16,
                 culoareText=(255, 255, 255),
                 valoare=""):
        self.display = display
        self.culoareFundal = culoareFundal
        self.culoareFundalSel = culoareFundalSel
        self.text = text
        self.font = font
        self.w = w
        self.h = h
        self.selectat = False
        self.fontDimensiune = fontDimensiune
        self.culoareText = culoareText
        fontObj = pygame.font.SysFont(self.font, self.fontDimensiune)
        self.textRandat = fontObj.render(self.text, True, self.culoareText)
        self.dreptunghi = pygame.Rect(left, top, w, h)
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)
        self.valoare = valoare

    def selecteaza(self, sel):
        self.selectat = sel
        self.deseneaza()

    def selecteazaDupacoord(self, coord):
        if self.dreptunghi.collidepoint(coord):
            self.selecteaza(True)
            return True
        return False

    def updateDreptunghi(self):
        self.dreptunghi.left = self.left
        self.dreptunghi.top = self.top
        self.dreptunghiText = self.textRandat.get_rect(center=self.dreptunghi.center)

    def deseneaza(self):
        culoareF = self.culoareFundalSel if self.selectat else self.culoareFundal
        pygame.draw.rect(self.display, culoareF, self.dreptunghi)
        self.display.blit(self.textRandat, self.dreptunghiText)


class GrupButoane:
    def __init__(self, listaButoane=[], indiceSelectat=0, spatiuButoane=10, left=0, top=0):
        self.listaButoane = listaButoane
        self.indiceSelectat = indiceSelectat
        self.listaButoane[self.indiceSelectat].selectat = True
        self.top = top
        self.left = left
        leftCurent = self.left
        for b in self.listaButoane:
            b.top = self.top
            b.left = leftCurent
            b.updateDreptunghi()
            leftCurent += spatiuButoane + b.w

    def selecteazaDupacoord(self, coord):
        for ib, b in enumerate(self.listaButoane):
            if b.selecteazaDupacoord(coord):
                self.listaButoane[self.indiceSelectat].selecteaza(False)
                self.indiceSelectat = ib
                return True
        return False

    def deseneaza(self):
        for b in self.listaButoane:
            b.deseneaza()

    def getValoare(self):
        return self.listaButoane[self.indiceSelectat].valoare


############# ecran initial ########################
def deseneaza_alegeri(display, tabla_curenta):
    btn_alg = GrupButoane(
        top=30,
        left=30,
        listaButoane=[
            Buton(display=display, w=80, h=30, text="Minimax", valoare="minimax"),
            Buton(display=display, w=80, h=30, text="Alphabeta", valoare="alphabeta"),
        ],
        indiceSelectat=1,
    )
    btn_juc = GrupButoane(
        top=100,
        left=30,
        listaButoane=[
            Buton(display=display, w=80, h=30, text="Jaguar", valoare="jaguar"),
            Buton(display=display, w=80, h=30, text="Caini", valoare="caini"),
        ],
        indiceSelectat=0,
    )
    btn_dificultate = GrupButoane(
        top=170,
        left=30,
        listaButoane=[
            Buton(display=display, w=80, h=30, text="Usor", valoare="usor"),
            Buton(display=display, w=80, h=30, text="Mediu", valoare="mediu"),
            Buton(display=display, w=80, h=30, text="Greu", valoare="greu"),
        ],
        indiceSelectat=0,
    )
    btn_estimare = GrupButoane(
        top=240,
        left=30,
        listaButoane=[
            Buton(display=display, w=80, h=30, text="Estimare 1", valoare="1"),
            Buton(display=display, w=80, h=30, text="Estimare 2", valoare="2"),
        ],
        indiceSelectat=0,
    )
    ok = Buton(display=display, top=310, left=30, w=40, h=30, text="Ok", culoareFundal=(155, 0, 55), )
    btn_alg.deseneaza()
    btn_juc.deseneaza()
    btn_dificultate.deseneaza()
    btn_estimare.deseneaza()
    ok.deseneaza()
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if not btn_alg.selecteazaDupacoord(pos):
                    if not btn_juc.selecteazaDupacoord(pos):
                        if not btn_dificultate.selecteazaDupacoord(pos):
                            if not btn_estimare.selecteazaDupacoord(pos):
                                if ok.selecteazaDupacoord(pos):
                                    display.fill((0, 0, 0))  # stergere ecran
                                    tabla_curenta.deseneaza_ecran_joc()
                                    return btn_juc.getValoare(), btn_alg.getValoare(), btn_dificultate.getValoare(), btn_estimare.getValoare()
        pygame.display.update()


# metoda folosita pt a obtine indexii nodurilor intre care exista muchii din lista noduri
def obtine_muchii(noduri):
    lista = []
    for k in Joc.coordonate_noduri:
        for item in Joc.lista_adiacenta[k]:
            lista.append((noduri.index((k[1], k[0])), noduri.index((item[1], item[0]))))
    return lista


def distEuclid(p0, p1):
    (x0, y0) = p0
    (x1, y1) = p1
    return math.sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)


class Graph:
    # coordonatele nodurilor ()
    noduri = []
    muchii = []

    scalare = 100
    translatie = 20
    razaPct = 10
    razaPiesa = 20

    @classmethod
    def initializeaza(cls):
        cls.noduri = [(y, x) for x, y in Joc.coordonate_noduri]
        muchii = []
        for nod in Joc.coordonate_noduri:
            for nod_adiacent in Joc.lista_adiacenta[nod]:
                muchii.append(
                    (cls.noduri.index((nod[1], nod[0])), cls.noduri.index((nod_adiacent[1], nod_adiacent[0]))))
        cls.muchii = muchii


def main():
    global ecran, piesaAlba, piesaNeagra, piesaSelectata, coordonateNoduri, nodPiesaSelectata, ESTIMARE, nr_mutari

    tabla_curenta = Joc()
    Graph.initializeaza()

    pygame.init()
    pygame.display.set_caption("Cordun Diana Alexandra | Adugo")
    ecran = pygame.display.set_mode(size=(440, 640))

    diametruPiesa = 2 * Graph.razaPiesa
    piesaAlba = pygame.image.load('piesa-alba.png')
    piesaAlba = pygame.transform.scale(piesaAlba, (diametruPiesa, diametruPiesa))
    piesaNeagra = pygame.image.load('piesa-neagra.png')
    piesaNeagra = pygame.transform.scale(piesaNeagra, (diametruPiesa, diametruPiesa))
    piesaSelectata = pygame.image.load('piesa-rosie.png')
    piesaSelectata = pygame.transform.scale(piesaSelectata, (diametruPiesa, diametruPiesa))

    coordonateNoduri = [[Graph.translatie + Graph.scalare * x for x in nod] for nod in Graph.noduri]
    nodPiesaSelectata = False

    Joc.JMIN, tip_algoritm, dificultate, estimare = deseneaza_alegeri(ecran, tabla_curenta)
    if Joc.JMIN == "jaguar":
        print("Dvs. jucati cu Jaguarul.")
    else:
        print("Dvs. jucati cu Cainii.")
    print("Algoritmul folosit: " + tip_algoritm)

    if dificultate == "usor":
        ADANCIME_MAX = 2
    elif dificultate == "mediu":
        ADANCIME_MAX = 3
    else:
        ADANCIME_MAX = 4

    if estimare == "1":
        ESTIMARE = 1
    else:
        ESTIMARE = 2

    Joc.JMAX = "caini" if Joc.JMIN == "jaguar" else "jaguar"

    print("Tabla initiala")
    print(str(tabla_curenta))

    # jaguarul muta primul
    stare_curenta = Stare(tabla_curenta, "jaguar", ADANCIME_MAX)

    tabla_curenta.deseneaza_ecran_joc()

    capturat = False
    nu_a_capturat = False
    mutare_efectuata = False

    t_start = int(round(time.time() * 1000))
    t_inainte = int(round(time.time() * 1000))
    l_info_mutari = []
    l_info_timp = []
    nr_mutari_jucatori = 0

    while True:
        if stare_curenta.j_curent == Joc.JMIN:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    t_final = int(round(time.time() * 1000))
                    print("Timpul final de joc: " + str(t_final - t_start) + " ms.")
                    print("\nNumar total mutari: " + str(nr_mutari_jucatori))
                    print("\nTimp de gandire:")
                    print("\nMinim: " + str(min(l_info_timp)))
                    print("\nMaxim: " + str(max(l_info_timp)))
                    print("\nMediu: " + str(statistics.mean(l_info_timp)))
                    print("\nMediana: " + str(statistics.median(l_info_timp)))
                    print("\nNumarul de noduri generate:")
                    print("\nMinim: " + str(min(l_info_mutari)))
                    print("\nMaxim: " + str(max(l_info_mutari)))
                    print("\nMediu: " + str(statistics.mean(l_info_mutari)))
                    print("\nMediana: " + str(statistics.median(l_info_mutari)))
                    pygame.quit()
                    sys.exit()
                elif ev.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()

                    # daca utilizatorul a apasat pe buton, deci si-a incheiat tura 
                    if stare_curenta.tabla_joc.buton.selecteazaDupacoord(pos) and mutare_efectuata:
                        # s-a realizat o mutare, schimb jucatorul cu cel opus
                        stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)
                        # afisarea starii jocului in urma mutarii utilizatorului
                        print("\nTabla dupa mutarea jucatorului")
                        print(str(stare_curenta))

                        t_final_tura = int(round(time.time() * 1000))
                        print("Timp de gandire: " + str(t_final_tura - t_inainte) + " ms.\n")

                        nodPiesaSelectata = False

                        capturat = False
                        nu_a_capturat = False
                        mutare_efectuata = False

                        nr_mutari_jucatori += 1

                        stare_curenta.tabla_joc.deseneaza_ecran_joc()

                    else:
                        for nod in coordonateNoduri:
                            if distEuclid(pos, nod) <= Graph.razaPiesa:

                                # utilizatorul a ales cainii
                                if Joc.JMIN == "caini":
                                    # a fost efectuat click pe un caine
                                    if nod in stare_curenta.tabla_joc.pozitii_caini_tabla():
                                        # daca cainele era deja selectat il deselectez, daca nu era selectat il selectez
                                        if nodPiesaSelectata == nod:
                                            nodPiesaSelectata = False
                                        else:
                                            nodPiesaSelectata = nod

                                    # cainele este selectat, trebuie efectuata o mutare
                                    elif nodPiesaSelectata:
                                        if nod in stare_curenta.tabla_joc.locuri_libere_tabla():
                                            y_caine, x_caine = nodPiesaSelectata
                                            y_caine = (y_caine - 20) // 100
                                            x_caine = (x_caine - 20) // 100

                                            y_nod, x_nod = nod
                                            y_nod = (y_nod - 20) // 100
                                            x_nod = (x_nod - 20) // 100

                                            # mutam cainele in locul in care a apasat utilizatorul (daca se poate)
                                            if (x_nod, y_nod) in Joc.lista_adiacenta[(x_caine, y_caine)]:
                                                stare_curenta.tabla_joc.matr[x_caine][y_caine] = Joc.GOL
                                                stare_curenta.tabla_joc.matr[x_nod][y_nod] = "@"
                                                nodPiesaSelectata = False
                                                mutare_efectuata = True

                                # utilizatorul a ales jaguarul
                                else:

                                    if nod in stare_curenta.tabla_joc.pozitie_jaguar_tabla():
                                        # daca era deja selectat il deselectez, daca nu era selectat il selectez
                                        if nodPiesaSelectata == nod:
                                            nodPiesaSelectata = False
                                        else:
                                            nodPiesaSelectata = nod

                                    # jaguarul este selectat, trebuie efectuata o mutare
                                    elif nodPiesaSelectata:
                                        # daca locul nou in care a apasat utilozatorul este liber
                                        if nod in stare_curenta.tabla_joc.locuri_libere_tabla():
                                            y_jaguar, x_jaguar = nodPiesaSelectata
                                            y_jaguar = (y_jaguar - 20) // 100
                                            x_jaguar = (x_jaguar - 20) // 100

                                            y_nod, x_nod = nod
                                            y_nod = (y_nod - 20) // 100
                                            x_nod = (x_nod - 20) // 100

                                            # daca jaguarul poate sa se mute in locul indicat si daca este prima lui mutare 
                                            if (x_nod, y_nod) in Joc.lista_adiacenta[(x_jaguar,
                                                                                      y_jaguar)] and capturat == False and nu_a_capturat == False:
                                                stare_curenta.tabla_joc.matr[x_jaguar][y_jaguar] = Joc.GOL
                                                stare_curenta.tabla_joc.matr[x_nod][y_nod] = "J"
                                                nodPiesaSelectata = False
                                                nu_a_capturat = True
                                                mutare_efectuata = True

                                            # daca jaguarul poate sa sara peste un caine si pana acum doar a mancat
                                            elif nod in stare_curenta.tabla_joc.pozitii_sarituri_posibile_tabla() and nu_a_capturat == False:
                                                stare_curenta.tabla_joc.matr[x_jaguar][y_jaguar] = Joc.GOL
                                                stare_curenta.tabla_joc.matr[x_nod][y_nod] = "J"
                                                stare_curenta.tabla_joc.matr[(x_jaguar + x_nod) // 2][
                                                    (y_jaguar + y_nod) // 2] = Joc.GOL
                                                nodPiesaSelectata = False
                                                capturat = True
                                                mutare_efectuata = True
                                                Joc.CAPTURI += 1

                                stare_curenta.tabla_joc.deseneaza_ecran_joc()

                                # daca jocul s-a terminat
                                if afis_daca_final(stare_curenta):
                                    t_final = int(round(time.time() * 1000))
                                    print("Timpul final de joc: " + str(t_final - t_start) + " ms.")
                                    print("\nNumar total mutari: " + str(nr_mutari_jucatori))
                                    print("\nTimp de gandire:")
                                    print("\nMinim: " + str(min(l_info_timp)))
                                    print("\nMaxim: " + str(max(l_info_timp)))
                                    print("\nMediu: " + str(statistics.mean(l_info_timp)))
                                    print("\nMediana: " + str(statistics.median(l_info_timp)))
                                    print("\nNumarul de noduri generate:")
                                    print("\nMinim: " + str(min(l_info_mutari)))
                                    print("\nMaxim: " + str(max(l_info_mutari)))
                                    print("\nMediu: " + str(statistics.mean(l_info_mutari)))
                                    print("\nMediana: " + str(statistics.median(l_info_mutari)))

                                    break

        else:  # jucatorul e JMAX (calculatorul)
            # Mutare calculator

            # preiau timpul in milisecunde de dinainte de mutare
            t_inainte = int(round(time.time() * 1000))
            if tip_algoritm == "minimax":
                stare_actualizata = min_max(stare_curenta)
            else:  # tip_algoritm=="alphabeta"
                stare_actualizata = alpha_beta(-500, 500, stare_curenta)
            stare_curenta.tabla_joc = stare_actualizata.stare_aleasa.tabla_joc

            print("Tabla dupa mutarea calculatorului\n" + str(stare_curenta))

            # preiau timpul in milisecunde de dupa mutare
            t_dupa = int(round(time.time() * 1000))
            print("Calculatorul a 'gandit' timp de " + str(t_dupa - t_inainte) + " milisecunde.")
            l_info_timp.append(t_dupa - t_inainte)

            print("Calculatorul a generat " + str(nr_mutari) + " noduri.")
            l_info_mutari.append(nr_mutari)
            nr_mutari = 0

            stare_curenta.tabla_joc.deseneaza_ecran_joc()
            if afis_daca_final(stare_curenta):
                t_final = int(round(time.time() * 1000))
                print("\nNumar total mutari: " + str(nr_mutari_jucatori))
                print("\nTimp de gandire:")
                print("\nMinim: " + str(min(l_info_timp)))
                print("\nMaxim: " + str(max(l_info_timp)))
                print("\nMediu: " + str(statistics.mean(l_info_timp)))
                print("\nMediana: " + str(statistics.median(l_info_timp)))
                print("\nNumarul de noduri generate:")
                print("\nMinim: " + str(min(l_info_mutari)))
                print("\nMaxim: " + str(max(l_info_mutari)))
                print("\nMediu: " + str(statistics.mean(l_info_mutari)))
                print("\nMediana: " + str(statistics.median(l_info_mutari)))

                break

            # s-a realizat o mutare, schimb jucatorul cu cel opus
            stare_curenta.j_curent = Joc.jucator_opus(stare_curenta.j_curent)

            nr_mutari_jucatori += 1

            t_inainte = int(round(time.time() * 1000))


if __name__ == "__main__":
    main()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
