"""
class BossManager:
    def __init__(self, bosses, boss_bullets):
        self.bosses = bosses
        self.boss_bullets = boss_bullets

    def update(self, dt, screen_size, player_pos):
        for boss in list(self.bosses):
            boss.update(dt, screen_size, target_pos=player_pos)
"""
