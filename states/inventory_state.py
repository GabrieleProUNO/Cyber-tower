"""
Inventory State: Schermata per gestire l'inventario del giocatore.
Mostra gli oggetti raccolti e permette di combinarli.
(Espanderemo nella Fase 5)
"""

import pygame
from config import *
from states.base_state import BaseState


class InventoryState(BaseState):
    """
    Schermata dell'Inventario.
    Placeholder per ora - espanderemo nella Fase 5 con logica di combinazione oggetti.

    Qui il giocatore:
    - Visualizza gli oggetti raccolti
    - Combinare oggetti per creare potenziamenti
    - Vendere/scambiare risorse
    """

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font_title = pygame.font.Font(None, 48)
        self.font_text = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

    def __enter__(self):
        """Inizializza l'inventario."""
        print("🎒 Entra in InventoryState")

    def handle_events(self, events):
        """Gestisce input nell'inventario."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                    self.change_state(STATE_HUB)

    def update(self, dt):
        """Logica di update dell'inventario."""
        pass

    def render(self):
        """Disegna l'inventario."""
        self.screen.fill(COLOR_DARK_GRAY)

        # Titolo
        title = self.font_title.render("INVENTARIO", True, COLOR_CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Stato inventario
        player_state = self.game_manager.player_state
        inventory = player_state["inventory"]

        if not inventory:
            empty_text = self.font_text.render(
                "Inventario vuoto", True, COLOR_LIGHT_GRAY
            )
            empty_rect = empty_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(empty_text, empty_rect)
        else:
            # Mostra oggetti (placeholder)
            items_text = self.font_text.render(
                f"Oggetti ({len(inventory)})", True, COLOR_YELLOW
            )
            items_rect = items_text.get_rect(topleft=(50, 120))
            self.screen.blit(items_text, items_rect)

            for i, item in enumerate(inventory[:10]):  # Max 10 visualizzati
                item_text = self.font_small.render(
                    f"  - {item}", True, COLOR_LIGHT_GRAY
                )
                item_rect = item_text.get_rect(topleft=(70, 160 + i * 30))
                self.screen.blit(item_text, item_rect)

        # Istruzioni
        instructions = self.font_small.render(
            "ESC o I per chiudere", True, COLOR_LIGHT_GRAY
        )
        instructions_rect = instructions.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        )
        self.screen.blit(instructions, instructions_rect)
