import random

import pygame


def normalized(direction, fallback):
    vec = pygame.math.Vector2(direction)
    if vec.length_squared() == 0:
        vec = pygame.math.Vector2(fallback)
    return vec.normalize()


def screen_rect():
    surface = pygame.display.get_surface()
    return surface.get_rect() if surface else pygame.Rect(0, 0, 800, 600)


class Bullet(pygame.sprite.Sprite):
    def __init__(
        self,
        pos,
        direction,
        speed=500,
        damage=1,
        owner=None,
        image=None,
        lifetime=None,
        effect_profile=None,
        status_effect_profile=None,
    ):
        super().__init__()
        self.image = image or pygame.Surface((5, 15))
        is_enemy_owner = (
            owner == "enemy" or owner == "boss" or getattr(owner, "is_enemy", False)
        )
        self.image.fill((255, 255, 0) if is_enemy_owner else (255, 0, 0))
        self.rect = self.image.get_rect(center=pos)
        self.velocity = normalized(direction, (0, -1)) * speed
        self.damage = damage
        self.owner = owner
        self.lifetime = lifetime
        self.spawn_time = pygame.time.get_ticks() if lifetime else None
        self.effect_profile = effect_profile or {}
        self.status_effect_profile = status_effect_profile or {}

    def update(self, dt):
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        if not screen_rect().colliderect(self.rect):
            self.kill()
            return

        if (
            self.spawn_time
            and pygame.time.get_ticks() - self.spawn_time >= self.lifetime
        ):
            self.kill()


class LaserBeam(pygame.sprite.Sprite):
    def __init__(
        self,
        pos,
        direction,
        damage=3,
        duration=2500,
        width=8,
        length=400,
        owner=None,
        color=(0, 255, 255),
    ):
        super().__init__()
        self.direction = normalized(direction, (0, 1))
        base_surface = pygame.Surface((width, length), pygame.SRCALPHA)
        base_surface.fill(color)
        angle = self.direction.angle_to(pygame.math.Vector2(0, -1))
        self.image = pygame.transform.rotate(base_surface, angle)
        anchor = (
            "midtop"
            if self.direction.y > 0.7
            else "midbottom"
            if self.direction.y < -0.7
            else "center"
        )
        self.rect = self.image.get_rect()
        if anchor == "midtop":
            self.rect.midtop = pos
        elif anchor == "midbottom":
            self.rect.midbottom = pos
        else:
            self.rect.center = pos
        self.damage = damage
        self.owner = owner
        self.duration = duration
        self.spawn_time = pygame.time.get_ticks()
        self.persistent = True

    def update(self, dt):
        if pygame.time.get_ticks() - self.spawn_time >= self.duration:
            self.kill()


class GrenadeBullet(Bullet):
    def __init__(
        self,
        pos,
        direction,
        speed=420,
        damage=0,
        owner=None,
        image=None,
        lifetime=None,
        deceleration=520,
        explosion_radius=100,
        explosion_damage=6,
        hover_time=6.0,
    ):
        if image is None:
            image = pygame.Surface((18, 18), pygame.SRCALPHA)
            pygame.draw.circle(image, (60, 210, 255), (9, 9), 8)
            pygame.draw.circle(image, (255, 255, 255), (9, 9), 3)

        direction_vec = normalized(direction, (0, -1))
        super().__init__(
            pos,
            direction_vec,
            speed=speed,
            damage=damage,
            owner=owner,
            image=image,
            lifetime=lifetime,
        )
        self.velocity = direction_vec * speed
        self.deceleration = deceleration
        self.explosion_radius = explosion_radius
        self.explosion_damage = explosion_damage
        self.hover_time = hover_time
        self.elapsed_time = 0.0
        self.state = "flying"
        self.explosion_duration = 0.2
        self.explosion_timer = 0.0
        self.persistent = True

    def update(self, dt):
        if self.state == "flying":
            self.update_flight(dt)
        else:
            self.update_explosion(dt)

    def update_flight(self, dt):
        self.elapsed_time += dt
        if self.velocity.y < 0:
            self.velocity.y = min(self.velocity.y + self.deceleration * dt, 0)

        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        if not screen_rect().colliderect(self.rect):
            self.detonate()
            return

        if self.elapsed_time >= self.hover_time:
            self.detonate()

    def update_explosion(self, dt):
        self.explosion_timer += dt
        if self.explosion_timer >= self.explosion_duration:
            self.kill()

    def detonate(self):
        if self.state == "exploding":
            return
        self.state = "exploding"
        self.damage = self.explosion_damage
        self.explosion_timer = 0.0
        center = self.rect.center
        diameter = self.explosion_radius * 2
        explosion_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(
            explosion_surface,
            (255, 200, 80, 220),
            (self.explosion_radius, self.explosion_radius),
            self.explosion_radius,
        )
        pygame.draw.circle(
            explosion_surface,
            (255, 120, 40, 230),
            (self.explosion_radius, self.explosion_radius),
            int(self.explosion_radius * 0.6),
        )
        self.image = explosion_surface
        self.rect = self.image.get_rect(center=center)
        self.velocity.xy = (0, 0)


class ThunderBullet(Bullet):
    def __init__(
        self,
        pos,
        direction,
        speed=520,
        damage=2,
        owner=None,
        image=None,
        lifetime=None,
        max_chain_targets=2,
        chain_radius=200,
        chain_damage_multiplier=0.8,
        chain_decay=0.8,
        arc_color=(120, 220, 255),
        arc_core=(255, 255, 255),
        glow_size=(16, 32),
        jitter=18,
        status_effects=None,
        pulse_rate=0.08,
    ):
        self.glow_size = glow_size
        self.jitter = jitter
        self.arc_color = arc_color
        self.arc_core = arc_core
        self.pulse_rate = pulse_rate
        self.frames = self.build_frames()
        self.frame_index = 0
        self.pulse_timer = 0.0
        if image is None:
            image = self.frames[0].copy()
        effect_profile = {
            "type": "thunder",
            "max_targets": max(0, int(max_chain_targets)),
            "chain_radius": max(20, chain_radius),
            "damage_multiplier": chain_damage_multiplier,
            "decay": chain_decay,
            "arc_color": arc_color,
            "arc_core": arc_core,
            "jitter": jitter,
        }
        status_effect_profile = {
            "type": "thunder_shock",
            "pool": status_effects
            or [
                {"type": "inverted_controls", "min_ms": 900, "max_ms": 1800},
                {"type": "stun", "min_ms": 700, "max_ms": 1300},
                {"type": "shoot_lock", "min_ms": 900, "max_ms": 1700},
            ],
        }
        super().__init__(
            pos,
            direction,
            speed=speed,
            damage=damage,
            owner=owner,
            image=image,
            lifetime=lifetime,
            effect_profile=effect_profile,
            status_effect_profile=status_effect_profile,
        )
        self.image = self.frames[self.frame_index].copy()
        self.rect = self.image.get_rect(center=pos)

    def update(self, dt):
        self.pulse_timer += dt
        if self.pulse_timer >= self.pulse_rate:
            self.pulse_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            current_center = self.rect.center
            self.image = self.frames[self.frame_index].copy()
            self.rect = self.image.get_rect(center=current_center)
        super().update(dt)

    def build_frames(self, frame_count=4):
        frames = []
        for i in range(frame_count):
            surface = pygame.Surface(self.glow_size, pygame.SRCALPHA)
            path_points = self.generate_arc_points(seed=i)
            if len(path_points) >= 2:
                pygame.draw.lines(surface, self.arc_color, False, path_points, 3)
                pygame.draw.lines(surface, self.arc_core, False, path_points, 1)
            pygame.draw.circle(
                surface,
                (*self.arc_color, 40),
                (self.glow_size[0] // 2, self.glow_size[1]),
                6,
            )
            frames.append(surface)
        return frames

    def generate_arc_points(self, seed=0):
        rng = random.Random(pygame.time.get_ticks() + seed + id(self))
        width, height = self.glow_size
        segments = max(4, height // 4)
        max_jitter = min(self.jitter, width * 0.45)
        points = []
        for i in range(segments + 1):
            t = i / segments
            x = width / 2 + rng.uniform(-max_jitter, max_jitter)
            y = height * (1 - t)
            points.append((x, y))
        return points


class LightningArc(Bullet):
    def __init__(
        self, start, end, color, core_color, jitter=18, segments=6, owner=None
    ):
        super().__init__((0, 0), (0, 0), speed=0, damage=0, owner=owner, lifetime=0.05)
        self.start = pygame.math.Vector2(start)
        self.end = pygame.math.Vector2(end)
        self.color = color
        self.core_color = core_color
        self.jitter = jitter
        self.segments = segments
        self.generate_points()
        self.create_image()
        self.persistent = False

    def generate_points(self):
        self.points = [self.start]
        for i in range(1, self.segments):
            t = i / self.segments
            point = self.start.lerp(self.end, t)
            normal = pygame.math.Vector2(
                -(self.end.y - self.start.y), self.end.x - self.start.x
            )
            if normal.length_squared() > 0:
                normal = normal.normalize()
            offset = random.uniform(-self.jitter, self.jitter)
            point += normal * offset
            self.points.append(point)
        self.points.append(self.end)

    def create_image(self):
        all_points = [p.xy for p in self.points]
        min_x = min(p[0] for p in all_points)
        max_x = max(p[0] for p in all_points)
        min_y = min(p[1] for p in all_points)
        max_y = max(p[1] for p in all_points)

        width = int(max_x - min_x) + 20
        height = int(max_y - min_y) + 20
        if width <= 0 or height <= 0:
            width = height = 1

        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        offset_points = [(p[0] - min_x + 10, p[1] - min_y + 10) for p in all_points]
        pygame.draw.lines(self.image, self.color, False, offset_points, 4)
        pygame.draw.lines(self.image, self.core_color, False, offset_points, 2)

        self.rect = self.image.get_rect(topleft=(min_x - 10, min_y - 10))

    def update(self, dt):
        super().update(dt)
