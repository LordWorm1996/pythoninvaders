import random
import pygame
from classes.entity import Entity
from classes.weapon import Weapon
from classes.bullet import Bullet, LaserBeam, GrenadeBullet, ThunderBullet
from classes.attack_patterns import straight_pattern, spread_pattern, laser_pattern, thunder_pattern


class Player(Entity):
    def __init__(self, x, y, image, speed=300, bullets_group=None, max_health=100):
        super().__init__(x, y, image.copy())
        self.base_image = self.image.copy()
        self.speed = speed
        self.bullets_group = bullets_group
        self.max_health = max_health
        self.health = max_health
        self.weapons = []
        self.current_weapon_index = 0
        self.switch_pressed = False
        self.fire_held = False
        self.active_grenade = None
        self.shot_count = 1
        self.max_shots = 4
        self.multi_shot_enabled = True
        self.drift_enabled = False
        self.drift_decay_rate = 5.0
        self.drift_stop_threshold = 10.0
        self.invincibility_duration = 1000
        self.invincible_until = 0
        self.invincibility_color = (255, 255, 255, 120)
        self.invincibility_radius_padding = 8
        self.status_effects = []
        self.initialize_weapons()

    def take_damage(self, amount):
        if self.is_invincible():
            return False

        self.health = max(0, self.health - amount)
        self.invincible_until = pygame.time.get_ticks() + self.invincibility_duration
        return self.health == 0

    def is_alive(self):
        return self.health > 0

    def is_invincible(self):
        return pygame.time.get_ticks() < self.invincible_until

    def get_health_percentage(self):
        return self.health / self.max_health if self.max_health else 0

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        return self.health

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        move_vector = pygame.math.Vector2(0, 0)
        stunned = self.has_status('stun')
        inverted = self.has_status('inverted_controls')

        if keys[pygame.K_q]:
            if not self.switch_pressed:
                self.cycle_weapon()
            self.switch_pressed = True
        else:
            self.switch_pressed = False

        if keys[pygame.K_w]:
            move_vector.y = -1
        if keys[pygame.K_s]:
            move_vector.y = 1
        if keys[pygame.K_a]:
            move_vector.x = -1
        if keys[pygame.K_d]:
            move_vector.x = 1

        if inverted:
            move_vector *= -1

        if stunned:
            move_vector.xy = (0, 0)

        if stunned:
            self.vel.xy = (0, 0)
        elif move_vector.length_squared() > 0:
            move_vector = move_vector.normalize() * self.speed
            self.vel.xy = move_vector
        elif self.drift_enabled:
            self.apply_drift(dt)
        else:
            self.vel.xy = (0, 0)


        if keys[pygame.K_1]:
            self.set_shot_count(1)
        elif keys[pygame.K_2]:
            self.set_shot_count(2)
        elif keys[pygame.K_3]:
            self.set_shot_count(3)
        elif keys[pygame.K_4]:
            self.set_shot_count(4)

        if keys[pygame.K_SPACE]:
            if not self.should_block_shooting():
                self.try_fire()
            else:
                self.fire_held = False
        else:
            self.fire_held = False

    def update(self, dt, screen_size):
        self.update_status_effects()
        self.image = self.base_image.copy()
        if self.is_invincible():
            self.draw_invincibility_effect()
        self.draw_status_overlay()

        self.handle_input(dt)
        if self.active_grenade and not self.active_grenade.alive():
            self.active_grenade = None
        super().update(dt)
        self.clamp_to_screen(*screen_size)

    def clamp_to_screen(self, screen_width, screen_height):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

    def set_shot_count(self, count):
        self.shot_count = max(1, min(self.max_shots, int(count)))

    def get_fire_positions(self):
        default_position = (self.rect.centerx, self.rect.top)
        if not getattr(self, 'multi_shot_enabled', True):
            return [default_position]

        if self.shot_count <= 1:
            return [default_position]

        margin = min(20, int(self.rect.width * 0.15))
        top_y = self.rect.top

        if self.shot_count == 2:
            return [
                (self.rect.left + margin, top_y),
                (self.rect.right - margin, top_y),
            ]

        usable_width = max(1, self.rect.width - 2 * margin)
        spacing = usable_width / (self.shot_count - 1)
        return [
            (self.rect.left + margin + spacing * i, top_y)
            for i in range(self.shot_count)
        ]

    def apply_drift(self, dt):
        decay = max(0.0, 1.0 - self.drift_decay_rate * dt)
        self.vel *= decay
        if self.vel.length() < self.drift_stop_threshold:
            self.vel.xy = (0, 0)

    def draw_invincibility_effect(self):
        overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        max_radius = min(self.image.get_width(), self.image.get_height()) // 2
        radius = max(1, max_radius - 2) + self.invincibility_radius_padding
        radius = min(max_radius, radius)
        center = (self.image.get_width() // 2, self.image.get_height() // 2)
        pygame.draw.circle(overlay, self.invincibility_color, center, radius, width=2)
        pygame.draw.circle(overlay, (*self.invincibility_color[:3], 40), center, radius - 2)
        self.image.blit(overlay, (0, 0))

    def initialize_weapons(self):
        if self.bullets_group is None:
            return

        self.weapons = [
            {
                'name': 'Blaster',
                'kind': 'weapon',
                'weapon': Weapon(Bullet, {'speed': 500, 'damage': 1}, 0.2, straight_pattern),
            },
            {
                'name': 'Spread',
                'kind': 'weapon',
                'weapon': Weapon(Bullet, {'speed': 450, 'damage': 1}, 0.35, spread_pattern),
            },
            {
                'name': 'Laser',
                'kind': 'weapon',
                'weapon': Weapon(
                    LaserBeam,
                    {'damage': 3, 'duration': 2000, 'length': 450, 'width': 10, 'color': (0, 255, 200)},
                    0.8,
                    laser_pattern,
                ),
            },
            {
                'name': 'Grenade Launcher',
                'kind': 'grenade',
                'weapon': Weapon(
                    GrenadeBullet,
                    {
                        'speed': 420,
                        'damage': 0,
                        'deceleration': 520,
                        'explosion_radius': 100,
                        'explosion_damage': 6,
                        'hover_time': 6.0,
                    },
                    0.4,
                    straight_pattern,
                ),
            },
            {
                'name': 'Thunder Lance',
                'kind': 'weapon',
                'weapon': Weapon(
                    ThunderBullet,
                    {
                        'speed': 560,
                        'damage': 2,
                        'max_chain_targets': 3,
                        'chain_radius': 220,
                        'chain_damage_multiplier': 0.85,
                        'chain_decay': 0.75,
                        'glow_size': (18, 34),
                        'jitter': 20,
                        'spread': 0.12,
                        'speed_variance': 45,
                    },
                    0.45,
                    thunder_pattern,
                ),
            },
        ]
        self.current_weapon_index = 4

    def cycle_weapon(self):
        if self.weapons:
            self.current_weapon_index = (self.current_weapon_index + 1) % len(self.weapons)

    def try_fire(self):
        if not self.weapons or self.fire_held or self.should_block_shooting():
            if self.should_block_shooting():
                self.fire_held = False
            return
        self.fire_current_weapon()
        self.fire_held = True

    def fire_current_weapon(self):
        if not self.weapons or self.bullets_group is None:
            return []

        current = self.weapons[self.current_weapon_index]
        self.multi_shot_enabled = current['kind'] != 'grenade'
        if current['kind'] != 'grenade':
            return current['weapon'].fire(self.rect.center, (0, -1), self.bullets_group, owner=self)

        if self.active_grenade and self.active_grenade.alive():
            self.active_grenade.detonate()
            self.active_grenade = None
            return []

        bullets = current['weapon'].fire(self.rect.center, (0, -1), self.bullets_group, owner=self)
        if bullets:
            self.active_grenade = bullets[0]
        return bullets

    def apply_status(self, status_type, duration_ms, metadata=None):
        expires_at = pygame.time.get_ticks() + max(0, int(duration_ms))
        metadata = metadata or {}
        self.status_effects = [s for s in self.status_effects if s['type'] != status_type]
        self.status_effects.append({'type': status_type, 'expires_at': expires_at, 'meta': metadata})

    def has_status(self, status_type):
        now = pygame.time.get_ticks()
        return any(effect['type'] == status_type and effect['expires_at'] > now for effect in self.status_effects)

    def apply_random_thunder_debuff(self, effect_profile=None):
        profile = effect_profile or {}
        pool = profile.get('pool')
        if not pool:
            pool = [
                {'type': 'inverted_controls', 'min_ms': 900, 'max_ms': 1800},
                {'type': 'stun', 'min_ms': 700, 'max_ms': 1400},
                {'type': 'shoot_lock', 'min_ms': 900, 'max_ms': 1600},
            ]
        choice = random.choice(pool)
        duration = random.randint(choice.get('min_ms', 800), choice.get('max_ms', 1600))
        self.apply_status(choice['type'], duration, metadata=choice)

    def update_status_effects(self):
        if not self.status_effects:
            return
        now = pygame.time.get_ticks()
        self.status_effects = [effect for effect in self.status_effects if effect['expires_at'] > now]
        if not self.status_effects:
            self.fire_held = False

    def draw_status_overlay(self):
        if not self.status_effects:
            return
        color = None
        if self.has_status('stun'):
            color = (255, 210, 120, 90)
        elif self.has_status('shoot_lock'):
            color = (190, 120, 255, 70)
        elif self.has_status('inverted_controls'):
            color = (120, 200, 255, 70)
        if color:
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill(color)
            pygame.draw.rect(overlay, (*color[:3], min(220, color[3] + 60)), overlay.get_rect(), width=2)
            self.image.blit(overlay, (0, 0))

    def should_block_shooting(self):
        return self.has_status('shoot_lock') or self.has_status('stun')
