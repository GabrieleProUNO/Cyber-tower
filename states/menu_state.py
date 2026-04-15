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
    Mostra opzioni: Inizia Gioco, Esci.
    """

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font_title = pygame.font.Font(None, 72)
        self.font_menu = pygame.font.Font(None, 48)
        self.selected_option = 0
        self.options = ["Inizia Gioco", "Esci"]

    def __enter__(self):
        """Inizializza il menu."""
        print("Entra in MenuState")

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
            self.game_manager.player_state["health"] = PLAYER_MAX_HEALTH
            self.game_manager.player_state["max_health"] = PLAYER_MAX_HEALTH
            self.game_manager.player_state["coins"] = 0
            self.game_manager.player_state["current_floor"] = HUB_FLOOR
            self.game_manager.player_state["inventory"] = []
            self.game_manager.player_state["completed_floors"] = []
            self.change_state(STATE_HUB)
        elif self.selected_option == 1:  # Esci
            self.game_manager.running = False

    def update(self, dt):
        """Update del menu (logica minima)."""
        pass

    def render(self):
        """Disegna il menu sullo schermo."""
        for y in range(SCREEN_HEIGHT):
            t = y / max(1, SCREEN_HEIGHT - 1)
            color = (
                int(10 + 20 * t),
                int(16 + 26 * t),
                int(24 + 34 * t),
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))

        for i in range(7):
            rect = pygame.Rect(120 + i * 170, 90 + (i % 2) * 24, 110, 240 + i * 18)
            pygame.draw.rect(self.screen, (14, 28, 38), rect)
            pygame.draw.rect(self.screen, (34, 78, 98), rect, 1)

        title_surface = self.font_title.render(GAME_TITLE, True, COLOR_CYAN)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        glow = self.font_title.render(GAME_TITLE, True, (70, 180, 200))
        glow.set_alpha(70)
        self.screen.blit(glow, (title_rect.x + 2, title_rect.y + 2))
        self.screen.blit(title_surface, title_rect)

        subtitle = self.font_menu.render("Echoes of Industry", True, COLOR_MAGENTA)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 60))
        self.screen.blit(subtitle, subtitle_rect)

        for i, option in enumerate(self.options):
            color = COLOR_CYAN if i == self.selected_option else (180, 196, 206)
            option_surface = self.font_menu.render(option, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + i * 60))
            panel = pygame.Rect(
                option_rect.left - 28,
                option_rect.top - 12,
                option_rect.width + 56,
                option_rect.height + 20,
            )
            pygame.draw.rect(self.screen, (14, 26, 38), panel, border_radius=8)
            pygame.draw.rect(
                self.screen,
                (70, 140, 166) if i == self.selected_option else (46, 76, 94),
                panel,
                2,
                border_radius=8,
            )
            self.screen.blit(option_surface, option_rect)

            if i == self.selected_option:
                arrow = self.font_menu.render(">", True, COLOR_YELLOW)
                arrow_rect = arrow.get_rect(right=option_rect.left - 20, centery=option_rect.centery)
                self.screen.blit(arrow, arrow_rect)

        instructions = self.font_menu.render("UP/DOWN naviga  |  ENTER conferma", True, COLOR_LIGHT_GRAY)
        instructions_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(instructions, instructions_rect)
