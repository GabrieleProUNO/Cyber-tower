# 🎮 FASE 3: Tilemap, Camera e Parallax - Documentazione

## 📋 Cosa è stato implementato

### 1. **Classe Tilemap** (`levels/tilemap.py`)

#### Responsabilità:
- ✅ Caricamento livelli da file CSV
- ✅ Rendering efficiente con culling (mostra solo tile visibili)
- ✅ Sistema parallax a 3 layer (far, mid, close background)
- ✅ Mappa di collisione per AABB detection
- ✅ Tipo di tile: solido, spikes, acqua, monete, uscita
- ✅ Grid debug mode (griglia di collisione)

#### Tile Types:
```python
TILE_EMPTY = 0        # Vuoto (passabile)
TILE_SOLID = 1        # Piattaforma solida
TILE_SPIKES = 2       # Punte letali
TILE_COLLECTIBLE = 3  # Moneta/Risorsa
TILE_WATER = 4        # Acqua (danno)
TILE_DOOR_EXIT = 5    # Uscita/Porta finale
```

#### Tile Size:
- **32x32 pixel** per tile (standard platformer)

#### Metodi Pubblici:
- `load_from_csv(filepath)` - Carica livello da CSV
- `render(surface, camera)` - Disegna con parallax
- `get_tile_at(world_x, world_y)` - Ottiene tile
- `is_solid(grid_x, grid_y)` - Verifica solidità
- `get_solids_in_rect(rect)` - Lista tile solidi in area
- `has_hazard(world_x, world_y)` - Verifica hazard
- `has_collectible(grid_x, grid_y)` - Verifica moneta
- `has_exit(grid_x, grid_y)` - Verifica uscita
- `get_world_size()` - Dimensioni mondo in pixel
- `get_grid_size()` - Dimensioni griglia in tile

#### Parallax System:
3 layer di background che scorrono a velocità diverse:
- **Far Background** (0.1x) - Stelle/nebula, molto lento
- **Mid Background** (0.3x) - Elementi intermedi
- **Close Background** (0.6x) - Elementi vicini

Ogni layer è generato proceduralmente basato sulla griglia.

#### CSV Format:
```csv
# Commenti con # all'inizio della riga
0,0,1,1,0,0,3,0,0,0
1,1,1,1,0,0,1,0,0,0
0,0,0,0,0,0,1,0,0,5
```

---

### 2. **Classe Camera** (`camera.py`)

#### Responsabilità:
- ✅ Seguire il player in tempo reale
- ✅ Smooth lerp (15% per frame)
- ✅ Limiti di bordo (non uscire dal mondo)
- ✅ Conversione coordinate mundo ↔ screen
- ✅ Viewport culling per ottimizzazione

#### Attributi:
```python
self.x, self.y              # Posizione camera (world coords)
self.target_x, target_y     # Target verso cui muovere
self.smooth_factor = 0.15   # Lerp factor
self.use_smooth = True      # Enable/disable smoothing
self.player_offset_x        # Posizione player sullo schermo
self.player_offset_y
```

#### Offset Player sulla Schermata:
- **X**: 1/3 da sinistra (416px su 1280px)
- **Y**: Un po' sopra il centro (288px su 720px)

Questo positioning rende il gioco più piacevole e fornisce spazio visivo davanti al player per mirare.

#### Metodi Pubblici:
- `update(player, tilemap, dt)` - Aggiorna posizione
- `world_to_screen(world_x, world_y)` - Converti coordinate
- `screen_to_world(screen_x, screen_y)` - Converti inverse
- `is_in_view(rect)` - Verifica se visibile
- `get_view_rect()` - Rettangolo di vista
- `set_position(x, y)` - Teleport camera
- `render_debug(surface, player, tilemap)` - Debug overlay

#### Smooth Movement:
Camera si muove con lerp **smooth** invece che seguire istaneamente il player. Questo:
- Rende il movimento fluido e gradevole
- Riduce il motion sickness
- È uno standard nei platform game moderni

**Formula**: `camera_pos += (target - camera_pos) * 0.15`

Ciò significa che il 15% della distanza viene coperto ogni frame, raggiungendo il target asintoticamente.

---

### 3. **Sistema Collisioni** (`collision.py`)

#### Responsabilità:
- ✅ AABB collision detection
- ✅ Sliding collision (platformer fluido)
- ✅ Hazard detection (spikes, water)
- ✅ Collectible detection
- ✅ Exit detection

#### Sliding Collision:
Uno dei pilastri di un buon platformer. Quando il player si scontra:
1. Viene esteso il rect di movimento
2. Risolve collisioni su assi separati (X, Y)
3. Player "scivola" lungo i muri

**Prima (no sliding)**:
```
Se player va diagonale contro un muro,
si ferma completamente.
```

**Dopo (with sliding)**:
```
Se player va diagonale contro muro,
continua a muoversi lateralmente
mentre slide lungo il muro verticale.
```

#### Metodi Pubblici:
- `check_collisions(player, tilemap)` - Risolve collisioni
- `check_hazards(player, tilemap)` - Verifica danno hazard
- `check_collectibles(player, tilemap)` - Verifica monete
- `check_exit(player, tilemap)` - Verifica uscita

#### Coyote Time Integration:
Il sistema collisioni aggiorna automaticamente il `coyote_timer` del player, permettendogli di saltare dopo aver lasciato una piattaforma per 0.1 secondi.

---

## 📊 File Livelli

### `levels/level_01.csv` - Tutorial Level
- **Dimensioni**: 20x15 tile (640x480px)
- **Difficoltà**: Facile
- **Contenuto**: Piattaforme semplici, alcune monete, una uscita
- **Scopo**: Insegnare controlled jump e raccolta

### `levels/level_02.csv` - Intermediate Level
- **Dimensioni**: 25x16 tile (800x512px)
- **Difficoltà**: Media
- **Contenuto**: Piattaforme complesse, hazard (spikes), molta raccolta
- **Scopo**: Test abilità jump e navigazione

### CSV Structure:
```
# Line 1-2: Commenti/header
# Colonne: Tile types separati da virgola
# Righe: Dall'alto al basso
# Linee vuote: Ignorate
```

---

## 🎨 Rendering Pipeline

### Order of Rendering:
1. **Parallax Layers** (dietro il tilemap)
   - Far background (stella)
   - Mid background (elementi intermedi)
   - Close background (elementi vicini)

2. **Tilemap** (colori per tile type)
   - Culling: Solo tile visibili dalla camera
   - Colori standardizzati
   - Grid debug (se DEBUG_MODE)

3. **Entities** (player, nemici, etc.)

4. **Proiettili**

5. **HUD** (salute, monete, tempo)

6. **Debug Info** (camera position, world size)

---

## 🔧 Configurazione

### Tilemap:
```python
TILE_SIZE = 32  # Pixel per tile
```

### Camera:
```python
smooth_factor = 0.15  # 15% lerp per frame
use_smooth = True     # Abilita smoothing
player_offset_x = SCREEN_WIDTH / 3      # Posizione X
player_offset_y = SCREEN_HEIGHT / 2.5   # Posizione Y
```

### Collision:
- **AABB Detection**: Standard industrie
- **Sliding**: Su asse separati
- **Hazard Cooldown**: 0.5s anti-spam
- **Collectible**: Raccolta istantanea

---

## 🕹️ Controlli (Fase 1-3 Integrati)

| Input | Azione |
|-------|--------|
| **WASD/Frecce** | Movimento |
| **Spazio** | Salto |
| **Mouse** | Mira |
| **Click SX** | Spara |
| **ESC** | Torna all'Hub |
| **F** | Danno (debug) |
| **H** | Heal (debug) |
| **Y** | Completa livello (test) |

---

## 🎯 Equilibrio Tilemaps

### Level 1 (Tutorial):
- Poche piattaforme, distanze corte
- Monete facili da raggiungere
- No hazard
- Uscita ovvia

### Level 2 (Intermediate):
- Piattaforme che richiedono timing
- Hazard a terra e intermedi
- Raccolta distribuita
- Uscita nascosta in alto

### Future Levels (Fase 3+):
- Aumentare complexity
- Introdurre nuovi tile types
- Aggiungere elementi dinamici

---

## 🐛 Debug Features

### DEBUG_MODE = True attiva:
- **Griglia di collisione** sullato tilemap
- **Info Camera**: Posizione, target, mondo size
- **Hitbox**: Verde attorno ai proiettili
- **Viewport**: Confini della camera visibili

### Comandi Debug:
- **F**: Danno al player
- **H**: Guarisci player
- **Y**: Completa livello

---

## 🚀 Performance Optimization

### Culling:
Solo i tile visibili dalla camera sono renderizzati.
- Standard: O(n) rendering
- Con culling: O(visible_tiles) <<< O(n)

### Parallax Layers:
Elementi procedurali, generati una sola volta al load anche se lievi al rendering.

### Collision Grid:
Precalcolata al load, non ricalcolata ogni frame.

---

## 🔮 Prossime Fasi

**Fase 4**: Nemici e Combattimento
- Classe Enemy base con IA
- Mini-boss
- Damageable enemies
- Enemy projectiles

**Fase 5**: UI e Inventario
- Menu inventario avanzato
- Combinazione oggetti
- NPC e dialoghi

**Fase 6**: Progressione
- Salvataggio gioco
- Progression logging
- Boss finale

---

## 📝 Note Tecniche

### Coordinate System:
- **World Coords**: Posizione nel mondo (0 a world_width)
- **Screen Coords**: Posizione sullo schermo (0 a SCREEN_WIDTH)
- **Conversione**: `screen = world - camera.x`

### Tile Coordinates:
- **Grid Coords**: Indice tile (0 a width-1, 0 a height-1)
- **Conversione**: `grid_x = world_x / TILE_SIZE`

### Physics Integration:
- Delta time indipendente
- Prevedibile e deterministic
- Velocità in pixel/sec

---

**✅ Fase 3 Completata! Tilemap, Camera e Parallax implementati** 🚀

Pronto per Fase 4: Nemici e Combattimento!
