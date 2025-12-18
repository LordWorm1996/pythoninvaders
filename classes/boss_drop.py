import pygame

import variables


class BossDrop(pygame.sprite.Sprite):
    DROP_TYPES = {
        "boss_health_pack": ((0, 200, 0), 20, variables.boss_health_pack),
        "boss_ultimate_pack": ((0, 120, 255), 20, variables.boss_ultimate_pack),
        "ultimate_ability": ((180, 80, 255), 20, 0),
        "boss_weapon": ((255, 255, 255), 20, 0),
    }

    def __init__(self, x, y, drop_type="boss_health_pack"):
        super().__init__()
        color, size, value = self.DROP_TYPES.get(
            drop_type, self.DROP_TYPES["boss_health_pack"]
        )
        self.drop_type = (
            drop_type if drop_type in self.DROP_TYPES else "boss_health_pack"
        )
        self.value = value

        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        pygame.draw.circle(
            self.image, (255, 255, 255), (size // 2, size // 2), size // 2, 2
        )
        self.rect = self.image.get_rect(center=(x, y))

        self.vel = pygame.math.Vector2(0, 100)
        self.lifetime = 10000
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt, screen_size=None):
        self.rect.y += self.vel.y * dt

        if screen_size:
            width, height = screen_size
            if (
                self.rect.right < 0
                or self.rect.left > width
                or self.rect.bottom < 0
                or self.rect.top > height
            ):
                self.kill()

        if pygame.time.get_ticks() - self.spawn_time >= self.lifetime:
            self.kill()
