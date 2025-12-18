import random

import pygame

import variables
from classes.attack_patterns import (
    laser_pattern,
    spread_pattern,
    straight_pattern,
    thunder_pattern,
)
from classes.boss_drop import BossDrop
from classes.bullet import Bullet, LaserBeam, ThunderBullet
from classes.enemy_drop import EnemyDrop
from classes.entity import Entity
from classes.ultimate_abilities import COLOR_TO_ULTIMATE_ID
from classes.weapon import Weapon

COLOR_TO_WEAPON_ID = {
    "yellow": "Spread",
    "blue": "Laser",
    "green": "Grenade Launcher",
    "purple": "Thunder Lance",
}


class Boss(Entity):
    def __init__(
        self,
        x,
        y,
        color="red",
        image=None,
        speed=0,
        health=1,
        damage=1,
        attack_pattern=None,
        attack_chance=0.01,
        bullets_group=None,
        aim_mode="player",
    ):
        self.color = (color or "red").lower()
        self.is_enemy = True

        if image is None:
            sprite_path = None
            if hasattr(variables, "boss_sprite_paths"):
                sprite_path = variables.boss_sprite_paths.get(self.color)
            if sprite_path:
                try:
                    image = pygame.image.load(sprite_path).convert_alpha()
                except Exception:
                    image = None
            if image is None:
                image = pygame.Surface((40, 40))
                image.fill((255, 255, 0))
                pygame.draw.polygon(image, (200, 0, 0), [(20, 40), (0, 0), (40, 0)])

        # CHATGPT
        scale_factor = getattr(variables, "boss_scale", 2.5)
        if scale_factor and scale_factor != 1.0:
            width = int(image.get_width() * scale_factor)
            height = int(image.get_height() * scale_factor)
            if width > 0 and height > 0:
                image = pygame.transform.scale(image, (width, height))

        super().__init__(x, y, image)

        hit_scale = getattr(variables, "boss_hitbox_scale", 0.7)
        if hit_scale and 0 < hit_scale < 1.0:
            cx, cy = self.rect.center
            new_w = max(1, int(self.rect.width * hit_scale))
            new_h = max(1, int(self.rect.height * hit_scale))
            self.rect.width = new_w
            self.rect.height = new_h
            self.rect.center = (cx, cy)

        self.base_image = self.image.copy()

        self.max_health = health * variables.boss_multiplier
        self.health = health * variables.boss_multiplier
        self.damage = damage
        self.speed = speed
        self.vel = pygame.math.Vector2(0, 0)

        self.bullets_group = bullets_group
        self.attack_chance = attack_chance
        self.aim_mode = aim_mode or "player"

        self.shot_count = 1
        self.max_shots = 4
        self.multi_shot_enabled = True

        self.status_effects = []

        self.rainbow_profiles = []
        self.attack_pattern, bullet_class, bullet_args, cooldown = (
            self._configure_by_color(damage)
        )

        self.weapon = Weapon(
            bullet_class=bullet_class,
            bullet_args=bullet_args,
            cooldown=cooldown,
            pattern=self.attack_pattern,
        )

    def _configure_by_color(self, damage):
        color = self.color
        pattern = straight_pattern
        bullet_class = Bullet
        bullet_args = {"speed": 300, "damage": damage}
        cooldown = 1.0

        if color == "red":
            self.shot_count = 1
            self.max_shots = 1
        elif color == "orange":
            self.shot_count = 3
            self.max_shots = 3
        elif color == "yellow":
            pattern = spread_pattern
            self.shot_count = 1
            self.max_shots = 1
        elif color == "blue":
            pattern = spread_pattern
            self.shot_count = 2
            self.max_shots = 2
        elif color == "green":
            pattern = laser_pattern
            bullet_class = LaserBeam
            bullet_args = {
                "damage": damage,
                "duration": 3000,
                "length": 500,
                "width": 12,
                "color": (0, 200, 255),
            }
            self.shot_count = 2
            self.max_shots = 2
            cooldown = 3.0
        elif color == "purple":
            pattern = thunder_pattern
            bullet_class = ThunderBullet
            bullet_args = {
                "speed": 460,
                "damage": damage,
                "max_chain_targets": 2,
                "chain_radius": 180,
                "chain_damage_multiplier": 0.75,
                "chain_decay": 0.8,
                "status_effects": [
                    {"type": "inverted_controls", "min_ms": 800, "max_ms": 1500},
                    {"type": "stun", "min_ms": 600, "max_ms": 1000},
                    {"type": "shoot_lock", "min_ms": 900, "max_ms": 1500},
                ],
            }
            self.shot_count = 3
            self.max_shots = 3
            cooldown = 1.4
        elif (
            color == "rainbow"
        ):  # rainbow can use all weapons and randomly choose each attack
            self.shot_count = 4
            self.max_shots = 4

            self.rainbow_profiles = [
                {
                    "pattern": straight_pattern,
                    "bullet_class": Bullet,
                    "bullet_args": {"speed": 320, "damage": damage},
                    "cooldown": 1.0,
                },
                {
                    "pattern": straight_pattern,
                    "bullet_class": Bullet,
                    "bullet_args": {"speed": 320, "damage": damage},
                    "cooldown": 1.0,
                },
                {
                    "pattern": spread_pattern,
                    "bullet_class": Bullet,
                    "bullet_args": {"speed": 300, "damage": damage},
                    "cooldown": 1.0,
                },
                {
                    "pattern": spread_pattern,
                    "bullet_class": Bullet,
                    "bullet_args": {"speed": 300, "damage": damage},
                    "cooldown": 1.0,
                },
                {
                    "pattern": laser_pattern,
                    "bullet_class": LaserBeam,
                    "bullet_args": {
                        "damage": damage,
                        "duration": 2500,
                        "length": 450,
                        "width": 12,
                        "color": (0, 200, 255),
                    },
                    "cooldown": 3.0,
                },
                {
                    "pattern": thunder_pattern,
                    "bullet_class": ThunderBullet,
                    "bullet_args": {
                        "speed": 460,
                        "damage": damage,
                        "max_chain_targets": 2,
                        "chain_radius": 180,
                        "chain_damage_multiplier": 0.75,
                        "chain_decay": 0.8,
                        "status_effects": [
                            {
                                "type": "inverted_controls",
                                "min_ms": 800,
                                "max_ms": 1500,
                            },
                            {
                                "type": "stun",
                                "min_ms": 600,
                                "max_ms": 1000,
                            },
                            {
                                "type": "shoot_lock",
                                "min_ms": 900,
                                "max_ms": 1500,
                            },
                        ],
                    },
                    "cooldown": 1.4,
                },
            ]

        return pattern, bullet_class, bullet_args, cooldown

    def set_shot_count(self, count):
        self.shot_count = max(1, min(self.max_shots, int(count)))

    def get_fire_positions(self):
        if self.aim_mode == "down":
            base_y = self.rect.bottom
        else:
            base_y = self.rect.centery
        default_position = (self.rect.centerx, base_y)

        if not getattr(self, "multi_shot_enabled", True):
            return [default_position]

        if self.shot_count <= 1:
            return [default_position]

        margin = min(30, int(self.rect.width * 0.18))
        usable_width = max(1, self.rect.width - 2 * margin)
        spacing = usable_width / (self.shot_count - 1)

        return [
            (self.rect.left + margin + spacing * i, base_y)
            for i in range(self.shot_count)
        ]

    def take_damage(self, damage_amount):
        if self.health <= 0:
            return False, None

        self.health -= damage_amount
        if self.health <= 0:
            x, y = self.rect.center
            self.kill()

            drops = pygame.sprite.Group()

            drops.add(EnemyDrop(x - 20, y, "health_pack"))
            drops.add(EnemyDrop(x + 20, y, "health_pack"))

            drops.add(EnemyDrop(x, y + 20, "ultimate_pack"))

            ability_id = COLOR_TO_ULTIMATE_ID.get(self.color)
            if ability_id:
                ability_drop = BossDrop(x, y - 20, "ultimate_ability")
                ability_drop.ability_id = ability_id
                drops.add(ability_drop)

            weapon_id = COLOR_TO_WEAPON_ID.get(self.color)
            if weapon_id:
                weapon_drop = BossDrop(x + 40, y - 20, "boss_weapon")
                weapon_drop.weapon_id = weapon_id
                drops.add(weapon_drop)

            return True, drops if len(drops) else None
        return False, None

    def attack(self, target_pos):
        if self.bullets_group is None:
            return

        if self.aim_mode == "down":
            direction = pygame.math.Vector2(0, 1)
        else:
            if target_pos is None:
                return
            direction = pygame.math.Vector2(target_pos) - pygame.math.Vector2(
                self.rect.center
            )
            if direction.length() == 0:
                return
            direction = direction.normalize()

        if self.color == "rainbow" and self.rainbow_profiles:
            profile = random.choice(self.rainbow_profiles)
            self.weapon.bullet_class = profile["bullet_class"]
            self.weapon.bullet_args = profile["bullet_args"]
            self.weapon.cooldown = profile["cooldown"]
            self.attack_pattern = profile["pattern"]
            self.weapon.pattern = self.attack_pattern

        self.weapon.fire(self.rect.center, direction, self.bullets_group, owner=self)

    def update(self, dt, screen_size=None, target_pos=None):
        self.image = self.base_image.copy()
        self.draw_status_overlay()

        if self.bullets_group is not None and random.random() < self.attack_chance:
            self.attack(target_pos)

        if screen_size:
            width, height = screen_size
            if (
                self.rect.right < 0
                or self.rect.left > width
                or self.rect.bottom < 0
                or self.rect.top > height
            ):
                self.kill()

    def apply_status(self, status_type, duration_ms, tick_damage=0, tick_interval_ms=0):
        now = pygame.time.get_ticks()
        expires_at = now + int(duration_ms)
        tick_damage = int(tick_damage)
        tick_interval_ms = int(tick_interval_ms)
        next_tick_at = now + tick_interval_ms if tick_interval_ms > 0 else 0

        self.status_effects = [
            effect for effect in self.status_effects if effect["type"] != status_type
        ]
        self.status_effects.append(
            {
                "type": status_type,
                "expires_at": expires_at,
                "tick_damage": tick_damage,
                "tick_interval_ms": tick_interval_ms,
                "next_tick_at": next_tick_at,
            }
        )

    def has_status(self, status_type):
        now = pygame.time.get_ticks()
        return any(
            effect["type"] == status_type and effect["expires_at"] > now
            for effect in self.status_effects
        )

    def draw_status_overlay(self):
        if not self.status_effects:
            return

        overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)

        if self.has_status("fire"):
            overlay.fill((255, 140, 0, 120))
        elif self.has_status("poison"):
            overlay.fill((160, 32, 240, 120))
        elif self.has_status("ice"):
            rect = overlay.get_rect()
            overlay.fill((64, 224, 208, 80))
            pygame.draw.rect(
                overlay,
                (64, 224, 208, 180),
                rect,
                width=2,
            )
        else:
            return

        self.image.blit(overlay, (0, 0))
