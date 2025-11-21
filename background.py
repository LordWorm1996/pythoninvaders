import pygame


class ScrollingBackground:
    def __init__(self, image_path, screen_size, speed_x=30, speed_y=50):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.screen_width, self.screen_height = screen_size
        self.bg_width, self.bg_height = self.image.get_size()
        self.offset = pygame.Vector2(0, 0)
        self.speed = pygame.Vector2(speed_x, speed_y)
        self.direction = pygame.Vector2(1, 1)

    def update(self, dt):
        self.offset.x += self.speed.x * dt * self.direction.x
        self.offset.y += self.speed.y * dt * self.direction.y
        max_x = max(0, self.bg_width - self.screen_width)
        max_y = max(0, self.bg_height - self.screen_height)

        if self.offset.x <= 0:
            self.offset.x, self.direction.x = 0, 1
        elif self.offset.x >= max_x:
            self.offset.x, self.direction.x = max_x, -1

        if self.offset.y <= 0:
            self.offset.y, self.direction.y = 0, 1
        elif self.offset.y >= max_y:
            self.offset.y, self.direction.y = max_y, -1

    def draw(self, surface):
        surface.blit(self.image, (-self.offset.x, -self.offset.y))
