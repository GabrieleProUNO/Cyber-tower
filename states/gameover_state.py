"""
GameOver State: Schermata di game over.
Mostra un messaggio di sconfitta e opzioni di retry o torna al menu.
"""

import pygame
from config import *
from states.base_state import BaseState


class GameOverState(BaseState):
    """
    Schermata di GameOver.
    Mostra quando la salute del giocatore scende a 0.
    """

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font_title = pygame.font.Font(None, 72)
        self.font_text = pygame.font.Font(None, 48)
        self.menu_options = ["Ritenta Livello", "Torna al Menu Principale"]
        self.selected_option = 0

    def __enter__(self):
        """Inizializza la schermata di game over."""
        print("💀 Entra in GameOverState")

    def handle_events(self, events):
        """Gestisce input nella schermata di game over."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN:
                    self.select_option()

    def select_option(self):
        """Esegue l'azione dell'opzione selezionata."""
        if self.selected_option == 0:  # Ritenta Livello
            # Reset della salute
            self.game_manager.set_player_health(PLAYER_MAX_HEALTH)
            self.change_state(STATE_LEVEL)
        elif self.selected_option == 1:  # Torna al Menu
            self.change_state(STATE_MENU)

    def update(self, dt):
        """Logica minimale."""
        pass

    def render(self):
        """Disegna la schermata di game over."""
        self.screen.fill(COLOR_BLACK)

        # Titolo GAME OVER
        title = self.font_title.render("GAME OVER", True, COLOR_RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        self.screen.blit(title, title_rect)

        # Messaggio
        message = self.font_text.render(
            f"Sei caduto al Piano {self.game_manager.player_state['current_floor']}",
            True,
            COLOR_LIGHT_GRAY,
        )
        message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(message, message_rect)

        # Menu opzioni
        y_start = SCREEN_HEIGHT // 2 + 50
        for i, option in enumerate(self.menu_options):
            color = COLOR_CYAN if i == self.selected_option else COLOR_LIGHT_GRAY
            option_text = self.font_text.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 70))
            self.screen.blit(option_text, option_rect)

            if i == self.selected_option:
                arrow = self.font_text.render(">", True, COLOR_YELLOW)
                arrow_rect = arrow.get_rect(right=option_rect.left - 20, centery=option_rect.centery)
                self.screen.blit(arrow, arrow_rect)

        # Istruzioni
        instructions = self.font_text.render(
            "↑↓ Navigare | ENTER Selezionare", True, COLOR_LIGHT_GRAY
        )
        instructions_rect = instructions.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        )
        self.screen.blit(instructions, instructions_rect)
