"""
Ending State: Schermata di fine gioco con credits.

Mostra:
- Schermata vittoria
- Statistiche finali
- Credits
- Opzione per ricominciare
"""

import pygame
from config import *
from states.base_state import BaseState


class EndingState(BaseState):
    """Schermata di ending e vittoria."""

    def __init__(self, game_manager, game_progression):
        """
        Inizializza lo stato ending.

        Args:
            game_manager: GameManager
            game_progression: GameProgression
        """
        super().__init__(game_manager)
        self.game_progression = game_progression

        self.font_huge = pygame.font.Font(None, 72)
        self.font_title = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        self.scroll_offset = 0.0
        self.scroll_speed = 30.0
        self.show_credits = False
        self.waiting_for_input = False
        self.input_timer = 3.0

    def __enter__(self):
        """Inizializza l'ending."""
        print("🎬 ENDING SCREEN")

    def handle_events(self, events):
        """Gestisce input."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.show_credits = not self.show_credits

                if event.key == pygame.K_RETURN and self.waiting_for_input:
                    # Ricomincia nuovo gioco
                    self.game_progression.reset_to_hub()
                    self.change_state(STATE_HUB)

    def update(self, dt):
        """Update dello stato."""
        if self.show_credits:
            self.scroll_offset += self.scroll_speed * dt

        self.input_timer -= dt
        if self.input_timer <= 0:
            self.waiting_for_input = True

    def render(self):
        """Disegna l'ending."""
        self.screen.fill(COLOR_BLACK)

        if not self.show_credits:
            self._render_victory_screen()
        else:
            self._render_credits()

    def _render_victory_screen(self):
        """Disegna schermata di vittoria."""
        # ====== TITOLO ======
        title = self.font_huge.render("🏆 VITTORIA! 🏆", True, COLOR_MAGENTA)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title, title_rect)

        subtitle = self.font_title.render(
            "Hai sconfitto la Cyber-Tower!", True, COLOR_CYAN
        )
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(subtitle, subtitle_rect)

        # ====== STATISTICHE ======
        stats = self.game_progression.get_stats()

        stats_y = 250
        stats_list = [
            f"Tempo totale: {self.game_progression.format_playtime()}",
            f"Piani completati: {stats['completed_floors']}/{stats['total_floors']}",
            f"Monete totali: {stats['coins']} 💰",
            f"Completamento: {stats['completion']}%",
        ]

        for stat in stats_list:
            stat_text = self.font_normal.render(stat, True, COLOR_YELLOW)
            stat_rect = stat_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
            self.screen.blit(stat_text, stat_rect)
            stats_y += 50

        # ====== MESSAGGI ======
        msg_y = stats_y + 60

        if not self.waiting_for_input:
            msg = self.font_small.render(
                "Caricamento in corso...", True, COLOR_LIGHT_GRAY
            )
        else:
            msg = self.font_normal.render(
                "Premi SPACE per Credits o ENTER per Ricominciare",
                True,
                COLOR_GREEN,
            )
            msg_y -= 20

        msg_rect = msg.get_rect(center=(SCREEN_WIDTH // 2, msg_y))
        self.screen.blit(msg, msg_rect)

        # ====== HINT CREDITS ======
        hint = self.font_small.render(
            "Premi SPACE per visualizzare i credits", True, COLOR_LIGHT_GRAY
        )
        hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(hint, hint_rect)

    def _render_credits(self):
        """Disegna i credits scorrevoli."""
        y_pos = SCREEN_HEIGHT - int(self.scroll_offset)

        credits_text = [
            "",
            "",
            "🎮 CYBER-TOWER: ECHOES OF INDUSTRY 🎮",
            "",
            "Un Action-Platformer Metroidvania-lite",
            "",
            "---",
            "",
            "SVILUPPATO DA:",
            "Developer & Game Designer",
            "",
            "---",
            "",
            "GRAZIE A:",
            "Tutti i tester e i supporter!",
            "",
            "---",
            "",
            "TECNOLOGIE:",
            "Python 3.x",
            "Pygame 2.5+",
            "",
            "---",
            "",
            "MUSICA E SUONI:",
            "Sound Design Ambientale",
            "Effetti Sonori Epici",
            "",
            "---",
            "",
            "GRAZIE PER AVER GIOCATO!",
            "",
            "La tua avventura nella torre è completa.",
            "Ma ci sono ancora segreti da scoprire...",
            "",
            "---",
            "",
            "Fine Credits",
            "",
            "",
        ]

        for line in credits_text:
            if y_pos > SCREEN_HEIGHT:
                continue
            if y_pos < -100:
                continue

            if line.startswith("---"):
                continue

            if "SVILUPPATO" in line or "GRAZIE" in line or "TECNOLOGIE" in line:
                font = self.font_title
                color = COLOR_MAGENTA
            elif line.startswith("🎮"):
                font = self.font_huge
                color = COLOR_CYAN
            else:
                font = self.font_normal
                color = COLOR_LIGHT_GRAY

            text = font.render(line, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_pos))

            if -100 < y_pos < SCREEN_HEIGHT + 100:
                self.screen.blit(text, text_rect)

            y_pos += 50

        # ====== BACK HINT ======
        back_hint = self.font_small.render(
            "Premi SPACE per tornare", True, COLOR_LIGHT_GRAY
        )
        back_hint_rect = back_hint.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)
        )
        self.screen.blit(back_hint, back_hint_rect)
