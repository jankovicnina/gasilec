import pygame, os, random
import networkx as nx

class Drevo:
    def __init__(self, x, y, screen):
        self.x = x
        self.y = y
        # crna barva je primarna
        self.barva = (0, 0, 0)
        self.sosedje = []
        self.image = None
        self.screen = screen

    def nalozi_sliko(self, ime_slike):
        path = os.path.join("Slike_in_fonti", ime_slike)
        self.image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.image, (40, 80))

    def narisi(self):
        if self.barva == (0, 0, 0):
            self.nalozi_sliko("negorece.png")
        # drevo je rdece
        elif self.barva == (255, 0, 0):
            self.nalozi_sliko("gorece.png")
        # drevo je zeleno
        else:
            self.nalozi_sliko("zasciteno.png")

        self.screen.blit(self.image, (self.x, self.y))

        # narise povezave med sosedi
        for neighbor in self.sosedje:
            pygame.draw.line(self.screen, (0, 0, 0), (self.x + 20, self.y + 40), (neighbor.x + 20, neighbor.y + 40), 2)

    # drevo zagori AKA postane rdece
    def zagori(self):
        self.barva = (255, 0, 0)

    # drevo resimo AKA postane zeleno
    def resi(self):
        if self.barva == (0, 0, 0):
            self.barva = (0, 255, 0)

    # zazna samo click na negorece (in nezasciteno) drevo
    def is_clicked(self, pos):
        if self.barva == (0, 0, 0):
            # topleft zagotovi, da lahko pritsnes katerikoli del drevesa
            tree_rect = self.image.get_rect(topleft=(self.x, self.y))
            return tree_rect.collidepoint(pos)
        else:
            return False
        


class Gozd():
    def __init__(self, st_dreves):
        self.sirina_zaslona, self.visina_zaslona = pygame.display.get_surface().get_size()
        self.st_dreves = st_dreves
        self.gozd = []
        self.goreca = []
        self.resena = []

    # generiranje nakljucnega grafa z RBA metodo
    def generiraj_gozd(self, st_dreves):
        ba = nx.barabasi_albert_graph(st_dreves, 1)
        min_razdalja = 10

        # vsakemi drevesu izbere random x in y koordinato
        for _ in range(st_dreves):
            # z -40 in -80 zagotovim, da se cela drevesa vidijo na ekranu (ker so velika 40x80)
            x = random.randint(0, self.sirina_zaslona - 40)
            y = random.randint(0, self.visina_zaslona - 80)

            # preveri, da se nobena drevesa ne prekrivajo (razdalja med njimi mora biti vsaj 10); ce pa se, jim pa doloci nove koordinate
            while any(((x - tree.x)**2 + (y - tree.y)**2)**0.5 < min_razdalja for tree in self.gozd):
                x = random.randint(0, self.sirina_zaslona - 40)
                y = random.randint(0, self.visina_zaslona - 80)

            drevo = Drevo(x, y)
            self.gozd.append(drevo)

        # shrani vse sosede
        for i, drevo in enumerate(self.gozd):
            sosedje_ba = list(ba.neighbors(i))
            drevo.sosedje = [self.gozd[sosed] for sosed in sosedje_ba]

        # nakljucno drevo zagori
        random_drevo = random.choice(self.gozd)
        random_drevo.barva = (255, 0, 0)

        return self.gozd


    def dobi_goreca_drevesa(self, gozd):
        for drevo in gozd:
            if drevo == (255, 0, 0):
                self.goreca.append(drevo)
        return self.goreca
    
    def naslednja_poteza(self):
        goreca_drevesa = self.dobi_goreca_drevesa(self.gozd)
        for gorece in goreca_drevesa:
            for sosed in gorece.sosedje:
                if sosed.barva == (0, 0, 0):
                    sosed.zagori()