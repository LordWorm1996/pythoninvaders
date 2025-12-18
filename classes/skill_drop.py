import random

import pygame

from classes.enemy_drop import EnemyDrop


class SkillDrop(EnemyDrop):
    FRAME_COUNT = 64
    PATH_PATTERN = "game_assets/drops/skill_drop/skill_drop{i:03d}.png"
    SIZE_PX = 24

    SKILL_TYPES = (
        "damage",
        "crit_chance",
        "crit_damage",
        "health",
        "move_speed",
        "poison",
        "fire",
        "ice",
        "drift",
        "shot",
    )

    #CHATGPT START : without this it crashes : TypeError:EnemyDrop.__new__() missing 1 reqquired positional argument
    def __new__(cls, *args, **kwargs):
        return pygame.sprite.Sprite.__new__(cls)
    ## CHATGPT END


    def __init__(self, x, y, skill_id=None):
        pygame.sprite.Sprite.__init__(self)

        if skill_id is None:
            skill_id = random.choice(self.SKILL_TYPES)

        self.drop_type = "skill"
        self.skill_id = skill_id
        self.value = 0

        self.frames = []
        for i in range(self.FRAME_COUNT):
            frame = pygame.image.load(
                self.PATH_PATTERN.format(i=i)
            ).convert_alpha()
            frame = pygame.transform.scale(frame, (self.SIZE_PX, self.SIZE_PX))
            self.frames.append(frame)

        self.current_frame = 0
        self.frame_time = 0
        self.animation_speed = 0.1
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))

        self.vel = pygame.math.Vector2(0, 100)
        self.lifetime = 10000
        self.spawn_time = pygame.time.get_ticks()

    def update(self, dt, screen_size=None):
        self.rect.y += self.vel.y * dt

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


