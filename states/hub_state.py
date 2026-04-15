"""
Hub State (Piano 0) del gioco.
Zona sicura dove il giocatore può prepararsi prima di affrontare i livelli.
Qui può dialogare con NPC, acquistare potenziamenti e gestire l'inventario.
"""

import pygame
from config import *
from states.base_state import BaseState


class HubState(BaseState):
    """
    Schermata dell'Hub (Piano 0).
    Mostra lo stato del giocatore e opzioni per:
    - Iniziare un livello
    - Aprire inventario
    - Parlare con NPC
    """

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font_title = pygame.font.Font(None, 48)
        self.font_text = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.menu_options = ["Inizia Livello", "Inventario", "Menu Principale"]
        self.selected_option = 0

    def __enter__(self):
        """Inizializza l'Hub."""
        print("🏛️  Entra in HubState (Piano 0)")

    def handle_events(self, events):
        """Gestisce input nell'Hub."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(
                        self.menu_options
                    )
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(
                        self.menu_options
                    )
                elif event.key == pygame.K_RETURN:
                    self.select_option()
                elif event.key == pygame.K_ESCAPE:
                    self.change_state(STATE_MENU)

    def select_option(self):
        """Esegue l'azione dell'opzione selezionata."""
        if self.selected_option == 0:  # Inizia Livello
            # Passa al primo livello (Piano 1)
            current_floor = self.game_manager.player_state["current_floor"]
            next_floor = current_floor + 1 if current_floor == 0 else current_floor

            # Assicurati di non superare il numero massimo di piani
            if next_floor <= FINAL_FLOOR:
                self.game_manager.set_current_floor(next_floor)
                self.change_state(STATE_LEVEL)
            else:
                print("✓ Hai completato il gioco!")
                self.change_state(STATE_MENU)

        elif self.selected_option == 1:  # Inventario
            self.change_state(STATE_INVENTORY)

        elif self.selected_option == 2:  # Menu Principale
            self.change_state(STATE_MENU)

    def update(self, dt):
        """Update dell'Hub (logica minima)."""
        pass

    def render(self):
        """Disegna l'Hub sullo schermo."""
        for y in range(SCREEN_HEIGHT):
            t = y / max(1, SCREEN_HEIGHT - 1)
            color = (
                int(14 + 18 * t),
                int(20 + 24 * t),
                int(26 + 30 * t),
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        floor_band = pygame.Rect(0, SCREEN_HEIGHT - 130, SCREEN_WIDTH, 130)
        pygame.draw.rect(self.screen, (24, 34, 42), floor_band)
        pygame.draw.line(self.screen, (62, 150, 174), (0, SCREEN_HEIGHT - 130), (SCREEN_WIDTH, SCREEN_HEIGHT - 130), 2)

        # Titolo
        title = self.font_title.render("CYBER-TOWER - HUB (Piano 0)", True, COLOR_CYAN)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Stato del giocatore
        player_state = self.game_manager.player_state
        stats_panel = pygame.Rect(36, 102, 430, 150)
        pygame.draw.rect(self.screen, (18, 28, 38), stats_panel, border_radius=10)
        pygame.draw.rect(self.screen, (62, 132, 158), stats_panel, 2, border_radius=10)

        health_text = self.font_text.render(
            f"HP: {player_state['health']}/{PLAYER_MAX_HEALTH}",
            True,
            COLOR_RED,
        )
        health_rect = health_text.get_rect(topleft=(50, 120))
        self.screen.blit(health_text, health_rect)

        coins_text = self.font_text.render(
            f"Monete: {player_state['coins']}", True, COLOR_YELLOW
        )
        coins_rect = coins_text.get_rect(topleft=(50, 160))
        self.screen.blit(coins_text, coins_rect)

        floor_text = self.font_text.render(
            f"Piano Attuale: {player_state['current_floor']}", True, COLOR_GREEN
        )
        floor_rect = floor_text.get_rect(topleft=(50, 200))
        self.screen.blit(floor_text, floor_rect)

        # Menu opzioni
        y_start = SCREEN_HEIGHT // 2
        for i, option in enumerate(self.menu_options):
            color = COLOR_CYAN if i == self.selected_option else COLOR_LIGHT_GRAY
            option_text = self.font_text.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 60))
            option_panel = pygame.Rect(option_rect.left - 24, option_rect.top - 10, option_rect.width + 48, option_rect.height + 16)
            pygame.draw.rect(self.screen, (14, 24, 32), option_panel, border_radius=8)
            pygame.draw.rect(
                self.screen,
                (74, 144, 170) if i == self.selected_option else (48, 78, 96),
                option_panel,
                2,
                border_radius=8,
            )
            self.screen.blit(option_text, option_rect)

            # Freccia di selezione
            if i == self.selected_option:
                arrow = self.font_text.render(">", True, COLOR_YELLOW)
                arrow_rect = arrow.get_rect(right=option_rect.left - 20, centery=option_rect.centery)
                self.screen.blit(arrow, arrow_rect)

        # Istruzioni fondo
        instructions = self.font_small.render(
            "↑↓ Naviga | ENTER Seleziona | ESC Menu", True, COLOR_LIGHT_GRAY
        )
        instructions_rect = instructions.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        )
        self.screen.blit(instructions, instructions_rect)
