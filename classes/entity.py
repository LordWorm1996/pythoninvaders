import pygame


class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.vel = pygame.math.Vector2()

    def update(self, dt):
        self.rect.x += self.vel.x * dt
        self.rect.y += self.vel.y * dt
