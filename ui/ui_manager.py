"""
UI Manager: Gestore centralizzato dell'interfaccia utente.

Responsabilità:
- Rendering HUD
- Rendering Inventario
- Rendering Dialoghi
- Rendering menu in-game
"""

import pygame
from config import *
from items import ItemType


class UIManager:
    """Gestisce l'interfaccia utente del gioco."""

    def __init__(self):
        """Inizializza il manager UI."""
        self.font_large = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
        self.font_tiny = pygame.font.Font(None, 20)

        # Stato UI
        self.show_inventory = False
        self.show_shop = False
        self.selected_inventory_slot = 0
        self.selected_shop_item = 0

    # ========================================================================
    # HUD PRINCIPALE
    # ========================================================================

    def render_main_hud(self, surface, player, level_state, camera=None):
        """
        Disegna l'HUD principale.

        Args:
            surface: Surface pygame
            player: Oggetto Player
            level_state: LevelState (per informazioni livello)
            camera: Oggetto Camera (opzionale)
        """
        y_offset = 20

        # ====== SALUTE ======
        health_text = self.font_normal.render(
            f"❤️  {player.health}/{player.max_health}",
            True,
            COLOR_RED,
        )
        surface.blit(health_text, (20, y_offset))

        # ====== MONETE ======
        coins_collected = getattr(level_state, "collected_coins", 0)
        coins_text = self.font_normal.render(
            f"💰 {coins_collected}", True, COLOR_YELLOW
        )
        surface.blit(coins_text, (20, y_offset + 40))

        # ====== PIANO ======
        floor_text = self.font_normal.render(
            f"📍 Piano {level_state.floor_number}", True, COLOR_CYAN
        )
        surface.blit(floor_text, (20, y_offset + 80))

        # ====== NEMICI ======
        enemy_count = level_state.enemy_manager.get_enemy_count()
        enemies_text = self.font_small.render(
            f"Nemici: {enemy_count}", True, COLOR_RED
        )
        surface.blit(enemies_text, (20, y_offset + 130))

        # ====== WAVE ======
        from levels.waves import get_waves_for_level
        total_waves = len(get_waves_for_level(level_state.floor_number))
        wave_text = self.font_small.render(
            f"Wave: {level_state.current_wave_index}/{total_waves}",
            True,
            COLOR_GREEN,
        )
        surface.blit(wave_text, (20, y_offset + 155))

        # ====== TEMPO ======
        time_text = self.font_tiny.render(
            f"⏱️  {level_state.level_time:.1f}s", True, COLOR_LIGHT_GRAY
        )
        surface.blit(time_text, (SCREEN_WIDTH - 200, y_offset))

        # ====== CONTROLLI HINT ======
        controls_text = self.font_tiny.render(
            "I: Inventario | E: Interagisci | ESC: Pausa", True, COLOR_LIGHT_GRAY
        )
        surface.blit(
            controls_text, (SCREEN_WIDTH - 450, SCREEN_HEIGHT - 30)
        )

    # ========================================================================
    # INVENTARIO UI
    # ========================================================================

    def render_inventory(self, surface, inventory, player_coins):
        """
        Disegna l'interfaccia inventario.

        Args:
            surface: Surface pygame
            inventory: Oggetto Inventory
            player_coins: Monete attuali
        """
        # ====== BACKGROUND OVERLAY ======
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(COLOR_BLACK)
        surface.blit(overlay, (0, 0))

        # ====== FINESTRA INVENTARIO ======
        inv_width = 600
        inv_height = 500
        inv_x = (SCREEN_WIDTH - inv_width) // 2
        inv_y = (SCREEN_HEIGHT - inv_height) // 2
        inv_rect = pygame.Rect(inv_x, inv_y, inv_width, inv_height)

        # Background
        pygame.draw.rect(surface, COLOR_DARK_GRAY, inv_rect)
        pygame.draw.rect(surface, COLOR_CYAN, inv_rect, 3)

        # ====== TITOLO ======
        title = self.font_normal.render("🎒 INVENTARIO", True, COLOR_CYAN)
        surface.blit(title, (inv_x + 20, inv_y + 10))

        # ====== INFO ======
        used_slots = inventory.get_used_slots()
        total_slots = inventory.max_slots
        info_text = self.font_small.render(
            f"Slot: {used_slots}/{total_slots} | Valore: {inventory.get_value()} 💰",
            True,
            COLOR_YELLOW,
        )
        surface.blit(info_text, (inv_x + 20, inv_y + 50))

        # ====== ITEMS ======
        y_offset = inv_y + 90
        for i, item in enumerate(inventory.get_slots()):
            # Sfondo slot
            slot_rect = pygame.Rect(inv_x + 20, y_offset, inv_width - 40, 30)
            slot_color = COLOR_MAGENTA if i == self.selected_inventory_slot else COLOR_DARK_GRAY
            pygame.draw.rect(surface, slot_color, slot_rect)
            pygame.draw.rect(surface, COLOR_LIGHT_GRAY, slot_rect, 1)

            if item is None:
                empty_text = self.font_small.render(f"[{i + 1}] Vuoto", True, COLOR_LIGHT_GRAY)
            else:
                icon = item.get_icon()
                name = item.get_name()
                qty_str = f" x{item.quantity}" if item.is_stackable() else ""
                text_str = f"[{i + 1}] {icon} {name}{qty_str}"
                empty_text = self.font_small.render(text_str, True, item.get_rarity_color())

            surface.blit(empty_text, (inv_x + 30, y_offset + 5))
            y_offset += 35

        # ====== ISTRUZIONI ======
        instr_y = inv_y + inv_height - 30
        instructions = [
            "↑↓: Seleziona | C: Combina | I: Chiudi",
        ]
        for instr in instructions:
            instr_text = self.font_small.render(instr, True, COLOR_LIGHT_GRAY)
            surface.blit(instr_text, (inv_x + 20, instr_y))
            instr_y -= 25

    # ========================================================================
    # HUB UI
    # ========================================================================

    def render_hub_stats(self, surface, game_manager):
        """
        Disegna le statistiche all'hub.

        Args:
            surface: Surface pygame
            game_manager: Oggetto GameManager
        """
        player_state = game_manager.player_state

        # ====== BACKGROUND ======
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(220)
        overlay.fill(COLOR_BLACK)
        surface.blit(overlay, (0, 0))

        # ====== TITLE ======
        title = self.font_large.render("📊 STATISTICHE", True, COLOR_MAGENTA)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        surface.blit(title, title_rect)

        # ====== STATS ======
        stats = [
            f"❤️  Salute: {player_state['health']}/{player_state.get('max_health', 4)}",
            f"💰 Monete: {player_state['coins']}",
            f"📍 Piano: {player_state['current_floor']}",
            f"📦 Slot Inventario: {len(player_state['inventory'])}",
        ]

        y_offset = SCREEN_HEIGHT // 2 - 80
        for stat in stats:
            stat_text = self.font_normal.render(stat, True, COLOR_CYAN)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            surface.blit(stat_text, stat_rect)
            y_offset += 60

        # ====== ISTRUZIONI ======
        instr = self.font_small.render("Premi ESC per chiudere", True, COLOR_LIGHT_GRAY)
        instr_rect = instr.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        surface.blit(instr, instr_rect)

    # ========================================================================
    # UTILITY
    # ========================================================================

    def toggle_inventory(self):
        """Toggle visualizzazione inventario."""
        self.show_inventory = not self.show_inventory

    def select_next_inventory_slot(self):
        """Seleziona lo slot successivo."""
        self.selected_inventory_slot = (self.selected_inventory_slot + 1) % 12

    def select_prev_inventory_slot(self):
        """Seleziona lo slot precedente."""
        self.selected_inventory_slot = (self.selected_inventory_slot - 1) % 12

    @staticmethod
    def render_text_centered(surface, text, font, color, y):
        """
        Disegna testo centrato.

        Args:
            surface: Surface pygame
            text: Testo da disegnare
            font: Font pygame
            color: Colore
            y: Posizione Y
        """
        text_surf = font.render(text, True, color)
        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, y))
        surface.blit(text_surf, text_rect)
