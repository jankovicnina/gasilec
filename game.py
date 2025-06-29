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
clock = pygame.time.Clock()


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

#rocks
rock_image = pygame.image.load(asset_path("rock.png")).convert_alpha()
rock_highlighted = pygame.image.load(asset_path("rock_highlighted.png")).convert_alpha()



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

    # Layout with tighter clustering
    layout = nx.kamada_kawai_layout(graph)

    avoid_rect = pygame.Rect(0, 0, 220, 110)
    min_distance = math.hypot(80, 100) + 10  # ≈ 130 pixels

    def is_far_enough(x, y):
        for tree in forest:
            dx = (tree.x + 40) - (x + 40)
            dy = (tree.y + 50) - (y + 50)
            if math.hypot(dx, dy) < min_distance:
                return False
        return True

    # Normalize positions to screen
    padding_x, padding_y = 100, 100  # Keep some space from screen edges
    for i in range(tree_count):
        pos = layout[i]
        x = int(padding_x + (pos[0] + 1) / 2 * (screen_width - 2 * padding_x - 80))
        y = int(padding_y + (pos[1] + 1) / 2 * (screen_height - 2 * padding_y - 100))

        # Retry if too close to other trees or the status box
        attempts = 0
        while avoid_rect.collidepoint(x + 20, y + 40) or not is_far_enough(x, y):
            x = random.randint(padding_x, screen_width - padding_x - 80)
            y = random.randint(padding_y, screen_height - padding_y - 100)
            attempts += 1
            if attempts > 500:
                break  # Prevent infinite loop

        tree = Tree(x, y)
        forest.append(tree)

    # Assign neighbors
    for i, tree in enumerate(forest):
        tree.neighbors = [forest[n] for n in graph.neighbors(i)]

    # Set a random burning tree with degree > 1
    candidates = [tree for tree in forest if len(tree.neighbors) > 1]
    initial_burning_tree = random.choice(candidates) if candidates else random.choice(forest)
    initial_burning_tree.color = RED

    return forest, initial_burning_tree



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



def draw_status_box(screen, forest, game_over):
    box_width, box_height = 200, 160
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
    # if the game is over, you display "Game over" text in the status box
    if game_over:
        current_time = pygame.time.get_ticks()
        # blinking time is 500ms
        if (current_time // 500) % 2 == 0:
            text4 = font.render("Game Over", True, RED)
            screen.blit(text4, (30, 130))


def draw_text_with_typing_effect(screen, text, font, color, x, y, delay=50):
    typed_text = ""
    for i, char in enumerate(text):
        typed_text += char
        text_surface = font.render(typed_text, True, color)
        # Clear speech bubble area (or redraw it)
        pygame.draw.rect(screen, WHITE, (x, y, WIDTH - 200, 100))  # Temp bubble
        screen.blit(text_surface, (x + 20, y + 20))  # Offset inside bubble
        pygame.display.flip()
        pygame.time.delay(delay)  # Controls speed
    return typed_text



# Load and scale the background
background_img = pygame.image.load(asset_path("background.jpg")).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
fire_main_img = pygame.image.load(asset_path("main_background_fire.jpg")).convert()
fire_main_img = pygame.transform.scale(fire_main_img, (WIDTH, HEIGHT))
no_fire_main_img = pygame.image.load(asset_path("main_bacground_notfire.jpg")).convert()
no_fire_main_img = pygame.transform.scale(no_fire_main_img, (WIDTH, HEIGHT))


def main_menu():
    # global screen, background, SCREEN_WIDTH, SCREEN_HEIGHT
    
    pygame.display.set_caption("Main Menu")

    while True:
        screen.blit(fire_main_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        base_text = pygame.image.load(asset_path("firefighter_txt.png")).convert_alpha()  # Use convert_alpha for transparency
        scale_factor = 1.5  # Increase this to make it bigger (e.g., 2.0 for 2x size)
        base_text = pygame.transform.scale(
            base_text,
            (int(base_text.get_width() * scale_factor), 
            int(base_text.get_height() * scale_factor)
        ))
        base_rect = base_text.get_rect(center=(WIDTH // 2, 100))

        play_button = Button(image=pygame.image.load(asset_path("play.png")), hovering_image=pygame.image.load(asset_path("play_hover.png")),pos=(WIDTH // 2, HEIGHT * 0.4))
        tutorial_button = Button(image=pygame.image.load(asset_path("tutorial.png")), hovering_image=pygame.image.load(asset_path("tutorial_hover.png")), pos=(WIDTH // 2, HEIGHT * 0.6))
        quit_button = Button(image=pygame.image.load(asset_path("quit.png")), hovering_image=pygame.image.load(asset_path("quit_hover.png")), pos=(WIDTH // 2, HEIGHT * 0.8))

        screen.blit(base_text, base_rect)

        for button in [play_button, tutorial_button, quit_button]:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(mouse_pos):
                    play()
                if tutorial_button.checkForInput(mouse_pos):
                    # tutorial()
                    game_over_screen(screen, 5, 8)
                if quit_button.checkForInput(mouse_pos):
                    pygame.quit()
                    exit()
        pygame.display.update()
        clock.tick(60)





def tutorial():
    clock = pygame.time.Clock()
    running = True
    current_line = 0
    dialogue = [
        "Hey there, rookie! The forest is on FIRE!",
        "See those rocky paths? Fire spreads ONLY along them!",
        "Hover over trees to see connections. Click to PROTECT one!",
        "Good! Protected trees (blue aura) won't burn. Watch the fire spread...",
        "The game ends when the fire can't spread further.",  # New line
        "You'll see how many trees you saved!",
        "Now try saving more trees before the forest is engulfed! Ready?"
    ]

    typed_text = ""
    typing = False
    typing_complete = False
    typing_start_time = 0
    player_protected = False  # Track if player protected a tree

    # Firefighter image
    firefighter_img = pygame.image.load(asset_path("firefighter.png")).convert_alpha()
    firefighter_img = pygame.transform.scale(firefighter_img, (132, 252))
    firefighter_rect = firefighter_img.get_rect(bottomleft=(50, HEIGHT-50))


    # Button 
    next_button = Button(image=pygame.image.load(asset_path("next.png")), 
        hovering_image=pygame.image.load(asset_path("next_hover.png")),
        pos=(WIDTH // 2, HEIGHT - 50)
    )


    # Mini forest setup (4 trees in a square)
    mini_trees = [
        Tree(x=int(WIDTH*0.6), y=int(HEIGHT*0.2)),  # Was 0.4 (moved up)
        Tree(x=int(WIDTH*0.8), y=int(HEIGHT*0.2)),  # Was 0.4 (moved up)
        Tree(x=int(WIDTH*0.6), y=int(HEIGHT*0.5)),  # Was 0.6 (moved up)
        Tree(x=int(WIDTH*0.8), y=int(HEIGHT*0.5))   # Was 0.6 (moved up)
    ]
    
    # Set up connections
    mini_trees[0].neighbors = [mini_trees[1], mini_trees[2]]
    mini_trees[1].neighbors = [mini_trees[0], mini_trees[3]]
    mini_trees[2].neighbors = [mini_trees[0], mini_trees[3]]
    mini_trees[3].neighbors = [mini_trees[1], mini_trees[2]]
    
    # Set initial burning tree
    mini_trees[2].catch_fire()
    hovered_tree = None

    while running:
        screen.blit(background_img, (0, 0))

        screen.blit(firefighter_img, firefighter_rect)
        
        # Speech bubble
        bubble_img = pygame.image.load(asset_path("bubble.png")).convert_alpha()
        bubble_x = firefighter_rect.left + 50
        bubble_y = firefighter_rect.top - 120
        bubble_rect = pygame.Rect(bubble_x, bubble_y, 550, 70)

        screen.blit(bubble_img, bubble_rect)

        # Button handling
        show_button = (typing_complete and current_line < len(dialogue) 
                      and not (current_line == 2 and not player_protected))

        if show_button:
            next_button.changeColor(mouse_pos)
            next_button.update(screen)


        # Draw connections
        for i, tree in enumerate(mini_trees):
            for neighbor in tree.neighbors:
                if i < mini_trees.index(neighbor):
                    start_pos = (tree.x + 40, tree.y + 50)
                    end_pos = (neighbor.x + 40, neighbor.y + 50)
                    if hovered_tree and (tree == hovered_tree or neighbor == hovered_tree):
                        draw_rocky_path(screen, start_pos, end_pos, rock_highlighted)
                    else:
                        draw_rocky_path(screen, start_pos, end_pos, rock_image)

        # Handle tree hovering
        mouse_pos = pygame.mouse.get_pos()
        hovered_tree = None
        for tree in mini_trees:
            if tree.is_hovered(mouse_pos):
                hovered_tree = tree
                break

        # Interactive protection during line 2
        if typing_complete and current_line == 2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for tree in mini_trees:
                        if tree.is_clicked(mouse_pos) and tree.color == (0, 0, 0):
                            tree.protect()
                            player_protected = True
                            current_line += 1  # Move to next explanation
                            typing_complete = False

        # Auto-advance after fire spread demonstration
        elif typing_complete and current_line == 3 and not any(t.color == (0, 0, 0) for t in mini_trees[2].neighbors):
            pygame.time.delay(1500)  # Let player observe
            current_line += 1
            typing_complete = False

        # Draw all trees
        for tree in mini_trees:
            tree.draw(screen)

        # Typing logic
        if not typing and not typing_complete and current_line < len(dialogue):
            typing = True
            typing_complete = False
            typed_text = ""
            typing_start_time = pygame.time.get_ticks()

        if typing:
            elapsed = pygame.time.get_ticks() - typing_start_time
            chars_to_show = min(len(dialogue[current_line]), elapsed // 50)
            typed_text = dialogue[current_line][:chars_to_show]
            
            if len(typed_text) == len(dialogue[current_line]):
                typing = False
                typing_complete = True
                # Auto-spread fire after protection explanation
                if current_line == 3:
                    for neighbor in mini_trees[2].neighbors:
                        if neighbor.color == (0, 0, 0):
                            neighbor.catch_fire()

        # Render text
        font = pygame.font.Font(FONT_PATH, 24)
        text_surface = font.render(typed_text, True, BLACK)
        screen.blit(text_surface, (bubble_rect.x + 25, bubble_rect.y + 25))

        # Show button when appropriate
        show_button = (typing_complete and current_line < len(dialogue) 
                      and not (current_line == 2 and not player_protected))
        
        if show_button:
            next_button.text_input = "PLAY!" if current_line == len(dialogue) - 1 else "NEXT"
            next_button.update(screen)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and show_button:
                if next_button.checkForInput(mouse_pos):
                    if current_line < len(dialogue) - 1:
                        current_line += 1
                        typing_complete = False
                    else:
                        return

        pygame.display.flip()
        clock.tick(60)


def game_over_screen(screen, saved_count, tree_count, forest=None):
    clock = pygame.time.Clock()
    running = True

    # Load button images at half size
    def load_half_size(image_path):
        img = pygame.image.load(asset_path(image_path)).convert_alpha()
        return pygame.transform.scale(img, (img.get_width() // 2, img.get_height() // 2))

    # Create buttons (half size)
    exit_button = Button(
        image=load_half_size("quit.png"), 
        hovering_image=load_half_size("quit_hover.png"),
        pos=(3 * WIDTH//4 + 65, HEIGHT//2 + 120)
    )
    replay_button = Button(
        image=load_half_size("replay.png"), 
        hovering_image=load_half_size("replay_hover.png"),
        pos=(3 * WIDTH//4 + 65, HEIGHT//2 + 60)
    )
    new_game_button = Button(
        image=load_half_size("new_game.png"), 
        hovering_image=load_half_size("new_game_hover.png"),
        pos=(3 * WIDTH//4 + 65, HEIGHT//2 )
    )

    # Loading the images for the background
    trophy_img = pygame.image.load(asset_path("firefighter_trophy.png")).convert_alpha()
    trophy_img = pygame.transform.scale(trophy_img, (trophy_img.get_width() * 2, trophy_img.get_height() * 2))  # Optional scaling
    trophy_rect = trophy_img.get_rect(bottomleft=(250, HEIGHT - 100))

    bubble_img = pygame.image.load(asset_path("bubble2.png")).convert_alpha()
    bubble_rect = bubble_img.get_rect(bottomleft=(100, HEIGHT//2 - 100  ))

    board_img = pygame.image.load(asset_path("board.png")).convert_alpha()
    board_rect = board_img.get_rect(topleft=(WIDTH // 2 - 50, HEIGHT//2 - 100))

    while running:
        # Draw the background(s)
        screen.blit(no_fire_main_img, (0, 0))
        screen.blit(trophy_img, trophy_rect)
        screen.blit(bubble_img, bubble_rect)
        screen.blit(board_img, board_rect)

        lines = ["After-action report:",
                f"- Trees saved: {saved_count}",
                f"- Efficiency: {100 * saved_count / tree_count}%",
                "Debrief when ready."]
        
        for i, line in enumerate(lines):
            text = font.render(line, True, BLACK)
            screen.blit(text, (WIDTH // 2 - 40 + 20, HEIGHT//2 - 25 + i*45))

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Update and draw buttons
        for button in [new_game_button, replay_button, exit_button]:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_button.checkForInput(mouse_pos):
                    pygame.quit()
                    sys.exit()
                elif replay_button.checkForInput(mouse_pos):
                    return "replay"
                elif new_game_button.checkForInput(mouse_pos):
                    return "new"

        pygame.display.flip()
        clock.tick(30)


def play():
    while True:
        tree_count = get_tree_count()
        forest, initial_burning_tree = generate_forest(tree_count)
        clock = pygame.time.Clock()
        running = True

        game_over = False
        game_over_time = None

        while running:
            screen.blit(background_img, (0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    for tree in forest:
                        if tree.is_clicked(pygame.mouse.get_pos()):
                            tree.protect()
                            next_turn(forest)
            
            if not game_over and all(all(n.color != BLACK for n in tree.neighbors) for tree in forest if tree.color == RED):
                game_over = True
                game_over_time = pygame.time.get_ticks()

            # If game is over and 3 seconds have passed, show game over screen
            if game_over and pygame.time.get_ticks() - game_over_time > 2500:
                saved_count = sum(tree.color != RED for tree in forest)
                action = game_over_screen(screen, saved_count, tree_count, forest)

                if action == "replay":
                        # Reset the same forest
                        for tree in forest:
                            tree.color = BLACK
                        # Set a random burning tree with degree > 1
                        initial_burning_tree.color = RED 
                        game_over = False
                        game_over_time = None
                        continue
                elif action == "new":
                    break  # Will restart outer loop with new forest

            hovered_tree = None
            if not game_over:
                mouse_pos = pygame.mouse.get_pos()
                for tree in forest:
                    if tree.is_hovered(mouse_pos):
                        hovered_tree = tree
                        break

            for i, tree in enumerate(forest):
                for neighbor in tree.neighbors:
                    if i < forest.index(neighbor):  # Avoid double-drawing paths
                        start_pos = (tree.x + 40, tree.y + 95)
                        end_pos = (neighbor.x + 40, neighbor.y + 50)

                        if not game_over and hovered_tree and (tree == hovered_tree or neighbor == hovered_tree):
                            draw_rocky_path(screen, start_pos, end_pos, rock_highlighted)
                        else:
                            draw_rocky_path(screen, start_pos, end_pos, rock_image)


            for tree in forest:
                tree.draw(screen)

            draw_status_box(screen, forest, game_over)

            pygame.display.flip()
            clock.tick(60)




if __name__ == "__main__":
    main_menu()