"""
Enemy Manager: gestisce tutti i nemici di un livello.
"""

import pygame
from entities.enemy_walker import WalkerEnemy
from entities.enemy_ranged import RangedEnemy
from entities.enemy_jumper import JumperEnemy
from config import *


class EnemyManager:
    """Gestisce tutti i nemici del livello."""

    WALKER = "walker"
    RANGED = "ranged"
    JUMPER = "jumper"

    def __init__(self):
        self.enemies = []
        self.dead_enemies = []
        self.loot_items = []

    def spawn_enemy(self, enemy_type, x, y, **kwargs):
        """Crea e aggiunge un nemico."""
        if enemy_type == self.WALKER:
            enemy_class = WalkerEnemy
        elif enemy_type == self.RANGED:
            enemy_class = RangedEnemy
        elif enemy_type == self.JUMPER:
            enemy_class = JumperEnemy
        else:
            print(f"Tipo nemico sconosciuto: {enemy_type}")
            return None

        try:
            enemy = enemy_class(x, y, **kwargs)
        except TypeError as exc:
            print(f"Parametri wave non validi per '{enemy_type}': {exc}")
            enemy = enemy_class(x, y)

        self.enemies.append(enemy)
        print(f"Nemico {enemy_type} spawnato a ({x}, {y})")
        return enemy

    def update(self, dt, player, tilemap, player_projectiles):
        """Aggiorna tutti i nemici."""
        for enemy in self.enemies[:]:
            enemy.update(dt, player, tilemap)

            self._check_projectile_damage(enemy, player_projectiles)

            if enemy.__class__.__name__ == "WalkerEnemy" and enemy.can_attack_player(player):
                enemy.attack_player(player)

            if hasattr(enemy, "projectiles"):
                self._check_enemy_projectile_damage(enemy.projectiles, player)

            if enemy.is_dead:
                self.dead_enemies.append(enemy)
                self.enemies.remove(enemy)

                loot = enemy.drop_loot()
                if loot:
                    self.loot_items.append(loot)

    def _check_projectile_damage(self, enemy, projectiles):
        """Collisione fra proiettili del player e nemico."""
        for projectile in projectiles[:]:
            if projectile.check_collision_circle(enemy.rect):
                enemy.take_damage(projectile.get_damage())
                projectiles.remove(projectile)

    def _check_enemy_projectile_damage(self, enemy_projectiles, player):
        """Collisione fra proiettili nemici e player."""
        for projectile in enemy_projectiles[:]:
            if projectile.check_collision_circle(player.rect):
                if player.take_damage(projectile.get_damage()):
                    enemy_projectiles.remove(projectile)

    def render(self, surface, camera):
        """Disegna tutti i nemici."""
        for enemy in self.enemies:
            enemy.render(surface, camera)

        for dead_enemy in self.dead_enemies[:]:
            if dead_enemy.death_time > 1.0:
                self.dead_enemies.remove(dead_enemy)

    def spawn_wave(self, wave_data, tilemap):
        """Spawna una wave da configurazione."""
        for enemy_data in wave_data:
            enemy_type = enemy_data.get("type", self.WALKER)
            x = enemy_data.get("x", 100)
            y = enemy_data.get("y", 100)
            enemy_kwargs = {
                key: value
                for key, value in enemy_data.items()
                if key not in {"type", "x", "y"}
            }

            if x < 0 or x > tilemap.world_width or y < 0 or y > tilemap.world_height:
                print(f"Spawn fuori mappa: ({x}, {y})")
                continue

            self.spawn_enemy(enemy_type, x, y, **enemy_kwargs)

    def collect_loot(self, player):
        """Raccoglie il loot caduto dai nemici."""
        total_coins = 0

        for loot in self.loot_items[:]:
            loot_rect = pygame.Rect(loot["pos"][0] - 10, loot["pos"][1] - 10, 20, 20)

            if player.rect.colliderect(loot_rect):
                if loot["type"] == "coins":
                    total_coins += loot["amount"]
                elif loot["type"] == "healing":
                    player.heal(loot["amount"])

                self.loot_items.remove(loot)

        return total_coins

    def render_loot(self, surface, camera):
        """Disegna il loot sullo schermo."""
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
        return len(self.enemies)

    def get_all_enemies(self):
        return self.enemies.copy()

    def clear_all(self):
        self.enemies.clear()
        self.dead_enemies.clear()
        self.loot_items.clear()
