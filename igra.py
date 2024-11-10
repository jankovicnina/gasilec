import pygame, random, os
import sys
import networkx as nx
from pygame.locals import *
from Razredi.gumbi import Button
from Razredi.Drevesa import Drevo

# Initialize Pygame
pygame.init()

# Set up the window
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
pygame.display.set_caption("Gasilec")

# Colors
BELA = (255, 255, 255)
ZELENA = (0, 255, 0)
RDECA = (255, 0, 0)
CRNA = (0, 0, 0)

def path(name):
    return os.path.join("Slike_in_fonti", name)

#fonti
FONT_PATH = path("Pixeltype.ttf")
font = pygame.font.Font(FONT_PATH, 40)

def dobi_st_dreves():
    running = True
    input_text = ""
    clock = pygame.time.Clock()

    napaka = ""

    while running:
        screen.fill(BELA)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                #ko pritisnes enter se vpisan text converta v integer
                if event.key == pygame.K_RETURN:
                    if input_text:
                        #preveri, ce je vpoisano stevilo med 3 in 20
                        try:
                            st_dreves = int(input_text)
                            if 3 <= st_dreves <= 20:
                                return st_dreves
                            else:
                                napaka = "Input an integer between 3 and 20."
                        except ValueError:
                            napaka = "Input an integer between 3 and 20."
                    else:
                        napaka = "Input an integer between 3 and 20."
                #izbrise zadnjo stevilko
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                    input_text += event.unicode

        screen_width, screen_height = pygame.display.get_surface().get_size()

        #vstavi besedilo na sredino
        text_surface = font.render("Number of trees:", True, CRNA)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 25))
        screen.blit(text_surface, text_rect)

        #narise okencek, kamor lahko vpisem besedilo
        input_box_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 25, 200, 50)
        pygame.draw.rect(screen, CRNA, input_box_rect, 2)
        text_surface = font.render(input_text, True, CRNA)
        screen.blit(text_surface, (input_box_rect.x + 98, input_box_rect.y + 18))

        if napaka:
            napaka_surface = font.render(napaka, True, RDECA)
            napaka_rect = napaka_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
            screen.blit(napaka_surface, napaka_rect)

        pygame.display.flip()
        clock.tick(30)


# generiranje nakljucnega grafa z RBA metodo
def generate_graph(st_dreves):
    ba = nx.barabasi_albert_graph(st_dreves, 1)
    gozd = []
    min_razdalja = 50
    screen_width, screen_height = pygame.display.get_surface().get_size()

    # vsakemi drevesu izbere random x in y koordinato
    for _ in range(st_dreves):
        # z -40 in -80 zagotovim, da se cela drevesa vidijo na ekranu (ker so velika 40x80)
        x = random.randint(0, screen_width - 40)
        y = random.randint(0, screen_height - 80)

        # preveri, da se nobena drevesa ne prekrivajo (razdalja med njimi mora biti vsaj 10); ce pa se, jim pa doloci nove koordinate
        while any(((x - tree.x)**2 + (y - tree.y)**2)**0.5 < min_razdalja for tree in gozd):
            x = random.randint(0, screen_width - 40)
            y = random.randint(0, screen_height - 80)

        #drevo = Drevesa.Drevo(x, y)
        drevo = Drevo(x, y)
        gozd.append(drevo)

    # shrani vse sosede
    for i, drevo in enumerate(gozd):
        sosedje_ba = list(ba.neighbors(i))
        drevo.sosedje = [gozd[sosed] for sosed in sosedje_ba]

    # nakljucno drevo zagori
    random_drevo = random.choice(gozd)
    random_drevo.barva = RDECA

    return gozd


def dobi_goreca_drevesa(gozd):
    goreca_drevesa = []
    for drevo in gozd:
        if drevo.barva == RDECA:
            goreca_drevesa.append(drevo)
    return goreca_drevesa


def naslednja_poteza(gozd):
    goreca_drevesa = dobi_goreca_drevesa(gozd)
    for gorece in goreca_drevesa:
        for sosed in gorece.sosedje:
            if sosed.barva == CRNA:
                sosed.zagori()


# Main game loop
def main():
    number_of_trees = dobi_st_dreves()
    trees = generate_graph(number_of_trees)
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(BELA)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for tree in trees:
                    if tree.is_clicked(pygame.mouse.get_pos()):
                        tree.resi()
                        naslednja_poteza(trees)
            elif event.type == pygame.VIDEORESIZE:
                global WIDTH, HEIGHT
                old_width, old_height = WIDTH, HEIGHT
                WIDTH, HEIGHT = event.w, event.h
                for tree in trees:
                    tree.x = tree.x * WIDTH // old_width
                    tree.y = tree.y * HEIGHT // old_height            

        for tree in trees:
            tree.narisi(screen)

        pygame.display.flip()
        clock.tick(60)

        all_neighbors_are_red_or_green = all(all(neighbor.barva != CRNA for neighbor in tree.sosedje) for tree in trees if tree.barva == RDECA)
        if all_neighbors_are_red_or_green:
            print("Game over! All neighbors of red trees are red or green.")
            saved_trees = sum(tree.barva != RDECA for tree in trees)
            print(f"You saved {saved_trees} trees.")
            running = False  # End the game loop


if __name__ == "__main__":
    main()