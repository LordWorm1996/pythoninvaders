import sys

import pygame
import pygame_menu

import fonts
import gameloop
import music
import skilltree
import variables

pygame.init()
#music.init_music()
fonts.init_font()

#music.play_theme()
screen = pygame.display.set_mode((1000, 800), pygame.RESIZABLE)
pygame.display.set_caption("Python Invaders")

menu = pygame_menu.Menu(
    "Python Invaders", 400, 300, theme=pygame_menu.themes.THEME_BLUE
)

menu.add.text_input("Name :", default="Jane Doe")
menu.add.button("Play", lambda _=None: gameloop.start_game(screen))
menu.add.button("Skilltree", skilltree.skilltree_menu(screen))
menu.add.button("Quit", pygame_menu.events.EXIT)

running = True
is_paused = False
while running:
    menu.mainloop(screen)

    pygame.display.flip()


#music.stop_theme()
#music.unload_theme()
fonts.quit_font()
pygame.quit()
sys.exit()
