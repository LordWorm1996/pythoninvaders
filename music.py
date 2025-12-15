import pygame

main_theme = "game_assets/sound_files/test_music.mp3"


def init_music():
    pygame.mixer.init()
    pygame.mixer.music.load(main_theme)
    pygame.mixer.music.set_volume(0.5)


def play_theme():
    pygame.mixer.music.play(-1, 0.0)


def pause_theme():
    pygame.mixer.music.pause()


def unpause_theme():
    pygame.mixer.music.unpause()


def stop_theme():
    pygame.mixer.music.stop()


def unload_theme():
    pygame.mixer.music.unload()
