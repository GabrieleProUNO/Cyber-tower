"""
Level State: Rappresenta un livello attivo ai piani 1-18.

Fase 3: Implementato Tilemap, Camera con Parallax, e Collision System.
- Caricamento livelli da CSV
- Camera che segue il player con smooth lerp
- Parallax background rendering
- AABB collision detection con sliding collision
- Hazard e collectible detection
"""

import pygame
import math
import os
from config import *
from states.base_state import BaseState
from entities.player import Player
from entities.projectile import Projectile
from levels.tilemap import Tilemap
from camera import Camera
from collision import CollisionSystem


class LevelState(BaseState):
    """
    Schermata di un livello attivo.

    Gestisce:
    - Player con controlli completi
    - Tilemap e rendering
    - Camera che segue
    - Collisioni precise
    - Proiettili e sparo
    """

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.floor_number = 0

        # ====== FONT ======
        self.font_title = pygame.font.Font(None, 48)
        self.font_text = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # ====== PLAYER E ENTITIES ======
        self.player = None
        self.projectiles = []
        self.fire_cooldown = 0.0
        self.fire_delay = 0.15

        # ====== LIVELLO ======
        self.tilemap = None
        self.camera = None
        self.level_complete = False
        self.level_time = 0.0

        # ====== STATO ======
        self.collected_coins = 0
        self.hazard_cooldown = 0.0  # Per evitare spam di danno

    def __enter__(self):
        """Inizializza il livello."""
        self.floor_number = self.game_manager.player_state["current_floor"]
        print(f"\n⚔️  ===== PIANO {self.floor_number} =====")

        # ====== CARICA TILEMAP ======
        # Calcola percorso del file basato su floor
        level_filename = f"levels/level_{self.floor_number:02d}.csv"

        # Se il file non esiste, usa un template
        if not os.path.exists(level_filename):
            if self.floor_number == 1:
                level_filename = "levels/level_01.csv"
            elif self.floor_number == 2:
                level_filename = "levels/level_02.csv"
            else:
                # Fallback: crea un livello simple
                print(f"⚠️  Livello {self.floor_number} non trovato, uso template...")
                level_filename = "levels/level_01.csv"

        self.tilemap = Tilemap()
        if not self.tilemap.load_from_csv(level_filename):
            print(f"❌ Errore caricamento tilemap!")
            return

        # ====== CREA PLAYER ======
        self.player = Player(100, 100)
        player_state = self.game_manager.player_state
        self.player.health = player_state["health"]
        print(f"🎮 Player creato")

        # ====== CREA CAMERA ======
        world_width, world_height = self.tilemap.get_world_size()
        self.camera = Camera(world_width, world_height)
        self.camera.set_position(
            self.player.rect.centerx - SCREEN_WIDTH / 3,
            self.player.rect.centery - SCREEN_HEIGHT / 2.5,
        )
        print(f"📷 Camera creata (mondo: {world_width}x{world_height}px)")

        # ====== RESET STATO ======
        self.projectiles = []
        self.fire_cooldown = 0.0
        self.collected_coins = 0
        self.hazard_cooldown = 0.0
        self.level_complete = False
        self.level_time = 0.0

        print(f"✓ Livello inizializzato!")

    def handle_events(self, events):
        """Gestisce input nel livello."""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_manager.set_player_health(self.player.health)
                    self.game_manager.add_coins(self.collected_coins)
                    self.change_state(STATE_HUB)

                elif event.key == pygame.K_F:
                    if DEBUG_MODE:
                        self.player.take_damage(1)

                elif event.key == pygame.K_H:
                    if DEBUG_MODE:
                        self.player.heal(1)

                elif event.key == pygame.K_y:
                    # Completa livello per test
                    print(f"✓ Livello completato (test)")
                    self.level_complete = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._fire_projectile()

    def _fire_projectile(self):
        """Crea e spara un proiettile."""
        if self.fire_cooldown > 0:
            return

        gun_pos = self.player.get_gun_position()
        direction = self.player.get_aim_direction()

        projectile = Projectile(
            gun_pos[0],
            gun_pos[1],
            direction[0],
            direction[1],
            speed=500,
            lifetime=10.0,
            damage=1,
        )

        self.projectiles.append(projectile)
        self.fire_cooldown = self.fire_delay

    def update(self, dt):
        """Logica di update del livello."""
        if dt > 0.1:
            dt = 0.1

        # ====== AGGIORNA PLAYER INPUT ======
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        self.player.handle_input(keys, mouse_pos)

        # ====== AGGIORNA PHYSICS PLAYER ======
        self.player.update(dt)

        # ====== GESTISCI COLLISIONI PLAYER ======
        CollisionSystem.check_collisions(self.player, self.tilemap)

        # ====== VERIFICA HAZARD (SPIKES, WATER) ======
        self.hazard_cooldown -= dt
        if self.hazard_cooldown <= 0:
            if CollisionSystem.check_hazards(self.player, self.tilemap):
                self.player.take_damage(1)
                self.hazard_cooldown = 0.5  # Cooldown anti-spam
                print(f"⚠️  Hazard! Salute: {self.player.health}")

        # ====== VERIFICA COLLECTIBILI ======
        collected = CollisionSystem.check_collectibles(self.player, self.tilemap)
        for grid_x, grid_y in collected:
            self.collected_coins += 1
            # Resetta il tile a empty (rimuovi moneta)
            self.tilemap.grid[grid_y][grid_x] = 0
            print(f"💰 Moneta! Totale: {self.collected_coins}")

        # ====== AGGIORNA CAMERA ======
        self.camera.update(self.player, self.tilemap, dt)

        # ====== AGGIORNA PROIETTILI ======
        self.fire_cooldown -= dt

        for projectile in self.projectiles[:]:
            projectile.update(dt)

            if not projectile.is_alive():
                self.projectiles.remove(projectile)

        # ====== VERIFICA USCITA ======
        if CollisionSystem.check_exit(self.player, self.tilemap):
            print(f"✓ Uscita trovata! Livello completato!")
            self.level_complete = True

        # ====== VERIFICA GAME OVER ======
        if not self.player.is_alive():
            print(f"💀 Game Over! Sei caduto al piano {self.floor_number}")
            self.game_manager.set_player_health(0)
            self.change_state(STATE_GAMEOVER)

        self.level_time += dt

    def render(self):
        """Disegna il livello."""
        self.screen.fill(COLOR_BLACK)

        # ====== RENDER TILEMAP (CON PARALLAX) ======
        self.tilemap.render(self.screen, self.camera)

        # ====== RENDER PLAYER ======
        self.player.render(self.screen)

        # ====== RENDER PROIETTILI ======
        for projectile in self.projectiles:
            projectile.render(self.screen)

        # ====== RENDER HUD ======
        self._render_hud()

        # ====== RENDER DEBUG (CAMERA, TILEMAP) ======
        if DEBUG_MODE:
            self.camera.render_debug(self.screen, self.player, self.tilemap)

        # ====== RENDER SCHERMATA COMPLETAMENTO ======
        if self.level_complete:
            self._render_level_complete()

    def _render_hud(self):
        """Disegna l'HUD in sovraimpressione."""
        y_offset = 20

        # Salute
        health_text = self.font_text.render(
            f"❤️  {self.player.health}/{self.player.max_health}",
            True,
            COLOR_RED,
        )
        self.screen.blit(health_text, (20, y_offset))

        # Monete raccolte
        coins_text = self.font_text.render(
            f"💰 {self.collected_coins}", True, COLOR_YELLOW
        )
        self.screen.blit(coins_text, (20, y_offset + 40))

        # Piano
        floor_text = self.font_text.render(
            f"📍 Piano {self.floor_number}", True, COLOR_CYAN
        )
        self.screen.blit(floor_text, (20, y_offset + 80))

        # Proiettili
        projectiles_text = self.font_small.render(
            f"Proiettili: {len(self.projectiles)}", True, COLOR_GREEN
        )
        self.screen.blit(projectiles_text, (20, y_offset + 120))

        # Tempo
        time_text = self.font_small.render(
            f"Tempo: {self.level_time:.1f}s", True, COLOR_LIGHT_GRAY
        )
        self.screen.blit(time_text, (SCREEN_WIDTH - 250, y_offset))

    def _render_level_complete(self):
        """Disegna la schermata di completamento."""
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

        # Statistiche
        stats_y = SCREEN_HEIGHT // 2
        time_text = self.font_text.render(
            f"Tempo: {self.level_time:.1f}s", True, COLOR_YELLOW
        )
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
        self.screen.blit(time_text, time_rect)

        coins_earned_text = self.font_text.render(
            f"+{self.collected_coins} monete!", True, COLOR_YELLOW
        )
        coins_rect = coins_earned_text.get_rect(
            center=(SCREEN_WIDTH // 2, stats_y + 50)
        )
        self.screen.blit(coins_earned_text, coins_rect)

        # Istruzioni
        next_text = self.font_text.render(
            "Premi ESC per tornare all'hub", True, COLOR_LIGHT_GRAY
        )
        next_rect = next_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        )
        self.screen.blit(next_text, next_rect)
