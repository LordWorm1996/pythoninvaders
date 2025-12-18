import xml.etree.ElementTree as ET
from pathlib import Path


class BossLoader:
    pattern_registry = {}

    @classmethod
    def register_pattern(cls, name, pattern_func):
        cls.pattern_registry[name] = pattern_func

    @classmethod
    def get_pattern(cls, name):
        return cls.pattern_registry.get(name)

    @classmethod
    def load_waves(cls, xml_path):
        path = Path(xml_path)
        if not path.exists():
            raise FileNotFoundError(f"Wave XML file not found: {xml_path}")

        root = ET.parse(path).getroot()
        return [cls.parse_wave(wave_elem) for wave_elem in root.findall('wave')]

    @classmethod
    def parse_wave(cls, wave_elem):
        wave_data = {
            'number': int(wave_elem.get('number', 1)),
            'enemies': [],
            'bosses': [],
        }

        grid_elem = wave_elem.find('grid')
        if grid_elem is not None:
            wave_data['grid'] = cls.parse_grid(grid_elem)

        for enemy_elem in wave_elem.findall('enemy'):
            wave_data['enemies'].append(cls.parse_enemy(enemy_elem))

        for boss_elem in wave_elem.findall('boss'):
            wave_data['bosses'].append(cls.parse_boss(boss_elem))

        return wave_data

    @classmethod
    def parse_grid(cls, grid_elem):
        grid_data = {
            'rows': int(grid_elem.get('rows', 1)),
            'cols': int(grid_elem.get('cols', 1)),
            'start_x': int(grid_elem.get('start_x', 100)),
            'start_y': int(grid_elem.get('start_y', 50)),
            'spacing_x': int(grid_elem.get('spacing_x', 60)),
            'spacing_y': int(grid_elem.get('spacing_y', 60)),
            'default_health': int(grid_elem.get('health', 1)),
            'default_attack_pattern': grid_elem.get('attack_pattern', 'straight'),
            'default_damage': int(grid_elem.get('damage', 1)),
            'default_aim': grid_elem.get('aim', 'player'),
        }

        enemies = []
        for enemy_elem in grid_elem.findall('enemy'):
            data = cls.parse_enemy(enemy_elem)
            if 'row' in enemy_elem.attrib:
                data['row'] = int(enemy_elem.get('row'))
            if 'col' in enemy_elem.attrib:
                data['col'] = int(enemy_elem.get('col'))
            enemies.append(data)

        grid_data['enemies'] = enemies
        return grid_data

    @classmethod
    def parse_enemy(cls, enemy_elem):
        enemy = {
            'x': int(enemy_elem.get('x', 0)),
            'y': int(enemy_elem.get('y', 0)),
            'health': int(enemy_elem.get('health', 1)),
            'damage': int(enemy_elem.get('damage', 1)),
            'attack_pattern': enemy_elem.get('attack_pattern', 'straight'),
            'speed': int(enemy_elem.get('speed', 0)),
            'aim': enemy_elem.get('aim', 'player'),
        }

        if enemy_elem.get('image'):
            enemy['image'] = enemy_elem.get('image')
        if enemy_elem.get('color'):
            enemy['color'] = enemy_elem.get('color')
        return enemy

    @classmethod
    def parse_boss(cls, boss_elem):
        boss = {
            'x': int(boss_elem.get('x', 0)),
            'y': int(boss_elem.get('y', 0)),
            'health': int(boss_elem.get('health', 1)),
            'damage': int(boss_elem.get('damage', 1)),
            'speed': int(boss_elem.get('speed', 0)),
            'aim': boss_elem.get('aim', 'player'),
            'color': boss_elem.get('color', 'red'),
        }
        if boss_elem.get('attack_pattern'):
            boss['attack_pattern'] = boss_elem.get('attack_pattern')
        return boss
