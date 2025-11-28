import pygame

import variables
from classes.attack_patterns import (
    laser_pattern,
    spread_pattern,
    straight_pattern,
    thunder_pattern,
)
from classes.boss import Boss
from classes.wave_loader import WaveLoader


class WaveSpawner:
    def __init__(self, screen_width, screen_height, xml_path="waves.xml"):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.xml_path = xml_path

        WaveLoader.register_pattern("straight", straight_pattern)
        WaveLoader.register_pattern("spread", spread_pattern)
        WaveLoader.register_pattern("laser", laser_pattern)
        WaveLoader.register_pattern("laser_pattern", laser_pattern)
        WaveLoader.register_pattern("thunder", thunder_pattern)
        WaveLoader.register_pattern("thunder_pattern", thunder_pattern)

        try:
            self.waves = WaveLoader.load_waves(xml_path)
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
        if hasattr(self, "bosses_spawned"):
            delattr(self, "bosses_spawned")
        print(f"Wave {self.current_wave_data['number']} started!")

    def spawn_wave_bosses(self, boss_group, boss_bullets_group):
        if not self.current_wave_data:
            return

        bosses_spawned = 0

        if "grid" in self.current_wave_data:
            grid = self.current_wave_data["grid"]
            bosses_spawned += self.spawn_grid_bosses(
                grid, boss_group, boss_bullets_group
            )

        for boss_data in self.current_wave_data["bosses"]:
            boss = self.create_boss_from_data(boss_data, boss_bullets_group)
            if boss:
                boss_group.add(boss)
                bosses_spawned += 1

        print(
            f"Spawned {bosses_spawned} bosses for wave {self.current_wave_data['number']}"
        )

    def spawn_grid_bosses(self, grid_data, boss_group, boss_bullets_group):
        rows = grid_data["rows"]
        cols = grid_data["cols"]
        start_x = grid_data["start_x"]
        start_y = grid_data["start_y"]
        spacing_x = grid_data["spacing_x"]
        spacing_y = grid_data["spacing_y"]

        default_health = grid_data["default_health"]
        default_pattern = grid_data["default_attack_pattern"]
        default_damage = grid_data["default_damage"]

        grid_bosses = grid_data.get("bosses", [])
        grid_boss_dict = {
            (e.get("row", -1), e.get("col", -1)): e
            for e in grid_bosses
            if "row" in e and "col" in e
        }

        bosses_spawned = 0

        for row in range(rows):
            for col in range(cols):
                x = start_x + col * spacing_x
                y = start_y + row * spacing_y

                if (row, col) in grid_boss_dict:
                    boss_data = dict(grid_boss_dict[(row, col)])
                    boss_data.pop("row", None)
                    boss_data.pop("col", None)
                else:
                    boss_data = {
                        "health": default_health,
                        "attack_pattern": default_pattern,
                        "damage": default_damage,
                        "speed": 0,
                        "aim": grid_data.get("default_aim", "player"),
                    }
                boss_data["x"] = x
                boss_data["y"] = y
                boss_data.setdefault("aim", grid_data.get("default_aim", "player"))

                boss = self.create_boss_from_data(boss_data, boss_bullets_group)
                if boss:
                    boss_group.add(boss)
                    bosses_spawned += 1

        return bosses_spawned

    def create_boss_from_data(self, boss_data, boss_bullets_group):
        pattern_name = boss_data.get("attack_pattern", "straight")
        attack_pattern = WaveLoader.get_pattern(pattern_name)

        if attack_pattern is None:
            print(
                f"Warning: Attack pattern '{pattern_name}' not found. Using 'straight'."
            )
            attack_pattern = WaveLoader.get_pattern("straight")

        base_attack_chance = 0.01
        attack_chance = base_attack_chance * variables.difficulty

        image = None
        if "image" in boss_data:
            try:
                image = pygame.image.load(boss_data["image"]).convert_alpha()
            except:
                print(f"Warning: Could not load image {boss_data['image']}")

        boss = Boss(
            x=boss_data["x"],
            y=boss_data["y"],
            image=image,
            speed=boss_data.get("speed", 0),
            health=boss_data.get("health", 1),
            damage=boss_data.get("damage", 1),
            attack_pattern=attack_pattern,
            attack_chance=attack_chance,
            bullets_group=boss_bullets_group,
            aim_mode=boss_data.get("aim", "player"),
        )

        return boss

    def update(self, dt, boss_group, boss_bullets_group=None, attack_pattern=None):
        if not self.wave_started:
            return

        if not hasattr(self, "bosses_spawned"):
            self.spawn_wave_bosses(boss_group, boss_bullets_group)
            self.bosses_spawned = True

        if (
            hasattr(self, "bosses_spawned")
            and self.bosses_spawned
            and len(boss_group) == 0
        ):
            wave_number = (
                self.current_wave_data["number"] if self.current_wave_data else 0
            )
            self.wave_started = False
            self.bosses_spawned = False
            print(f"Wave {wave_number} complete!")
            self.start_wave()

    def is_wave_active(self):
        return self.wave_started

    @property
    def wave_number(self):
        if self.current_wave_data:
            return self.current_wave_data["number"]
        return 0

    def spawn_boss_manual(
        self,
        x,
        y,
        health=1,
        attack_pattern="straight",
        damage=1,
        speed=0,
        aim_mode="player",
        boss_bullets_group=None,
    ):
        pattern = WaveLoader.get_pattern(attack_pattern)
        if pattern is None:
            pattern = WaveLoader.get_pattern("straight")

        base_attack_chance = 0.01
        attack_chance = base_attack_chance * variables.difficulty

        boss_data = {
            "x": x,
            "y": y,
            "health": health,
            "damage": damage,
            "attack_pattern": attack_pattern,
            "speed": speed,
            "aim": aim_mode,
        }

        return self.create_boss_from_data(boss_data, boss_bullets_group)
