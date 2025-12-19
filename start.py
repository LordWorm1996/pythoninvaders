import pygame

import fonts
import music
import save
import variables
from classes.skilltree import (
    add_coins,
    load_skill,
)


def start_game() -> str:
    pygame.init()
    music.init_music()
    fonts.init_font()
    game_data = save.load_game()

    variables.difficulty = game_data.get("difficulty", 0.5)
    add_coins(game_data.get("coins", 0))
    variables.score = game_data.get("high_score", 0)
    name = game_data.get("name", "Jane Doe")
    variables.gem_inv = game_data.get("gems", 0)
    load_skill("health_boost", game_data.get("skilltree_hb", 0))
    load_skill("rapid_fire", game_data.get("skilltree_rf", 0))
    load_skill("double_shot", game_data.get("skilltree_ds", 0))
    load_skill("shield", game_data.get("skilltree_sh", 0))
    load_skill("super_shot", game_data.get("skilltree_su", 0))

    music.play_theme()

    return name
