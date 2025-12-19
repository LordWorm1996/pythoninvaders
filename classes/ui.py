import pygame

import variables
from classes.boss import Boss


class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 72)
        self.death_time = None
        self.revive_timer_duration = 10000  # 10 seconds in milliseconds
        self.revive_processed = False
        self.last_revive_key_state = False
        self.last_mouse_button_state = False
        self.game_over_time = None
        self.game_over_duration = 5000  # 5 seconds in milliseconds
        self.wave_countdown_time = None
        self.wave_countdown_duration = 5000  # 5 seconds in milliseconds

    def draw_health_bar(self, player, x=20, y=20, width=200, height=30):
        pct = player.get_health_percentage()
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (100, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)

        if pct > 0:
            fill_width = int(width * pct)
            health_rect = pygame.Rect(x, y, fill_width, height)
            if pct > 0.5:
                red = int(255 * ((pct - 0.5) * 2))
                color = (red, 255, 0)
            else:
                green = int(255 * (pct * 2))
                color = (255, green, 0)
            pygame.draw.rect(self.screen, color, health_rect)

        text = self.small_font.render(
            f"{player.health}/{player.max_health}", True, (255, 255, 255)
        )
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text, text_rect)

    def draw_ultimate_bar(self, player, x=20, y=60, width=200, height=30):
        pct = player.get_ultimate_percentage()
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, (100, 0, 0), bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)

        if pct > 0:
            fill_width = int(width * pct)
            ult_rect = pygame.Rect(x, y, fill_width, height)
            if pct > 0.5:
                yellow = int(255 * ((pct - 0.5) * 2))
                color = (yellow, yellow, 0)
            else:
                blue = int(255 * (pct * 2))
                color = (0, 0, blue)
            pygame.draw.rect(self.screen, color, ult_rect)

        text = self.small_font.render(
            f"{player.ultimate}/{player.max_ultimate}", True, (0, 0, 0)
        )
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text, text_rect)

        label = player.get_current_ultimate_label()
        ready = player.can_cast_current_ultimate()
        state_text = "Ready" if ready else "Not Ready"
        info_text = self.small_font.render(
            f"{label} [{state_text}] (E)", True, (255, 255, 255)
        )
        self.screen.blit(info_text, (x + width + 12, y + 4))

    def draw_wave_info(self, wave_number, enemy_count, x=20, y=100):
        wave_text = self.font.render(f"Wave: {wave_number}", True, (255, 255, 255))
        enemies_text = self.font.render(
            f"Enemies: {enemy_count}", True, (255, 255, 255)
        )
        self.screen.blit(wave_text, (x, y))
        self.screen.blit(enemies_text, (x, y + 40))

    def draw_score(self, score, x=20, y=180):
        score_text = self.font.render(f"Score {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (x, y))

    def draw_boss_health_bars_from_enemies(self, enemies, margin=20, height=18, spacing=6):
        """Draw one health bar per alive boss along the bottom of the screen."""
        bosses = [e for e in enemies if isinstance(e, Boss)]
        alive_bosses = [
            b
            for b in bosses
            if getattr(b, "health", 0) > 0 and getattr(b, "max_health", 0) > 0
        ]
        if not alive_bosses:
            return

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        total_width = screen_width - 2 * margin
        total_height = len(alive_bosses) * height + (len(alive_bosses) - 1) * spacing
        start_y = screen_height - margin - total_height

        for index, boss in enumerate(alive_bosses):
            y = start_y + index * (height + spacing)
            x = margin
            pct = boss.health / boss.max_health if boss.max_health else 0

            bg_rect = pygame.Rect(x, y, total_width, height)
            pygame.draw.rect(self.screen, (60, 0, 0), bg_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)

            if pct > 0:
                fill_width = int(total_width * pct)
                health_rect = pygame.Rect(x, y, fill_width, height)
                pygame.draw.rect(self.screen, (255, 0, 0), health_rect)

            label = self.small_font.render(
                f"Boss {index + 1}: {boss.health}/{boss.max_health}",
                True,
                (0, 0, 0),
            )
            label_rect = label.get_rect(center=(x + total_width // 2, y + height // 2))
            self.screen.blit(label, label_rect)

    def start_game_over_timer(self):
        if self.game_over_time is None:
            self.game_over_time = pygame.time.get_ticks()

    def reset_game_over_timer(self):
        self.game_over_time = None

    def get_remaining_game_over_time(self):
        if self.game_over_time is None:
            return 0
        elapsed = pygame.time.get_ticks() - self.game_over_time
        remaining = max(0, self.game_over_duration - elapsed)
        return remaining

    def should_return_to_menu(self):
        return self.game_over_time is not None and self.get_remaining_game_over_time() <= 0

    def draw_game_over(self):
        if self.game_over_time is None:
            self.start_game_over_timer()

        remaining_ms = self.get_remaining_game_over_time()
        remaining_seconds = remaining_ms / 1000.0

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(
            center=(screen_width // 2, screen_height // 2 - 60)
        )
        self.screen.blit(game_over_text, text_rect)

        if remaining_seconds > 0:
            countdown_text = self.font.render(
                f"Returning to menu in {remaining_seconds:.1f}s...", True, (255, 255, 255)
            )
            countdown_rect = countdown_text.get_rect(
                center=(screen_width // 2, screen_height // 2 + 40)
            )
            self.screen.blit(countdown_text, countdown_rect)
        else:
            return_text = self.font.render(
                "Returning to menu...", True, (255, 255, 255)
            )
            return_rect = return_text.get_rect(
                center=(screen_width // 2, screen_height // 2 + 40)
            )
            self.screen.blit(return_text, return_rect)

    def start_death_timer(self):
        self.death_time = pygame.time.get_ticks()

    def reset_death_timer(self):
        self.death_time = None
        self.revive_processed = False
        self.last_revive_key_state = False
        self.last_mouse_button_state = False
        self.reset_game_over_timer()

    def get_remaining_revive_time(self):
        if self.death_time is None:
            return 0
        elapsed = pygame.time.get_ticks() - self.death_time
        remaining = max(0, self.revive_timer_duration - elapsed)
        return remaining

    def is_revive_timer_active(self):
        return self.get_remaining_revive_time() > 0

    def draw_revive_menu(self, player):
        if player.is_alive():
            self.reset_death_timer()
            return None

        gems = variables.get_gem()
        if gems <= 0:
            return None

        if self.death_time is None:
            self.start_death_timer()
            self.revive_processed = False

        if self.revive_processed:
            return None

        remaining_ms = self.get_remaining_revive_time()
        if remaining_ms <= 0:
            return None

        remaining_seconds = remaining_ms / 1000.0
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_text = self.large_font.render("YOU DIED", True, (255, 0, 0))
        title_rect = title_text.get_rect(center=(screen_width // 2, screen_height // 2 - 120))
        self.screen.blit(title_text, title_rect)

        timer_text = self.font.render(
            f"Time remaining: {remaining_seconds:.1f}s", True, (255, 255, 255)
        )
        timer_rect = timer_text.get_rect(center=(screen_width // 2, screen_height // 2 - 40))
        self.screen.blit(timer_text, timer_rect)

        gem_text = self.font.render(f"Gems: {gems}", True, (255, 215, 0))
        gem_rect = gem_text.get_rect(center=(screen_width // 2, screen_height // 2))
        self.screen.blit(gem_text, gem_rect)

        button_width = 250
        button_height = 60
        button_x = screen_width // 2 - button_width // 2
        button_y = screen_height // 2 + 40
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_hover = button_rect.collidepoint(mouse_pos)
        
        if mouse_hover:
            button_color = (50, 200, 50)
            button_border_color = (100, 255, 100)
        else:
            button_color = (40, 150, 40)
            button_border_color = (80, 200, 80)
        
        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, button_border_color, button_rect, 3)
        
        button_text = self.font.render("REVIVE (1 Gem)", True, (255, 255, 255))
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)
        
        instruction_text = self.small_font.render(
            "Click the button above or press R to Revive", True, (200, 200, 200)
        )
        instruction_rect = instruction_text.get_rect(
            center=(screen_width // 2, screen_height // 2 + 120)
        )
        self.screen.blit(instruction_text, instruction_rect)

        keys = pygame.key.get_pressed()
        current_key_state = keys[pygame.K_r]
        current_mouse_state = pygame.mouse.get_pressed()[0]  # Left mouse button
        
        if mouse_hover and current_mouse_state and not self.last_mouse_button_state:
            self.revive_processed = True
            self.last_mouse_button_state = True
            return "revive"
        
        if current_key_state and not self.last_revive_key_state:
            self.revive_processed = True
            self.last_revive_key_state = True
            return "revive"
        
        self.last_revive_key_state = current_key_state
        self.last_mouse_button_state = current_mouse_state
        return None

    def handle_death_state(self, player):

        if player.is_alive():
            self.reset_death_timer()
            return True

        gems = variables.get_gem()
        
        if gems <= 0:
            self.draw_game_over()
            return not self.should_return_to_menu()
        
        revive_action = self.draw_revive_menu(player)
        if revive_action == "revive":
            if gems > 0:
                variables.gem_inv -= 1
                player.health = player.max_health
                self.reset_death_timer()
                print(f"Player revived! Gems remaining: {variables.get_gem()}")
            return True
        elif not self.is_revive_timer_active():
            self.draw_game_over()
            return not self.should_return_to_menu()
        
        return True

    def start_wave_countdown(self):
        if self.wave_countdown_time is None:
            self.wave_countdown_time = pygame.time.get_ticks()

    def reset_wave_countdown(self):
        self.wave_countdown_time = None

    def get_remaining_wave_countdown_time(self):
        if self.wave_countdown_time is None:
            return 0
        elapsed = pygame.time.get_ticks() - self.wave_countdown_time
        remaining = max(0, self.wave_countdown_duration - elapsed)
        return remaining

    def is_wave_countdown_complete(self):
        return self.wave_countdown_time is not None and self.get_remaining_wave_countdown_time() <= 0

    def draw_wave_countdown(self):
        remaining_ms = self.get_remaining_wave_countdown_time()
        remaining_seconds = remaining_ms / 1000.0

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        countdown_text = self.large_font.render(
            f"Wave starting in {remaining_seconds:.1f}s", True, (255, 255, 255)
        )
        countdown_rect = countdown_text.get_rect(
            center=(screen_width // 2, screen_height // 2)
        )
        self.screen.blit(countdown_text, countdown_rect)
