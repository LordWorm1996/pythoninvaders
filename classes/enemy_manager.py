class EnemyManager:
    def __init__(self, enemies, enemy_bullets):
        self.enemies = enemies
        self.enemy_bullets = enemy_bullets

    def update(self, dt, screen_size, player_pos):
        for enemy in list(self.enemies):
            enemy.update(dt, screen_size, target_pos=player_pos)
