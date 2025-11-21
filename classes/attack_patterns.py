import random
import pygame


def get_owner_positions(owner, fallback_pos):
    if owner and hasattr(owner, 'get_fire_positions'):
        positions = owner.get_fire_positions()
        if positions:
            return positions
    return [fallback_pos]


def straight_pattern(pos, direction, bullet_class, bullet_args, owner):
    args = dict(bullet_args or {})
    positions = get_owner_positions(owner, pos)
    return [bullet_class(muzzle_pos, direction, owner=owner, **args) for muzzle_pos in positions]


def spread_pattern(pos, direction, bullet_class, bullet_args, owner):
    args = dict(bullet_args or {})
    base = pygame.math.Vector2(direction or (0, -1))
    positions = get_owner_positions(owner, pos)
    bullets = []
    for muzzle_pos in positions:
        for offset in (-0.2, 0, 0.2):
            bullets.append(bullet_class(muzzle_pos, base.rotate_rad(offset), owner=owner, **args))
    return bullets


def laser_pattern(pos, direction, bullet_class, bullet_args, owner):
    args = {
        'damage': 3,
        'duration': 2500,
        'length': 450,
        'width': 10,
        'color': (0, 255, 255),
    }
    args.update(bullet_args or {})
    positions = get_owner_positions(owner, pos)
    return [bullet_class(muzzle_pos, direction, owner=owner, **args) for muzzle_pos in positions]


def thunder_pattern(pos, direction, bullet_class, bullet_args, owner):
    args = dict(bullet_args or {})
    spread = args.pop('spread', 0.08)
    speed_variance = args.pop('speed_variance', 30)
    base_dir = pygame.math.Vector2(direction or (0, -1))
    positions = get_owner_positions(owner, pos)
    bullets = []
    for muzzle_pos in positions:
        jitter = random.uniform(-spread, spread)
        dir_vec = base_dir.rotate_rad(jitter)
        speed_offset = random.uniform(-speed_variance, speed_variance)
        shot_args = dict(args)
        if 'speed' in shot_args:
            shot_args['speed'] = max(200, shot_args['speed'] + speed_offset)
        bullets.append(bullet_class(muzzle_pos, dir_vec, owner=owner, **shot_args))
    return bullets
