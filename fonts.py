import pygame


def init_font():
    pygame.font.init()


def quit_font():
    pygame.font.quit()


def spawn_font(font, size):
    font = pygame.font.SysFont(font, size)
    return font
