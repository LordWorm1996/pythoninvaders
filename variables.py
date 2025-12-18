import random

# import pygame


# Base Stats
health = 1
damage = 1
speed = 1
health_regen = 0
ultimate_regen = 1
ultimate_full = 100
health_on_kill = 0
ult_on_kill = 2

# Multipliers
random_multiplier = random.randint(1, 10)
elite_enemy_multiplier = 10
boss_multiplier = 1
final_boss_multiplier = 1

# Packs
health_pack = 1
big_health_pack = 2
boss_health_pack = 10
ultimate_pack = 10
big_ultimate_pack = 20
boss_ultimate_pack = 100
coin = 1

gem = 0

# Boosters
health_booster = 1
health_regen_booster = 1
ultimate_regen_booster = 1
ultimate_decreaser = -1

# Kill Effects
health_on_kill = 1
ult_on_kill = 1

# Difficulty multiplier for enemy attack chance (0.0 to 1.0)
# Higher values = enemies attack more frequently
difficulty = 0.5  # Default: 50% of base attack chance

if difficulty == 0.5:
    no_drop_chance = 40
    health_chance = 30
    big_health_chance = 10
    coin_chance = 20
    gem_chance = 5
    skill_chance = 5
elif difficulty > 0.5:
    no_drop_chance = 50
    health_chance = 25
    big_health_chance = 10
    coin_chance = 15
    gem_chance = 5
    skill_chance = 5
else:
    no_drop_chance = 30
    health_chance = 30
    big_health_chance = 15
    coin_chance = 25
    gem_chance = 10
    skill_chance = 5


skill_drop_sky_chance = 0.001

poison_duration_ms = 4000
poison_tick_interval_ms = 500
poison_tick_damage = 1

fire_duration_ms = 3500
fire_tick_interval_ms = 400
fire_tick_damage = 2

ice_duration_ms = 3000

enemy_sprite_paths = {
    "red": "game_assets/enemies/crab_red1.png",
    "orange": "game_assets/enemies/crab_orange1.png",
    "yellow": "game_assets/enemies/crab_yellow1.png",
    "blue": "game_assets/enemies/crab_blue1.png",
    "green": "game_assets/enemies/crab_green1.png",
    "purple": "game_assets/enemies/crab_purple1.png",
    "rainbow": "game_assets/enemies/crab_rainbow1.png",
}

boss_sprite_paths = enemy_sprite_paths

#make them bigger
enemy_scale = 2.0
boss_scale = 2.5


enemy_hitbox_scale = 0.7
boss_hitbox_scale = 0.7
