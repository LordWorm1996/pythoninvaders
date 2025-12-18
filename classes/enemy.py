import random
from statistics import variance

import pygame

import variables
from classes.attack_patterns import straight_pattern
from classes.bullet import Bullet, LaserBeam, ThunderBullet
from classes.enemy_drop import EnemyDrop
from classes.entity import Entity
from classes.player import Player
from classes.skill_drop import SkillDrop
from classes.ui import UI
from classes.weapon import Weapon


class Enemy(Entity):
    def __init__(
        self,
        x,
        y,
        image=None,
        speed=0,
        health=1,
        damage=1,
        attack_pattern=None,
        attack_chance=0.01,
        bullets_group=None,
        aim_mode="player",
        color=None,
    ):
        self.color = (color or "red").lower() if color else None

        if image is None:
            sprite_path = None
            if self.color and hasattr(variables, "enemy_sprite_paths"):
                sprite_path = variables.enemy_sprite_paths.get(self.color)
            if sprite_path:
                try:
                    image = pygame.image.load(sprite_path).convert_alpha()
                except Exception:
                    image = None
            if image is None:
                image = pygame.Surface((40, 40))
                image.fill((255, 0, 0))
                pygame.draw.polygon(image, (200, 0, 0), [(20, 40), (0, 0), (40, 0)])

        # CHATGPT
        scale_factor = getattr(variables, "enemy_scale", 2.0)
        if scale_factor and scale_factor != 1.0:
            width = int(image.get_width() * scale_factor)
            height = int(image.get_height() * scale_factor)
            if width > 0 and height > 0:
                image = pygame.transform.scale(image, (width, height))
        # end CHATGPT
        
        super().__init__(x, y, image)


        hit_scale = getattr(variables, "enemy_hitbox_scale", 0.7)
        if hit_scale and 0 < hit_scale < 1.0:
            cx, cy = self.rect.center
            new_w = max(1, int(self.rect.width * hit_scale))
            new_h = max(1, int(self.rect.height * hit_scale))
            self.rect.width = new_w
            self.rect.height = new_h
            self.rect.center = (cx, cy)

        self.base_image = self.image.copy()
        self.max_health = health
        self.health = health
        self.damage = damage
        self.speed = speed
        self.vel = pygame.math.Vector2(0, 0)
        self.status_effects = []

        self.bullets_group = bullets_group
        self.attack_chance = attack_chance
        self.attack_pattern = attack_pattern if attack_pattern else straight_pattern
        self.aim_mode = aim_mode or "player"
        pattern_name = getattr(self.attack_pattern, "__name__", "straight")
        bullet_class = Bullet
        bullet_args = {"speed": 300, "damage": damage}
        cooldown = 1.0
        if pattern_name == "laser_pattern":
            bullet_class = LaserBeam
            bullet_args = {
                "damage": damage,
                "duration": 3000,
                "length": 500,
                "width": 12,
                "color": (0, 200, 255),
            }
            cooldown = 3.0
        elif "thunder" in pattern_name:
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
            cooldown = 1.4

        self.weapon = Weapon(
            bullet_class=bullet_class,
            bullet_args=bullet_args,
            cooldown=cooldown,
            pattern=self.attack_pattern,
        )

    def take_damage(self, damage_amount):
        if self.health <= 0:
            return False, None

        self.health -= damage_amount


        if self.health <= 0:
            drop_key = random.choices(
                population=[
                    "no_drop",
                    "health_pack",
                    "big_health_pack",
                    "coin",
                    "gem",
                    "skill",
                ],
                weights=[
                    variables.no_drop_chance,
                    variables.health_chance,
                    variables.big_health_chance,
                    variables.coin_chance,
                    variables.gem_chance,
                    variables.skill_chance,
                ],
                k=1,
            )[0]

            if getattr(self, "color", None) != "rainbow" and drop_key == "gem":
                drop_key = "no_drop"

            drop = None
            if drop_key == "skill":
                drop = SkillDrop(self.rect.centerx, self.rect.centery)
            elif drop_key != "no_drop":
                drop = EnemyDrop(self.rect.centerx, self.rect.centery, drop_key)
            self.kill()
            return True, drop
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
        self.weapon.fire(self.rect.center, direction, self.bullets_group, owner="enemy")

    def update(self, dt, screen_size=None, target_pos=None):
        self.image = self.base_image.copy()
        self.draw_status_overlay()

        if (
            self.bullets_group is not None
            and not self.has_status("ice")
            and random.random() < self.attack_chance
        ):
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
