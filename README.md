#  Firefighter
**Firefighter** is a Python-based game where you play as a firefighter aiming to protect trees from spreading fires in a randomly generated forest. The game is inspired by Hartnell's pursuit-evasion game on graphs, with unique challenges where each decision could save or doom part of the forest.

## Game Overview
In **Firefighter**, a fire breaks out in a procedurally generated forest where:

- Trees are nodes in a complex network
- Rocky paths between trees serve as fire spread routes
- Fire spreads turn-by-turn to connected, unprotected trees
- You can protect one tree per turn to create firebreaks


# Installation
For Windows Users:

- Go to the Releases section on GitHub (on the right side of the screen)
- Download both:
  - Firefighter.exe (executable)
  - Source Code.zip (game assets)
- Extract the Source Code.zip
- Move Firefighter.exe into the extracted folder
- Double-click Firefighter.exe and wait a few seconds for the game to launch


![](https://github.com/user-attachments/assets/a8027b89-1d5c-4ddf-a5db-89665297038c)


# Gameplay Mechanics
## Core Systems:

- Turn-Based Strategy: Each click counts as a turn where you protect one tree while the fire spreads to adjacent unprotected trees
- Procedural Forests: Every game generates a unique forest layout using Barabási-Albert network algorithms
- Fire Propagation: Flames spread through these phases:
  - Random ignition point
  - Spreads to connected unprotected trees each turn
  - Fire burns out when no new trees can be reached

## Controls:

- Mouse:
  - Click trees to protect them (turns blue)
  - Hover to see fire spread connections


## Technical Details
Gasilec is built using Python 3 as its core programming language, leveraging the Pygame library for all graphical rendering and user interaction. The game utilizes NetworkX's sophisticated graph algorithms to generate biologically plausible forest structures, implementing the mathematical model of Hartnell's Firefighter problem to simulate realistic fire spread patterns. Designed for flexibility, the game engine supports both immersive fullscreen and convenient windowed display modes, adapting seamlessly to different screen resolutions while maintaining consistent gameplay mechanics.
