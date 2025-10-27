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

pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fullscreen Red Window")

music.init_music()
music.play_theme()

running = True
is_paused = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_p:
                if is_paused:
                    music.unpause_theme()
                    is_paused = False
                else:
                    music.pause_theme()
                    is_paused = True

    screen.fill((255, 0, 0))

    pygame.display.flip()

music.stop_theme()
music.unload_theme()
pygame.quit()
sys.exit()
