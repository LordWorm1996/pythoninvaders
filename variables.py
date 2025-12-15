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
boss_multiplier = 100
final_boss_multiplier = 500

# Packs
health_pack = 1
big_health_pack = 2
boss_health_pack = 10
ultimate_pack = 10
big_ultimate_pack = 20
boss_ultimate_pack = 100

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
    no_drop_chance = 50
    health_chance = 40
    big_health_chance = 10
elif difficulty > 0.5:
    no_drop_chance = 60
    health_chance = 30
    big_health_chance = 10
else:
    no_drop_chance = 40
    health_chance = 40
    big_health_chance = 20
