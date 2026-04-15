"""
Enemy Manager: Gestisce tutti i nemici di un livello.

Responsabilità:
- Spawnare nemici
- Aggiornare lista nemici
- Gestire collisioni (proiettili vs nemici)
- Gestire danno (player vs nemici, nemici vs player)
- Drop loot
"""

import pygame
from entities.enemy_walker import WalkerEnemy
from entities.enemy_ranged import RangedEnemy
from entities.enemy_jumper import JumperEnemy
from config import *


class EnemyManager:
    """
    Gestisce tutti i nemici del livello.

    Metodi:
        - spawn_enemy(type, x, y): Crea un nemico
        - update(dt, player, tilemap, projectiles): Aggiorna nemici
        - render(surface, camera): Disegna nemici
        - check_damage(): Controlla danni fra nemici e player
        - get_all_loot(): Raccoglie loot dai nemici morti
    """

    # Tipi di nemico disponibili
    WALKER = "walker"
    RANGED = "ranged"
    JUMPER = "jumper"

    def __init__(self):
        """Inizializza il manager."""
        self.enemies = []
        self.dead_enemies = []
        self.loot_items = []  # Monete e ricompense droppate

    def spawn_enemy(self, enemy_type, x, y, **kwargs):
        """
        Crea e aggiunge un nemico.

        Args:
            enemy_type: Tipo di nemico (WALKER, RANGED, JUMPER)
            x, y: Posizione di spawn
            **kwargs: Parametri aggiuntivi (health, speed, aggro_range)

        Returns:
            Il nemico creato
        """
        if enemy_type == self.WALKER:
            enemy = WalkerEnemy(x, y, **kwargs)
        elif enemy_type == self.RANGED:
            enemy = RangedEnemy(x, y, **kwargs)
        elif enemy_type == self.JUMPER:
            enemy = JumperEnemy(x, y, **kwargs)
        else:
            print(f"❌ Tipo nemico sconosciuto: {enemy_type}")
            return None

        self.enemies.append(enemy)
        print(
            f"✓ Nemico {enemy_type} spawnato a ({x}, {y})"
        )
        return enemy

    def update(self, dt, player, tilemap, player_projectiles):
        """
        Aggiorna tutti i nemici.

        Args:
            dt: Delta time
            player: Oggetto Player
            tilemap: Oggetto Tilemap
            player_projectiles: Lista di proiettili del player
        """
        # ====== AGGIORNA NEMICI VIVI ======
        for enemy in self.enemies[:]:
            enemy.update(dt, player, tilemap)

            # ====== CONTROLLA DANNO DA PROIETTILI ======
            self._check_projectile_damage(enemy, player_projectiles)

            # ====== CONTROLLA DANNO DA CONTATTO (WALKER) ======
            if enemy.__class__.__name__ == "WalkerEnemy":
                if enemy.can_attack_player(player):
                    enemy.attack_player(player)

            # ====== CONTROLLA PROIETTILI NEMICI (RANGED) ======
            if hasattr(enemy, "projectiles"):
                self._check_enemy_projectile_damage(enemy.projectiles, player)

            # ====== GESTISCI MORTE ======
            if enemy.is_dead:
                self.dead_enemies.append(enemy)
                self.enemies.remove(enemy)

                # Drop loot
                loot = enemy.drop_loot()
                if loot:
                    self.loot_items.append(loot)

    def _check_projectile_damage(self, enemy, projectiles):
        """
        Verifica collisione fra proiettili del player e nemico.

        Args:
            enemy: Nemico da controllare
            projectiles: Lista di proiettili del player
        """
        for projectile in projectiles[:]:
            if enemy.rect.collidepoint(projectile.x, projectile.y):
                # Proiettile colpisce nemico
                damage = projectile.get_damage()
                enemy.take_damage(damage)

                # Rimuovi proiettile
                projectiles.remove(projectile)
                print(
                    f"💥 Proiettile colpisce nemico! "
                    f"({enemy.health}/{enemy.max_health})"
                )

    def _check_enemy_projectile_damage(self, enemy_projectiles, player):
        """
        Verifica collisione fra proiettili nemici e player.

        Args:
            enemy_projectiles: Lista di proiettili nemici
            player: Oggetto Player
        """
        for projectile in enemy_projectiles[:]:
            # Collisione circolare con il player
            if projectile.check_collision_circle(player.rect):
                # Proiettile colpisce player
                damage = projectile.get_damage()
                if player.take_damage(damage):
                    enemy_projectiles.remove(projectile)
                    print(f"💥 Proiettile nemico colpisce player!")

    def render(self, surface, camera):
        """
        Disegna tutti i nemici.

        Args:
            surface: Surface pygame
            camera: Oggetto Camera
        """
        for enemy in self.enemies:
            enemy.render(surface, camera)

        # Disegna anche nemici morti per un po' (effetto sparizione)
        for dead_enemy in self.dead_enemies[:]:
            if dead_enemy.death_time > 1.0:
                self.dead_enemies.remove(dead_enemy)

    def spawn_wave(self, wave_data, tilemap):
        """
        Spavna una wave di nemici da dati.

        Format wave_data:
        [
            {"type": "walker", "x": 100, "y": 200, "health": 3},
            {"type": "ranged", "x": 300, "y": 200, "health": 2},
        ]

        Args:
            wave_data: Lista di nemici da spawnare
            tilemap: Oggetto Tilemap (per validazione)
        """
        for enemy_data in wave_data:
            enemy_type = enemy_data.get("type", self.WALKER)
            x = enemy_data.get("x", 100)
            y = enemy_data.get("y", 100)

            # Validazione semplice
            if x < 0 or x > tilemap.world_width:
                print(f"⚠️  Spawn X out of bounds: {x}")
                continue

            self.spawn_enemy(enemy_type, x, y)

    def collect_loot(self, player):
        """
        Raccoglie il loot caduto dai nemici.

        Args:
            player: Oggetto Player

        Returns:
            Quantità di monete raccolte
        """
        total_coins = 0

        for loot in self.loot_items[:]:
            loot_rect = pygame.Rect(loot["pos"][0] - 10, loot["pos"][1] - 10, 20, 20)

            if player.rect.colliderect(loot_rect):
                if loot["type"] == "coins":
                    total_coins += loot["amount"]
                    print(f"💰 Raccolto {loot['amount']} monete!")
                elif loot["type"] == "healing":
                    player.heal(loot["amount"])
                    print(f"✨ Pozione trovata!")

                self.loot_items.remove(loot)

        return total_coins

    def render_loot(self, surface, camera):
        """
        Disegna il loot sullo schermo.

        Args:
            surface: Surface pygame
            camera: Oggetto Camera
        """
        font = pygame.font.Font(None, 20)

        for loot in self.loot_items:
            screen_x, screen_y = camera.world_to_screen(loot["pos"][0], loot["pos"][1])

            if loot["type"] == "coins":
                pygame.draw.circle(surface, COLOR_YELLOW, (int(screen_x), int(screen_y)), 5)
                text = font.render(f"+{loot['amount']}", True, COLOR_YELLOW)
                surface.blit(text, (int(screen_x) + 10, int(screen_y) - 5))
            elif loot["type"] == "healing":
                pygame.draw.circle(surface, COLOR_RED, (int(screen_x), int(screen_y)), 5)
                text = font.render("+1HP", True, COLOR_RED)
                surface.blit(text, (int(screen_x) + 10, int(screen_y) - 5))

    def get_enemy_count(self):
        """Ritorna il numero di nemici vivi."""
        return len(self.enemies)

    def get_all_enemies(self):
        """Ritorna lista di tutti i nemici vivi."""
        return self.enemies.copy()

    def clear_all(self):
        """Rimuove tutti i nemici (per cambio livello)."""
        self.enemies.clear()
        self.dead_enemies.clear()
        self.loot_items.clear()
