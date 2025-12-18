import pygame

import variables
from classes.attack_patterns import (
    laser_pattern,
    spread_pattern,
    straight_pattern,
    thunder_pattern,
)
from classes.boss import Boss
from classes.enemy import Enemy
from classes.wave_loader import BossLoader


class WaveSpawner:
    def __init__(self, screen_width, screen_height, xml_path="waves.xml"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.xml_path = xml_path

        BossLoader.register_pattern("straight", straight_pattern)
        BossLoader.register_pattern("spread", spread_pattern)
        BossLoader.register_pattern("laser", laser_pattern)
        BossLoader.register_pattern("laser_pattern", laser_pattern)
        BossLoader.register_pattern("thunder", thunder_pattern)
        BossLoader.register_pattern("thunder_pattern", thunder_pattern)

        try:
            self.waves = BossLoader.load_waves(xml_path)
            print(f"Loaded {len(self.waves)} waves from {xml_path}")
        except FileNotFoundError:
            print(f"Warning: {xml_path} not found. Using default waves.")
            self.waves = []

        self.current_wave_index = -1
        self.wave_started = False
        self.current_wave_data = None

    def start_wave(self, wave_number=None):
        if wave_number is not None:
            for i, wave in enumerate(self.waves):
                if wave["number"] == wave_number:
                    self.current_wave_index = i
                    break
            else:
                print(f"Wave {wave_number} not found in XML")
                return
        else:
            self.current_wave_index += 1

        if self.current_wave_index >= len(self.waves):
            print("All waves complete!")
            self.wave_started = False
            return

        self.current_wave_data = self.waves[self.current_wave_index]
        self.wave_started = True
        if hasattr(self, "enemies_spawned"):
            delattr(self, "enemies_spawned")
        print(f"Wave {self.current_wave_data['number']} started!")

    def spawn_wave_enemies(self, enemy_group, enemy_bullets_group):
        if not self.current_wave_data:
            return

        enemies_spawned = 0
        bosses_spawned = 0

        if "grid" in self.current_wave_data:
            grid = self.current_wave_data["grid"]
            enemies_spawned += self.spawn_grid_enemies(
                grid, enemy_group, enemy_bullets_group
            )

        for enemy_data in self.current_wave_data["enemies"]:
            enemy = self.create_enemy_from_data(enemy_data, enemy_bullets_group)
            if enemy:
                enemy_group.add(enemy)
                enemies_spawned += 1

        for boss_data in self.current_wave_data.get("bosses", []):
            boss = self.create_boss_from_data(boss_data, enemy_bullets_group)
            if boss:
                enemy_group.add(boss)
                bosses_spawned += 1

        print(
            f"Spawned {enemies_spawned} enemies and {bosses_spawned} bosses for wave {self.current_wave_data['number']}"
        )

    def spawn_grid_enemies(self, grid_data, enemy_group, enemy_bullets_group):
        rows = grid_data["rows"]
        cols = grid_data["cols"]
        start_x = grid_data["start_x"]
        start_y = grid_data["start_y"]
        spacing_x = grid_data["spacing_x"]
        spacing_y = grid_data["spacing_y"]

        default_health = grid_data["default_health"]
        default_pattern = grid_data["default_attack_pattern"]
        default_damage = grid_data["default_damage"]

        grid_enemies = grid_data.get("enemies", [])
        grid_enemy_dict = {
            (e.get("row", -1), e.get("col", -1)): e
            for e in grid_enemies
            if "row" in e and "col" in e
        }

        enemies_spawned = 0

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y

                if (row, col) in grid_enemy_dict:
                    enemy_data = dict(grid_enemy_dict[(row, col)])
                    enemy_data.pop("row", None)
                    enemy_data.pop("col", None)
                else:
                    enemy_data = {
                        "health": default_health,
                        "attack_pattern": default_pattern,
                        "damage": default_damage,
                        "speed": 0,
                        "aim": grid_data.get("default_aim", "player"),
                    }
                enemy_data["x"] = x
                enemy_data["y"] = y
                enemy_data.setdefault("aim", grid_data.get("default_aim", "player"))

                enemy = self.create_enemy_from_data(enemy_data, enemy_bullets_group)
                if enemy:
                    enemy_group.add(enemy)
                    enemies_spawned += 1

        return enemies_spawned

    def create_enemy_from_data(self, enemy_data, enemy_bullets_group):
        pattern_name = enemy_data.get("attack_pattern", "straight")
        attack_pattern = BossLoader.get_pattern(pattern_name)

        if attack_pattern is None:
            print(
                f"Warning: Attack pattern '{pattern_name}' not found. Using 'straight'."
            )
            attack_pattern = BossLoader.get_pattern("straight")

        base_attack_chance = 0.01
        attack_chance = base_attack_chance * variables.difficulty

        image = None
        if "image" in enemy_data:
            try:
                image = pygame.image.load(enemy_data["image"]).convert_alpha()
            except Exception:
                print(f"Warning: Could not load image {enemy_data['image']}")

        enemy = Enemy(
            x=enemy_data["x"],
            y=enemy_data["y"],
            image=image,
            speed=enemy_data.get("speed", 0),
            health=enemy_data.get("health", 1),
            damage=enemy_data.get("damage", 1),
            attack_pattern=attack_pattern,
            attack_chance=attack_chance,
            bullets_group=enemy_bullets_group,
            aim_mode=enemy_data.get("aim", "player"),
            color=enemy_data.get("color"),
        )

        return enemy

    def create_boss_from_data(self, boss_data, enemy_bullets_group):
        base_attack_chance = 0.01
        attack_chance = base_attack_chance * variables.difficulty

        boss = Boss(
            x=boss_data["x"],
            y=boss_data["y"],
            color=boss_data.get("color", "red"),
            speed=boss_data.get("speed", 0),
            health=boss_data.get("health", 1),
            damage=boss_data.get("damage", 1),
            attack_pattern=None,
            attack_chance=attack_chance,
            bullets_group=enemy_bullets_group,
            aim_mode=boss_data.get("aim", "player"),
        )

        return boss

    def update(self, dt, enemy_group, enemy_bullets_group=None, attack_pattern=None):
        if not self.wave_started:
            return

        if not hasattr(self, "enemies_spawned"):
            self.spawn_wave_enemies(enemy_group, enemy_bullets_group)
            self.enemies_spawned = True

        if (
            hasattr(self, "enemies_spawned")
            and self.enemies_spawned
            and len(enemy_group) == 0
        ):
            wave_number = (
                self.current_wave_data["number"] if self.current_wave_data else 0
            )
            self.wave_started = False
            self.enemies_spawned = False
            print(f"Wave {wave_number} complete!")
            self.start_wave()

    def is_wave_active(self):
        return self.wave_started

    @property
    def wave_number(self):
        if self.current_wave_data:
            return self.current_wave_data["number"]
        return 0

    def spawn_enemy_manual(
        self,
        x,
        y,
        health=1,
        attack_pattern="straight",
        damage=1,
        speed=0,
        aim_mode="player",
        enemy_bullets_group=None,
    ):
        pattern = BossLoader.get_pattern(attack_pattern)
        if pattern is None:
            pattern = BossLoader.get_pattern("straight")

        base_attack_chance = 0.01
        attack_chance = base_attack_chance * variables.difficulty

        enemy_data = {
            "x": x,
            "y": y,
            "health": health,
            "damage": damage,
            "attack_pattern": attack_pattern,
            "speed": speed,
            "aim": aim_mode,
        }

        return self.create_enemy_from_data(enemy_data, enemy_bullets_group)
