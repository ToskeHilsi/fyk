"""
FlyKnight Game - Configuration and Constants
"""

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TITLE = "FlyKnight - Dungeon Crawler"

# Network settings
DEFAULT_PORT = 5555
MAX_PLAYERS = 4
NETWORK_TICK_RATE = 30  # Updates per second

# Camera settings
CAMERA_SMOOTH = 0.1

# Player settings
PLAYER_SIZE = 32
PLAYER_SPEED = 200  # pixels per second
PLAYER_SPRINT_MULTIPLIER = 1.5
PLAYER_MAX_HP = 100
PLAYER_MAX_STAMINA = 100
PLAYER_STAMINA_REGEN = 30  # per second
PLAYER_INVENTORY_SIZE = 20

# Combat settings
ATTACK_STAMINA_COST = 15
BLOCK_STAMINA_COST_PER_HIT = 10
SPRINT_STAMINA_COST = 40  # per second

# Weapon stats: (damage, attack_speed, range, stamina_cost, two_handed)
WEAPON_STATS = {
    'sword': (30, 1.0, 50, 15, False),
    'hammer': (60, 0.5, 50, 20, True),
    'daggers': (30, 1.5, 35, 12, True),
    'spear': (30, 0.6, 75, 18, True)
}

# Shield stats: (block_amount, stamina_cost_per_block)
SHIELD_STATS = {
    'parrying_buckler': (0.3, 5),
    'soldier_board': (0.5, 10),
    'tower_shield': (0.7, 15)
}

# Armor stats: (damage_reduction, stamina_regen_multiplier)
ARMOR_STATS = {
    'knight': (0.3, 1.0),
    'samurai': (0.6, 0.5),
    'ranger': (0.15, 0.9)
}

# Enemy settings
ENEMY_STATS = {
    'larva': {
        'size': 20,
        'speed': 80,
        'hp': 30,
        'damage': 10,
        'group_size': (5, 8),
        'spawn_weight': 50,
        'detection_range': 300,
        'jump_speed': 400,
        'jump_cooldown': 2.0
    },
    'ant': {
        'size': 28,
        'speed': 120,
        'hp': 60,
        'damage': 20,
        'group_size': (1, 2),
        'spawn_weight': 35,
        'detection_range': 250,
        'bow_chance': 0.1,
        'bow_range': 400,
        'bow_cooldown': 2.5
    },
    'wasp': {
        'size': 32,
        'speed': 140,
        'hp': 100,
        'damage': 35,
        'group_size': (1, 1),
        'spawn_weight': 15,
        'detection_range': 300,
        'wander_radius': 150
    }
}

# Drop rates (chance per enemy)
DROP_RATES = {
    'larva': {
        'sword': 0.05,
    },
    'ant': {
        'sword': 0.1,
        'daggers': 0.02,
        'spear': 0.02,
        'parrying_buckler': 0.05,
        'soldier_board': 0.03,
        'ranger_helmet': 0.01,
        'ranger_chestplate': 0.01,
        'ranger_greaves': 0.01
    },
    'wasp': {
        'hammer': 0.05,
        'tower_shield': 0.03,
        'samurai_helmet': 0.02,
        'samurai_chestplate': 0.02,
        'samurai_greaves': 0.02
    }
}

# Room settings
ROOM_MIN_SIZE = 400
ROOM_MAX_SIZE = 700
ROOM_PADDING = 100
TILE_SIZE = 32

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 50, 200)
YELLOW = (200, 200, 50)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
GOLD = (255, 215, 0)

# UI Colors
UI_BG = (40, 40, 40, 200)
UI_BORDER = (200, 200, 200)
UI_TEXT = WHITE
UI_HIGHLIGHT = (100, 150, 200)
