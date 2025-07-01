import pygame, os

class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (0, 0, 0)  # BLACK
        self.neighbors = []
        self.image = None

    def load_image(self, image_name):
        path = os.path.join("Slike_in_fonti", image_name)
        self.image = pygame.image.load(path)
        self.image = pygame.transform.scale(self.image, (80, 100))
    
    def draw(self, screen):
        if self.color == (0, 0, 0):
            self.load_image("negorece.png")
        elif self.color == (255, 0, 0):
            self.load_image("gorece.png")
        else:
            self.load_image("zasciteno.png")
        screen.blit(self.image, (self.x, self.y))

        # for neighbor in self.neighbors:
        #     pygame.draw.line(screen, (0, 0, 0), (self.x + 35, self.y + 45), (neighbor.x + 35, neighbor.y + 45), 2)

    def catch_fire(self):
        self.color = (255, 0, 0)

    def protect(self):
        if self.color == (0, 0, 0):
            self.color = (0, 255, 0)

    def is_clicked(self, pos):
        if self.color == (0, 0, 0):
            rect = self.image.get_rect(topleft=(self.x, self.y))
            return rect.collidepoint(pos)
        return False
    
    def is_hovered(self, mouse_pos):
        tree_rect = pygame.Rect(self.x, self.y, 80, 100)
        return tree_rect.collidepoint(mouse_pos)
