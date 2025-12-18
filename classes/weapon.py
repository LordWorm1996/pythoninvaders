import pygame
from classes.bullet import Bullet


class Weapon:
    def __init__(self, bullet_class=Bullet, bullet_args=None, cooldown=0.25, pattern=None):
        self.bullet_class = bullet_class
        self.bullet_args = bullet_args or {}
        self.cooldown = cooldown
        self.last_shot = -cooldown * 1000
        self.pattern = pattern 

    def fire(self, pos, direction, bullets_group, owner=None):
        try:
            now = pygame.time.get_ticks()
            time_since_last_shot = now - self.last_shot
            cooldown_ms = self.cooldown * 1000

            if owner is not None and hasattr(owner, "has_status"):
                if owner.has_status("frenzy"):
                    cooldown_ms *= 0.4
            
            if time_since_last_shot >= cooldown_ms:
                if self.pattern is None:
                    return []
                bullets = self.pattern(pos, direction, self.bullet_class, self.bullet_args, owner)
                for b in bullets:
                    bullets_group.add(b)
                self.last_shot = now
                return bullets
            return []
        except Exception as e:
            print("Weapon.fire ERROR:", e)
            import traceback
            traceback.print_exc()
            return []


