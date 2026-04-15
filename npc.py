"""
Sistema NPC: Gestisce personaggi non-giocatori con dialoghi e shop.

Responsabilità:
- Dialoghi multi-linea
- Shop integrate all'NPC
- Interazione con player
- Rendering NPC
"""

import pygame
from items import Item, ItemType, ITEM_PROPERTIES
from config import *


class Dialog:
    """Rappresenta una finestra di dialogo."""

    def __init__(self, lines, options=None):
        """
        Inizializza un dialogo.

        Args:
            lines: Lista di righe di testo
            options: Dizionario {label -> dialog_padre}
        """
        self.lines = lines
        self.options = options or {}
        self.current_line = 0

    def get_current_line(self):
        """Ritorna la riga attuale."""
        if self.current_line < len(self.lines):
            return self.lines[self.current_line]
        return None

    def next_line(self):
        """Passa alla riga successiva."""
        self.current_line += 1
        return self.current_line < len(self.lines)

    def is_complete(self):
        """Verifica se dialogo completato."""
        return self.current_line >= len(self.lines)

    def get_options(self):
        """Ritorna le opzioni disponibili."""
        return list(self.options.keys())


class ShopItem:
    """Rappresenta un item in vendita nel shop."""

    def __init__(self, item_type, price, quantity=1):
        """
        Inizializza un item di shop.

        Args:
            item_type: Tipo di item
            price: Prezzo in monete
            quantity: Quantità disponibile (-1 = infinita)
        """
        self.item = Item(item_type, 1)
        self.price = price
        self.quantity_available = quantity  # -1 = unlimited

    def can_buy(self, player_coins):
        """Verifica se il giocatore può comprare."""
        return player_coins >= self.price and (
            self.quantity_available < 0 or self.quantity_available > 0
        )

    def buy(self):
        """Acquista il prodotto."""
        if self.quantity_available > 0:
            self.quantity_available -= 1
        return self.item


class NPC:
    """Rappresenta un personaggio non-giocatore."""

    def __init__(self, name, x, y, dialog, shop_items=None):
        """
        Inizializza un NPC.

        Args:
            name: Nome dell'NPC
            x, y: Posizione
            dialog: Dialog di benvenuto
            shop_items: Lista di ShopItem (opzionale)
        """
        self.name = name
        self.rect = pygame.Rect(x, y, 32, 32)
        self.start_dialog = dialog
        self.current_dialog = None
        self.shop_items = shop_items or []
        self.color = COLOR_GREEN
        self.is_talking = False

    def start_conversation(self, player):
        """Inizia una conversazione con il player."""
        self.current_dialog = self.start_dialog
        self.is_talking = True
        print(f"💬 {self.name}: {self.current_dialog.get_current_line()}")

    def advance_dialog(self):
        """Avanza il dialogo."""
        if self.current_dialog is None:
            return False

        if not self.current_dialog.next_line():
            self.is_talking = False
            print(f"✓ Conversazione completata")
            return False

        print(f"💬 {self.name}: {self.current_dialog.get_current_line()}")
        return True

    def end_conversation(self):
        """Termina la conversazione."""
        self.is_talking = False
        self.current_dialog = None

    def render(self, surface, camera):
        """Disegna l'NPC sullo schermo."""
        screen_x, screen_y = camera.world_to_screen(self.rect.x, self.rect.y)

        # Corpo NPC
        pygame.draw.rect(
            surface,
            self.color,
            (screen_x, screen_y, self.rect.width, self.rect.height),
        )
        pygame.draw.rect(
            surface,
            COLOR_WHITE,
            (screen_x, screen_y, self.rect.width, self.rect.height),
            2,
        )

        # Nome sopra
        font = pygame.font.Font(None, 24)
        name_text = font.render(self.name, True, self.color)
        surface.blit(name_text, (int(screen_x) - 10, int(screen_y) - 25))

        # Freccia se interagibile
        if not self.is_talking:
            arrow_text = font.render("⬆️", True, COLOR_YELLOW)
            surface.blit(arrow_text, (int(screen_x) + 5, int(screen_y) - 45))

    def render_dialog(self, surface):
        """Disegna il dialogo sullo schermo."""
        if not self.is_talking or self.current_dialog is None:
            return

        # ====== DIALOG BOX ======
        dialog_height = 100
        dialog_y = SCREEN_HEIGHT - dialog_height - 20
        dialog_rect = pygame.Rect(20, dialog_y, SCREEN_WIDTH - 40, dialog_height)

        # Background
        pygame.draw.rect(surface, COLOR_BLACK, dialog_rect)
        pygame.draw.rect(surface, COLOR_CYAN, dialog_rect, 2)

        # Nome NPC
        font_name = pygame.font.Font(None, 28)
        name_text = font_name.render(f"{self.name}:", True, COLOR_CYAN)
        surface.blit(name_text, (40, dialog_y + 10))

        # Testo dialogo
        font_dialog = pygame.font.Font(None, 24)
        current_line = self.current_dialog.get_current_line()
        if current_line:
            dialog_text = font_dialog.render(current_line, True, COLOR_WHITE)
            surface.blit(dialog_text, (40, dialog_y + 40))

        # Istruzioni
        font_small = pygame.font.Font(None, 20)
        if not self.current_dialog.is_complete():
            instructions = font_small.render(
                "Premi E per continuare", True, COLOR_LIGHT_GRAY
            )
        else:
            instructions = font_small.render(
                "Premi E per chiudere", True, COLOR_LIGHT_GRAY
            )
        surface.blit(
            instructions,
            (SCREEN_WIDTH - 300, dialog_y + dialog_height - 30),
        )

    def render_shop(self, surface):
        """Disegna il menu shop."""
        if not self.shop_items:
            return

        # ====== SHOP WINDOW ======
        shop_width = 400
        shop_height = 300
        shop_x = (SCREEN_WIDTH - shop_width) // 2
        shop_y = (SCREEN_HEIGHT - shop_height) // 2
        shop_rect = pygame.Rect(shop_x, shop_y, shop_width, shop_height)

        # Background
        pygame.draw.rect(surface, COLOR_DARK_GRAY, shop_rect)
        pygame.draw.rect(surface, COLOR_MAGENTA, shop_rect, 3)

        # Titolo
        font_title = pygame.font.Font(None, 32)
        title = font_title.render(f"🛍️ {self.name} - Shop", True, COLOR_MAGENTA)
        surface.blit(title, (shop_x + 20, shop_y + 10))

        # Item disponibili
        font_item = pygame.font.Font(None, 24)
        y_offset = shop_y + 60

        for i, shop_item in enumerate(self.shop_items):
            # Item name e icon
            item_name = shop_item.item.get_name()
            icon = shop_item.item.get_icon()
            price = shop_item.price

            text = f"{icon} {item_name} - {price}💰"
            item_text = font_item.render(text, True, shop_item.item.get_rarity_color())
            surface.blit(item_text, (shop_x + 30, y_offset))

            y_offset += 40

    def get_shop_items(self):
        """Ritorna gli item disponibili nel shop."""
        return self.shop_items

    def buy_item(self, item_idx, player_coins):
        """
        Acquista un item dallo shop.

        Args:
            item_idx: Indice dell'item
            player_coins: Monete del player

        Returns:
            Tuple (Item acquistato, prezzo) o (None, 0) se fallito
        """
        if item_idx < 0 or item_idx >= len(self.shop_items):
            return None, 0

        shop_item = self.shop_items[item_idx]

        if not shop_item.can_buy(player_coins):
            print(f"❌ Non puoi permetterti {shop_item.item.get_name()}")
            return None, 0

        item = shop_item.buy()
        print(f"✓ Acquistato {item.get_name()} per {shop_item.price} monete")
        return item, shop_item.price

    def is_near_player(self, player, distance=100):
        """
        Verifica se il player è abbastanza vicino.

        Args:
            player: Oggetto Player
            distance: Distanza minima

        Returns:
            True se vicino
        """
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        actual_distance = (dx**2 + dy**2) ** 0.5
        return actual_distance < distance


# ============================================================================
# NPC FACTORY - NPCS PREDEFINITI
# ============================================================================

def create_merchant():
    """Crea l'NPC Commerciante."""
    dialog = Dialog([
        "Benvenuto nel mio negozio!",
        "Vendo i migliori upgrade della città.",
        "Dai un'occhiata ai miei prodotti.",
    ])

    shop_items = [
        ShopItem(ItemType.HEALTH_POTION, 50, -1),
        ShopItem(ItemType.UPGRADE_DAMAGE, 200, -1),
        ShopItem(ItemType.UPGRADE_SPEED, 200, -1),
        ShopItem(ItemType.UPGRADE_HEALTH, 250, -1),
    ]

    return NPC("Commerciante", 400, 600, dialog, shop_items)


def create_elder():
    """Crea l'NPC Anziano (supporto)."""
    dialog = Dialog([
        "Ah, ciao giovane guerriero!",
        "Vedi di fare attenzione nella torre.",
        "Molti pericoli ti aspettano...",
    ])

    return NPC("Anziano Saggio", 300, 600, dialog)


def create_forge_master():
    """Crea l'NPC Mastro della Fucina."""
    dialog = Dialog([
        "Benvenuto alla mia fucina!",
        "Qui puoi combinare gli oggetti.",
        "Usa il tuo inventario saggiamente.",
    ])

    shop_items = [
        ShopItem(ItemType.SCRAP_METAL, 30, -1),
        ShopItem(ItemType.ENERGY_CORE, 100, -1),
    ]

    return NPC("Mastro della Fucina", 600, 600, dialog, shop_items)
