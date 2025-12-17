from typing import Dict, List

import pygame
import pygame_menu


class Skill:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        cost: int,
        requirements: List[str] = None,
        max_level: int = 1,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.cost = cost
        self.requirements = requirements or []
        self.max_level = max_level
        self.current_level = 0
        self.unlocked = False

    def can_unlock(self, unlocked_skills: Dict[str, "Skill"]) -> bool:
        if self.current_level >= self.max_level:
            return False

        for req_id in self.requirements:
            if req_id not in unlocked_skills or not unlocked_skills[req_id].unlocked:
                return False
        return True

    def upgrade(self) -> bool:
        if self.current_level < self.max_level:
            self.current_level += 1
            if self.current_level == 1:
                self.unlocked = True
            return True
        return False


class SkillTree:
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self.unlocked_skills: Dict[str, Skill] = {}
        self.coins = 0
        self._initialize_skills()

    def _initialize_skills(self):
        self.skills["health_boost"] = Skill(
            "health_boost", "Health Boost", "+25% Health", 3, max_level=3
        )
        self.skills["rapid_fire"] = Skill(
            "rapid_fire", "Rapid Fire", "+25% Attack Speed", 3, max_level=3
        )
        self.skills["double_shot"] = Skill(
            "double_shot", "Double Shot", "Shoots two bullets", 4, ["rapid_fire"]
        )
        self.skills["shield"] = Skill(
            "shield", "Energy Shield", "Blocks one hit", 4, ["health_boost"]
        )
        self.skills["super_shot"] = Skill(
            "super_shot",
            "Super Shot",
            "Triple Damage",
            5,
            ["health_boost", "shield", "double_shot", "rapid_fire"],
        )

    def add_coins(self, coins: int):
        self.coins += coins

    def can_upgrade_skill(self, skill_id: str) -> bool:
        if skill_id not in self.skills:
            return False

        skill = self.skills[skill_id]
        return (
            self.coins >= skill.cost
            and skill.can_unlock(self.unlocked_skills)
            and skill.current_level < skill.max_level
        )

    def upgrade_skill(self, skill_id: str) -> bool:
        if not self.can_upgrade_skill(skill_id):
            return False

        skill = self.skills[skill_id]
        self.coins -= skill.cost
        skill.upgrade()

        if skill.unlocked:
            self.unlocked_skills[skill_id] = skill

        return True


skill_tree = SkillTree()


def skilltree_menu(screen):
    theme = pygame_menu.themes.THEME_BLUE.copy()
    theme.title_font_size = 25
    theme.widget_font_size = 14

    menu = pygame_menu.Menu("Skill Tree", 700, 500, theme=theme)

    menu.add.label(
        f"Coins: {skill_tree.coins}",
        label_id="coins_display",
        font_size=20,
    )
    menu.add.vertical_margin(20)

    info_label = menu.add.label(
        "Click a circle to upgrade skill",
        label_id="skill_info",
        font_size=16,
        max_char=-1,
    )

    skills_frame = menu.add.frame_h(
        width=610, height=160, background_color=(0, 0, 0, 0)
    )

    skill_order = ["rapid_fire", "double_shot", "health_boost", "shield", "super_shot"]

    for skill_id in skill_order:
        skill = skill_tree.skills[skill_id]

        btn = menu.add.button(
            "+",
            lambda s_id=skill_id: upgrade_skill_callback(s_id, menu, info_label),
            button_id=f"skill_{skill_id}",
            align=pygame_menu.locals.ALIGN_CENTER,
            font_size=64,
            padding=(20, 40),
        )

        update_circle_button_appearance(btn, skill_id)
        skills_frame.pack(btn, align=pygame_menu.locals.ALIGN_CENTER)

    names_frame = menu.add.frame_h(width=600, height=50, background_color=(0, 0, 0, 0))
    for skill_id in skill_order:
        skill = skill_tree.skills[skill_id]
        name_label = menu.add.label(skill.name, font_size=17)
        names_frame.pack(name_label, align=pygame_menu.locals.ALIGN_CENTER)

    menu.add.button("Back to Menu", pygame_menu.events.BACK)

    return menu


def update_circle_button_appearance(button, skill_id: str):
    skill = skill_tree.skills[skill_id]

    if skill.current_level >= skill.max_level:
        button.set_background_color((0, 200, 0))
    elif skill_tree.can_upgrade_skill(skill_id):
        button.set_background_color((0, 100, 255))
    elif skill.unlocked:
        button.set_background_color((100, 150, 255))
    else:
        button.set_background_color((100, 100, 100))

    button.update_font({"color": (255, 255, 255)})


def upgrade_skill_callback(skill_id: str, menu, info_label):
    skill = skill_tree.skills[skill_id]
    skill_btn = menu.get_widget(f"skill_{skill_id}")
    coins_label = menu.get_widget("coins_display")

    if skill_tree.upgrade_skill(skill_id):
        info_label.set_title(f"Upgraded {skill.name}!")

        if coins_label:
            coins_label.set_title(f"Coins: {skill_tree.coins}")

        if skill_btn:
            update_circle_button_appearance(skill_btn, skill_id)

    else:
        if skill.current_level >= skill.max_level:
            info_label.set_title(f"{skill.name} is maxed out!")
        elif skill_tree.coins < skill.cost:
            info_label.set_title(
                f"Need {skill.cost} coins! You have {skill_tree.coins}"
            )
        elif not skill.can_unlock(skill_tree.unlocked_skills):
            info_label.set_title("Upgrade previous skills first!")
        else:
            info_label.set_title(f"Can't upgrade {skill.name}")


# Functions to use in game
def add_coins(coins: int):
    skill_tree.add_coins(coins)


def get_skill_level(skill_id: str) -> int:
    if skill_id in skill_tree.skills:
        return skill_tree.skills[skill_id].current_level
    return 0
