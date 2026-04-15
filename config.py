"""
Configurazione globale del gioco Cyber-Tower: Echoes of Industry
Contiene costanti, risoluzioni e impostazioni generali.
"""

# ============================================================================
# SCHERMO E GRAFICA
# ============================================================================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "Cyber-Tower: Echoes of Industry"

# Colori (RGB)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_DARK_GRAY = (30, 30, 30)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_CYAN = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_RED = (255, 50, 50)
COLOR_GREEN = (50, 255, 50)
COLOR_YELLOW = (255, 255, 0)

# ============================================================================
# GAMEPLAY
# ============================================================================
PLAYER_MAX_HEALTH = 4  # 4 cuori
PLAYER_START_POSITION = (100, 300)

# Gravità e movimento
GRAVITY = 0.5
PLAYER_MAX_SPEED = 10
PLAYER_ACCELERATION = 0.8
PLAYER_FRICTION = 0.85
PLAYER_JUMP_FORCE = -15

# ============================================================================
# LIVELLI
# ============================================================================
TOTAL_FLOORS = 18  # Piani 1-17 + Piano 18 finale (Piano 0 è l'hub)
HUB_FLOOR = 0
FINAL_FLOOR = 18

# ============================================================================
# INVENTARIO E ECONOMIA
# ============================================================================
MAX_INVENTORY_SLOTS = 12
COINS_DROP_MIN = 1
COINS_DROP_MAX = 5

# ============================================================================
# STATES
# ============================================================================
STATE_MENU = "menu"
STATE_HUB = "hub"
STATE_LEVEL = "level"
STATE_INVENTORY = "inventory"
STATE_GAMEOVER = "gameover"
STATE_PAUSED = "paused"

# ============================================================================
# DEBUG
# ============================================================================
DEBUG_MODE = False  # Attiva visualizzazione di hitbox e info debug
