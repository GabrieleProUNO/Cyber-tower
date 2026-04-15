"""
Classe Projectile: Gestisce i proiettili sparati dal giocatore.

Responsabilità:
- Movimento lineare uniforme
- Collisioni con bordi dello schermo
- Collision detection semplice
- Rendering
- Lifetime e distruzione automatica
"""

import pygame
import math
from config import *


class Projectile(pygame.sprite.Sprite):
    """
    Rappresenta un proiettile sparato dal giocatore.

    Attributi:
        - Posizione (x, y)
        - Velocità e direzione
        - Raggio collider
        - Tempo di vita (lifetime)
        - Danno inflitto

    Metodi:
        - update(dt): Aggiorna posizione e lifetime
        - render(): Disegna il proiettile
        - is_alive(): Controlla se è ancora attivo
    """

    def __init__(self, x, y, direction_x, direction_y, speed=15, lifetime=5.0, damage=1):
        """
        Inizializza un proiettile.

        Args:
            x, y: Posizione iniziale (dalla bocca del tubo)
            direction_x, direction_y: Direzione normalizzata (-1 a 1)
            speed: Velocità del proiettile (pixel/sec)
            lifetime: Tempo massimo di vita (secondi)
            damage: Danno inflitto (default 1)
        """
        super().__init__()

        # ====== POSIZIONE ======
        self.x = float(x)
        self.y = float(y)
        self.radius = 5  # Raggio della sfera collider

        # ====== VELOCITÀ ======
        # Normalizza direzione per evitare velocità incoerenti.
        direction_len = math.hypot(direction_x, direction_y)
        if direction_len == 0:
            direction_x, direction_y = 1.0, 0.0
        else:
            direction_x /= direction_len
            direction_y /= direction_len

        self.vx = direction_x * speed
        self.vy = direction_y * speed
        self.speed = speed

        # ====== LIFETIME ======
        self.lifetime = lifetime
        self.age = 0.0

        # ====== DANNO ======
        self.damage = damage

        # ====== RENDERING ======
        self.color = COLOR_YELLOW
        self.trail_size = 3

    def update(self, dt):
        """
        Aggiorna il proiettile.

        Args:
            dt: Delta time (secondi)
        """
        # Aggiorna lifetime
        self.age += dt

        # Movimento lineare
        self.x += self.vx * dt
        self.y += self.vy * dt

    def render(self, surface, camera=None):
        """
        Disegna il proiettile.

        Args:
            surface: Surface pygame dove disegnare
        """
        # Converte coordinate mondo -> schermo se la camera è disponibile.
        if camera is not None:
            screen_x, screen_y = camera.world_to_screen(self.x, self.y)
        else:
            screen_x, screen_y = self.x, self.y

        screen_x = int(screen_x)
        screen_y = int(screen_y)

        # Disegna il corpo principale
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.radius)

        # Disegna una traccia (effetto scia)
        trail_length = int(self.speed * 0.3)
        trail_x = screen_x - int(self.vx * 0.1)
        trail_y = screen_y - int(self.vy * 0.1)
        pygame.draw.line(
            surface,
            COLOR_MAGENTA,
            (screen_x, screen_y),
            (trail_x, trail_y),
            1,
        )

        # Debug: Mostra hitbox se DEBUG_MODE attivo
        if DEBUG_MODE:
            pygame.draw.circle(surface, COLOR_GREEN, (screen_x, screen_y), self.radius, 1)

    def is_alive(self, world_size=None):
        """
        Controlla se il proiettile è ancora attivo.

        Returns:
            True se il proiettile è ancora in vita e nello schermo
        """
        # Fuori dal mondo (se disponibile), altrimenti fallback alla viewport.
        if world_size is not None:
            world_w, world_h = world_size
            margin = 64
            if self.x < -margin or self.x > world_w + margin:
                return False
            if self.y < -margin or self.y > world_h + margin:
                return False
        else:
            if self.x < -50 or self.x > SCREEN_WIDTH + 50:
                return False
            if self.y < -50 or self.y > SCREEN_HEIGHT + 50:
                return False

        # Lifetime scaduto
        if self.age >= self.lifetime:
            return False

        return True

    def get_rect(self):
        """
        Ritorna un rettangolo per facilità di collision detection.

        Returns:
            Oggetto pygame.Rect intorno al proiettile
        """
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    def check_collision_circle(self, other_rect):
        """
        Verifica collisione circolare con un rettangolo.

        Args:
            other_rect: pygame.Rect da controllare

        Returns:
            True se c'è collisione
        """
        # Distanza dal centro del proiettile al rettangolo
        closest_x = max(other_rect.left, min(self.x, other_rect.right))
        closest_y = max(other_rect.top, min(self.y, other_rect.bottom))

        distance_x = self.x - closest_x
        distance_y = self.y - closest_y

        distance = math.sqrt(distance_x**2 + distance_y**2)
        return distance < self.radius

    def get_damage(self):
        """Ritorna il danno del proiettile."""
        return self.damage

    def get_position(self):
        """Ritorna la posizione del proiettile."""
        return (self.x, self.y)
