import pygame

import variables


class EnemyDrop(pygame.sprite.Sprite):
    DROP_TYPES = {
        "health_pack": ((0, 255, 0), 15, variables.health_pack),
        "big_health_pack": ((0, 200, 0), 20, variables.big_health_pack),
        "ultimate_pack": ((0, 120, 255), 15, variables.ultimate_pack),
        "big_ultimate_pack": ((0, 120, 255), 20, variables.big_ultimate_pack),
        "coin": (None, 15, variables.coin),
        "gem": (None, 20, 1), # should we add a value to the gem in variables ?
    }

    def __new__(cls, x, y, drop_type):
        if drop_type == "no_drop":
            return None
        return super().__new__(cls)

    def __init__(self, x, y, drop_type):
        super().__init__()

        color, size, value = self.DROP_TYPES[drop_type]
        self.drop_type = drop_type
        self.value = value

        if drop_type in ("coin", "gem"):
            self.frames = []
            size_px = 20
            if drop_type == "coin":
                frame_count = 23
                path_pattern = "game_assets/drops/coin/coin{i:03d}.png"
            else:  
                frame_count = 4
                path_pattern = "game_assets/drops/gem/gem{i:03d}.png"

            for i in range(frame_count):
                frame = pygame.image.load(
                    path_pattern.format(i=i)
                ).convert_alpha()
                frame = pygame.transform.scale(frame, (size_px, size_px))
                self.frames.append(frame)

            self.current_frame = 0
            self.frame_time = 0
            self.animation_speed = 0.1
            self.image = self.frames[0]
        else:
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

        if self.drop_type in ("coin", "gem"):
            self.frame_time += dt
            if self.frame_time >= self.animation_speed:
                self.frame_time = 0
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                self.rect = self.image.get_rect(center=self.rect.center)

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
