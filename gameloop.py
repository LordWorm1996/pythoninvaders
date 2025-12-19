import random

import pygame

import variables
from background import ScrollingBackground
from classes.combat_manager import CombatManager
from classes.enemy_manager import EnemyManager
from classes.player import Player
from classes.skill_drop import SkillDrop
from classes.ui import UI
from classes.wave_spawner import WaveSpawner


def start_game(screen):
    clock = pygame.time.Clock()
    bg = ScrollingBackground(
        "game_assets/backgrounds/3000x3000.png",
        screen.get_size(),
        speed_y=50,
    )

    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    enemy_drops = pygame.sprite.Group()

    player_image = pygame.image.load("game_assets/shipfullhealth.png").convert_alpha()
    player = Player(
        400,
        300,
        player_image,
        bullets_group=player_bullets,
        max_health=10,
    )
    player.apply_skilltree_buffs()
    all_sprites = pygame.sprite.Group(player)

    score = [
        0
    ]  # score is a list because we need to pass it to the combat manager (idea from CHATGPT)

    combat_manager = CombatManager(
        player, player_bullets, enemies, enemy_bullets, enemy_drops, score
    )
    enemy_manager = EnemyManager(enemies, enemy_bullets)
    ui = UI(screen)
    wave_spawner = WaveSpawner(
        screen.get_width(), screen.get_height(), xml_path="waves.xml"
    )

    ui.start_wave_countdown()

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        bg.update(dt)
        all_sprites.update(dt, screen.get_size())
        player_bullets.update(dt)
        enemy_bullets.update(dt)
        enemy_drops.update(dt, screen.get_size())

        if not wave_spawner.is_wave_active() and ui.is_wave_countdown_complete():
            wave_spawner.start_wave()

        wave_spawner.update(dt, enemies, enemy_bullets_group=enemy_bullets)
        enemy_manager.update(dt, screen.get_size(), player.rect.center)
        combat_manager.update()

        # temp
        if random.random() < variables.skill_drop_sky_chance:
            x = random.randint(0, screen.get_width())
            y = (
                -SkillDrop.SIZE_PX // 2 + 1
            )  # Spawn just at/above the top edge so the drop is not immediately killed (CHATGPT)
            enemy_drops.add(SkillDrop(x, y))
        # temp
        screen.fill((0, 0, 0))
        bg.draw(screen)
        all_sprites.draw(screen)
        player_bullets.draw(screen)
        enemy_bullets.draw(screen)
        enemies.draw(screen)
        enemy_drops.draw(screen)

        ui.draw_health_bar(player)
        ui.draw_ultimate_bar(player)
        ui.draw_wave_info(wave_spawner.wave_number, len(enemies))
        ui.draw_score(score[0])
        ui.draw_boss_health_bars_from_enemies(enemies)
        
        if not ui.is_wave_countdown_complete():
            ui.draw_wave_countdown()
        
        if not ui.handle_death_state(player):
            running = False
        
        pygame.display.flip()
