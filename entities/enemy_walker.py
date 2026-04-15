"""
Classe WalkerEnemy: Nemico base che cammina e attacca.

Sottoclasse di Enemy per il nemico più semplice.
Cammina su piattaforme e insegue il player da vicino.
"""

import pygame
from entities.enemy import Enemy
from config import *


class WalkerEnemy(Enemy):
    """
    Nemico base che cammina su piattaforme.

    Attributi aggiuntivi:
        - attack_range: Distanza di attacco close-range
        - attack_cooldown: Tempo fra attacchi
    """

    def __init__(self, x, y, width=32, height=32, health=3, speed=2.5, aggro_range=200):
        """
        Inizializza il nemico walker.

        Args:
            x, y: Posizione
            width, height: Dimensioni
            health: Salute standard
            speed: Velocità movimento standard
            aggro_range: Raggio aggro standard
        """
        super().__init__(x, y, width, height, health, speed, aggro_range)

        # ====== ATTACCO ======
        self.attack_range = 50  # Distanza per close-range attack
        self.attack_cooldown = 0.0
        self.attack_delay = 1.0  # Attacca ogni 1 secondo quando in range

        # ====== RENDERING ======
        self.color = COLOR_RED  # Il colore default rosso

    def update(self, dt, player, tilemap):
        """Aggiorna il nemico walker."""
        super().update(dt, player, tilemap)

        if self.is_dead:
            return

        # ====== AGGIORNA COOLDOWN ATTACCO ======
        self.attack_cooldown -= dt

    def _ai_chase(self, player):
        """WalkerEnemy insegue il player aggressivamente."""
        target_x = player.rect.centerx
        dx = target_x - self.rect.centerx

        # Muove verso player
        if dx > 5:
            self.direction = 1
            self.vx = self.speed * 1.2
        elif dx < -5:
            self.direction = -1
            self.vx = self.speed * 1.2
        else:
            self.vx = 0

    def can_attack_player(self, player):
        """
        Verifica se il nemico può attaccare il player.

        Args:
            player: Oggetto Player

        Returns:
            True se in range e cooldown permette
        """
        if self.attack_cooldown > 0:
            return False

        # Calcola distanza dal player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        # Usa distanza Manhattan per semplicità
        distance = abs(dx) + abs(dy)

        return distance < self.attack_range

    def attack_player(self, player):
        """
        Attacca il player (infligge danno).

        Args:
            player: Oggetto Player

        Returns:
            True se attacco riuscito
        """
        if not self.can_attack_player(player):
            return False

        # Infliggi danno
        player.take_damage(1)
        self.attack_cooldown = self.attack_delay

        print(f"⚔️  WalkerEnemy attacca il player! Salute: {player.health}")
        return True

    def drop_loot(self):
        """WalkerEnemy droppa una quantità standard di loot."""
        return super().drop_loot()

    def set_attack_range(self, range_distance):
        """Imposta il raggio di attacco."""
        self.attack_range = range_distance
