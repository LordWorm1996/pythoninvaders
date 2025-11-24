import pygame

from background import ScrollingBackground
from classes.combat_manager import CombatManager
from classes.debug_menu import DebugMenu
from classes.enemy_manager import EnemyManager
from classes.player import Player
from classes.ui import UI
from classes.wave_spawner import WaveSpawner
from skilltree import add_skill_points

add_skill_points(3)


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

    combat_manager = CombatManager(
        player, player_bullets, enemies, enemy_bullets, enemy_drops
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

        screen.fill((0, 0, 0))
        bg.draw(screen)
        all_sprites.draw(screen)
        player_bullets.draw(screen)
        enemy_bullets.draw(screen)
        enemies.draw(screen)
        enemy_drops.draw(screen)

        ui.draw_health_bar(player)
        ui.draw_wave_info(wave_spawner.wave_number, len(enemies))
        if not player.is_alive():
            ui.draw_game_over()

        debug_menu.draw()
        pygame.display.flip()
