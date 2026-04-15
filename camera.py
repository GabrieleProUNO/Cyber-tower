"""
Sistema Camera: Gestisce la telecamera che segue il player.

Responsabilità:
- Seguire il player con smooth lerp
- Limiti di bordo (non esce dal mondo)
- Conversione coordinate mondo -> schermo
- Effetti camera (shake, zoom - per future fasi)
"""

import pygame
from config import *


class Camera:
    """
    Gestisce la telecamera del gioco.

    Attributi:
        - x, y: Posizione della camera (world coords)
        - target_x, target_y: Target verso cui muovere la camera
        - width, height: Dimensioni di visualizzazione (SCREEN_WIDTH/HEIGHT)
        - smooth_factor: Fattore di lerp (0-1)
        - world_width, world_height: Dimensioni del mondo

    Metodi:
        - update(player, tilemap, dt): Aggiorna posizione camera
        - world_to_screen(x, y): Converte coordinate
        - is_in_view(rect): Controlla se visibile
        - render_debug(surface): Debug info camera
    """

    def __init__(self, world_width=SCREEN_WIDTH, world_height=SCREEN_HEIGHT):
        """
        Inizializza la camera.

        Args:
            world_width, world_height: Dimensioni del mondo
        """
        # Posizione camera
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0

        # Dimensioni camera (viewport)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT

        # Dimensioni mondo
        self.world_width = world_width
        self.world_height = world_height

        # Smoothing
        self.smooth_factor = 0.15  # Lerp factor (15% per frame)
        self.use_smooth = True  # Abilita/disabilita smoothing

        # Offset da player (dove posizionare il player sullo schermo)
        self.player_offset_x = SCREEN_WIDTH / 3  # Leggermente a sinistra
        self.player_offset_y = SCREEN_HEIGHT / 2.5  # Leggermente sopra il centro

    def update(self, player, tilemap, dt):
        """
        Aggiorna la posizione della camera.

        Args:
            player: Oggetto Player per seguire
            tilemap: Oggetto Tilemap per limiti
            dt: Delta time (non usato, ma disponibile)
        """
        # Calcola target position basato su player
        self.target_x = player.rect.centerx - self.player_offset_x
        self.target_y = player.rect.centery - self.player_offset_y

        # Smooth movement verso target
        if self.use_smooth:
            self.x += (self.target_x - self.x) * self.smooth_factor
            self.y += (self.target_y - self.y) * self.smooth_factor
        else:
            self.x = self.target_x
            self.y = self.target_y

        # Applica limiti (non uscire dal mondo)
        self._apply_bounds(tilemap)

    def _apply_bounds(self, tilemap):
        """
        Applica limiti di bordo per non uscire dal mondo.

        Args:
            tilemap: Oggetto Tilemap con dimensioni mondo
        """
        world_width, world_height = tilemap.get_world_size()

        # Se il mondo è più piccolo della viewport, mantieni camera ancorata a 0.
        max_x = max(0, world_width - self.width)
        max_y = max(0, world_height - self.height)

        # Clamp finale.
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))

    def world_to_screen(self, world_x, world_y):
        """
        Converte coordinate mondo a coordinate schermo.

        Args:
            world_x, world_y: Coordinate nel mondo

        Returns:
            Tupla (screen_x, screen_y)
        """
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return (screen_x, screen_y)

    def screen_to_world(self, screen_x, screen_y):
        """
        Converte coordinate schermo a coordinate mondo.

        Args:
            screen_x, screen_y: Coordinate sullo schermo

        Returns:
            Tupla (world_x, world_y)
        """
        world_x = screen_x + self.x
        world_y = screen_y + self.y
        return (world_x, world_y)

    def is_in_view(self, rect):
        """
        Controlla se un rettangolo è visibile dalla camera.

        Args:
            rect: pygame.Rect in coordinate mondo

        Returns:
            True se almeno parzialmente visibile
        """
        # Bordo esteso per essere conservativi
        margin = 100

        return (
            rect.right > self.x - margin
            and rect.left < self.x + self.width + margin
            and rect.bottom > self.y - margin
            and rect.top < self.y + self.height + margin
        )

    def get_view_rect(self):
        """
        Ritorna il rettangolo di view della camera in coordinate mondo.

        Returns:
            pygame.Rect della viewport attuale
        """
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def set_position(self, world_x, world_y):
        """
        Setta la posizione camera (per teleport o cutscene).

        Args:
            world_x, world_y: Nuova posizione in coordinate mondo
        """
        self.x = world_x
        self.y = world_y
        self.target_x = world_x
        self.target_y = world_y

    def shake(self, intensity=5.0, duration=0.2):
        """
        Effetto camera shake (implementazione base).

        Args:
            intensity: Intensità dello shake in pixel
            duration: Durata dello shake in secondi

        Nota: Implementazione completa nella Fase 5 (VFX)
        """
        # TODO: Implementare shake effect completo
        pass

    def render_debug(self, surface, player, tilemap):
        """
        Disegna debug info della camera.

        Args:
            surface: Surface pygame
            player: Oggetto Player (per visualizzare target)
            tilemap: Oggetto Tilemap
        """
        if not DEBUG_MODE:
            return

        font = pygame.font.Font(None, 24)

        # Info camera
        camera_text = font.render(
            f"Cam: ({self.x:.0f}, {self.y:.0f}) | "
            f"Target: ({self.target_x:.0f}, {self.target_y:.0f})",
            True,
            COLOR_GREEN,
        )
        surface.blit(camera_text, (10, SCREEN_HEIGHT - 100))

        # Info player mondo
        player_text = font.render(
            f"Player: ({player.rect.centerx}, {player.rect.centery})",
            True,
            COLOR_YELLOW,
        )
        surface.blit(player_text, (10, SCREEN_HEIGHT - 70))

        # Info mondo
        world_width, world_height = tilemap.get_world_size()
        world_text = font.render(
            f"World: {world_width}x{world_height} px",
            True,
            COLOR_CYAN,
        )
        surface.blit(world_text, (10, SCREEN_HEIGHT - 40))

        # Disegna bordo viewport
        view_rect = self.get_view_rect()
        screen_top_left = self.world_to_screen(view_rect.left, view_rect.top)
        screen_size = (view_rect.width, view_rect.height)

        pygame.draw.rect(
            surface,
            COLOR_GREEN,
            (*screen_top_left, *screen_size),
            2,
        )
