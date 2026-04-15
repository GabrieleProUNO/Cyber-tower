"""
Sistema Item: Gestisce oggetti collezionabili e inventario.

Responsabilità:
- Definire tipi di oggetti
- Gestire proprietà degli oggetti
- Sistema di ricette/combinazione
- Rendering item nel mondo
"""

import pygame
import math
from config import *


# ============================================================================
# ITEM TYPES
# ============================================================================
class ItemType:
    """Constanti per tipi di oggetto."""
    COIN = "coin"
    HEALTH_POTION = "health_potion"
    SCRAP_METAL = "scrap_metal"
    ENERGY_CORE = "energy_core"
    BLUEPRINT = "blueprint"
    UPGRADE_DAMAGE = "upgrade_damage"
    UPGRADE_SPEED = "upgrade_speed"
    UPGRADE_HEALTH = "upgrade_health"
    KEY = "key"


# ============================================================================
# ITEM PROPERTIES
# ============================================================================
ITEM_PROPERTIES = {
    ItemType.COIN: {
        "name": "Moneta",
        "description": "Valuta di base",
        "icon": "💰",
        "stackable": True,
        "rarity": "common",
        "value": 1,
    },
    ItemType.HEALTH_POTION: {
        "name": "Pozione di Guarigione",
        "description": "Recupera 1 punto vita",
        "icon": "🧪",
        "stackable": True,
        "rarity": "uncommon",
        "value": 50,
    },
    ItemType.SCRAP_METAL: {
        "name": "Rottame Metallico",
        "description": "Materiale di crafting",
        "icon": "⚙️",
        "stackable": True,
        "rarity": "common",
        "value": 10,
    },
    ItemType.ENERGY_CORE: {
        "name": "Core Energetico",
        "description": "Nucleo di potenza",
        "icon": "⚡",
        "stackable": True,
        "rarity": "rare",
        "value": 100,
    },
    ItemType.BLUEPRINT: {
        "name": "Progetto Tecnico",
        "description": "Piano per upgrades",
        "icon": "📋",
        "stackable": False,
        "rarity": "rare",
        "value": 75,
    },
    ItemType.UPGRADE_DAMAGE: {
        "name": "Upgrade Danno",
        "description": "+1 Danno proiettili",
        "icon": "💥",
        "stackable": False,
        "rarity": "epic",
        "value": 200,
    },
    ItemType.UPGRADE_SPEED: {
        "name": "Upgrade Velocità",
        "description": "+2 velocità movimento",
        "icon": "⚡",
        "stackable": False,
        "rarity": "epic",
        "value": 200,
    },
    ItemType.UPGRADE_HEALTH: {
        "name": "Upgrade Salute",
        "description": "+1 massimo vita",
        "icon": "❤️",
        "stackable": False,
        "rarity": "epic",
        "value": 250,
    },
    ItemType.KEY: {
        "name": "Chiave Antica",
        "description": "Apre porte speciali",
        "icon": "🔑",
        "stackable": False,
        "rarity": "epic",
        "value": 150,
    },
}

# ============================================================================
# RICETTE COMBINAZIONE
# ============================================================================
RECIPES = {
    # (item1, item2) -> output
    (ItemType.SCRAP_METAL, ItemType.ENERGY_CORE): ItemType.UPGRADE_DAMAGE,
    (ItemType.SCRAP_METAL, ItemType.SCRAP_METAL): ItemType.BLUEPRINT,
    (ItemType.ENERGY_CORE, ItemType.BLUEPRINT): ItemType.UPGRADE_SPEED,
}

# Colori per rarità
RARITY_COLORS = {
    "common": COLOR_WHITE,
    "uncommon": COLOR_GREEN,
    "rare": COLOR_CYAN,
    "epic": COLOR_MAGENTA,
}


class Item:
    """Rappresenta un singolo oggetto nel gioco."""

    def __init__(self, item_type, quantity=1):
        """
        Inizializza un item.

        Args:
            item_type: Tipo di oggetto (da ItemType)
            quantity: Quantità (default 1)
        """
        self.item_type = item_type
        self.quantity = quantity
        self.properties = ITEM_PROPERTIES.get(item_type, {})

    def get_name(self):
        """Ritorna il nome dell'oggetto."""
        return self.properties.get("name", "Unknown Item")

    def get_description(self):
        """Ritorna la descrizione."""
        return self.properties.get("description", "")

    def get_icon(self):
        """Ritorna l'icona emoji."""
        return self.properties.get("icon", "?")

    def get_value(self):
        """Ritorna il valore in monete."""
        return self.properties.get("value", 0) * self.quantity

    def is_stackable(self):
        """Verifica se stackabile."""
        return self.properties.get("stackable", False)

    def get_rarity(self):
        """Ritorna la rarità."""
        return self.properties.get("rarity", "common")

    def get_rarity_color(self):
        """Ritorna il colore della rarità."""
        rarity = self.get_rarity()
        return RARITY_COLORS.get(rarity, COLOR_WHITE)

    def can_combine_with(self, other_item):
        """
        Verifica se questo item può combinarsi con un altro.

        Args:
            other_item: Altro Item

        Returns:
            Tipo di item risultato, o None
        """
        if not isinstance(other_item, Item):
            return None

        # Ricerca nelle ricette
        key1 = (self.item_type, other_item.item_type)
        key2 = (other_item.item_type, self.item_type)

        if key1 in RECIPES:
            return RECIPES[key1]
        elif key2 in RECIPES:
            return RECIPES[key2]

        return None

    def __repr__(self):
        """String representation."""
        if self.is_stackable():
            return f"{self.get_name()} x{self.quantity}"
        return self.get_name()


class WorldItem:
    """Rappresenta un item caduto nel mondo (da raccogliere)."""

    def __init__(self, item_type, world_x, world_y, quantity=1):
        """
        Inizializza un item nel mondo.

        Args:
            item_type: Tipo di oggetto
            world_x, world_y: Posizione mondo
            quantity: Quantità
        """
        self.item = Item(item_type, quantity)
        self.x = world_x
        self.y = world_y
        self.lifetime = 30.0  # Secondi prima di sparire
        self.age = 0.0
        self.bob_offset = 0.0  # Per animazione su/giù
        self.bob_speed = 2.0

    def update(self, dt):
        """Aggiorna l'item nel mondo."""
        self.age += dt
        self.bob_offset = math.sin(self.age * self.bob_speed) * 5

        return self.age < self.lifetime

    def render(self, surface, camera):
        """Disegna l'item nel mondo."""
        screen_x, screen_y = camera.world_to_screen(self.x, self.y + self.bob_offset)

        font = pygame.font.Font(None, 28)

        # Icona item
        icon_text = font.render(self.item.get_icon(), True, self.item.get_rarity_color())
        surface.blit(icon_text, (int(screen_x) - 14, int(screen_y) - 14))

        # Label quantità se stackabile
        if self.item.is_stackable() and self.item.quantity > 1:
            small_font = pygame.font.Font(None, 16)
            quantity_text = small_font.render(
                f"x{self.item.quantity}", True, COLOR_WHITE
            )
            surface.blit(quantity_text, (int(screen_x) + 5, int(screen_y) + 5))

    def get_rect(self):
        """Ritorna il rettangolo di collisione."""
        return pygame.Rect(self.x - 10, self.y - 10, 20, 20)

    def get_item(self):
        """Ritorna l'item (per raccolta)."""
        return self.item


# ============================================================================
# ITEM FACTORY
# ============================================================================
def create_item_from_drop(drop_data):
    """
    Crea un Item da dati di drop nemico.

    Args:
        drop_data: Dizionario con "type" e "amount"

    Returns:
        Item creato
    """
    if drop_data["type"] == "coins":
        return Item(ItemType.COIN, drop_data["amount"])
    elif drop_data["type"] == "healing":
        return Item(ItemType.HEALTH_POTION, drop_data["amount"])

    return None


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
def get_item_by_name(name):
    """Ritorna il tipo di item dal nome."""
    for item_type, props in ITEM_PROPERTIES.items():
        if props.get("name") == name:
            return item_type
    return None


def get_all_items():
    """Ritorna lista di tutti i tipi di item."""
    return list(ITEM_PROPERTIES.keys())

