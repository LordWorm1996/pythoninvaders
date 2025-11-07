import pygame
import fonts
import pygame_menu

skills = {
    "Strength": {"pos": (200, 300), "unlocked": True, "next": ["Power Strike"]},
    "Power Strike": {"pos": (400, 200), "unlocked": False, "next": ["Berserk"]},
    "Berserk": {"pos": (600, 300), "unlocked": False, "next": []},
}

fonts.init_font()

FONT = fonts.spawn_font("arial", 24)


def draw_skill_tree(surface):
    for name, data in skills.items():
        for next_skill in data["next"]:
            start = data["pos"]
            end = skills[next_skill]["pos"]
            pygame.draw.line(surface, (100, 100, 100), start, end, 3)

    for name, data in skills.items():
        color = (0, 200, 0) if data["unlocked"] else (200, 0, 0)
        pygame.draw.circle(surface, color, data["pos"], 40)
        text = FONT.render(name, True, (255, 255, 255))
        text_rect = text.get_rect(center=data["pos"])
        surface.blit(text, text_rect)


def on_skill_click(name):
    for next_skill in skills[name]["next"]:
        skills[next_skill]["unlocked"] = True


def skilltree_menu(screen):
    running = True
    while running:
        screen.fill((30, 30, 40))
        draw_skill_tree(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                for name, data in skills.items():
                    x, y = data["pos"]
                    if (pos[0] - x) ** 2 + (pos[1] - y) ** 2 < 40**2:
                        if data["unlocked"]:
                            on_skill_click(name)
