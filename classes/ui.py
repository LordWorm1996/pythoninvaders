import pygame


class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

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

    def draw_boss_health_bars(self, bosses, margin=20, height=18, spacing=6):
        """Draw one health bar per alive boss along the bottom of the screen."""
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

    def draw_game_over(self):
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
        )
        self.screen.blit(game_over_text, text_rect)
