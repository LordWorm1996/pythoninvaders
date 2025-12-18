import random

import pygame

import variables
from classes.attack_patterns import (
    laser_pattern,
    spread_pattern,
    straight_pattern,
    thunder_pattern,
)
from classes.bullet import Bullet, GrenadeBullet, LaserBeam, ThunderBullet
from classes.entity import Entity
from classes.ultimate_abilities import (
    DEFAULT_ULTIMATE_ORDER,
    ULTIMATE_REGISTRY,
)
from classes.weapon import Weapon


class Player(Entity):
    def __init__(
        self,
        x,
        y,
        image,
        speed=300,
        bullets_group=None,
        max_health=100,
        max_ultimate=100,
    ):
        super().__init__(x, y, image.copy())
        self.base_image = self.image.copy()
        self.speed = speed
        self.bullets_group = bullets_group
        self.max_health = max_health
        self.health = max_health
        self.max_ultimate = max_ultimate
        self.ultimate = max_ultimate
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
        self.damage_multiplier = 1.0
        self.flat_damage_bonus = 0
        self.crit_chance = 0.0
        self.crit_multiplier = 1.5
        self.elemental_status_profile = None

        self.ultimate_abilities = ULTIMATE_REGISTRY
        self.ultimate_order = list(DEFAULT_ULTIMATE_ORDER)
        self.unlocked_ultimates = set()
        self.current_ultimate_id = None
        self.ultimate_switch_pressed = False
        self.ultimate_cast_pressed = False

        self.unlocked_weapons = set()

        self.dash_active = False
        self.dash_velocity = pygame.math.Vector2(0, 0)
        self.dash_time_left_ms = 0.0

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

    def get_ultimate_percentage(self):
        return self.ultimate / self.max_ultimate if self.max_ultimate else 0

    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        return self.health

    def charge_ultimate(self, amount):
        if amount <= 0:
            return
        self.ultimate = min(self.max_ultimate, self.ultimate + amount)

    def spend_full_ultimate(self):
        self.ultimate = 0

    def has_full_ultimate(self):
        return self.ultimate >= self.max_ultimate

    def get_unlocked_ultimate_ids(self):
        return [uid for uid in self.ultimate_order if uid in self.unlocked_ultimates]

    def get_current_ultimate(self):
        if not self.current_ultimate_id:
            return None
        return self.ultimate_abilities.get(self.current_ultimate_id)

    def get_current_ultimate_label(self):
        ultimate = self.get_current_ultimate()
        if not ultimate:
            return "None"
        return ultimate.display_name

    def can_cast_current_ultimate(self):
        if not self.has_full_ultimate():
            return False
        ultimate = self.get_current_ultimate()
        if not ultimate:
            return False
        now = pygame.time.get_ticks()
        context = {"now": now}
        return ultimate.can_activate(self, context)

    def try_activate_ultimate(self, move_vector):
        if not self.has_full_ultimate():
            return
        ultimate = self.get_current_ultimate()
        if not ultimate or self.bullets_group is None:
            return

        now = pygame.time.get_ticks()
        context = {
            "now": now,
            "move_vector": pygame.math.Vector2(move_vector) if move_vector else None,
            "bullets_group": self.bullets_group,
        }

        if not ultimate.can_activate(self, context):
            return

        ultimate.activate(self, context)
        self.spend_full_ultimate()

    def start_dash(
        self, direction, distance=220, duration_ms=160, invincibility_ms=260
    ):
        direction_vec = pygame.math.Vector2(direction)
        if direction_vec.length_squared() == 0:
            return
        direction_vec = direction_vec.normalize()

        self.dash_active = True
        self.dash_time_left_ms = float(duration_ms)

        speed = distance * 1000.0 / max(1.0, float(duration_ms))
        self.dash_velocity = direction_vec * speed

        now = pygame.time.get_ticks()
        self.invincible_until = max(self.invincible_until, now + int(invincibility_ms))

    def cycle_ultimate(self):
        ids = self.get_unlocked_ultimate_ids()
        if not ids:
            self.current_ultimate_id = None
            return

        if self.current_ultimate_id not in ids:
            self.current_ultimate_id = ids[0]
            return

        index = ids.index(self.current_ultimate_id)
        next_index = (index + 1) % len(ids)
        self.current_ultimate_id = ids[next_index]

    def unlock_ultimate(self, ability_id):
        if ability_id not in self.ultimate_abilities:
            return
        ultimate = self.ultimate_abilities[ability_id]
        print(f"[UltimateDrop] picked: {ability_id} ({ultimate.display_name})")
        self.unlocked_ultimates.add(ability_id)
        if ability_id not in self.ultimate_order:
            self.ultimate_order.append(ability_id)
        if not self.current_ultimate_id:
            self.current_ultimate_id = ability_id

    def get_unlocked_weapon_indices(self):
        if not self.weapons or not self.unlocked_weapons:
            return []
        return [
            i
            for i, entry in enumerate(self.weapons)
            if entry.get("name") in self.unlocked_weapons
        ]

    def unlock_weapon(self, weapon_name):
        names = [entry.get("name") for entry in self.weapons]
        if weapon_name not in names:
            print(f"[BossDrop] unknown weapon_id: {weapon_name}")
            return
        if weapon_name in self.unlocked_weapons:
            return
        self.unlocked_weapons.add(weapon_name)
        print(f"[BossDrop] weapon unlocked: {weapon_name}")

        if not self.weapons:
            return
        if self.weapons[self.current_weapon_index]["name"] not in self.unlocked_weapons:
            for idx, entry in enumerate(self.weapons):
                if entry.get("name") == weapon_name:
                    self.current_weapon_index = idx
                    break

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        move_vector = pygame.math.Vector2(0, 0)
        stunned = self.has_status("stun")
        inverted = self.has_status("inverted_controls")

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
            speed = self.speed
            if self.has_status("frenzy"):
                speed *= 1.7
            move_vector = move_vector.normalize() * speed
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

        if keys[pygame.K_r]:
            if not self.ultimate_switch_pressed:
                self.cycle_ultimate()
            self.ultimate_switch_pressed = True
        else:
            self.ultimate_switch_pressed = False

        if keys[pygame.K_e]:
            if not self.ultimate_cast_pressed and not stunned:
                self.try_activate_ultimate(move_vector)
            self.ultimate_cast_pressed = True
        else:
            self.ultimate_cast_pressed = False

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
        if self.is_invincible() and not self.has_status("shield"):
            self.draw_invincibility_effect()
        self.draw_status_overlay()

        self.handle_input(dt)

        if self.dash_active:
            self.dash_time_left_ms -= dt * 1000.0
            self.vel.xy = self.dash_velocity
            if self.dash_time_left_ms <= 0:
                self.dash_active = False
                self.vel.xy = (0, 0)

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
        if not getattr(self, "multi_shot_enabled", True):
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
        pygame.draw.circle(
            overlay, (*self.invincibility_color[:3], 40), center, radius - 2
        )
        self.image.blit(overlay, (0, 0))

    def initialize_weapons(self):
        if self.bullets_group is None:
            return

        self.weapons = [
            {
                "name": "Blaster",
                "kind": "weapon",
                "weapon": Weapon(
                    Bullet, {"speed": 500, "damage": 1}, 0.2, straight_pattern
                ),
            },
            {
                "name": "Spread",
                "kind": "weapon",
                "weapon": Weapon(
                    Bullet, {"speed": 450, "damage": 1}, 0.35, spread_pattern
                ),
            },
            {
                "name": "Laser",
                "kind": "weapon",
                "weapon": Weapon(
                    LaserBeam,
                    {
                        "damage": 3,
                        "duration": 2000,
                        "length": 450,
                        "width": 10,
                        "color": (0, 255, 200),
                    },
                    0.8,
                    laser_pattern,
                ),
            },
            {
                "name": "Grenade Launcher",
                "kind": "grenade",
                "weapon": Weapon(
                    GrenadeBullet,
                    {
                        "speed": 420,
                        "damage": 0,
                        "deceleration": 520,
                        "explosion_radius": 100,
                        "explosion_damage": 6,
                        "hover_time": 6.0,
                    },
                    0.4,
                    straight_pattern,
                ),
            },
            {
                "name": "Thunder Lance",
                "kind": "weapon",
                "weapon": Weapon(
                    ThunderBullet,
                    {
                        "speed": 560,
                        "damage": 2,
                        "max_chain_targets": 3,
                        "chain_radius": 220,
                        "chain_damage_multiplier": 0.85,
                        "chain_decay": 0.75,
                        "glow_size": (18, 34),
                        "jitter": 20,
                        "spread": 0.12,
                        "speed_variance": 45,
                    },
                    0.45,
                    thunder_pattern,
                ),
            },
        ]
        # only the blaster is available at the start -> the rest are from bosses
        self.current_weapon_index = 0
        if not self.unlocked_weapons:
            self.unlocked_weapons.add(self.weapons[0]["name"])

    def cycle_weapon(self):
        if not self.weapons:
            return

        unlocked_indices = self.get_unlocked_weapon_indices()
        if not unlocked_indices:
            return

        current = self.current_weapon_index
        if current not in unlocked_indices:
            self.current_weapon_index = unlocked_indices[0]
            return

        pos = unlocked_indices.index(current)
        next_pos = (pos + 1) % len(unlocked_indices)
        self.current_weapon_index = unlocked_indices[next_pos]

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
        self.multi_shot_enabled = current["kind"] != "grenade"
        if current["kind"] != "grenade":
            bullets = current["weapon"].fire(
                self.rect.center, (0, -1), self.bullets_group, owner=self
            )
            if not bullets:
                return []
            self.apply_bullet_modifiers(bullets)
            return bullets

        if self.active_grenade and self.active_grenade.alive():
            self.active_grenade.detonate()
            self.active_grenade = None
            return []

        bullets = current["weapon"].fire(
            self.rect.center, (0, -1), self.bullets_group, owner=self
        )
        if bullets:
            self.active_grenade = bullets[0]
            self.apply_bullet_modifiers(bullets)
        return bullets

    def apply_skill_effect(self, skill_id):
        print(f"[SkillDrop] picked: {skill_id}")

        if skill_id == "damage":
            before = self.damage_multiplier
            self.damage_multiplier += 0.2
            after = self.damage_multiplier
            print(f"[SkillDrop] damage_multiplier: {before} -> {after}")
        elif skill_id == "crit_chance":
            before = self.crit_chance
            self.crit_chance = min(0.9, self.crit_chance + 0.1)
            after = self.crit_chance
            print(f"[SkillDrop] crit_chance: {before} -> {after}")
        elif skill_id == "crit_damage":
            before = self.crit_multiplier
            self.crit_multiplier += 0.5
            after = self.crit_multiplier
            print(f"[SkillDrop] crit_multiplier: {before} -> {after}")
        elif skill_id == "health":
            max_before = self.max_health
            hp_before = self.health
            bonus = 20
            self.max_health += bonus
            self.health = min(self.max_health, self.health + bonus)
            print(
                f"[SkillDrop] max_health: {max_before} -> {self.max_health}, "
                f"health: {hp_before} -> {self.health}"
            )
        elif skill_id == "move_speed":
            before = self.speed
            self.speed += 40
            after = self.speed
            print(f"[SkillDrop] speed: {before} -> {after}")
        elif skill_id == "drift":
            before = self.drift_enabled
            self.drift_enabled = True
            after = self.drift_enabled
            print(f"[SkillDrop] drift_enabled: {before} -> {after}")
        elif skill_id == "shot":
            max_before = self.max_shots
            count_before = self.shot_count
            self.max_shots += 1
            self.set_shot_count(self.shot_count + 1)
            print(
                f"[SkillDrop] max_shots: {max_before} -> {self.max_shots}, "
                f"shot_count: {count_before} -> {self.shot_count}"
            )
        elif skill_id == "poison":
            self.set_elemental_status("poison")
            print("[SkillDrop] elemental_status: None -> poison")
        elif skill_id == "fire":
            self.set_elemental_status("fire")
            print("[SkillDrop] elemental_status: None -> fire")
        elif skill_id == "ice":
            self.set_elemental_status("ice")
            print("[SkillDrop] elemental_status: None -> ice")

    def set_elemental_status(self, status_type):
        if status_type == "poison":
            self.elemental_status_profile = {
                "type": "poison",
                "duration_ms": variables.poison_duration_ms,
                "tick_interval_ms": variables.poison_tick_interval_ms,
                "tick_damage": variables.poison_tick_damage,
            }
        elif status_type == "fire":
            self.elemental_status_profile = {
                "type": "fire",
                "duration_ms": variables.fire_duration_ms,
                "tick_interval_ms": variables.fire_tick_interval_ms,
                "tick_damage": variables.fire_tick_damage,
            }
        elif status_type == "ice":
            self.elemental_status_profile = {
                "type": "ice",
                "duration_ms": variables.ice_duration_ms,
            }

    def apply_bullet_modifiers(self, bullets):
        for bullet in bullets:
            base_damage = bullet.damage + self.flat_damage_bonus

            frenzy_bonus = 1.5 if self.has_status("frenzy") else 1.0
            scaled_damage = max(
                1, int(round(base_damage * self.damage_multiplier * frenzy_bonus))
            )

            crit_chance = self.crit_chance
            crit_multiplier = self.crit_multiplier
            if self.has_status("frenzy"):
                crit_chance = min(1.0, crit_chance + 0.25)
                crit_multiplier += 0.5

            if crit_chance > 0.0 and crit_multiplier > 1.0:
                if random.random() < crit_chance:
                    scaled_damage = max(1, int(round(scaled_damage * crit_multiplier)))
                    setattr(bullet, "is_crit", True)

            bullet.damage = scaled_damage

            if self.elemental_status_profile and hasattr(
                bullet, "status_effect_profile"
            ):
                bullet.status_effect_profile = dict(self.elemental_status_profile)

            if hasattr(bullet, "explosion_damage"):
                bullet.explosion_damage = max(
                    1,
                    int(round(bullet.explosion_damage * self.damage_multiplier)),
                )

    def apply_status(self, status_type, duration_ms, metadata=None):
        expires_at = pygame.time.get_ticks() + max(0, int(duration_ms))
        metadata = metadata or {}
        self.status_effects = [
            s for s in self.status_effects if s["type"] != status_type
        ]
        self.status_effects.append(
            {"type": status_type, "expires_at": expires_at, "meta": metadata}
        )

    def has_status(self, status_type):
        now = pygame.time.get_ticks()
        return any(
            effect["type"] == status_type and effect["expires_at"] > now
            for effect in self.status_effects
        )

    def apply_random_thunder_debuff(self, effect_profile=None):
        profile = effect_profile or {}
        pool = profile.get("pool")
        if not pool:
            pool = [
                {"type": "inverted_controls", "min_ms": 900, "max_ms": 1800},
                {"type": "stun", "min_ms": 700, "max_ms": 1400},
                {"type": "shoot_lock", "min_ms": 900, "max_ms": 1600},
            ]
        choice = random.choice(pool)
        duration = random.randint(choice.get("min_ms", 800), choice.get("max_ms", 1600))
        self.apply_status(choice["type"], duration, metadata=choice)

    def update_status_effects(self):
        if not self.status_effects:
            return
        now = pygame.time.get_ticks()
        self.status_effects = [
            effect for effect in self.status_effects if effect["expires_at"] > now
        ]
        if not self.status_effects:
            self.fire_held = False

    def draw_status_overlay(self):
        if not self.status_effects:
            return
        if self.has_status("shield"):
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            max_radius = min(self.image.get_width(), self.image.get_height()) // 2
            radius = max_radius + 4
            center = (self.image.get_width() // 2, self.image.get_height() // 2)
            edge_color = (80, 200, 255, 180)
            fill_color = (80, 200, 255, 70)
            pygame.draw.circle(overlay, edge_color, center, radius, width=3)
            pygame.draw.circle(overlay, fill_color, center, radius - 2)
            self.image.blit(overlay, (0, 0))
            return

        color = None
        if self.has_status("frenzy"):
            color = (255, 160, 40, 90)
        elif self.has_status("stun"):
            color = (255, 210, 120, 90)
        elif self.has_status("shoot_lock"):
            color = (190, 120, 255, 70)
        elif self.has_status("inverted_controls"):
            color = (120, 200, 255, 70)
        if color:
            overlay = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            overlay.fill(color)
            pygame.draw.rect(
                overlay,
                (*color[:3], min(220, color[3] + 60)),
                overlay.get_rect(),
                width=2,
            )
            self.image.blit(overlay, (0, 0))

    def should_block_shooting(self):
        return self.has_status("shoot_lock") or self.has_status("stun")
