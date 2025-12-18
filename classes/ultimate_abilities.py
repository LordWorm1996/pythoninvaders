import math

import pygame

from classes.bullet import Bullet


class UltimateBase:
    """Base class for all player ultimate abilities."""

    id = ""
    display_name = ""

    def __init__(self, cooldown_ms=0):
        self.cooldown_ms = cooldown_ms
        self.last_used_at = -10_000_000

    def is_ready(self, now=None):
        if self.cooldown_ms <= 0:
            return True
        if now is None:
            now = pygame.time.get_ticks()
        return now - self.last_used_at >= self.cooldown_ms

    def can_activate(self, player, context):
        now = context.get("now") if context else None
        return self.is_ready(now)

    def mark_used(self, now=None):
        if now is None:
            now = pygame.time.get_ticks()
        self.last_used_at = now

    def activate(self, player, context):
        raise NotImplementedError


class RadialBurstUltimate(UltimateBase):
    """Fire several rings of bullets in all directions."""

    id = "radial_burst"
    display_name = "Radial Burst"

    def __init__(self):
        # Cooldown is effectively handled by the ultimate meter, but keep a small
        # internal cooldown to prevent accidental double-casts in the same frame.
        super().__init__(cooldown_ms=300) #CHATGPT

    def activate(self, player, context):
        bullets_group = context["bullets_group"]
        now = context.get("now")

        origin = player.rect.center
        directions_per_ring = 24
        base_vector = pygame.math.Vector2(1, 0)
        angle_step = 360 / directions_per_ring

        speeds = (380, 520, 660)
        damage = 2

        bullets = []
        for speed in speeds:
            for i in range(directions_per_ring):
                direction = base_vector.rotate(i * angle_step)
                bullet = Bullet(
                    origin,
                    direction,
                    speed=speed,
                    damage=damage,
                    owner=player,
                )
                bullets_group.add(bullet)
                bullets.append(bullet)

        if bullets:
            player.apply_bullet_modifiers(bullets)

        self.mark_used(now)


class HealUltimate(UltimateBase):

    id = "heal"
    display_name = "Heal"

    def __init__(self):
        super().__init__(cooldown_ms=300)

    def activate(self, player, context):
        now = context.get("now")
        player.heal(player.max_health) # max_health temporary 
        self.mark_used(now)


class DashUltimate(UltimateBase):

    id = "dash"
    display_name = "Dash"

    def __init__(self):
        super().__init__(cooldown_ms=500)

    def activate(self, player, context):
        now = context.get("now")
        move_vector = context.get("move_vector")

        if move_vector is None or move_vector.length_squared() == 0:
            direction = pygame.math.Vector2(0, -1)
        else:
            direction = pygame.math.Vector2(move_vector).normalize()

        player.start_dash(direction)
        self.mark_used(now)


class ShieldUltimate(UltimateBase):

    id = "shield"
    display_name = "Shield"

    def __init__(self):
        super().__init__(cooldown_ms=500)

    def activate(self, player, context):
        now = context.get("now")
        duration_ms = 3000

        player.invincible_until = max(player.invincible_until, now + duration_ms)
        player.apply_status("shield", duration_ms)

        self.mark_used(now)


class FrenzyUltimate(UltimateBase):

    id = "frenzy"
    display_name = "Frenzy"

    def __init__(self):
        super().__init__(cooldown_ms=500)

    def activate(self, player, context):
        now = context.get("now")
        duration_ms = 5000
        player.apply_status("frenzy", duration_ms)
        self.mark_used(now)


ULTIMATE_REGISTRY = {
    RadialBurstUltimate.id: RadialBurstUltimate(),
    HealUltimate.id: HealUltimate(),
    DashUltimate.id: DashUltimate(),
    ShieldUltimate.id: ShieldUltimate(),
    FrenzyUltimate.id: FrenzyUltimate(),
}

DEFAULT_ULTIMATE_ORDER = [
    RadialBurstUltimate.id,
    HealUltimate.id,
    DashUltimate.id,
    ShieldUltimate.id,
    FrenzyUltimate.id,
]

COLOR_TO_ULTIMATE_ID = {
    "red": HealUltimate.id,
    "orange": ShieldUltimate.id,
    "yellow": FrenzyUltimate.id,
    "blue": DashUltimate.id,
}


