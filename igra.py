import pygame, random, os
import sys
import networkx as nx
from pygame.locals import *
from Razredi.buttons import Button
from Razredi.trees import Tree
import math

# Initialize Pygame
pygame.init()

# Set up the window
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF)
pygame.display.set_caption("Firefighter")



# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

def draw_rocky_path(screen, start_pos, end_pos, rock_img, spacing=16):
    dx = end_pos[0] - start_pos[0]
    dy = end_pos[1] - start_pos[1]
    distance = math.hypot(dx, dy)
    steps = int(distance // spacing)

    for i in range(steps + 1):
        t = i / steps
        x = int(start_pos[0] + t * dx)
        y = int(start_pos[1] + t * dy)

        rect = rock_img.get_rect(center=(x, y))
        screen.blit(rock_img, rect)


def asset_path(name):
    return os.path.join("Slike_in_fonti", name)

# Fonts
FONT_PATH = asset_path("Pixeltype.ttf")
font = pygame.font.Font(FONT_PATH, 40)
rock_image = pygame.image.load(asset_path("rock.png")).convert_alpha()

def get_tree_count():
    running = True
    input_text = ""
    clock = pygame.time.Clock()
    error = ""

    while running:
        screen.fill(WHITE)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if input_text:
                        try:
                            count = int(input_text)
                            if 3 <= count <= 20:
                                return count
                            else:
                                error = "Input an integer between 3 and 20."
                        except ValueError:
                            error = "Input an integer between 3 and 20."
                    else:
                        error = "Input an integer between 3 and 20."
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key in range(pygame.K_0, pygame.K_9 + 1):
                    input_text += event.unicode

        screen_width, screen_height = pygame.display.get_surface().get_size()
        text_surface = font.render("Number of trees:", True, BLACK)
        text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2 - 25))
        screen.blit(text_surface, text_rect)

        input_box = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 25, 200, 50)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        input_surface = font.render(input_text, True, BLACK)
        screen.blit(input_surface, (input_box.x + 98, input_box.y + 18))

        if error:
            error_surface = font.render(error, True, RED)
            error_rect = error_surface.get_rect(center=(screen_width // 2, screen_height // 2 + 100))
            screen.blit(error_surface, error_rect)

        pygame.display.flip()
        clock.tick(30)

def generate_forest(tree_count):
    graph = nx.barabasi_albert_graph(tree_count, 1)
    forest = []
    screen_width, screen_height = pygame.display.get_surface().get_size()

    layout = nx.spring_layout(graph, seed=random.randint(0, 10000))
    min_x, max_x = min(pos[0] for pos in layout.values()), max(pos[0] for pos in layout.values())
    min_y, max_y = min(pos[1] for pos in layout.values()), max(pos[1] for pos in layout.values())

    avoid_rect = pygame.Rect(0, 0, 220, 110)
    min_distance = 16  # Minimum distance between trees

    def is_far_enough(x, y):
        for tree in forest:
            dx = (tree.x + 40) - (x + 40)
            dy = (tree.y + 50) - (y + 50)
            if math.hypot(dx, dy) < min_distance:
                return False
        return True

    for i in range(tree_count):
        pos = layout[i]
        x = int((pos[0] - min_x) / (max_x - min_x) * (screen_width - 80))
        y = int((pos[1] - min_y) / (max_y - min_y) * (screen_height - 100))

        # Ensure trees don't spawn in the top-left info box or too close to others
        attempts = 0
        while avoid_rect.collidepoint(x + 20, y + 40) or not is_far_enough(x, y):
            x = random.randint(0, screen_width - 80)
            y = random.randint(0, screen_height - 100)
            attempts += 1
            if attempts > 500:
                break  # Avoid infinite loop in rare layout failures

        tree = Tree(x, y)
        forest.append(tree)

    for i, tree in enumerate(forest):
        tree.neighbors = [forest[n] for n in graph.neighbors(i)]

    candidates = [tree for tree in forest if len(tree.neighbors) > 1]
    if candidates:
        random.choice(candidates).color = RED
    else:
        random.choice(forest).color = RED

    return forest


def get_burning_trees(forest):
    return [tree for tree in forest if tree.color == RED]

def next_turn(forest):
    burning = get_burning_trees(forest)
    for tree in burning:
        for neighbor in tree.neighbors:
            if neighbor.color == BLACK:
                neighbor.catch_fire()

def is_reachable(current, target, visited):
    if current == target:
        return True
    visited.add(current)
    for neighbor in current.neighbors:
        if neighbor not in visited and neighbor.color == BLACK:
            if is_reachable(neighbor, target, visited):
                return True
    return False

def count_saved_trees(forest):
    saved = 0
    for tree in forest:
        if tree.color == GREEN:
            saved += 1
        elif tree.color == BLACK:
            # Check if all burning trees can't reach this one
            reachable = False
            for burning_tree in forest:
                if burning_tree.color == RED and is_reachable(burning_tree, tree, set()):
                    reachable = True
                    break
            if not reachable:
                saved += 1
    return saved



def draw_status_box(screen, forest):
    box_width, box_height = 250, 150
    pygame.draw.rect(screen, GRAY, (0, 0, box_width, box_height))

    burning = sum(tree.color == RED for tree in forest)
    protected = sum(tree.color == GREEN for tree in forest)
    saved = count_saved_trees(forest)

    text1 = font.render(f"Burning: {burning}", True, BLACK)
    text2 = font.render(f"Protected: {protected}", True, BLACK)
    text3 = font.render(f"Saved: {saved}", True, BLACK)

    screen.blit(text1, (10, 10))
    screen.blit(text2, (10, 50))
    screen.blit(text3, (10, 90))


# Load and scale the background
background_img = pygame.image.load(asset_path("background.jpg")).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))


def main():
    tree_count = get_tree_count()
    forest = generate_forest(tree_count)
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.blit(background_img, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for tree in forest:
                    if tree.is_clicked(pygame.mouse.get_pos()):
                        tree.protect()
                        next_turn(forest)

        for i, tree in enumerate(forest):
            for neighbor in tree.neighbors:
                if i < forest.index(neighbor):  # Avoid double-drawing paths
                    start_pos = (tree.x + 40, tree.y + 95)     # Bottom center of current tree
                    end_pos = (neighbor.x + 40, neighbor.y + 50)     # Top center of neighbor tree
                    draw_rocky_path(screen, start_pos, end_pos, rock_image)


        for tree in forest:
            tree.draw(screen)

        draw_status_box(screen, forest)

        pygame.display.flip()
        clock.tick(60)

        if all(all(n.color != BLACK for n in tree.neighbors) for tree in forest if tree.color == RED):
            print("Game over! All neighbors of burning trees are either burning or protected.")
            saved = sum(tree.color != RED for tree in forest)
            print(f"You saved {saved} trees.")
            running = False

if __name__ == "__main__":
    main()
