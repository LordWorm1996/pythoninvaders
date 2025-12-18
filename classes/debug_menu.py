import pygame


class DebugMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.show_main_menu = False
        self.show_spawn_menu = False

        self.selected_pattern = "straight"
        self.selected_aim_mode = "player"
        self.patterns = ["straight", "spread", "laser"]
        self.aim_modes = ["player", "down"]
        self.health_value = 1

        self.slider_dragging = False
        self.button_width = 200
        self.button_height = 40
        self.button_spacing = 50
        self.panel_margin = 20

    def toggle_main_menu(self):
        self.show_main_menu = not self.show_main_menu
        if not self.show_main_menu:
            self.show_spawn_menu = False

    def handle_event(self, event, wave_spawner, enemies_group, enemy_bullets_group):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.toggle_main_menu()

        if not self.show_main_menu:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.show_spawn_menu:
                if self.handle_spawn_menu_click(
                    event.pos, wave_spawner, enemies_group, enemy_bullets_group
                ):
                    return True
                if self.slider_rect().collidepoint(event.pos):
                    self.slider_dragging = True
                    self.update_slider(event.pos[0])
                    return True
            else:
                return self.handle_main_menu_click(event.pos, wave_spawner)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.slider_dragging = False

        if (
            event.type == pygame.MOUSEMOTION
            and self.show_spawn_menu
            and self.slider_dragging
        ):
            self.update_slider(event.pos[0])
            return True

        return False

    def panel_origin(self):
        return self.screen.get_width() - self.button_width - self.panel_margin, 50

    def slider_rect(self):
        start_x, start_y = self.panel_origin()
        return pygame.Rect(start_x, start_y + 50, self.button_width, 20)

    def update_slider(self, mouse_x):
        slider_rect = self.slider_rect()
        rel = max(0, min(slider_rect.width, mouse_x - slider_rect.x))
        self.health_value = max(1, min(100, int((rel / slider_rect.width) * 100)))

    def handle_main_menu_click(self, pos, wave_spawner):
        start_x, start_y = self.panel_origin()

        start_rect = pygame.Rect(
            start_x, start_y, self.button_width, self.button_height
        )
        spawn_rect = pygame.Rect(
            start_x,
            start_y + self.button_spacing,
            self.button_width,
            self.button_height,
        )

        if start_rect.collidepoint(pos):
            if not wave_spawner.is_wave_active():
                wave_spawner.start_wave(1)
            return True

        if spawn_rect.collidepoint(pos):
            self.show_spawn_menu = True
            return True

        return False

    def handle_spawn_menu_click(
        self, pos, wave_spawner, enemies_group, enemy_bullets_group
    ):
        start_x, start_y = self.panel_origin()
        screen_rect = self.screen.get_rect()

        pattern_start = start_y + 100
        for i, pattern in enumerate(self.patterns):
            button_rect = pygame.Rect(
                start_x,
                pattern_start + i * (self.button_height + 10),
                self.button_width,
                self.button_height,
            )
            if button_rect.collidepoint(pos):
                self.selected_pattern = pattern
                return True

        aim_start = pattern_start + len(self.patterns) * (self.button_height + 10) + 30
        for i, aim_mode in enumerate(self.aim_modes):
            button_rect = pygame.Rect(
                start_x,
                aim_start + i * (self.button_height + 10),
                self.button_width,
                self.button_height,
            )
            if button_rect.collidepoint(pos):
                self.selected_aim_mode = aim_mode
                return True

        spawn_y = aim_start + len(self.aim_modes) * (self.button_height + 10) + 30
        spawn_rect = pygame.Rect(
            start_x, spawn_y, self.button_width, self.button_height
        )
        back_rect = pygame.Rect(
            start_x,
            spawn_y + self.button_spacing,
            self.button_width,
            self.button_height,
        )

        if spawn_rect.collidepoint(pos):
            enemy = wave_spawner.spawn_enemy_manual(
                screen_rect.centerx,
                screen_rect.centery,
                health=self.health_value,
                attack_pattern=self.selected_pattern,
                aim_mode=self.selected_aim_mode,
                enemy_bullets_group=enemy_bullets_group,
            )
            if enemy:
                enemies_group.add(enemy)
            return True

        if back_rect.collidepoint(pos):
            self.show_spawn_menu = False
            return True

        return False

    def draw(self):
        if not self.show_main_menu:
            text = self.small_font.render(
                "Press F1 for Debug Menu", True, (200, 200, 200)
            )
            self.screen.blit(text, (10, self.screen.get_height() - 30))
            return

        start_x, start_y = self.panel_origin()
        panel_rect = pygame.Rect(
            start_x - 10, start_y - 10, self.button_width + 20, 500
        )
        pygame.draw.rect(self.screen, (40, 40, 50), panel_rect)
        pygame.draw.rect(self.screen, (100, 100, 120), panel_rect, 2)

        if self.show_spawn_menu:
            self.draw_spawn_menu(start_x, start_y)
        else:
            self.draw_main_menu(start_x, start_y)

    def draw_button(self, rect, color, text):
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)
        label = self.small_font.render(text, True, (255, 255, 255))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_main_menu(self, start_x, start_y):
        title = self.font.render("Debug Menu", True, (255, 255, 255))
        self.screen.blit(title, (start_x, start_y - 40))

        self.draw_button(
            pygame.Rect(start_x, start_y, self.button_width, self.button_height),
            (0, 150, 0),
            "Start waves",
        )
        self.draw_button(
            pygame.Rect(
                start_x,
                start_y + self.button_spacing,
                self.button_width,
                self.button_height,
            ),
            (150, 0, 150),
            "Spawn enemy",
        )

    def draw_spawn_menu(self, start_x, start_y):
        title = self.font.render("Spawn Enemy", True, (255, 255, 255))
        self.screen.blit(title, (start_x, start_y - 40))

        slider_rect = self.slider_rect()
        pygame.draw.rect(self.screen, (60, 60, 60), slider_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), slider_rect, 2)
        fill_width = int((self.health_value / 100) * slider_rect.width)
        pygame.draw.rect(
            self.screen,
            (0, 255, 0),
            pygame.Rect(slider_rect.x, slider_rect.y, fill_width, slider_rect.height),
        )
        health_text = self.small_font.render(
            f"Health: {self.health_value}", True, (255, 255, 255)
        )
        self.screen.blit(health_text, (start_x, slider_rect.y + 25))

        pattern_y = start_y + 100
        label = self.small_font.render("Attack Pattern", True, (255, 255, 255))
        self.screen.blit(label, (start_x, pattern_y - 20))

        for i, pattern in enumerate(self.patterns):
            rect = pygame.Rect(
                start_x,
                pattern_y + i * (self.button_height + 10),
                self.button_width,
                self.button_height,
            )
            color = (
                (100, 100, 200) if pattern == self.selected_pattern else (80, 80, 80)
            )
            self.draw_button(rect, color, pattern.capitalize())

        aim_y = pattern_y + len(self.patterns) * (self.button_height + 10) + 30
        aim_label = self.small_font.render("Aim Mode", True, (255, 255, 255))
        self.screen.blit(aim_label, (start_x, aim_y - 20))

        for i, aim_mode in enumerate(self.aim_modes):
            rect = pygame.Rect(
                start_x,
                aim_y + i * (self.button_height + 10),
                self.button_width,
                self.button_height,
            )
            color = (
                (100, 100, 200) if aim_mode == self.selected_aim_mode else (80, 80, 80)
            )
            label_text = "Toward Player" if aim_mode == "player" else "Straight Down"
            self.draw_button(rect, color, label_text)

        spawn_y = aim_y + len(self.aim_modes) * (self.button_height + 10) + 30
        self.draw_button(
            pygame.Rect(start_x, spawn_y, self.button_width, self.button_height),
            (0, 200, 0),
            "Spawn Enemy",
        )
        self.draw_button(
            pygame.Rect(
                start_x,
                spawn_y + self.button_spacing,
                self.button_width,
                self.button_height,
            ),
            (150, 0, 0),
            "Back",
        )
