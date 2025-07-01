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


def asset_path(name):
    
    """
    Helper function to get full asset path
    """

    return os.path.join("Slike_in_fonti", name)


# Font setup
FONT_PATH = asset_path("Pixeltype.ttf")
font = pygame.font.Font(FONT_PATH, 40)

# Load assets
rock_image = pygame.image.load(asset_path("rock.png")).convert_alpha()
rock_highlighted = pygame.image.load(asset_path("rock_highlighted.png")).convert_alpha()
background_img = pygame.image.load(asset_path("background.jpg")).convert()
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
fire_main_img = pygame.image.load(asset_path("main_background_fire.jpg")).convert()
fire_main_img = pygame.transform.scale(fire_main_img, (WIDTH, HEIGHT))
no_fire_main_img = pygame.image.load(asset_path("main_bacground_notfire.jpg")).convert()
no_fire_main_img = pygame.transform.scale(no_fire_main_img, (WIDTH, HEIGHT))


def draw_rocky_path(screen, start_pos, end_pos, rock_img, spacing=16):

    """
    Draws a path between two points using rock images
    """

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


def get_tree_count():
    """
    Gets number of trees from player input (3-20)
    Now includes a Next button and disabled Enter key confirmation
    """
    running = True
    input_text = ""
    error = ""
    
    # Create Next button
    next_button = Button(
        image=pygame.image.load(asset_path("next.png")),
        hovering_image=pygame.image.load(asset_path("next_hover.png")),
        pos=(WIDTH // 2, HEIGHT - 100)
    )

    while running:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_img, (0, 0))
        
        # Draw input UI
        text_surface = font.render("Number of trees (3-20):", True, BLACK)
        text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 25))
        screen.blit(text_surface, text_rect)

        input_box = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 25, 200, 50)
        pygame.draw.rect(screen, BLACK, input_box, 2)
        
        # Render input text centered in the box
        input_surface = font.render(input_text, True, BLACK)
        text_width = input_surface.get_width()
        screen.blit(input_surface, (input_box.x + (input_box.width - text_width) // 2, input_box.y + 15))

        # Update and draw Next button
        next_button.changeColor(mouse_pos)
        next_button.update(screen)
        
        if error:
            error_surface = font.render(error, True, RED)
            error_rect = error_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            screen.blit(error_surface, error_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            elif event.type == pygame.KEYDOWN:
                # Disabled Enter key functionality
                if event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key in range(pygame.K_0, pygame.K_9 + 1):
                    if len(input_text) < 2:  # Limit to 2 digits (max 20)
                        input_text += event.unicode
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if next_button.checkForInput(mouse_pos):
                    if input_text:
                        try:
                            count = int(input_text)
                            if 3 <= count <= 20:
                                return count
                            error = "Please enter a number between 3-20"
                        except ValueError:
                            error = "Please enter a valid number"
                    else:
                        error = "Please enter number of trees first"

        pygame.display.flip()
        clock.tick(30)


def generate_forest(tree_count):

    """
    Generates a forest with given number of trees using networkx graph
    """

    graph = nx.barabasi_albert_graph(tree_count, 1)
    forest = []
    
    # Use spring layout for better node distribution
    layout = nx.spring_layout(graph, k=15/math.sqrt(tree_count), iterations=100)
    
    # Define boundaries
    screen_rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
    avoid_rect = pygame.Rect(0, 0, 220, 160)  # Status board area
    min_distance = 80  # Minimum distance between trees
    tree_size = 80  # Approximate size of tree sprites


    def is_valid_position(x, y):

        """
        Check if position is valid (not in avoid area and not too close to others)
        """

        # Check screen boundaries
        if (x < avoid_rect.width + 20 or 
            x > WIDTH - tree_size - 20 or
            y < 20 or 
            y > HEIGHT - tree_size - 20):
            return False
            
        # Check proximity to other trees
        for tree in forest:
            if math.hypot(tree.x - x, tree.y - y) < min_distance:
                return False
        return True
    

    # Place trees on screen
    for i in range(tree_count):
        pos = layout[i]

        # Map layout coordinates to safe screen area
        safe_width = WIDTH - avoid_rect.width - 100 - tree_size
        safe_height = HEIGHT - 100 - tree_size
        x = int(avoid_rect.width + 100 + pos[0] * safe_width)
        y = int(100 + (pos[1] + 1) / 2 * safe_height)

        # Ensure valid position
        attempts = 0
        while not is_valid_position(x, y) and attempts < 100:
            x = random.randint(avoid_rect.width + 100, WIDTH - tree_size - 100)
            y = random.randint(100, HEIGHT - tree_size - 100)
            attempts += 1

        forest.append(Tree(x, y))

    # Assign neighbors from graph
    for i, tree in enumerate(forest):
        tree.neighbors = [forest[n] for n in graph.neighbors(i)]

    # Set initial burning tree (prefer trees with multiple connections)
    candidates = [tree for tree in forest if len(tree.neighbors) > 1]
    initial_burning_tree = random.choice(candidates) if candidates else random.choice(forest)
    initial_burning_tree.color = RED

    return forest, initial_burning_tree


def next_turn(forest):

    """
    Advances the game state by spreading fire to unprotected neighbors
    """

    for tree in [t for t in forest if t.color == RED]:
        for neighbor in tree.neighbors:
            if neighbor.color == BLACK:
                neighbor.catch_fire()


def count_saved_trees(forest):

    """
    Counts trees that are either protected or unreachable by fire
    """

    saved = 0
    for tree in forest:
        if tree.color == GREEN:
            saved += 1
        elif tree.color == BLACK:
            # Check if any burning tree can reach this one
            reachable = any(
                burning_tree.color == RED and 
                is_reachable(burning_tree, tree, set()) 
                for burning_tree in forest
            )
            if not reachable:
                saved += 1
    return saved


def is_reachable(current, target, visited):
    
    """
    Recursive helper to check fire path between trees
    """

    if current == target:
        return True
    visited.add(current)
    for neighbor in current.neighbors:
        if neighbor not in visited and neighbor.color == BLACK:
            if is_reachable(neighbor, target, visited):
                return True
    return False


def draw_status_box(screen, forest, game_over):

    """
    Draws the game status board with stats
    """

    board_img = pygame.image.load(asset_path("board1.png")).convert_alpha()
    board_img = pygame.transform.scale(board_img, (200, 200))
    screen.blit(board_img, (0, 0))

    # Helper function to center text
    def center_text(text, y_offset, color=BLACK):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(100, y_offset))
        screen.blit(text_surface, text_rect)

    # Display stats
    center_text(f"Burning: {sum(t.color == RED for t in forest)}", 35)
    center_text(f"Protected: {sum(t.color == GREEN for t in forest)}", 75)
    center_text(f"Saved: {count_saved_trees(forest)}", 115)
    
    # Blinking game over text
    if game_over and (pygame.time.get_ticks() // 500) % 2 == 0:
        center_text("GAME OVER", 150, WHITE)


def get_funny_remark(saved_count, tree_count):

    """
    Returns humorous remark based on player's performance
    """

    efficiency = int(100 * saved_count / tree_count)
    remarks = [
        (0, "*spits* Let's go again."),
        (10, f"That's {saved_count} less trees to replant."),
        (20, "At least we didn't start the fire... right?"),
        (30, "Call that a controlled burn!"),
        (40, "Not our worst day, not our best."),
        (50, "Halfway to a perfect score!"),
        (60, "Now we're cooking with gas!"),
        (70, "Chief might actually smile about this!"),
        (80, "Who needs a hose when you've got skills?"),
        (90, "Save some trees for the next shift!")
    ]
    
    # Find the appropriate remark
    for threshold, remark in sorted(remarks, reverse=True):
        if efficiency >= threshold:
            return remark



def main_menu(): 

    """
    Main menu screen with play/tutorial/quit options
    """

    while True:
        screen.blit(fire_main_img, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        play_button = Button(
            image=pygame.image.load(asset_path("play.png")), 
            hovering_image=pygame.image.load(asset_path("play_hover.png")),
            pos=(WIDTH // 2, HEIGHT * 0.4)
            )
        tutorial_button = Button(
            image=pygame.image.load(asset_path("tutorial.png")), 
            hovering_image=pygame.image.load(asset_path("tutorial_hover.png")), 
            pos=(WIDTH // 2, HEIGHT * 0.6)
            )
        quit_button = Button(
            image=pygame.image.load(asset_path("quit.png")), 
            hovering_image=pygame.image.load(asset_path("quit_hover.png")), 
            pos=(WIDTH // 2, HEIGHT * 0.8)
            )


        base_text = pygame.image.load(asset_path("firefighter_txt.png")).convert_alpha()  # Use convert_alpha for transparency
        scale_factor = 1.5  # Increase this to make it bigger (e.g., 2.0 for 2x size)
        base_text = pygame.transform.scale(
            base_text,
            (int(base_text.get_width() * scale_factor), 
            int(base_text.get_height() * scale_factor)
        ))
        base_rect = base_text.get_rect(center=(WIDTH // 2, 100))


        screen.blit(base_text, base_rect)

        for button in [play_button, tutorial_button, quit_button]:
            button.changeColor(mouse_pos)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.checkForInput(mouse_pos):
                    play()
                if tutorial_button.checkForInput(mouse_pos):
                    tutorial()
                if quit_button.checkForInput(mouse_pos):
                    pygame.quit()
                    sys.exit()
        pygame.display.update()
        clock.tick(60)



def tutorial():

    """
    Interactive tutorial that teaches the game mechanics through step-by-step instructions
    and a mini forest demonstration with visual feedback.
    """

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

    # Load play button images and scale them to half size
    play_img = pygame.image.load(asset_path("play.png")).convert_alpha()
    play_hover_img = pygame.image.load(asset_path("play_hover.png")).convert_alpha()
    
    # Scale images to half size
    play_img = pygame.transform.scale(play_img, (play_img.get_width() // 2, play_img.get_height() // 2))
    play_hover_img = pygame.transform.scale(play_hover_img, 
                                          (play_hover_img.get_width() // 2, play_hover_img.get_height() // 2))
    
    play_button = Button(image=play_img, 
        hovering_image=play_hover_img,
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
                        if tree.is_clicked(mouse_pos) and tree.color == BLACK:
                            tree.protect()
                            player_protected = True
                            tree_protected = True
                            break
                        
                    if tree_protected:
                        # Immediate visual update
                        screen.blit(background_img, (0, 0))
                        screen.blit(firefighter_img, firefighter_rect)
                        screen.blit(bubble_img, bubble_rect)

                        for i, tree in enumerate(mini_trees):
                            for neighbor in tree.neighbors:
                                if i < mini_trees.index(neighbor):
                                    start_pos = (tree.x + 40, tree.y + 50)
                                    end_pos = (neighbor.x + 40, neighbor.y + 50)
                                    draw_rocky_path(screen, start_pos, end_pos, rock_image)
                        
                        for tree in mini_trees:
                            tree.draw(screen)
                            
                        # Update display
                        pygame.display.flip()
                        
                        # Auto-advance after showing protection
                        pygame.time.delay(800)  # Let player see the protection
                        current_line += 1
                        typing_complete = False

        # Auto-advance after fire spread demonstration
        elif typing_complete and current_line == 3 and not any(t.color == BLACK for t in mini_trees[2].neighbors):
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
                        if neighbor.color == BLACK:
                            neighbor.catch_fire()

        # Render text
        font = pygame.font.Font(FONT_PATH, 24)
        text_surface = font.render(typed_text, True, BLACK)
        screen.blit(text_surface, (bubble_rect.x + 25, bubble_rect.y + 25))

        # Show appropriate button when needed
        show_button = (typing_complete and 
                       current_line < len(dialogue) and 
                       current_line != 3 and  # No button during fire spread
                       not (current_line == 2 and not player_protected)
        )
        
        if show_button:
            if current_line == len(dialogue) - 1:  # Last line - show PLAY button
                play_button.changeColor(mouse_pos)
                play_button.update(screen)
            else:  # Show NEXT button for other lines
                next_button.changeColor(mouse_pos)
                next_button.update(screen)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and show_button:
                if current_line == len(dialogue) - 1:  # Last line
                    if play_button.checkForInput(mouse_pos):
                        play()  # Redirect to tree count selection
                else:
                    if next_button.checkForInput(mouse_pos):
                        current_line += 1
                        typing_complete = False

        pygame.display.flip()
        clock.tick(60)



def game_over_screen(screen, saved_count, tree_count, forest=None):

    """
    Displays the game over screen with statistics and options to replay or start a new game.
    Shows saved tree count, efficiency percentage, and a humorous remark based on performance.
    """

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

    # Dialogue configuration
    phases = [
        {"text": "Let's check the stats...", "target": "bubble", "delay": 30},
        {"text": "After-action report:", "target": "board", "delay": 40, "show_after": 0},
        {"text": f"  - Trees saved: {saved_count}", "target": "board", "delay": 30, "show_after": 1},
        {"text": f"  - Efficiency: {int(100*saved_count/tree_count)}%", "target": "board", "delay": 30, "show_after": 2},
        {"text": "Debrief when ready.", "target": "board", "delay": 30, "show_after": 3},
        {"text": get_funny_remark(saved_count, tree_count), "target": "bubble", "delay": 40}
    ]
    
    # Text rendering
    current_phase = 0
    current_char = 0
    phase_start_time = pygame.time.get_ticks()
    active_texts = {"bubble": "", "board": []}
    bubble_font = pygame.font.Font(FONT_PATH, 24)
    board_font = pygame.font.Font(FONT_PATH, 28)

    while running:
        # Draw the background(s)
        screen.blit(no_fire_main_img, (0, 0))
        screen.blit(trophy_img, trophy_rect)
        screen.blit(bubble_img, bubble_rect)
        screen.blit(board_img, board_rect)

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
                

        # Text animation logic
        if current_phase < len(phases):
            phase = phases[current_phase]
            
            if current_char < len(phase["text"]):
                if pygame.time.get_ticks() - phase_start_time > phase["delay"]:
                    current_char += 1
                    phase_start_time = pygame.time.get_ticks()
                    
                    if phase["target"] == "bubble":
                        active_texts["bubble"] = phase["text"][:current_char]
                    else:
                        idx = phase.get("show_after", 0)
                        while len(active_texts["board"]) <= idx:
                            active_texts["board"].append("")
                        active_texts["board"][idx] = phase["text"][:current_char]
            else:
                current_phase += 1
                current_char = 0
                phase_start_time = pygame.time.get_ticks()
                if current_phase < len(phases) and phases[current_phase]["target"] == "bubble":
                    active_texts["bubble"] = ""
        
        # Draw speech bubble with text
        if active_texts["bubble"]:
            bubble_text = bubble_font.render(active_texts["bubble"], True, BLACK)
            text_rect = bubble_text.get_rect(
                centerx=bubble_rect.centerx,
                centery=bubble_rect.centery - 35 
            )            
            screen.blit(bubble_text, text_rect)
        
        # Draw board text
        for i, line in enumerate(active_texts["board"]):
            if line:  # Only render if text exists
                text_surface = board_font.render(line, True, BLACK)
                screen.blit(text_surface, (WIDTH // 2 - 10 + 20, HEIGHT//2 - 25 + i*45))

        pygame.display.flip()
        clock.tick(30)


def play():

    """
    Main game loop that handles the core gameplay:
    - Gets tree count from player
    - Generates and manages the forest
    - Handles player interactions (tree protection)
    - Controls fire spread and game state
    - Triggers game over when appropriate
    """

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