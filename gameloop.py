import random

import pygame

from background import ScrollingBackground
from classes.boss import Boss
from classes.combat_manager import CombatManager
from classes.debug_menu import DebugMenu
from classes.enemy_manager import EnemyManager
from classes.player import Player
from classes.skill_drop import SkillDrop
from classes.ui import UI
from classes.wave_spawner import WaveSpawner
import variables


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
        max_health=100,
    )
    all_sprites = pygame.sprite.Group(player)

    score = [0] # score is a list because we need to pass it to the combat manager (CHATGPT)
    combat_manager = CombatManager(
        player, player_bullets, enemies, enemy_bullets, enemy_drops, score
    )
    enemy_manager = EnemyManager(enemies, enemy_bullets)
    ui = UI(screen)
    debug_menu = DebugMenu(screen)
    wave_spawner = WaveSpawner(
        screen.get_width(), screen.get_height(), xml_path="waves.xml"
    )

    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            debug_menu.handle_event(event, wave_spawner, enemies, enemy_bullets)

        bg.update(dt)
        all_sprites.update(dt, screen.get_size())
        player_bullets.update(dt)
        enemy_bullets.update(dt)
        enemy_drops.update(dt, screen.get_size())

        wave_spawner.update(dt, enemies, enemy_bullets_group=enemy_bullets)
        enemy_manager.update(dt, screen.get_size(), player.rect.center)
        combat_manager.update()

        #temp 
        if random.random() < variables.skill_drop_sky_chance:
            x = random.randint(0, screen.get_width())
            y = -SkillDrop.SIZE_PX // 2 + 1             # Spawn just at/above the top edge so the drop is not immediately killed (CHATGPT)
            enemy_drops.add(SkillDrop(x, y))
        #temp
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

        #temp 
        bosses = [e for e in enemies if isinstance(e, Boss)]
        ui.draw_boss_health_bars(bosses)
        if not player.is_alive():
            ui.draw_game_over()
        #temp
        debug_menu.draw()
        pygame.display.flip()
