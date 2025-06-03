import os, pygame
from Razredi.buttons import Button
from pygame.locals import *

#inicializacija
pygame.init()

#nastavitve zaslona
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE) #te zadnji atributi povejo, da se okencek, kjer se igrca odpre, lahko poveca/zmanjsa

#ura
clock = pygame.time.Clock()

def path(name):
    return os.path.join("Slike_in_fonti", name)

#fonti
FONT_PATH = path("Pixeltype.ttf")
TEST_FONT = pygame.font.Font(FONT_PATH, 50)


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

#ozadja
test_surface = pygame.image.load(path("glavno_ozadje.jpg"))
test_surface1 = pygame.image.load(path("konec_ozadje.jpeg"))
background = pygame.transform.smoothscale(test_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
background1 = pygame.transform.smoothscale(test_surface1, (SCREEN_WIDTH, SCREEN_HEIGHT))

def zacetna_stran():
    global screen, background, SCREEN_WIDTH, SCREEN_HEIGHT
    
    pygame.display.set_caption("Gasilec")

    while True:
        screen.blit(background, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        zacetno_besedilo = TEST_FONT.render('Gasilec', False, BLACK)
        zacetni_rect = zacetno_besedilo.get_rect(center=(SCREEN_WIDTH // 2, 100))

        igraj_gumb = Button(image=pygame.image.load(path("Rect.png")), hovering_image=pygame.image.load(path("Rect1.png")),
                            pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.4), text_input="PLAY", font=TEST_FONT, base_color=BLACK, hovering_color=WHITE)
        navodila_gumb = Button(image=pygame.image.load(path("Rect.png")), hovering_image=pygame.image.load(path("Rect1.png")),
                               pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.6), text_input="HOW TO PLAY", font=TEST_FONT, base_color=BLACK, hovering_color=WHITE)
        izhod_gumb = Button(image=pygame.image.load(path("Rect.png")), hovering_image=pygame.image.load(path("Rect1.png")),
                            pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.8), text_input="EXIT", font=TEST_FONT, base_color=BLACK, hovering_color=WHITE)

        screen.blit(zacetno_besedilo, zacetni_rect)

        for gumb in [igraj_gumb, navodila_gumb, izhod_gumb]:
            gumb.changeColor(mouse_pos)
            gumb.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if igraj_gumb.checkForInput(mouse_pos):
                    igraj()
                if navodila_gumb.checkForInput(mouse_pos):
                    navodila()
                if izhod_gumb.checkForInput(mouse_pos):
                    pygame.quit()
                    exit()
            if event.type == VIDEORESIZE:
                SCREEN_WIDTH, SCREEN_HEIGHT = event.size
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), HWSURFACE | DOUBLEBUF | RESIZABLE)
                background = pygame.transform.smoothscale(test_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))

        pygame.display.update()
        clock.tick(60)


def igraj():
    pygame.display.set_caption("PLAY")

    running = True
    while running:
        igraj_miska_pos = pygame.mouse.get_pos()

        screen.fill(BLACK)

        igraj_besedilo = TEST_FONT.render('To morm še zrihtat', False, WHITE)
        igraj_rect = igraj_besedilo.get_rect(center=(SCREEN_WIDTH // 2, 100))

        screen.blit(igraj_besedilo, igraj_rect)

        nazaj = Button(image=None, hovering_image=None, pos=(640, 460), text_input="BACK", font=TEST_FONT,
                       base_color=WHITE, hovering_color=BLACK)

        nazaj.changeColor(igraj_miska_pos)
        nazaj.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if nazaj.checkForInput(igraj_miska_pos):
                    zacetna_stran()

        pygame.display.update()
        clock.tick(60)

def navodila():
    pygame.display.set_caption("HOW TO PLAY")

    running = True
    while running:
        navodila_miska_pos = pygame.mouse.get_pos()

        background1 = pygame.transform.smoothscale(test_surface1, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(background1, (0,0))

        pygame.draw.rect(screen, (250, 250, 250), [600, 100, 500, 400]) # (left, top, width, height)
        pygame.draw.rect(screen, (0, 0, 0), [600, 100, 500, 400], width = 3)


        navodila_besedilo1 = TEST_FONT.render('Game over!', False, BLACK)
        navodila_rect1 = navodila_besedilo1.get_rect(topleft=(750, 150)) # center = (left+width//2, top + 50)
        screen.blit(navodila_besedilo1, navodila_rect1)

        resevanje_besedilo = TEST_FONT.render('You saved 5 trees.', False, BLACK)
        resevanje_rect = resevanje_besedilo.get_rect(topleft=(720, 250))
        screen.blit(resevanje_besedilo, resevanje_rect)

        resevanje_besedilo2 = TEST_FONT.render('Congrats!', False, BLACK)
        resevanje_rect2 = resevanje_besedilo2.get_rect(topleft=(795, 350))
        screen.blit(resevanje_besedilo2, resevanje_rect2)

        

        nazaj = Button(image=None, hovering_image=None, pos=(640, 460), text_input="BACK", font=TEST_FONT,
                       base_color=WHITE, hovering_color=BLACK)

        nazaj.changeColor(navodila_miska_pos)
        nazaj.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if nazaj.checkForInput(navodila_miska_pos):
                    zacetna_stran()

        pygame.display.update()
        clock.tick(60)


#tuki bo za igro dejanski input loh
# def konec_igre():
#     pygame.display.set_caption("Konec igre")

#     running = True
#     while running:
#         navodila_miska_pos = pygame.mouse.get_pos()

#         screen.blit(background1, (0, 0))

#         navodila_besedilo = TEST_FONT.render('To morm tut še zrihtat', False, WHITE)
#         navodila_rect = navodila_besedilo.get_rect(center=(SCREEN_WIDTH // 2, 100))

#         screen.blit(navodila_besedilo, navodila_rect)

#         nazaj = Button(image=None, hovering_image=None, pos=(640, 460), text_input="NAZAJ", font=TEST_FONT,
#                        base_color=WHITE, hovering_color=BLACK)

#         nazaj.changeColor(navodila_miska_pos)
#         nazaj.update(screen)

#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 running = False
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if nazaj.checkForInput(navodila_miska_pos):
#                     zacetna_stran()

#         pygame.display.update()
#         clock.tick(60)


zacetna_stran()