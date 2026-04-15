"""
Level State: Rappresenta un livello attivo alle piani 1-18.
Qui il giocatore esplora, combatte nemici e affronta il mini-boss.
(Per ora è una placeholder, sarà espanso nelle Fasi 3-4)
"""

import pygame
from config import *
from states.base_state import BaseState


class LevelState(BaseState):
    """
    Schermata di un livello attivo.
    Placeholder per ora - espanderemo nella Fase 3 (Tilemap) e Fase 4 (Nemici).

    Qui il giocatore:
    - Esplora il livello
    - Combatte nemici
    - Raccoglie risorse
    - Affronta il mini-boss
    """

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.font_title = pygame.font.Font(None, 48)
        self.font_text = pygame.font.Font(None, 32)
        self.floor_number = 0
        self.level_complete = False

    def __enter__(self):
        """Inizializza il livello."""
        self.floor_number = self.game_manager.player_state["current_floor"]
        print(f"⚔️  Entra in LevelState (Piano {self.floor_number})")
        print(f"🎮 [PLACEHOLDER] Livello Piano {self.floor_number} non ancora implementato")
        print(f"   Versione finale avrà: Player, Nemici, Tilemap, Telecamera")

    def handle_events(self, events):
        """Gestisce input nel livello."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Ritorna all'hub
                    self.change_state(STATE_HUB)
                elif event.key == pygame.K_SPACE:
                    # Simula completamento del livello per test
                    print(f"✓ Livello Piano {self.floor_number} COMPLETATO (simulato)")
                    self.level_complete = True

    def update(self, dt):
        """Logica di update del livello."""
        # Placeholder
        pass

    def render(self):
        """Disegna il livello."""
        self.screen.fill(COLOR_DARK_GRAY)

        # Titolo
        title = self.font_title.render(
            f"PIANO {self.floor_number}", True, COLOR_CYAN
        )
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Stato del giocatore
        player_state = self.game_manager.player_state
        health_display = self.font_text.render(
            f"❤️  {player_state['health']}/{PLAYER_MAX_HEALTH}",
            True,
            COLOR_RED,
        )
        health_rect = health_display.get_rect(topleft=(20, 20))
        self.screen.blit(health_display, health_rect)

        coins_display = self.font_text.render(
            f"💰 {player_state['coins']}", True, COLOR_YELLOW
        )
        coins_rect = coins_display.get_rect(topleft=(20, 60))
        self.screen.blit(coins_display, coins_rect)

        # Placeholder content
        placeholder_text = self.font_text.render(
            "Piano {self.floor_number} - Placeholder (Fase 3-4)",
            True,
            COLOR_LIGHT_GRAY,
        )
        placeholder_rect = placeholder_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        self.screen.blit(placeholder_text, placeholder_rect)

        # Istruzioni
        instructions_text = self.font_text.render(
            "SPACE per completare il livello (test) | ESC per tornare all'hub",
            True,
            COLOR_LIGHT_GRAY,
        )
        instructions_rect = instructions_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        )
        self.screen.blit(instructions_text, instructions_rect)

        # Se il livello è completato, mostra messaggio
        if self.level_complete:
            complete_text = self.font_title.render(
                "LIVELLO COMPLETATO!", True, COLOR_GREEN
            )
            complete_rect = complete_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
            )
            self.screen.blit(complete_text, complete_rect)

            next_text = self.font_text.render(
                "Premi ESC per tornare all'hub", True, COLOR_LIGHT_GRAY
            )
            next_rect = next_text.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            )
            self.screen.blit(next_text, next_rect)
