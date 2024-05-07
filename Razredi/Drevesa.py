import pygame, os

class Drevo():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # crna barva je primarna
        self.barva = (0, 0, 0)
        self.sosedje = []
        self.image = None

    def nalozi_sliko(self, ime_slike):
        path = os.path.join("Slike_in_fonti", ime_slike)
        self.image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.image, (40, 80))

    def narisi(self, screen):
        if self.barva == (0, 0, 0):
            self.nalozi_sliko("negorece.png")
        # drevo je rdece
        elif self.barva == (255, 0, 0):
            self.nalozi_sliko("gorece.png")
        # drevo je zeleno
        else:
            self.nalozi_sliko("zasciteno.png")

        screen.blit(self.image, (self.x, self.y))

        # narise povezave med sosedi
        for neighbor in self.sosedje:
            pygame.draw.line(screen, (0, 0, 0), (self.x + 20, self.y + 40), (neighbor.x + 20, neighbor.y + 40), 2)

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