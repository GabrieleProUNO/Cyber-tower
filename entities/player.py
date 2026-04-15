"""
Classe Player: Gestisce il giocatore principale.

Responsabilità:
- Movimento fluido (accelerazione/frizione)
- Salto e gravità
- Mira con mouse e sparo
- Gestione della salute (4 punti)
- Collisioni con piattaforme (placeholder)
- Rendering
"""

import pygame
import math
from config import *


class Player(pygame.sprite.Sprite):
    """
    Rappresenta il giocatore nella scena di gioco.

    Attributi:
        - Posizione e velocità (x, y, vx, vy)
        - Salute (health)
        - Stato di salto (jumping, coyote time)
        - Mira e sparo (direzione tubo)
        - Dimensioni del collider

    Metodi:
        - handle_input(): Gestisce WASD e mouse
        - update(dt): Aggiorna fisica
        - render(): Disegna il player
        - take_damage(): Subisce danno
        - add_coins(): Raccoglie monete
    """

    def __init__(self, x, y, width=40, height=40):
        """
        Inizializza il Player.

        Args:
            x, y: Posizione iniziale
            width, height: Dimensioni del rect collider
        """
        super().__init__()

        # ====== POSIZIONE E DIMENSIONI ======
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height

        # ====== FISICA ======
        self.vx = 0.0  # Velocità X
        self.vy = 0.0  # Velocità Y (positivo = giù)
        self.gravity = GRAVITY
        self.max_speed = PLAYER_MAX_SPEED
        self.acceleration = PLAYER_ACCELERATION
        self.friction = PLAYER_FRICTION

        # ====== SALTO ======
        self.jump_force = PLAYER_JUMP_FORCE
        self.is_jumping = False
        self.is_grounded = True
        self.coyote_time = 0.1  # Tempo per saltare dopo aver lasciato la piattaforma
        self.coyote_timer = 0.0

        # ====== SALUTE ======
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.invulnerable = False
        self.invulnerable_time = 0.0
        self.invulnerable_duration = 0.5  # 0.5 secondi di invulnerabilità dopo colpo

        # ====== MIRA E SPARO ======
        self.aim_x = 0.0
        self.aim_y = 0.0
        self.gun_offset_distance = 30  # Distanza del tubo dal centro

        # ====== RENDERING ======
        self.color_normal = COLOR_CYAN
        self.color_hit = COLOR_RED
        self.color_current = self.color_normal
        self.facing_right = True
        self.use_simple_bounds = False

    # ========================================================================
    # METODI DI INPUT E AGGIORNAMENTO
    # ========================================================================

    def handle_input(self, keys, mouse_pos):
        """
        Gestisce l'input del giocatore (tastiera e mouse).

        Args:
            keys: Dict di tasti premuti (pygame.key.get_pressed())
            mouse_pos: Posizione del mouse (x, y)
        """
        # ====== MOVIMENTO ORIZZONTALE ======
        input_x = 0.0

        # WASD o Frecce
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            input_x -= 1.0
            self.facing_right = False
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            input_x += 1.0
            self.facing_right = True

        # Accelerazione fluida
        if input_x != 0:
            self.vx += input_x * self.acceleration
            # Limita velocità massima
            if abs(self.vx) > self.max_speed:
                self.vx = self.max_speed if self.vx > 0 else -self.max_speed
        else:
            # Frizione quando nessun input
            self.vx *= self.friction

        # ====== SALTO ======
        if keys[pygame.K_SPACE]:
            if self.is_grounded or self.coyote_timer > 0:
                self.is_jumping = True
                self.vy = self.jump_force
                self.is_grounded = False
                self.coyote_timer = 0.0  # Consuma il coyote time

        # ====== MIRA CON MOUSE ======
        self._update_aim(mouse_pos)

    def _update_aim(self, mouse_pos):
        """
        Aggiorna la direzione di mira basandosi sulla posizione del mouse.

        Args:
            mouse_pos: Posizione del mouse (x, y)
        """
        player_center_x = self.rect.centerx
        player_center_y = self.rect.centery

        # Calcola vettore dal player al mouse
        dx = mouse_pos[0] - player_center_x
        dy = mouse_pos[1] - player_center_y

        # Normalizza (evita divisione per zero)
        distance = math.sqrt(dx**2 + dy**2)
        if distance > 0:
            dx /= distance
            dy /= distance

        self.aim_x = dx
        self.aim_y = dy

    def update(self, dt):
        """
        Aggiorna la logica del player ogni frame.

        Args:
            dt: Delta time (secondi dal frame precedente)
        """
        if dt > 0.1:
            dt = 0.1  # Cap delta time per stabilità

        # ====== GRAVITÀ ======
        if not self.is_grounded:
            self.vy += self.gravity

        # ====== MOVIMENTO ======
        self.rect.x += self.vx
        self.rect.y += self.vy

        # ====== COLLISIONI SEMPLICI (opzionali, utili solo in sandbox locale) ======
        if self.use_simple_bounds:
            self._handle_collisions()

        # ====== COYOTE TIME ======
        if not self.is_grounded:
            self.coyote_timer -= dt
        else:
            self.coyote_timer = self.coyote_time

        # ====== INVULNERABILITÀ POST-DANNO ======
        if self.invulnerable:
            self.invulnerable_time -= dt
            if self.invulnerable_time <= 0:
                self.invulnerable = False
                self.color_current = self.color_normal

    def _handle_collisions(self):
        """
        Gestisce collisioni semplici (bordi schermo e piattaforme base).
        (Espanderemo con tilemap nella Fase 3)
        """
        # Bordi orizzontali dello schermo
        if self.rect.left < 0:
            self.rect.left = 0
            self.vx = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            self.vx = 0

        # Piattaforma inferiore (ground level)
        ground_y = SCREEN_HEIGHT - 100
        if self.rect.bottom >= ground_y:
            self.rect.bottom = ground_y
            self.vy = 0
            self.is_grounded = True
            self.is_jumping = False
        else:
            self.is_grounded = False

        # Tetto
        if self.rect.top < 0:
            self.rect.top = 0
            self.vy = 0

    def render(self, surface, camera=None):
        """
        Disegna il player sullo schermo.

        Args:
            surface: Surface pygame dove disegnare
        """
        # Aggiorna colore (effetto di danno)
        if self.invulnerable:
            # Lampo rosso durante invulnerabilità
            flash = int(self.invulnerable_time * 10) % 2
            color = self.color_hit if flash == 0 else self.color_normal
        else:
            color = self.color_normal

        if camera is not None:
            draw_rect = pygame.Rect(
                int(self.rect.x - camera.x),
                int(self.rect.y - camera.y),
                self.rect.width,
                self.rect.height,
            )
        else:
            draw_rect = self.rect

        # Corpo del player
        pygame.draw.rect(surface, color, draw_rect)

        # Bordo
        pygame.draw.rect(surface, COLOR_WHITE, draw_rect, 2)

        # Disegna il tubo di mira (gun barrel)
        self._render_gun_barrel(surface, color, camera)

        # Disegna la salute (4 cuori sopra il player)
        self._render_health(surface, draw_rect)

    def _render_gun_barrel(self, surface, color, camera=None):
        """Disegna il tubo di mira dal player verso il mouse."""
        if camera is not None:
            start_x = self.rect.centerx - camera.x
            start_y = self.rect.centery - camera.y
        else:
            start_x = self.rect.centerx
            start_y = self.rect.centery

        end_x = start_x + self.aim_x * self.gun_offset_distance
        end_y = start_y + self.aim_y * self.gun_offset_distance

        pygame.draw.line(surface, COLOR_YELLOW, (start_x, start_y), (end_x, end_y), 3)
        pygame.draw.circle(surface, COLOR_RED, (int(end_x), int(end_y)), 4)

    def _render_health(self, surface, draw_rect):
        """Disegna i 4 cuori della salute sopra il player."""
        heart_y = draw_rect.top - 20
        heart_x = draw_rect.centerx - (self.max_health * 8)

        for i in range(self.max_health):
            if i < self.health:
                # Cuore pieno
                pygame.draw.rect(
                    surface,
                    COLOR_RED,
                    (heart_x + i * 16, heart_y, 12, 12),
                )
            else:
                # Cuore vuoto
                pygame.draw.rect(
                    surface,
                    COLOR_DARK_GRAY,
                    (heart_x + i * 16, heart_y, 12, 12),
                )
                pygame.draw.rect(
                    surface,
                    COLOR_RED,
                    (heart_x + i * 16, heart_y, 12, 12),
                    1,
                )

    # ========================================================================
    # METODI DI AZIONE (Danno, Raccolta, ecc.)
    # ========================================================================

    def take_damage(self, damage=1):
        """
        Subisce danno. Se è invulnerabile, ignora il danno.

        Args:
            damage: Quantità di danno (default 1)

        Returns:
            True se il giocatore è stato colpito, False se invulnerabile
        """
        if self.invulnerable:
            return False

        self.health -= damage
        self.health = max(0, self.health)

        # Attiva invulnerabilità per evitare spam di danno
        self.invulnerable = True
        self.invulnerable_time = self.invulnerable_duration
        self.color_current = self.color_hit

        print(f"💥 Player danneggiato! Salute: {self.health}/{self.max_health}")
        return True

    def heal(self, amount=1):
        """
        Guarisce il giocatore.

        Args:
            amount: Quantità di guarigione (default 1)

        Returns:
            Vera se guarigione applicata, False se già a salute massima
        """
        if self.health >= self.max_health:
            return False

        self.health += amount
        self.health = min(self.health, self.max_health)
        print(f"✨ Player guarito! Salute: {self.health}/{self.max_health}")
        return True

    def is_alive(self):
        """Ritorna True se il giocatore è vivo."""
        return self.health > 0

    def get_gun_position(self):
        """
        Ritorna la posizione della bocca del tubo (per sparare).

        Returns:
            Tupla (x, y) della posizione della bocca dal tubo
        """
        gun_x = self.rect.centerx + self.aim_x * self.gun_offset_distance
        gun_y = self.rect.centery + self.aim_y * self.gun_offset_distance
        return (gun_x, gun_y)

    def get_aim_direction(self):
        """
        Ritorna la direzione di mira normalizzata.

        Returns:
            Tupla (aim_x, aim_y) con valori fra -1 e 1
        """
        return (self.aim_x, self.aim_y)

    def reset_position(self, x, y):
        """
        Resetta il player a una posizione iniziale.

        Args:
            x, y: Nuova posizione
        """
        self.rect.x = x
        self.rect.y = y
        self.vx = 0
        self.vy = 0
        print(f"🔄 Player resettato a ({x}, {y})")
