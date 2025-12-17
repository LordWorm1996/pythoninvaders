import random

import pygame

import variables
from classes.attack_patterns import straight_pattern
from classes.boss_drop import BossDrop
from classes.bullet import Bullet, LaserBeam, ThunderBullet
from classes.entity import Entity
from classes.weapon import Weapon


class Boss(Entity):
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
    ):
        if image is None:
            image = pygame.Surface((40, 40))
            image.fill((255, 255, 0))
            pygame.draw.polygon(image, (200, 0, 0), [(20, 40), (0, 0), (40, 0)])

        super().__init__(x, y, image)
        self.max_health = health * variables.boss_multiplier
        self.health = health * variables.boss_multiplier
        self.damage = damage
        self.speed = speed
        self.vel = pygame.math.Vector2(0, 0)

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

        player_ult = Player.ultimate
        player_score = UI.score

        self.health -= damage_amount
        if self.health <= 0:
            x, y = self.rect.center
            BossDrop(x, y, "boss_health_pack")
            BossDrop(x + 30, y, "boss_ultimate_pack")
            BossDrop(x - 30, y, "weapon_types")  # needs implementation
            player_ult += 100
            player_score += 100
            self.kill()
            return True
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
        self.weapon.fire(self.rect.center, direction, self.bullets_group, owner="boss")

    def update(self, dt, screen_size=None, target_pos=None):
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
