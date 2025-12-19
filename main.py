import pygame
import pygame_menu

import gameloop
import quit
import start
import variables
from classes.skilltree import skilltree_menu

name = start.start_game()

screen = pygame.display.set_mode((1000, 800), pygame.RESIZABLE)
pygame.display.set_caption("Python Invaders")

menu = pygame_menu.Menu(
    "Python Invaders", 500, 500, theme=pygame_menu.themes.THEME_BLUE
)

menu.add.label(f"High Score: {variables.get_score()}")
menu.add.label(f"Gems (Revives): {variables.get_gem()}")
username = menu.add.text_input("Name :", default=name)
menu.add.button("Play", lambda _=None: gameloop.start_game(screen))
menu.add.range_slider(
    "Select Difficulty",
    variables.get_difficulty(),
    (0.1, 1.0),
    1,
    rangeslider_id="range_slider",
    value_format=lambda x: f"{x:.1f}",
    onchange=lambda x: variables.change_difficulty(x),
)
menu.add.button("Skilltree", skilltree_menu(screen))
menu.add.button("Quit", quit.quit_game, username)

running = True
is_paused = False
while running:
    menu.mainloop(screen)

    pygame.display.flip()
