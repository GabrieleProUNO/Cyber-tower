"""
BossEnemy: Nemico boss finale specializzato.

Responsabilità:
- IA complessa con fasi
- Attacchi combinati
- Pattern movimento elaborato
- Effetti speciali
- Loot raro
"""

import pygame
import math
import random
from entities.enemy import Enemy
from entities.projectile import Projectile
from config import *


class BossEnemy(Enemy):
    """
    Nemico boss finale con IA avanzata.

    Attributi:
        - phase: Fase del boss (1, 2, 3)
        - attack_pattern: Pattern di attacco attuale
        - minions: Nemici minori generati
        - shield: Scudo temporaneo
        - ultimate_cooldown: Cooldown attacco finale
    """

    def __init__(self, x, y, boss_name="Boss Finale", floor=18):
        """
        Inizializza il boss.

        Args:
            x, y: Posizione
            boss_name: Nome del boss
            floor: Piano (scala difficoltà)
        """
        # Salute scale con floor
        health = 15 + (floor - 18) * 2

        super().__init__(x, y, width=48, height=48, health=health, speed=1.8, aggro_range=400)

        # ====== BOSS SPECIFICO ======
        self.boss_name = boss_name
        self.floor = floor

        # ====== FASI ======
        self.phase = 1  # 1, 2, 3
        self.phase_timer = 0.0
        self.phase_health_threshold = [
            health,  # Inizio
            health * 0.66,  # Fase 2 a 66%
            health * 0.33,  # Fase 3 a 33%
        ]

        # ====== ATTACCHI ======
        self.attack_pattern = 0  # Pattern attuale (0-3)
        self.pattern_timer = 0.0
        self.pattern_duration = 3.0

        self.fire_cooldown = 0.0
        self.fire_delay = 1.5  # Spara ogni 1.5 secondi

        self.projectiles = []

        # ====== SPECIAL ATTACKS ======
        self.ultimate_cooldown = 0.0
        self.ultimate_delay = 8.0  # Ultimate ogni 8 secondi

        self.shield = 0.0  # Scudo extra
        self.shield_max = 5.0

        # ====== RENDERING ======
        self.color = COLOR_MAGENTA  # Boss color
        self.glow_offset = 0.0

        print(f"⚔️  BOSS SPAWNED: {boss_name} (Piano {floor})")
        print(f"   Salute: {health} | Fase: {self.phase}")

    def update(self, dt, player, tilemap):
        """Aggiorna il boss cada frame."""
        super().update(dt, player, tilemap)

        if self.is_dead:
            return

        # ====== AGGIORNA FASI ======
        self._update_phase(dt)

        # ====== AGGIORNA ATTACCHI ======
        self._update_attacks(dt, player)
        self._update_projectiles(dt, tilemap)

        # ====== AGGIORNA SCUDO ======
        if self.shield > 0:
            self.shield -= dt * 0.5  # Scudo diminuisce nel tempo

        # ====== AGGIORNA GLOW ======
        self.glow_offset = math.sin(self.phase_timer * 3) * 5

        # ====== AGGIORNA IA ======
        if self.state == self.STATE_CHASE:
            self._ai_boss_chase(player)

    def _update_phase(self, dt):
        """Aggiorna le fasi del boss."""
        if self.health <= self.phase_health_threshold[2] and self.phase != 3:
            self.phase = 3
            print(f"⚔️  FASE 3! Il boss si infuria!")

        elif self.health <= self.phase_health_threshold[1] and self.phase != 2:
            self.phase = 2
            print(f"⚔️  FASE 2! Il boss accelera!")

        self.phase_timer += dt

    def _update_projectiles(self, dt, tilemap):
        """Aggiorna i proiettili del boss."""
        world_size = tilemap.get_world_size()
        for projectile in self.projectiles[:]:
            projectile.update(dt)
            if not projectile.is_alive(world_size):
                self.projectiles.remove(projectile)

    def _update_attacks(self, dt, player):
        """Aggiorna il sistema di attacco del boss."""
        self.fire_cooldown -= dt
        self.ultimate_cooldown -= dt
        self.pattern_timer -= dt

        if self.pattern_timer <= 0:
            self.pattern_timer = self.pattern_duration
            self.attack_pattern = random.randint(0, 3)

        # ====== ESEGUI PATTERN ======
        if self.state == self.STATE_CHASE:
            if self.attack_pattern == 0:
                self._attack_burst_fire(player)
            elif self.attack_pattern == 1:
                self._attack_spiral(player)
            elif self.attack_pattern == 2:
                self._attack_aimed(player)
            elif self.attack_pattern == 3:
                self._attack_spread(player)

            # ====== ULTIMATE ======
            if self.ultimate_cooldown <= 0 and self.health < self.max_health * 0.5:
                self._attack_ultimate(player)
                self.ultimate_cooldown = self.ultimate_delay

    def _attack_burst_fire(self, player):
        """Attacco: Sparo rapido in serie."""
        if self.fire_cooldown > 0:
            return

        # Calcola direzione verso player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            dx /= distance
            dy /= distance

        # Spara 2-3 proiettili
        num_projectiles = 2 if self.phase == 1 else 3
        for i in range(num_projectiles):
            angle_offset = (i - num_projectiles // 2) * 15
            angle_rad = math.atan2(dy, dx) + math.radians(angle_offset)

            proj_dx = math.cos(angle_rad)
            proj_dy = math.sin(angle_rad)

            projectile = Projectile(
                self.rect.centerx,
                self.rect.centery,
                proj_dx,
                proj_dy,
                speed=300,
                lifetime=10.0,
                damage=1,
            )
            self.projectiles.append(projectile)

        self.fire_cooldown = self.fire_delay

    def _attack_spiral(self, player):
        """Attacco: Proiettili a spirale."""
        if self.fire_cooldown > 0:
            return

        angle = (self.phase_timer * 360) % 360
        angle_rad = math.radians(angle)

        dx = math.cos(angle_rad)
        dy = math.sin(angle_rad)

        projectile = Projectile(
            self.rect.centerx,
            self.rect.centery,
            dx,
            dy,
            speed=280,
            lifetime=10.0,
            damage=1,
        )
        self.projectiles.append(projectile)

        self.fire_cooldown = self.fire_delay * 0.7

    def _attack_aimed(self, player):
        """Attacco: Mirato preciso al player."""
        if self.fire_cooldown > 0:
            return

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            dx /= distance
            dy /= distance

            projectile = Projectile(
                self.rect.centerx,
                self.rect.centery,
                dx,
                dy,
                speed=350,  # Più veloce
                lifetime=10.0,
                damage=1,
            )
            self.projectiles.append(projectile)

        self.fire_cooldown = self.fire_delay * 1.2

    def _attack_spread(self, player):
        """Attacco: 8 proiettili a ventola."""
        if self.fire_cooldown > 0:
            return

        for i in range(8):
            angle = (i / 8) * 360
            angle_rad = math.radians(angle)

            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)

            projectile = Projectile(
                self.rect.centerx,
                self.rect.centery,
                dx,
                dy,
                speed=250,
                lifetime=8.0,
                damage=1,
            )
            self.projectiles.append(projectile)

        self.fire_cooldown = self.fire_delay * 2.5

    def _attack_ultimate(self, player):
        """Attacco finale: Massiccia scarica."""
        print(f"⚡ {self.boss_name} usa l'attacco FINALE!")

        # Attacco spread * 2
        for i in range(16):
            angle = (i / 16) * 360
            angle_rad = math.radians(angle)

            dx = math.cos(angle_rad)
            dy = math.sin(angle_rad)

            projectile = Projectile(
                self.rect.centerx,
                self.rect.centery,
                dx,
                dy,
                speed=200,
                lifetime=6.0,
                damage=2,  # Più danno!
            )
            self.projectiles.append(projectile)

        # Scudo temporaneo
        self.shield = self.shield_max
        print(f"🛡️  Boss si protegge con scudo!")

    def _ai_boss_chase(self, player):
        """IA del boss: Insegue e attacca."""
        dx = player.rect.centerx - self.rect.centerx
        distance = abs(dx)

        # Mantieni distanza
        preferred_distance = 200

        if distance > preferred_distance + 50:
            self.vx = self.speed * 1.5 * (1 if dx > 0 else -1)
        elif distance < preferred_distance - 50:
            self.vx = -self.speed * (1 if dx > 0 else -1)
        else:
            self.vx = 0

    def take_damage(self, damage=1):
        """Boss riceve danno."""
        # Scudo riduce danno
        if self.shield > 0:
            shield_reduction = min(self.shield, damage * 0.5)
            damage -= shield_reduction
            self.shield -= shield_reduction

        if damage > 0:
            return super().take_damage(int(damage))

        return False

    def drop_loot(self):
        """Boss droppa loot raro."""
        if not self.can_drop_loot:
            return None

        self.can_drop_loot = False

        # Boss sempre droppa roba buona
        loot_type = random.choices(
            ["epic_weapon", "epic_item", "massive_coins"],
            weights=[40, 40, 20],
        )[0]

        if loot_type == "epic_weapon":
            return {
                "type": "epic_upgrade",
                "amount": 1,
                "pos": (self.rect.centerx, self.rect.centery),
            }
        elif loot_type == "epic_item":
            return {
                "type": "rare_item",
                "amount": 3,
                "pos": (self.rect.centerx, self.rect.centery),
            }
        else:
            return {
                "type": "coins",
                "amount": 500,
                "pos": (self.rect.centerx, self.rect.centery),
            }

    def render(self, surface, camera):
        """Disegna il boss con effetti speciali."""
        if self.is_dead:
            return

        screen_x, screen_y = camera.world_to_screen(
            self.rect.x, self.rect.y + self.glow_offset
        )

        # ====== SCUDO ======
        if self.shield > 0:
            shield_radius = int(30 + self.shield * 5)
            pygame.draw.circle(
                surface,
                COLOR_CYAN,
                (int(screen_x + self.width // 2), int(screen_y + self.height // 2)),
                shield_radius,
                3,
            )

        # ====== CORPO BOSS ======
        pygame.draw.rect(
            surface, self.color, (screen_x, screen_y, self.width, self.height)
        )
        pygame.draw.rect(
            surface, COLOR_WHITE, (screen_x, screen_y, self.width, self.height), 3
        )

        # ====== NOME ======
        font = pygame.font.Font(None, 28)
        name_text = font.render(self.boss_name, True, self.color)
        surface.blit(name_text, (int(screen_x) - 20, int(screen_y) - 30))

        # ====== BARRA SALUTE ======
        bar_width = self.width + 10
        bar_height = 8
        bar_y = screen_y - 15

        # Barra grigia
        pygame.draw.rect(surface, COLOR_DARK_GRAY, (screen_x - 5, bar_y, bar_width, bar_height))

        # Barra salute
        health_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(surface, COLOR_RED, (screen_x - 5, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, COLOR_WHITE, (screen_x - 5, bar_y, bar_width, bar_height), 1)

        # ====== LABEL FASE ======
        fase_text = font.render(f"FASE {self.phase}", True, COLOR_MAGENTA)
        surface.blit(fase_text, (int(screen_x) + self.width - 30, int(screen_y) - 30))

        # ====== PROIETTILI ======
        for projectile in self.projectiles:
            projectile.render(surface, camera)

    def get_projectiles(self):
        """Ritorna i proiettili sparati."""
        return self.projectiles
