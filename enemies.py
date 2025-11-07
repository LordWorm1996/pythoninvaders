import pygame
import variables


class Enemy:
    def __init__(self, color="red"):
        self.color = color.lower()
        self.health = variables.health
        self.speed = variables.speed
        self.damage = variables.damage
        self.random_multiplier = variables.random_multiplier

        self.apply_color_modifiers()

    def apply_color_modifiers(self):
        match self.color:
            case "red":
                pass
            case "yellow":
                self.speed *= 5
                self.damage -= 0.5
            case "orange":
                self.health *= 10
                self.speed -= 0.5
                self.damage = 0
            case "green":
                self.health += 1
                self.speed += 1
                self.damage += 1
            case "blue":
                self.health += 5
                self.speed += 2
                self.damage += 2
            case "purple":
                self.health += 10
                self.speed += 2
                self.damage += 5
            case "special":
                self.health *= self.random_multiplier
                self.speed *= self.random_multiplier
                self.damage *= self.random_multiplier
            case _:
                raise ValueError(f"Unknown enemy color: {self.color}")

    def __repr__(self):
        return f"Enemy(color={self.color}, health={self.health}, speed={self.speed}, damage={self.damage})"


class Boss:
    def __init__(self, color="red"):
        self.color = color.lower()
        self.health = variables.health * variables.boss_multiplier
        self.speed = variables.speed
        self.damage = variables.damage
        self.random_multiplier = variables.random_multiplier

        self.apply_color_modifiers()

    def apply_color_modifiers(self):
        match self.color:
            case "red":
                pass
            case "yellow":
                self.speed *= 5
                self.damage -= 0.5
            case "orange":
                self.health *= 5
            case "green":
                self.speed += 2
                self.damage += 2
            case "blue":
                self.speed += 5
                self.damage += 5
            case "purple":
                self.speed += 5
                self.damage += 10
            case "final":
                self.health = variables.health * variables.final_boss_multiplier
                self.speed += 5
                self.damage *= self.random_multiplier
            case _:
                raise ValueError(f"Unknown boss color: {self.color}")

    def __repr__(self):
        return f"Boss(color={self.color}, health={self.health}, speed={self.speed}, damage={self.damage})"


class Spawner:
    @staticmethod
    def create(enemy_type="enemy", color="red"):
        enemy_type = enemy_type.lower()
        color = color.lower()

        match enemy_type:
            case "enemy":
                return Enemy(color)
            case "boss":
                return Boss(color)
            case _:
                raise ValueError(f"Unknown enemy type: {enemy_type}")
