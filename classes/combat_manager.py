import random

import pygame

import variables
from classes.bullet import LightningArc
from classes.skill_drop import SkillDrop
from skilltree import add_coins


class CombatManager:
    def __init__(
        self, player, player_bullets, enemies, enemy_bullets, enemy_drops=None, score=None
    ):
        self.player = player
        self.player_bullets = player_bullets
        self.enemies = enemies
        self.enemy_bullets = enemy_bullets
        self.enemy_drops = enemy_drops
        self.score = score if score is not None else [0]

    def update(self):
        self.handle_player_bullets_vs_enemies()
        self.handle_enemy_bullets_vs_player()
        self.handle_player_vs_enemies()
        self.handle_enemy_status_effects()
        if self.enemy_drops:
            self.handle_player_vs_drops()

    def handle_player_bullets_vs_enemies(self):
        hits = pygame.sprite.groupcollide(
            self.player_bullets, self.enemies, False, False
        )
        processed_enemies = set()
        for bullet, enemy_list in hits.items():
            for enemy in enemy_list:
                enemy_id = id(enemy)
                if enemy_id in processed_enemies:
                    continue
                processed_enemies.add(enemy_id)
                destroyed, drop = enemy.take_damage(bullet.damage)
                if hasattr(bullet, "stick_to"):
                    bullet.stick_to(enemy)
                if destroyed:
                    self.score[0] += 1
                    self.player.charge_ultimate(1)
                    if drop is not None and self.enemy_drops is not None:
                        self.enemy_drops.add(drop)
                self.trigger_bullet_enemy_effect(bullet, enemy)
            if not getattr(bullet, "persistent", False):
                bullet.kill()

    def handle_enemy_bullets_vs_player(self):
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, False)
        total_damage = 0
        for bullet in hits:
            total_damage += bullet.damage
            if hasattr(bullet, "stick_to"):
                bullet.stick_to(self.player)
            self.trigger_bullet_player_effect(bullet)
            if not getattr(bullet, "persistent", False) or self.player.has_status(
                "shield"
            ):
                bullet.kill()
        if total_damage:
            self.player.take_damage(total_damage)

    def handle_player_vs_enemies(self):
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        total_damage = 0
        for enemy in hits:
            total_damage += enemy.damage
        if total_damage:
            self.player.take_damage(total_damage)

    def handle_player_vs_drops(self):
        hits = pygame.sprite.spritecollide(self.player, self.enemy_drops, True)
        for drop in hits:
            if drop.drop_type in {"health_pack", "big_health_pack"}:
                self.player.heal(drop.value)
            elif drop.drop_type in {"ultimate_pack", "big_ultimate_pack"}:
                self.player.charge_ultimate(drop.value)
            elif drop.drop_type == "coin":
                add_coins(drop.value)
            elif drop.drop_type == "gem":
                variables.gem += drop.value
            elif isinstance(drop, SkillDrop):
                self.player.apply_skill_effect(drop.skill_id)
            elif getattr(drop, "drop_type", None) == "ultimate_ability":
                ability_id = getattr(drop, "ability_id", None)
                if ability_id:
                    self.player.unlock_ultimate(ability_id)
            elif getattr(drop, "drop_type", None) == "boss_weapon":
                weapon_id = getattr(drop, "weapon_id", None)
                if weapon_id:
                    self.player.unlock_weapon(weapon_id)
            if drop.drop_type in {
                "boss_health_pack",
                "boss_ultimate_pack",
            }:
                self.player.heal(drop.value)

    def trigger_bullet_enemy_effect(self, bullet, primary_enemy):
        effect_profile = getattr(bullet, "effect_profile", {})
        if effect_profile.get("type") == "thunder":
            self.apply_thunder_chain(
                primary_enemy, effect_profile, initial_damage=bullet.damage
            )

        status_profile = getattr(bullet, "status_effect_profile", {})
        status_type = status_profile.get("type")

        if status_type == "poison":
            primary_enemy.apply_status(
                "poison",
                status_profile.get("duration_ms", variables.poison_duration_ms),
                status_profile.get("tick_damage", variables.poison_tick_damage),
                status_profile.get(
                    "tick_interval_ms", variables.poison_tick_interval_ms
                ),
            )
        elif status_type == "fire":
            primary_enemy.apply_status(
                "fire",
                status_profile.get("duration_ms", variables.fire_duration_ms),
                status_profile.get("tick_damage", variables.fire_tick_damage),
                status_profile.get(
                    "tick_interval_ms", variables.fire_tick_interval_ms
                ),
            )
        elif status_type == "ice":
            primary_enemy.apply_status(
                "ice",
                status_profile.get("duration_ms", variables.ice_duration_ms),
                0,
                0,
            )

    def trigger_bullet_player_effect(self, bullet):
        if self.player.has_status("shield"):
            return
        profile = getattr(bullet, "status_effect_profile", None)
        if not profile or profile.get("type") != "thunder_shock":
            return
        self.player.apply_random_thunder_debuff(profile)

    def handle_enemy_status_effects(self):
        now = pygame.time.get_ticks()
        for enemy in list(self.enemies):
            effects = getattr(enemy, "status_effects", [])
            if not effects:
                continue

            remaining = []
            enemy_dead = False

            for effect in effects:
                if effect["expires_at"] <= now:
                    continue

                if effect["type"] in ("poison", "fire"):
                    tick_interval_ms = effect["tick_interval_ms"]
                    if tick_interval_ms and now >= effect["next_tick_at"]:
                        effect["next_tick_at"] = now + tick_interval_ms
                        destroyed, drop = enemy.take_damage(effect["tick_damage"])
                        if destroyed:
                            enemy_dead = True
                            self.score[0] += 1
                            self.player.charge_ultimate(1)
                            if drop is not None and self.enemy_drops is not None:
                                self.enemy_drops.add(drop)
                            break

                remaining.append(effect)

            if not enemy_dead:
                enemy.status_effects = remaining

    def apply_thunder_chain(self, initial_enemy, profile, initial_damage):
        max_targets = profile.get("max_targets", 0)
        if max_targets <= 0:
            return
        chain_radius = profile.get("chain_radius", 200)
        damage_multiplier = profile.get("damage_multiplier", 0.75)
        decay = profile.get("decay", 0.8)
        arc_color = profile.get("arc_color", (120, 220, 255))
        arc_core = profile.get("arc_core", (255, 255, 255))
        jitter = profile.get("jitter", 18)

        remaining_targets = max_targets
        last_enemy = initial_enemy
        damage = max(1, initial_damage * damage_multiplier)
        visited = {initial_enemy}

        while remaining_targets > 0:
            target = self.find_chain_target(last_enemy, visited, chain_radius)
            if target is None:
                break
            visited.add(target)
            dmg_amount = max(1, int(round(damage)))
            destroyed, drop = target.take_damage(dmg_amount)
            if destroyed:
                self.score[0] += 1
                self.player.charge_ultimate(1)
                if drop is not None and self.enemy_drops is not None:
                    self.enemy_drops.add(drop)
            self.render_lightning_arc(
                last_enemy.rect.center,
                target.rect.center,
                arc_color,
                arc_core,
                jitter,
                owner="player",
            )
            last_enemy = target
            remaining_targets -= 1
            damage = max(1, damage * decay)

    def find_chain_target(self, source_enemy, visited, radius):
        candidates = []
        source_pos = pygame.math.Vector2(source_enemy.rect.center)
        radius_sq = radius * radius
        for enemy in self.enemies:
            if enemy in visited:
                continue
            if not enemy.alive():
                continue
            target_pos = pygame.math.Vector2(enemy.rect.center)
            offset = target_pos - source_pos
            dist_sq = offset.length_squared()
            if dist_sq <= radius_sq:
                candidates.append((dist_sq, enemy))
        if not candidates:
            return None
        candidates.sort(key=lambda entry: entry[0])
        return candidates[0][1]

    def render_lightning_arc(
        self, start, end, color, core_color, jitter, owner="player"
    ):
        arc = LightningArc(start, end, color, core_color, jitter, owner=owner)
        if owner == "player":
            self.player_bullets.add(arc)
        else:
            self.enemy_bullets.add(arc)
