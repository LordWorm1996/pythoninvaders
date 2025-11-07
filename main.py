import pygame
import sys
import pygame_menu

import fonts
import enemies
import menus
import music
import skilltree
import sound
import variables
import weapons

pygame.init()
music.init_music()
fonts.init_font()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Python Invaders")

menu = pygame_menu.Menu(
    "Python Invaders", 400, 300, theme=pygame_menu.themes.THEME_BLUE
)

running = True
is_paused = False
while running:
    menu.add.text_input("Name :", default="Jane Doe")
    menu.add.button("Play", music.play_theme())
    menu.add.button("Skilltree", skilltree.skilltree_menu(screen))
    menu.add.button("Quit", pygame_menu.events.EXIT)

    menu.mainloop(screen)

    pygame.display.flip()

music.stop_theme()
music.unload_theme()
fonts.quit_font()
pygame.quit()
sys.exit()
