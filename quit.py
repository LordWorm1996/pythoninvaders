import sys

import pygame

import fonts
import music
import save
import variables
from classes.skilltree import (
    get_coins,
    get_skill_level,
)

game_data = save.load_game()
old_high_score = game_data.get("high_score", 0)
current_score = variables.get_score()[0]
new_high_score = max(old_high_score, current_score)


def quit_game():
    save.save_game(
        {
            "difficulty": variables.get_difficulty(),
            "coins": get_coins(),
            "high_score": new_high_score,
            "gems": variables.get_gem(),
            "skilltree_hb": get_skill_level("health_boost"),
            "skilltree_rf": get_skill_level("rapid_fire"),
            "skilltree_ds": get_skill_level("double_shot"),
            "skilltree_sh": get_skill_level("shield"),
            "skilltree_su": get_skill_level("super_shot"),
        }
    )
    music.stop_theme()
    music.unload_theme()
    fonts.quit_font()
    pygame.quit()
    sys.exit()
