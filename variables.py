import pygame
import random

health = 1
damage = 1
speed = 1
health_regen = 0
ultimate_regen = 1
ultimate_full = 100
health_on_kill = 0
ult_on_kill = 2

random_multiplier = random.randint(1, 10)
elite_enemy_multiplier = 10
boss_multiplier = 100
final_boss_multiplier = 500

health_pack = 1
big_health_pack = 2
ultimate_pack = 10
big_ultimate_pack = 20
health_booster = 1
health_regen_booster = 1
ultimate_regen_booster = 1
health_on_kill_boost = 1
ult_on_kill_boost = 1
ultimate_boost = -1

# Difficulty multiplier for enemy attack chance (0.0 to 1.0)
# Higher values = enemies attack more frequently
difficulty = 0.2  # Default: 50% of base attack chance