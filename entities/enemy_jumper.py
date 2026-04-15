"""
Classe JumperEnemy: Nemico che salta verso il player.

Sottoclasse di Enemy che implementa abilità di salto aggressivo.
Salta verso il player quando lo vede.
"""

import pygame
import math
from entities.enemy import Enemy
from config import *


class JumperEnemy(Enemy):
    """
    Nemico che salta verso il player in modo aggressivo.

    Attributi aggiuntivi:
        - jump_force: Forza del salto
        - jump_cooldown: Tempo fra salti
        - jump_range: Distanza minima per saltare
    """

    def __init__(self, x, y, width=32, height=32, health=4, speed=3.0, aggro_range=220):
        """
        Inizializza il nemico che salta.

        Args:
            x, y: Posizione
            width, height: Dimensioni
            health: Salute (più dei ranged, meno dei walker)
            speed: Velocità movimento
            aggro_range: Raggio aggro
        """
        super().__init__(x, y, width, height, health, speed, aggro_range)

        # ====== SALTO ======
        self.jump_force = -12  # Forza salto
        self.jump_cooldown = 0.0
        self.jump_delay = 1.2  # Salta ogni 1.2 secondi
        self.jump_range = 150  # Saltà se player è più vicino

        # ====== RENDERING ======
        self.color = COLOR_YELLOW  # Diverso dagli altri

    def update(self, dt, player, tilemap):
        """Aggiorna il nemico jumper."""
        super().update(dt, player, tilemap)

        if self.is_dead:
            return

        # ====== AGGIORNA COOLDOWN SALTO ======
        self.jump_cooldown -= dt

        # ====== SALTA VERSO PLAYER SE IN RANGE ======
        if self.state == self.STATE_CHASE:
            self._try_jump_at_player(player)

    def _ai_chase(self, player):
        """JumperEnemy muove verso il player più velocemente."""
        target_x = player.rect.centerx
        dx = target_x - self.rect.centerx

        if dx > 5:
            self.direction = 1
            self.vx = self.speed * 1.3  # Più veloce del walker
        elif dx < -5:
            self.direction = -1
            self.vx = self.speed * 1.3
        else:
            self.vx = 0

    def _try_jump_at_player(self, player):
        """
        Prova a saltare verso il player.

        Args:
            player: Oggetto Player
        """
        if self.jump_cooldown > 0:
            return

        # Calcola distanza
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        # Salta se player è abbastanza vicino e a terra
        if distance < self.jump_range and self.is_grounded:
            self.vy = self.jump_force
            self.jump_cooldown = self.jump_delay

            # Aggiusta velocità orizzontale per mirare al player
            if abs(dx) > 10:
                self.vx = (self.speed * 1.5) * (1 if dx > 0 else -1)

            print(f"⬆️  JumperEnemy salta verso player!")

    def drop_loot(self):
        """JumperEnemy droppa una quantità media di loot."""
        return super().drop_loot()
