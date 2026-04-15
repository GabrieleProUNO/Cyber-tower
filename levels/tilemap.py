"""
Sistema Tilemap: Gestisce il caricamento e rendering dei livelli.

Responsabilità:
- Caricamento da file CSV
- Rendering efficiente con tile batching
- Mappa di collisione per AABB detection
- Layer system per parallax
- Tile types (piattaforme, spikes, collectibles, etc.)
"""

import pygame
import csv
import os
from config import *


# ============================================================================
# TILE TYPES
# ============================================================================
TILE_EMPTY = 0
TILE_SOLID = 1           # Piattaforma solida
TILE_SPIKES = 2          # Punte letali
TILE_COLLECTIBLE = 3     # Moneta/Risorsa
TILE_WATER = 4           # Acqua (danno)
TILE_DOOR_EXIT = 5       # Uscita/Porta

# Tile size in pixel
TILE_SIZE = 32

# Mappa colori per tile types
TILE_COLORS = {
    TILE_EMPTY: COLOR_DARK_GRAY,
    TILE_SOLID: COLOR_CYAN,
    TILE_SPIKES: COLOR_RED,
    TILE_COLLECTIBLE: COLOR_YELLOW,
    TILE_WATER: COLOR_MAGENTA,
    TILE_DOOR_EXIT: COLOR_GREEN,
}


class Tilemap:
    """
    Gestisce il caricamento e rendering del tilemap del livello.

    Attributi:
        - grid: Array 2D dei tile types
        - width, height: Dimensioni in tile
        - parallax_layers: Dizionario di layer parallax
        - collision_grid: Mappa di collisione (True = solido)

    Metodi:
        - load_from_csv(filepath): Carica livello da file
        - render(surface, camera): Disegna il tilemap
        - get_collision_grid(): Ritorna mappa di collisione
        - get_tile_at(x, y): Ottiene tile coordinate schermo
        - is_solid(grid_x, grid_y): Controlla se solido
    """

    def __init__(self):
        """Inizializza il tilemap vuoto."""
        self.grid = []  # 2D array di tile types
        self.width = 0  # Larghezza in tile
        self.height = 0  # Altezza in tile
        self.collision_grid = []  # Cache collisione
        self.parallax_layers = {}  # Layer per effetto parallax
        self.world_width = 0  # Larghezza mondo in pixel
        self.world_height = 0  # Altezza mondo in pixel
        self.tile_surfaces = self._create_tile_surfaces()

    def load_from_csv(self, filepath):
        """
        Carica un livello da file CSV.

        Formato CSV:
        - Righe: Rappresentano righe verticali del livello (alto a basso)
        - Colonne: Rappresentano colonne orizzontali (sinistra a destra)
        - Valori: 0-5 per tipo tile
        - Linee vuote o con '#' all'inizio: Ignorate (commenti)

        Args:
            filepath: Percorso file CSV
        """
        if not os.path.exists(filepath):
            print(f"❌ Errore: File {filepath} non trovato!")
            return False

        self.grid = []

        try:
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                for row_index, row in enumerate(reader):
                    # Salta linee vuote e commenti
                    if not row or row[0].startswith('#'):
                        continue

                    # Converti stringhe a interi
                    tile_row = []
                    for col_index, cell in enumerate(row):
                        cell = cell.strip()
                        try:
                            tile_type = int(cell)
                            # Valida tile type (0-5 standard)
                            if tile_type not in TILE_COLORS:
                                tile_type = TILE_EMPTY
                        except ValueError:
                            tile_type = TILE_EMPTY

                        tile_row.append(tile_type)

                    self.grid.append(tile_row)

            if not self.grid:
                print(f"❌ Errore: CSV vuoto o non valido!")
                return False

            # Calcola dimensioni
            self.height = len(self.grid)
            self.width = max(len(row) for row in self.grid) if self.grid else 0

            # Normalizza righe (riempie con empty se necessario)
            for row in self.grid:
                while len(row) < self.width:
                    row.append(TILE_EMPTY)

            # Calcola dimensioni mondo
            self.world_width = self.width * TILE_SIZE
            self.world_height = self.height * TILE_SIZE

            # Costruisci mappa di collisione
            self._build_collision_grid()

            # Crea layer parallax
            self._create_parallax_layers()

            print(
                f"✓ Tilemap caricato: {filepath}"
            )
            print(
                f"  Dimensioni: {self.width}x{self.height} tile "
                f"({self.world_width}x{self.world_height} px)"
            )
            return True

        except Exception as e:
            print(f"❌ Errore caricamento CSV: {e}")
            return False

    def _build_collision_grid(self):
        """Costruisce la griglia di collisione per AABB detection."""
        self.collision_grid = []
        for row in self.grid:
            collision_row = []
            for tile_type in row:
                # Tile solidi: 1 (SOLID), 2 (SPIKES), 4 (WATER)
                is_solid = tile_type in [TILE_SOLID, TILE_SPIKES, TILE_WATER]
                collision_row.append(is_solid)
            self.collision_grid.append(collision_row)

    def _create_parallax_layers(self):
        """Crea layer parallax per effetto profondità."""
        self.parallax_layers = {
            "far_background": {
                "speed_factor": 0.1,  # Molto lento
                "color": (54, 76, 96),
                "elements": self._generate_far_background(),
            },
            "mid_background": {
                "speed_factor": 0.3,  # Medio
                "color": (74, 112, 140),
                "elements": self._generate_mid_background(),
            },
            "close_background": {
                "speed_factor": 0.6,  # Vicino
                "color": (95, 142, 168),
                "elements": self._generate_close_background(),
            },
        }

    def _create_tile_surfaces(self):
        """Crea sprite procedurali per tile più dettagliati."""
        surfaces = {}

        # Solid tile (metallo industriale)
        solid = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        solid.fill((28, 40, 52))
        pygame.draw.rect(solid, (52, 78, 98), (2, 2, TILE_SIZE - 4, TILE_SIZE - 4), 2)
        pygame.draw.line(solid, (80, 125, 148), (4, 8), (TILE_SIZE - 4, 8), 1)
        pygame.draw.line(solid, (20, 28, 40), (4, TILE_SIZE - 8), (TILE_SIZE - 4, TILE_SIZE - 8), 1)
        for bolt in ((6, 6), (TILE_SIZE - 6, 6), (6, TILE_SIZE - 6), (TILE_SIZE - 6, TILE_SIZE - 6)):
            pygame.draw.circle(solid, (130, 164, 184), bolt, 2)
        surfaces[TILE_SOLID] = solid

        # Spikes tile
        spikes = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        spikes.fill((24, 18, 22))
        spike_w = TILE_SIZE // 4
        for i in range(4):
            x = i * spike_w
            points = [(x, TILE_SIZE), (x + spike_w // 2, 6), (x + spike_w, TILE_SIZE)]
            pygame.draw.polygon(spikes, (200, 68, 78), points)
            pygame.draw.polygon(spikes, (255, 130, 120), points, 1)
        surfaces[TILE_SPIKES] = spikes

        # Collectible tile
        collectible = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(collectible, (255, 220, 90, 70), (TILE_SIZE // 2, TILE_SIZE // 2), 14)
        pygame.draw.circle(collectible, (250, 210, 80), (TILE_SIZE // 2, TILE_SIZE // 2), 8)
        pygame.draw.circle(collectible, (255, 246, 170), (TILE_SIZE // 2 - 2, TILE_SIZE // 2 - 2), 3)
        surfaces[TILE_COLLECTIBLE] = collectible

        # Water tile
        water = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        water.fill((20, 42, 72))
        for y in range(5, TILE_SIZE, 6):
            pygame.draw.line(water, (76, 170, 230), (2, y), (TILE_SIZE - 2, y), 1)
        pygame.draw.rect(water, (110, 220, 255), (0, 0, TILE_SIZE, 4))
        surfaces[TILE_WATER] = water

        # Exit tile
        exit_tile = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        exit_tile.fill((24, 48, 30))
        pygame.draw.rect(exit_tile, (88, 220, 110), (3, 3, TILE_SIZE - 6, TILE_SIZE - 6), 2)
        pygame.draw.rect(exit_tile, (150, 255, 180, 90), (8, 5, TILE_SIZE - 16, TILE_SIZE - 10))
        pygame.draw.circle(exit_tile, (206, 255, 220), (TILE_SIZE // 2, TILE_SIZE // 2), 3)
        surfaces[TILE_DOOR_EXIT] = exit_tile

        return surfaces

    def _generate_far_background(self):
        """Genera elementi per il far background (stelle, nebula)."""
        elements = []
        for x in range(self.width):
            for y in range(self.height):
                if (x * 7 + y * 13) % 23 == 0:
                    elements.append((x * TILE_SIZE + 10, y * TILE_SIZE + 10))
        return elements

    def _generate_mid_background(self):
        """Genera elementi per il mid background."""
        elements = []
        for x in range(self.width):
            for y in range(self.height):
                if (x * 11 + y * 17) % 31 == 0:
                    elements.append((x * TILE_SIZE + 15, y * TILE_SIZE + 15))
        return elements

    def _generate_close_background(self):
        """Genera elementi per il close background."""
        elements = []
        for x in range(self.width):
            for y in range(self.height):
                if (x * 5 + y * 19) % 29 == 0:
                    elements.append((x * TILE_SIZE + 8, y * TILE_SIZE + 8))
        return elements

    def render(self, surface, camera):
        """
        Disegna il tilemap sullo schermo con parallax.

        Args:
            surface: Surface pygame
            camera: Oggetto Camera per transformazioni
        """
        self._render_atmosphere(surface, camera)

        # Render parallax layers
        for layer_name, layer_data in self.parallax_layers.items():
            self._render_parallax_layer(surface, layer_data, camera)

        # Render tilemap principale
        self._render_tilemap(surface, camera)

        # Render debug grid (se abilitato)
        if DEBUG_MODE:
            self._render_debug_grid(surface, camera)

    def _render_parallax_layer(self, surface, layer_data, camera):
        """Disegna un layer parallax con offset basato sulla camera."""
        speed_factor = layer_data["speed_factor"]
        color = layer_data["color"]
        elements = layer_data["elements"]

        # Disegna elementi
        for elem_x, elem_y in elements:
            screen_x = elem_x - camera.x * speed_factor
            screen_y = elem_y - camera.y * speed_factor

            # Disegna solo se visibile
            if -50 < screen_x < SCREEN_WIDTH + 50 and -50 < screen_y < SCREEN_HEIGHT + 50:
                pygame.draw.circle(surface, color, (int(screen_x), int(screen_y)), 2)

    def _render_atmosphere(self, surface, camera):
        """Renderizza gradiente e silhouette industriali."""
        top = (8, 14, 24)
        bottom = (18, 32, 48)
        for y in range(SCREEN_HEIGHT):
            t = y / max(1, SCREEN_HEIGHT - 1)
            color = (
                int(top[0] + (bottom[0] - top[0]) * t),
                int(top[1] + (bottom[1] - top[1]) * t),
                int(top[2] + (bottom[2] - top[2]) * t),
            )
            pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

        # Sagoma edifici/paratie, leggermente parallax.
        skyline_y = SCREEN_HEIGHT - 180
        for i in range(12):
            width = 70 + (i % 3) * 30
            height = 80 + (i % 5) * 30
            x = (i * 140) - int(camera.x * 0.08) % 1800
            rect = pygame.Rect(x - 200, skyline_y + 140 - height, width, height)
            pygame.draw.rect(surface, (16, 24, 34), rect)
            pygame.draw.rect(surface, (40, 90, 110), rect, 1)

    def _render_tilemap(self, surface, camera):
        """Disegna i tile del livello."""
        # Calcola range di tile visibili (ottimizzazione)
        start_x = max(0, int(camera.x / TILE_SIZE) - 2)
        end_x = min(self.width, int((camera.x + SCREEN_WIDTH) / TILE_SIZE) + 2)
        start_y = max(0, int(camera.y / TILE_SIZE) - 2)
        end_y = min(self.height, int((camera.y + SCREEN_HEIGHT) / TILE_SIZE) + 2)

        # Disegna tile visibili
        for grid_y in range(start_y, end_y):
            for grid_x in range(start_x, end_x):
                tile_type = self.grid[grid_y][grid_x]

                if tile_type == TILE_EMPTY:
                    continue

                # Calcola posizione schermo
                world_x = grid_x * TILE_SIZE
                world_y = grid_y * TILE_SIZE
                screen_x = world_x - camera.x
                screen_y = world_y - camera.y

                # Disegna tile
                tile_rect = pygame.Rect(int(screen_x), int(screen_y), TILE_SIZE, TILE_SIZE)
                tile_surface = self.tile_surfaces.get(tile_type)
                if tile_surface is not None:
                    surface.blit(tile_surface, tile_rect)
                else:
                    color = TILE_COLORS.get(tile_type, COLOR_WHITE)
                    pygame.draw.rect(surface, color, tile_rect)

                if DEBUG_MODE:
                    pygame.draw.rect(surface, COLOR_WHITE, tile_rect, 1)

    def _render_debug_grid(self, surface, camera):
        """Disegna griglia di debug sopra il tilemap."""
        start_x = max(0, int(camera.x / TILE_SIZE) - 1)
        end_x = min(self.width, int((camera.x + SCREEN_WIDTH) / TILE_SIZE) + 1)
        start_y = max(0, int(camera.y / TILE_SIZE) - 1)
        end_y = min(self.height, int((camera.y + SCREEN_HEIGHT) / TILE_SIZE) + 1)

        for grid_x in range(start_x, end_x):
            world_x = grid_x * TILE_SIZE
            screen_x = world_x - camera.x
            pygame.draw.line(surface, (100, 100, 100), (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)

        for grid_y in range(start_y, end_y):
            world_y = grid_y * TILE_SIZE
            screen_y = world_y - camera.y
            pygame.draw.line(surface, (100, 100, 100), (0, screen_y), (SCREEN_WIDTH, screen_y), 1)

    # ========================================================================
    # METODI DI QUERY
    # ========================================================================

    def get_tile_at(self, world_x, world_y):
        """
        Ottiene il tipo di tile alle coordinate mondo.

        Args:
            world_x, world_y: Coordinate mondo in pixel

        Returns:
            Tile type (0-5) o -1 se fuori limiti
        """
        grid_x = int(world_x / TILE_SIZE)
        grid_y = int(world_y / TILE_SIZE)

        if grid_x < 0 or grid_x >= self.width or grid_y < 0 or grid_y >= self.height:
            return -1

        return self.grid[grid_y][grid_x]

    def is_solid(self, grid_x, grid_y):
        """
        Controlla se un tile è solido.

        Args:
            grid_x, grid_y: Coordinate griglia

        Returns:
            True se solido, False altrimenti
        """
        if grid_x < 0 or grid_x >= self.width or grid_y < 0 or grid_y >= self.height:
            return False

        return self.collision_grid[grid_y][grid_x]

    def get_collision_rect(self, grid_x, grid_y):
        """
        Ottiene il rettangolo di collisione per un tile.

        Args:
            grid_x, grid_y: Coordinate griglia

        Returns:
            Rect per il tile
        """
        return pygame.Rect(
            grid_x * TILE_SIZE,
            grid_y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
        )

    def get_solids_in_rect(self, rect):
        """
        Ottiene tutti i tile solidi in un rettangolo mondo.

        Útile per collision detection.

        Args:
            rect: pygame.Rect in coordinate mondo

        Returns:
            Lista di Rect dei tile solidi
        """
        solids = []

        start_x = int(rect.left / TILE_SIZE)
        end_x = int(rect.right / TILE_SIZE) + 1
        start_y = int(rect.top / TILE_SIZE)
        end_y = int(rect.bottom / TILE_SIZE) + 1

        for grid_y in range(start_y, end_y):
            for grid_x in range(start_x, end_x):
                if self.is_solid(grid_x, grid_y):
                    solids.append(self.get_collision_rect(grid_x, grid_y))

        return solids

    def has_hazard(self, world_x, world_y):
        """
        Controlla se c'è un hazard alle coordinate.

        Args:
            world_x, world_y: Coordinate mondo

        Returns:
            True se c'è uno spike o water
        """
        tile_type = self.get_tile_at(world_x, world_y)
        return tile_type in [TILE_SPIKES, TILE_WATER]

    def has_collectible(self, grid_x, grid_y):
        """
        Controlla se c'è un collectible al tile.

        Args:
            grid_x, grid_y: Coordinate griglia

        Returns:
            True se collectible presente
        """
        if grid_x < 0 or grid_x >= self.width or grid_y < 0 or grid_y >= self.height:
            return False

        return self.grid[grid_y][grid_x] == TILE_COLLECTIBLE

    def has_exit(self, grid_x, grid_y):
        """
        Controlla se c'è un'uscita al tile.

        Args:
            grid_x, grid_y: Coordinate griglia

        Returns:
            True se exit presente
        """
        if grid_x < 0 or grid_x >= self.width or grid_y < 0 or grid_y >= self.height:
            return False

        return self.grid[grid_y][grid_x] == TILE_DOOR_EXIT

    def get_world_size(self):
        """Ritorna le dimensioni del mondo (width, height) in pixel."""
        return (self.world_width, self.world_height)

    def get_grid_size(self):
        """Ritorna le dimensioni della griglia (width, height) in tile."""
        return (self.width, self.height)
