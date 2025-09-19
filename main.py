import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the fullscreen display
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fullscreen Red Window")

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

    # Fill the screen with red (RGB: 255, 0, 0)
    screen.fill((255, 0, 0))

    # Update the display
    pygame.display.flip()

# Clean up
pygame.quit()
sys.exit()
