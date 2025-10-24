import pygame
import sys

import fonts
import enemies
import menus
import music
import skilltree
import sound
import variables
import weapons


# Initialize Pygame
pygame.init()

# Set up the fullscreen display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fullscreen Red Window")

music.play_theme

# Main loop
running = True
while running:
    for event in pygame.event.get():
        # Check for quit events
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Exit on ESC key
                running = False

        elif event.key == pygame.K_p:
            if is_paused:
                music.unpause_theme()
                is_paused = False
            else:
                music.pause_theme()
                is_paused = True
    # Fill the screen with red (RGB: 255, 0, 0)
    screen.fill((255, 0, 0))

    # Update the display
    pygame.display.flip()

# Clean up
music.stop_theme()
music.unload_theme()
pygame.quit()
sys.exit()
