"""
Classe Enemy Base: Rappresenta un nemico generico.

Responsabilità:
- Posizione e movimento
- Salute e invulnerabilità
- AI semplice (pattugliamento, inseguimento)
- Rendering
- Loot drop (monete)
- Collision detection

Questa è una classe base da cui derivare nemici specializzati.
"""

import pygame
import math
import random
from config import *


class Enemy(pygame.sprite.Sprite):
    """
    Classe base per tutti i nemici del gioco.

    Attributi:
        - Posizione (rect)
        - Velocità (vx, vy)
        - Salute (health)
        - Raggio di aggro (distanza per inseguire player)
        - Estado (patrolling, chasing, attacking, dead)

    Metodi:
        - update(dt, player, tilemap): Aggiorna stato e movimento
        - take_damage(damage): Riceve danno
        - render(surface, camera): Disegna il nemico
        - drop_loot(): Genera loot alla morte
        - is_alive(): Controlla se vivo
    """

    # Classe enum-like per stati
    STATE_PATROL = "patrol"      # Pattuglia area
    STATE_CHASE = "chase"         # Insegue player
    STATE_ATTACK = "attack"       # Attacca
    STATE_DEAD = "dead"           # Morto

    def __init__(
        self,
        x,
        y,
        width=32,
        height=32,
        health=3,
        speed=2.0,
        aggro_range=200,
    ):
        """
        Inizializza il nemico.

        Args:
            x, y: Posizione iniziale
            width, height: Dimensioni collider
            health: Punti vita
            speed: Velocità di movimento
            aggro_range: Distanza per iniziare a inseguire
        """
        super().__init__()

        # ====== POSIZIONE E DIMENSIONI ======
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height

        # ====== FISICA ======
        self.vx = 0.0
        self.vy = 0.0
        self.speed = speed
        self.gravity = GRAVITY

        # ====== SALUTE ======
        self.health = health
        self.max_health = health
        self.is_dead = False
        self.death_time = 0.0

        # ====== IA ======
        self.state = self.STATE_PATROL
        self.aggro_range = aggro_range
        self.patrol_left = x - 80
        self.patrol_right = x + 80
        self.direction = 1  # 1 = destra, -1 = sinistra
        self.state_timer = 0.0

        # ====== RENDERING ======
        self.color = COLOR_RED
        self.color_dead = COLOR_DARK_GRAY

        # ====== FLAGS ======
        self.is_grounded = False
        self.can_drop_loot = True

    # ========================================================================
    # METODI PRINCIPALI
    # ========================================================================

    def update(self, dt, player, tilemap):
        """
        Aggiorna il nemico ogni frame.

        Args:
            dt: Delta time
            player: Oggetto Player (per inseguimento)
            tilemap: Oggetto Tilemap (per collisioni)
        """
        if self.is_dead:
            self.death_time += dt
            return

        # ====== AGGIORNA IA ======
        self._update_ai(player)

        # ====== AGGIORNA MOVIMENTO ======
        self._update_movement(dt)

        # ====== APPLICA GRAVITÀ ======
        if not self.is_grounded:
            self.vy += self.gravity
        else:
            self.vy = 0

        # ====== AGGIORNA POSIZIONE ======
        self.rect.x += self.vx
        self.rect.y += self.vy

        # ====== GESTISCI COLLISIONI ======
        self._handle_collisions(tilemap)

    def _update_ai(self, player):
        """
        Aggiorna la logica IA del nemico.

        Args:
            player: Oggetto Player
        """
        # Calcola distanza dal player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        # Cambia stato in base a distanza
        if distance < self.aggro_range:
            # Player visibile - passa a chase
            self.state = self.STATE_CHASE
        else:
            # Player troppo lontano - ritorna patrol
            self.state = self.STATE_PATROL

        # Esegui logica stato
        if self.state == self.STATE_PATROL:
            self._ai_patrol()
        elif self.state == self.STATE_CHASE:
            self._ai_chase(player)

    def _ai_patrol(self):
        """IA: Pattuglia avanti e indietro."""
        # Muovi nella direzione corrente
        self.vx = self.speed * self.direction

        # Cambia direzione ai confini della patrol zone
        if self.rect.centerx <= self.patrol_left:
            self.direction = 1
        elif self.rect.centerx >= self.patrol_right:
            self.direction = -1

    def _ai_chase(self, player):
        """
        IA: Insegue il player.

        Args:
            player: Oggetto Player
        """
        # Calcola direzione verso player
        target_x = player.rect.centerx
        dx = target_x - self.rect.centerx

        if dx > 5:
            self.direction = 1
            self.vx = self.speed * 1.2  # Più veloce quando insegue
        elif dx < -5:
            self.direction = -1
            self.vx = self.speed * 1.2
        else:
            self.vx = 0

    def _update_movement(self, dt):
        """Aggiorna il movimento fisico del nemico."""
        pass  # Da implementare nelle sottoclassi se necessario

    def _handle_collisions(self, tilemap):
        """
        Gestisce le collisioni del nemico.

        Args:
            tilemap: Oggetto Tilemap
        """
        from collision import CollisionSystem

        CollisionSystem.check_collisions(self, tilemap)

    def render(self, surface, camera):
        """
        Disegna il nemico sullo schermo.

        Args:
            surface: Surface pygame
            camera: Oggetto Camera
        """
        if self.is_dead:
            return  # Non disegnare nemici morti

        # Converti a screen coords
        screen_x, screen_y = camera.world_to_screen(self.rect.x, self.rect.y)

        # Disegna corpo nemico
        pygame.draw.rect(surface, self.color, (screen_x, screen_y, self.width, self.height))
        pygame.draw.rect(surface, COLOR_WHITE, (screen_x, screen_y, self.width, self.height), 2)

        # Disegna la salute sopra il nemico
        self._render_health(surface, screen_x, screen_y)

        # Debug: mostra direzione
        if DEBUG_MODE:
            end_x = screen_x + (10 * self.direction)
            pygame.draw.line(
                surface,
                COLOR_YELLOW,
                (screen_x + self.width // 2, screen_y + self.height // 2),
                (end_x, screen_y + self.height // 2),
                2,
            )

    def _render_health(self, surface, screen_x, screen_y):
        """Disegna la barra di salute sopra il nemico."""
        bar_width = self.width
        bar_height = 4
        bar_y = screen_y - 8

        # Barra di fondo (grigia)
        pygame.draw.rect(surface, COLOR_DARK_GRAY, (screen_x, bar_y, bar_width, bar_height))

        # Barra di salute (rossa se danneggito, verde se pieno)
        health_percentage = self.health / self.max_health
        health_bar_width = int(bar_width * health_percentage)
        color = COLOR_GREEN if health_percentage > 0.5 else COLOR_RED
        pygame.draw.rect(surface, color, (screen_x, bar_y, health_bar_width, bar_height))

        # Bordo
        pygame.draw.rect(surface, COLOR_WHITE, (screen_x, bar_y, bar_width, bar_height), 1)

    # ========================================================================
    # METODI DI AZIONE
    # ========================================================================

    def take_damage(self, damage=1):
        """
        Riceve danno dal player.

        Args:
            damage: Quantità di danno (default 1)

        Returns:
            True se il nemico è stato colpito
        """
        if self.is_dead:
            return False

        self.health -= damage
        self.health = max(0, self.health)

        if self.health <= 0:
            self._die()

        return True

    def _die(self):
        """Gestisce la morte del nemico."""
        self.is_dead = True
        self.state = self.STATE_DEAD
        self.vx = 0
        self.vy = 0
        print(f"💀 Nemico sconfitto! ({self.rect.centerx}, {self.rect.centery})")

    def drop_loot(self):
        """
        Genera il loot quando il nemico muore.

        Returns:
            Dizionario con tipo e quantità loot
        """
        if not self.can_drop_loot:
            return None

        self.can_drop_loot = False

        # Genera loot casuale
        loot_type = random.choices(
            ["coins", "healing", "nothing"],
            weights=[60, 30, 10],
        )[0]

        if loot_type == "coins":
            amount = random.randint(COINS_DROP_MIN, COINS_DROP_MAX)
            return {"type": "coins", "amount": amount, "pos": (self.rect.centerx, self.rect.centery)}
        elif loot_type == "healing":
            return {"type": "healing", "amount": 1, "pos": (self.rect.centerx, self.rect.centery)}

        return None

    def is_alive(self):
        """Ritorna True se il nemico è vivo."""
        return not self.is_dead

    def get_position(self):
        """Ritorna la posizione del nemico."""
        return (self.rect.centerx, self.rect.centery)

    def set_patrol_zone(self, left, right):
        """
        Imposta la zona di pattugliamento.

        Args:
            left, right: Coordinate sinistra e destra
        """
        self.patrol_left = left
        self.patrol_right = right

    def set_aggro_range(self, range_distance):
        """Imposta il raggio di aggro."""
        self.aggro_range = range_distance
