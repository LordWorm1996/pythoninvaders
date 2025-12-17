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

    def draw_ultimate_bar(self, player, x=30, y=20, width=200, height=30):
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
            f"{player.ultimate}/{player.max_ultimate}", True, (255, 255, 255)
        )
        text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text, text_rect)

    def draw_wave_info(self, wave_number, enemy_count, x=20, y=70):
        wave_text = self.font.render(f"Wave: {wave_number}", True, (255, 255, 255))
        enemies_text = self.font.render(
            f"Enemies: {enemy_count}", True, (255, 255, 255)
        )
        self.screen.blit(wave_text, (x, y))
        self.screen.blit(enemies_text, (x, y + 40))

    def draw_score(self, score, x=30, y=70):
        score_text = self.font.render(f"Score {score}", True, (255, 255, 255))
        self.screen.blit(score_text, (x, y))

    def draw_game_over(self):
        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        text_rect = game_over_text.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2)
        )
        self.screen.blit(game_over_text, text_rect)
