"""
Sistema Collisioni: Gestisce le collisioni AABB e sliding collision.

Responsabilità:
- Collision detection rettangoli
- Sliding collision (per platformer realistico)
- Hazard detection (spikes, acqua)
- Collectible detection

Nota: Sliding collision è essenziale per un platformer fluido.
Permette al player di scivolare lungo i muri mentre salta.
"""

import pygame
from config import *
from levels.tilemap import TILE_SIZE


class CollisionSystem:
    """
    Gestisce tutti i sistemi di collisione del gioco.

    Metodi:
        - check_collisions(player, tilemap): Risolve collisioni player
        - check_hazards(player, tilemap): Verifica hazard
        - check_collectibles(player, tilemap): Verifica collectible
    """

    @staticmethod
    def check_collisions(player, tilemap):
        """
        Risolve le collisioni del player con il tilemap.

        Implementa sliding collision:
        1. Verifica collisione sui 4 lati
        2. Risolve movimento parziale (sliding)
        3. Aggiorna stato grounded

        Args:
            player: Oggetto Player
            tilemap: Oggetto Tilemap
        """
        player_rect = player.rect
        move_x = int(player.vx)
        move_y = int(player.vy)
        if player.vx > 0:
            move_x = max(1, move_x)
        elif player.vx < 0:
            move_x = min(-1, move_x)
        if player.vy > 0:
            move_y = max(1, move_y)
        elif player.vy < 0:
            move_y = min(-1, move_y)

        # Estende rect con velocità per detection predittiva
        extended_rect = player_rect.copy()
        if move_x > 0:
            extended_rect.width += move_x
        else:
            extended_rect.x += move_x
            extended_rect.width += abs(move_x)

        if move_y > 0:
            extended_rect.height += move_y
        else:
            extended_rect.y += move_y
            extended_rect.height += abs(move_y)

        # Ottieni tile solidi nel range
        solids = tilemap.get_solids_in_rect(extended_rect)

        # Risolvi collisioni per X (movimento orizzontale)
        CollisionSystem._resolve_collision_axis(
            player_rect, solids, "horizontal", player
        )

        # Risolvi collisioni per Y (movimento verticale)
        CollisionSystem._resolve_collision_axis(
            player_rect, solids, "vertical", player
        )

        # Aggiorna stato grounded
        CollisionSystem._update_grounded(player, tilemap)

    @staticmethod
    def _resolve_collision_axis(player_rect, solids, axis, player=None):
        """
        Risolve collisioni su un asse (X o Y).

        Implementa sliding collision:
        - Trova la distanza di penetrazione minima
        - Risolve solo su quell'asse
        - Player scivola lungo il muro

        Args:
            player_rect: pygame.Rect del player
            solids: Lista di rect solidi
            axis: "horizontal" o "vertical"
            player: Oggetto Player (opzionale, per aggiornare velocità)
        """
        for solid in solids:
            if not player_rect.colliderect(solid):
                continue

            # Calcola penetrazione
            overlap_left = player_rect.right - solid.left
            overlap_right = solid.right - player_rect.left
            overlap_top = player_rect.bottom - solid.top
            overlap_bottom = solid.bottom - player_rect.top

            if axis == "horizontal":
                # Risolvi collisione X
                if overlap_left < overlap_right:
                    # Collisione da destra
                    player_rect.right = solid.left
                    if player:
                        player.vx = 0
                else:
                    # Collisione da sinistra
                    player_rect.left = solid.right
                    if player:
                        player.vx = 0

            elif axis == "vertical":
                # Risolvi collisione Y
                if overlap_top < overlap_bottom:
                    # Collisione da sotto (player salta su tile)
                    player_rect.bottom = solid.top
                    if player:
                        player.vy = 0
                        player.is_grounded = True
                else:
                    # Collisione da sopra (player va sotto tile)
                    player_rect.top = solid.bottom
                    if player:
                        player.vy = 0

    @staticmethod
    def _update_grounded(player, tilemap):
        """
        Aggiorna lo stato grounded del player.

        Verifica se il player è a contatto con una piattaforma.

        Args:
            player: Oggetto Player
            tilemap: Oggetto Tilemap
        """
        # Crea un ray di test sotto il player
        test_y = player.rect.bottom + 2

        test_rect = pygame.Rect(
            player.rect.left,
            test_y,
            player.rect.width,
            1,
        )

        solids = tilemap.get_solids_in_rect(test_rect)
        player.is_grounded = len(solids) > 0

    @staticmethod
    def check_hazards(player, tilemap):
        """
        Verifica se il player sta toccando un hazard.

        Args:
            player: Oggetto Player
            tilemap: Oggetto Tilemap

        Returns:
            True se in contatto con hazard
        """
        # Controlla i 4 angoli e il centro del player
        check_points = [
            (player.rect.left + 5, player.rect.top + 5),      # Top-left
            (player.rect.right - 5, player.rect.top + 5),     # Top-right
            (player.rect.left + 5, player.rect.bottom - 5),   # Bottom-left
            (player.rect.right - 5, player.rect.bottom - 5),  # Bottom-right
            (player.rect.centerx, player.rect.centery),       # Center
        ]

        for check_x, check_y in check_points:
            if tilemap.has_hazard(check_x, check_y):
                return True

        return False

    @staticmethod
    def check_collectibles(player, tilemap):
        """
        Verifica se il player può raccogliere collectible.

        Args:
            player: Oggetto Player
            tilemap: Oggetto Tilemap

        Returns:
            Lista di (grid_x, grid_y) dei collectible toccati
        """
        collected = []

        # Controlla tile attorno al player
        grid_left = int(player.rect.left / TILE_SIZE)
        grid_right = int(player.rect.right / TILE_SIZE)
        grid_top = int(player.rect.top / TILE_SIZE)
        grid_bottom = int(player.rect.bottom / TILE_SIZE)

        for grid_y in range(grid_top, grid_bottom + 1):
            for grid_x in range(grid_left, grid_right + 1):
                if tilemap.has_collectible(grid_x, grid_y):
                    collected.append((grid_x, grid_y))

        return collected

    @staticmethod
    def check_exit(player, tilemap):
        """
        Verifica se il player ha raggiunto l'uscita.

        Args:
            player: Oggetto Player
            tilemap: Oggetto Tilemap

        Returns:
            True se sulla uscita
        """
        grid_x = int(player.rect.centerx / TILE_SIZE)
        grid_y = int(player.rect.centery / TILE_SIZE)

        return tilemap.has_exit(grid_x, grid_y)

    @staticmethod
    def get_aabb_overlap(rect1, rect2):
        """
        Calcola l'overlap AABB tra due rettangoli.

        Args:
            rect1, rect2: pygame.Rect

        Returns:
            Tupla (overlap_x, overlap_y) o (0, 0) se no overlap
        """
        if not rect1.colliderect(rect2):
            return (0, 0)

        overlap_left = rect1.right - rect2.left
        overlap_right = rect2.right - rect1.left
        overlap_top = rect1.bottom - rect2.top
        overlap_bottom = rect2.bottom - rect1.top

        overlap_x = min(overlap_left, overlap_right)
        overlap_y = min(overlap_top, overlap_bottom)

        return (overlap_x, overlap_y)
