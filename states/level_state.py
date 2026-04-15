"""
Level State: Rappresenta un livello attivo ai piani 1-18.
Qui il giocatore esplora, combatte nemici e affronta il mini-boss.

Fase 2: Implementato Player Controller con movimento e sparo.
Fasi future: Nemici (Fase 4), Tilemap (Fase 3), NPC/Dialoghi (Fase 5)
"""

import pygame
import math
from config import *
from states.base_state import BaseState
from entities.player import Player
from entities.projectile import Projectile


class LevelState(BaseState):
    """
    Schermata di un livello attivo.

    Gestisce:
    - Player con controlli
    - Proiettili e sparo
    - Nemici (placeholder per Fase 4)
    - Collisioni
    - Rendering ambiente
    """

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.floor_number = 0

        # ====== FONT ======
        self.font_title = pygame.font.Font(None, 48)
        self.font_text = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # ====== PLAYER ======
        self.player = None

        # ====== PROIETTILI ======
        self.projectiles = []
        self.fire_cooldown = 0.0
        self.fire_delay = 0.15  # Minimo tempo fra spari (secondi)

        # ====== STATO LIVELLO ======
        self.level_complete = False
        self.level_time = 0.0

        # ====== NEMICI (Placeholder per Fase 4) ======
        self.enemies = []

    def __enter__(self):
        """Inizializza il livello."""
        self.floor_number = self.game_manager.player_state["current_floor"]
        print(f"\n⚔️  ===== PIANO {self.floor_number} =====")

        # Crea il player
        self.player = Player(PLAYER_START_POSITION[0], PLAYER_START_POSITION[1])

        # Sincronizza salute del player con game state
        player_state = self.game_manager.player_state
        self.player.health = player_state["health"]

        print(f"🎮 Player creato a posizione {PLAYER_START_POSITION}")
        print(f"💚 Salute: {self.player.health}/{self.player.max_health}")
        print(f"📍 Piano: {self.floor_number}")

        self.level_complete = False
        self.level_time = 0.0
        self.fire_cooldown = 0.0

    def handle_events(self, events):
        """Gestisce input nel livello."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Salva la salute del player prima di uscire
                    self.game_manager.set_player_health(self.player.health)
                    self.change_state(STATE_HUB)

                elif event.key == pygame.K_F:
                    # Debug: Simula danno al player
                    if DEBUG_MODE:
                        self.player.take_damage(1)
                        print(f"[DEBUG] Danno inferto! Salute: {self.player.health}")

                elif event.key == pygame.K_H:
                    # Debug: Guarisci il player
                    if DEBUG_MODE:
                        self.player.heal(1)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click sinistro = spara
                    self._fire_projectile()

    def _fire_projectile(self):
        """Crea e spara un proiettile dalla posizione del tubo."""
        if self.fire_cooldown > 0:
            return  # Cooldown attivo

        # Ottiene posizione bocca tubo e direzione
        gun_pos = self.player.get_gun_position()
        direction = self.player.get_aim_direction()

        # Crea il proiettile
        projectile = Projectile(
            gun_pos[0],
            gun_pos[1],
            direction[0],
            direction[1],
            speed=500,  # pixel/sec
            lifetime=10.0,
            damage=1,
        )

        self.projectiles.append(projectile)
        self.fire_cooldown = self.fire_delay

        print(f"💥 Sparo! ({int(gun_pos[0])}, {int(gun_pos[1])})")

    def update(self, dt):
        """Logica di update del livello."""
        if dt > 0.1:
            dt = 0.1  # Cap delta time

        # ====== AGGIORNA COOLDOWN SPARO ======
        self.fire_cooldown -= dt

        # ====== AGGIORNA PLAYER ======
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        self.player.handle_input(keys, mouse_pos)
        self.player.update(dt)

        # ====== AGGIORNA PROIETTILI ======
        for projectile in self.projectiles[:]:
            projectile.update(dt)

            # Rimuovi proiettili scaduti
            if not projectile.is_alive():
                self.projectiles.remove(projectile)

        # ====== VERIFICA CONDIZIONI DI VITTORIA/SCONFITTA ======
        if not self.player.is_alive():
            print(f"💀 Game Over! Sei caduto al piano {self.floor_number}")
            # Salva stato e vai a game over
            self.game_manager.set_player_health(0)
            self.change_state(STATE_GAMEOVER)

        # ====== COMPLETAMENTO LIVELLO (Test: premi Y) ======
        if pygame.key.get_pressed()[pygame.K_y]:
            print(f"✓ Livello Piano {self.floor_number} COMPLETATO!")
            self.level_complete = True
            # Salva salute prima di uscire
            self.game_manager.set_player_health(self.player.health)

        self.level_time += dt

    def render(self):
        """Disegna il livello."""
        self.screen.fill(COLOR_DARK_GRAY)

        # ====== SCENOGRAFIA DI FONDO ======
        self._render_background()

        # ====== DISEGNA PLAYER ======
        self.player.render(self.screen)

        # ====== DISEGNA PROIETTILI ======
        for projectile in self.projectiles:
            projectile.render(self.screen)

        # ====== HUD IN ALTO A SINISTRA ======
        self._render_hud()

        # ====== ISTRUZIONI ======
        self._render_instructions()

        # ====== SCHERMATA DI COMPLETAMENTO ======
        if self.level_complete:
            self._render_level_complete()

    def _render_background(self):
        """Disegna lo sfondo del livello (placeholder)."""
        # Sfondo gradiato semplice
        for i in range(SCREEN_HEIGHT):
            color_value = int(40 + (i / SCREEN_HEIGHT) * 20)
            pygame.draw.line(
                self.screen,
                (color_value, color_value, color_value),
                (0, i),
                (SCREEN_WIDTH, i),
            )

        # Piattaforma inferiore (ground)
        ground_y = SCREEN_HEIGHT - 100
        pygame.draw.rect(self.screen, COLOR_MAGENTA, (0, ground_y, SCREEN_WIDTH, 100))
        pygame.draw.rect(self.screen, COLOR_CYAN, (0, ground_y, SCREEN_WIDTH, 100), 3)

        # Testo floor in background
        floor_text = self.font_title.render(
            f"PIANO {self.floor_number}", True, (50, 50, 50)
        )
        floor_rect = floor_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        self.screen.blit(floor_text, floor_rect)

    def _render_hud(self):
        """Disegna l'HUD (salute, monete, piano)."""
        y_offset = 20

        # Salute
        health_text = self.font_text.render(
            f"❤️  {self.player.health}/{self.player.max_health}",
            True,
            COLOR_RED,
        )
        self.screen.blit(health_text, (20, y_offset))

        # Monete
        coins = self.game_manager.player_state["coins"]
        coins_text = self.font_text.render(f"💰 {coins}", True, COLOR_YELLOW)
        self.screen.blit(coins_text, (20, y_offset + 40))

        # Piano
        floor_text = self.font_text.render(f"📍 Piano {self.floor_number}", True, COLOR_CYAN)
        self.screen.blit(floor_text, (20, y_offset + 80))

        # Proiettili
        projectiles_text = self.font_small.render(
            f"Proiettili: {len(self.projectiles)}", True, COLOR_GREEN
        )
        self.screen.blit(projectiles_text, (20, y_offset + 120))

    def _render_instructions(self):
        """Disegna le istruzioni di controllo."""
        instructions = [
            "WASD/Frecce: Muovi | Spazio: Salta",
            "Mouse: Mira | Click: Spara",
            "F/H: Danno/Heal (debug) | Y: Completa test",
            "ESC: Torna all'Hub",
        ]

        y = SCREEN_HEIGHT - 120
        for instruction in instructions:
            text = self.font_small.render(instruction, True, COLOR_LIGHT_GRAY)
            self.screen.blit(text, (20, y))
            y += 25

    def _render_level_complete(self):
        """Disegna la schermata di livello completato."""
        # Overlay semi-trasparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))

        # Testo vittoria
        complete_text = self.font_title.render(
            "LIVELLO COMPLETATO!", True, COLOR_GREEN
        )
        complete_rect = complete_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3)
        )
        self.screen.blit(complete_text, complete_rect)

        # Time
        time_text = self.font_text.render(
            f"Tempo: {self.level_time:.1f}s", True, COLOR_YELLOW
        )
        time_rect = time_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        )
        self.screen.blit(time_text, time_rect)

        # Monete guadagnate (placeholder)
        coins_earned = 50
        coins_text = self.font_text.render(
            f"+{coins_earned} monete!", True, COLOR_YELLOW
        )
        coins_rect = coins_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
        )
        self.screen.blit(coins_text, coins_rect)

        # Istruzioni
        next_text = self.font_text.render(
            "Premi ESC per tornare all'hub", True, COLOR_LIGHT_GRAY
        )
        next_rect = next_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        )
        self.screen.blit(next_text, next_rect)
