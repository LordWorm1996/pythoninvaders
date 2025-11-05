from tkinter import Variable
import pygame
import variables


def red_enemy():
    health = variables.health
    speed = variables.speed
    damage = variables.damage


def yellow_enemy():
    health = variables.health
    speed = variables.speed * 5
    damage = variables.damage - 0.5


def orange_enemy():
    health = variables.health * 10
    speed = variables.speed - 0.5
    damage = 0


def green_enemy():
    health = variables.health + 1
    speed = variables.speed + 1
    damage = variables.damage + 1


def blue_enemy():
    health = variables.health + 5
    speed = variables.speed + 2
    damage = variables.damage + 2


def purple_enemy():
    health = variables.health + 10
    speed = variables.speed + 2
    damage = variables.damage + 5


def special_enemy():
    health = variables.health * variables.random_multiplier
    speed = variables.speed * variables.random_multiplier
    damage = variables.damage * variables.random_multiplier


def red_boss():
    health = variables.health * variables.boss_multiplier
    speed = variables.speed
    damage = variables.damage


def yellow_boss():
    health = variables.health * variables.boss_multiplier
    speed = variables.speed * 5
    damage = variables.damage - 0.5


def orange_boss():
    health = variables.health * 5 * variables.boss_multiplier
    speed = variables.speed
    damage = variables.damage


def green_boss():
    health = variables.health * variables.boss_multiplier
    speed = variables.speed + 2
    damage = variables.damage + 2


def blue_boss():
    health = variables.health * variables.boss_multiplier
    speed = variables.speed + 5
    damage = variables.damage + 5


def purple_boss():
    health = variables.health * variables.boss_multiplier
    speed = variables.speed + 5
    damage = variables.damage + 10


def final_boss():
    health = variables.health * variables.final_boss_multiplier
    speed = variables.speed + 5
    damage = variables.damage * variables.random_multiplier
