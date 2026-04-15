"""
Classe RangedEnemy: Nemico che spara proiettili.

Sottoclasse di Enemy che implementa abilità di sparo.
Spara verso il player quando lo vede.
"""

import pygame
import math
import random
from entities.enemy import Enemy
from entities.projectile import Projectile
from config import *


class RangedEnemy(Enemy):
    """
    Nemico che spara proiettili verso il player.

    Attributi aggiuntivi:
        - fire_cooldown: Tempo fra spari
        - projectiles: Lista di proiettili sparati
        - aim_x, aim_y: Direzione di mira
    """

    def __init__(self, x, y, width=32, height=32, health=2, speed=1.5, aggro_range=250):
        """
        Inizializza il nemico a distanza.

        Args:
            x, y: Posizione
            width, height: Dimensioni
            health: Salute (solitamente meno degli altri)
            speed: Velocità movimento (lento, spara da distanza)
            aggro_range: Raggio aggro più grande
        """
        super().__init__(x, y, width, height, health, speed, aggro_range)

        # ====== SPARO ======
        self.fire_cooldown = 0.0
        self.fire_delay = 2.0  # Spara ogni 2 secondi
        self.projectiles = []
        self.projectile_speed = 250  # Lento rispetto al player

        # ====== MIRA ======
        self.aim_x = 0.0
        self.aim_y = 0.0

        # ====== RENDERING ======
        self.color = COLOR_MAGENTA  # Diverso dal walker

    def update(self, dt, player, tilemap):
        """Aggiorna il nemico ranged."""
        super().update(dt, player, tilemap)

        if self.is_dead:
            return

        # ====== AGGIORNA COOLDOWN SPARO ======
        self.fire_cooldown -= dt

        # ====== AGGIORNA PROIETTILI ======
        self._update_projectiles()

        # ====== SPARA SE IN RANGE ======
        if self.state == self.STATE_CHASE:
            self._try_fire_at_player(player)

    def _update_projectiles(self):
        """Aggiorna i proiettili sparati da questo nemico."""
        for projectile in self.projectiles[:]:
            projectile.update(0.016)  # Assume 60 FPS

            if not projectile.is_alive():
                self.projectiles.remove(projectile)

    def _try_fire_at_player(self, player):
        """
        Prova a sparare al player.

        Args:
            player: Oggetto Player
        """
        if self.fire_cooldown > 0:
            return

        # Calcola direzione verso player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            dx /= distance
            dy /= distance

        # Crea proiettile nemico
        projectile = Projectile(
            self.rect.centerx,
            self.rect.centery,
            dx,
            dy,
            speed=self.projectile_speed,
            lifetime=8.0,
            damage=1,
        )

        self.projectiles.append(projectile)
        self.fire_cooldown = self.fire_delay

    def _ai_patrol(self):
        """RangedEnemy si muove lentamente in pattugliamento."""
        super()._ai_patrol()

    def _ai_chase(self, player):
        """RangedEnemy si ferma quando vede il player (spara da distanza)."""
        # Non muoversi quando spara - resta fermo
        self.vx = 0

    def render(self, surface, camera):
        """Disegna il nemico e i proiettili."""
        super().render(surface, camera)

        # Disegna proiettili
        for projectile in self.projectiles:
            projectile.render(surface)

    def drop_loot(self):
        """RangedEnemy droppa un po' più di loot."""
        loot = super().drop_loot()

        if loot and loot["type"] == "coins":
            loot["amount"] = int(loot["amount"] * 1.5)  # 50% più monete

        return loot

    def get_projectiles(self):
        """Ritorna i proiettili sparati dal nemico."""
        return self.projectiles
