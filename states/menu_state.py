"""
Menu Principale del gioco.
Permette al giocatore di iniziare una nuova partita o uscire.
"""

import pygame
from config import *
from states.base_state import BaseState


class MenuState(BaseState):
    """
    Schermata del Menu Principale.
    Mostra opzioni: Inizia Gioco, Continua (se disponibile), Esci.
    """

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font_title = pygame.font.Font(None, 72)
        self.font_menu = pygame.font.Font(None, 48)
        self.selected_option = 0
        self.options = ["Inizia Gioco", "Esci"]

    def __enter__(self):
        """Inizializza il menu."""
        print("🎮 Entra in MenuState")

    def handle_events(self, events):
        """Gestisce input nel menu."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.select_option()
            elif event.type == pygame.QUIT:
                self.game_manager.running = False

    def select_option(self):
        """Esegue l'azione dell'opzione selezionata."""
        if self.selected_option == 0:  # Inizia Gioco
            # Reset dello stato del giocatore
            self.game_manager.player_state["health"] = PLAYER_MAX_HEALTH
            self.game_manager.player_state["coins"] = 0
            self.game_manager.player_state["current_floor"] = HUB_FLOOR
            self.game_manager.player_state["inventory"] = []

            # Cambia a Hub
            self.change_state(STATE_HUB)
        elif self.selected_option == 1:  # Esci
            self.game_manager.running = False

    def update(self, dt):
        """Update del menu (logica minima)."""
        pass

    def render(self):
        """Disegna il menu sullo schermo."""
        self.screen.fill(COLOR_DARK_GRAY)

        # Titolo
        title_surface = self.font_title.render(GAME_TITLE, True, COLOR_CYAN)
        title_rect = title_surface.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        )
        self.screen.blit(title_surface, title_rect)

        # Sottotitolo
        subtitle = self.font_menu.render("Echoes of Industry", True, COLOR_MAGENTA)
        subtitle_rect = subtitle.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 60)
        )
        self.screen.blit(subtitle, subtitle_rect)

        # Opzioni
        for i, option in enumerate(self.options):
            color = COLOR_CYAN if i == self.selected_option else COLOR_LIGHT_GRAY
            option_surface = self.font_menu.render(option, True, color)
            option_rect = option_surface.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 60)
            )
            self.screen.blit(option_surface, option_rect)

            # Freccia di selezione
            if i == self.selected_option:
                arrow = self.font_menu.render(">", True, COLOR_YELLOW)
                arrow_rect = arrow.get_rect(
                    right=option_rect.left - 20, centery=option_rect.centery
                )
                self.screen.blit(arrow, arrow_rect)

        # Istruzioni
        instructions = self.font_menu.render(
            "↑ ↓ per navigare, ENTER per selezionare", True, COLOR_LIGHT_GRAY
        )
        instructions_rect = instructions.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        )
        self.screen.blit(instructions, instructions_rect)
