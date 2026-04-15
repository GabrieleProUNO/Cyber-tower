# 🎮 FASE 4: Nemici e Combattimento - Documentazione

## 📋 Cosa è stato implementato

### 1. **Classe Enemy Base** (`entities/enemy.py`) - 380+ righe

#### Responsabilità:
- ✅ Posizione e movimento con gravità
- ✅ Salute e sistema di danno
- ✅ IA base con stati (patrol, chase, attack, dead)
- ✅ Aggro range (distanza per inseguire player)
- ✅ Rendering con barra salute
- ✅ Loot drop system
- ✅ Collision detection

#### Stati Enemy:
```python
STATE_PATROL = "patrol"    # Pattuglia zona, comportamento passivo
STATE_CHASE = "chase"      # Insegue il player attivamente
STATE_ATTACK = "attack"    # Attacca (per future implementazioni)
STATE_DEAD = "dead"        # Morto, sarà rimosso
```

#### IA Semplice:
- **Patrol**: Cammina fra patrol_left e patrol_right, cambia direzione ai confini
- **Chase**: Se player è dentro aggro_range, insegue con velocità aumentata
- **Distanza**: Usa math.sqrt(dx² + dy²) per calcolo distanza euclidea

#### Rendering:
- Rettangolo colorato (rosso di default)
- Barra salute sopra con colore dinamico (verde/rosso)
- Debug: freccia che mostra direzione

#### Loot Drop:
```python
60% - Monete (COINS_DROP_MIN a COINS_DROP_MAX)
30% - Healing (+1 HP)
10% - Nothing
```

---

### 2. **WalkerEnemy** (`entities/enemy_walker.py`) - 100+ righe

**Specialità**: Nemico base che cammina e attacca da vicino

#### Attributi:
- **attack_range**: 50px (attacco close-range)
- **attack_cooldown**: 1 secondo fra attacchi
- **health**: 3 punti (standard)
- **color**: Rosso

#### IA Customizzata:
- Insegue aggressivamente il player
- Quando in range di attacco, colpisce il player
- Fa danno di 1 punto per attacco

#### Loot:
- Quantità standard

---

### 3. **RangedEnemy** (`entities/enemy_ranged.py`) - 140+ righe

**Specialità**: Nemico che spara proiettili dal distanza

#### Attributi:
- **fire_delay**: 2 secondi fra spari
- **projectile_speed**: 250 px/sec (più lento del player)
- **health**: 2 punti (fragile)
- **color**: Magenta

#### IA Customizzata:
- Si ferma quando vede il player (non muove)
- Spara continuamente verso il player in chase
- Proiettili personalizzati (nemico)

#### Loot:
- 50% più monete rispetto al walker

---

### 4. **JumperEnemy** (`entities/enemy_jumper.py`) - 100+ righe

**Specialità**: Nemico che salta aggressivamente verso il player

#### Attributi:
- **jump_force**: -12 px/sec
- **jump_delay**: 1.2 secondi fra salti
- **jump_range**: 150px (distanza per attivare salto)
- **health**: 4 punti (resistente)
- **color**: Giallo

#### IA Customizzata:
- Move velocemente verso il player
- Quando player è abbastanza vicino, salta
- Calcola direzione per mirare al player durante salto

#### Loot:
- Quantità standard

---

### 5. **EnemyManager** (`entities/enemy_manager.py`) - 380+ righe

**Centralizza la gestione di tutti i nemici**

#### Responsabilità:
- ✅ Spawn nemici con `spawn_enemy(type, x, y)`
- ✅ Update di lista nemici
- ✅ Collision detection (proiettili vs nemici)
- ✅ Damage application (player vs enemy, ranged vs player)
- ✅ Loot collection e rendering
- ✅ Wave management

#### Metodi Pubblici:
```python
spawn_enemy(type, x, y, **kwargs)       # Crea nemico
update(dt, player, tilemap, projectiles) # Aggiorna tutti
render(surface, camera)                  # Disegna nemici
render_loot(surface, camera)             # Disegna loot
collect_loot(player)                     # Raccogli monete
spawn_wave(wave_data, tilemap)          # Spawna wave
get_enemy_count()                        # Conta nemici
clear_all()                              # Pulisce per cambio level
```

#### Damage System:
1. **Proiettile Player vs Enemy**: 
   - Verifica collisione
   - Applica danno
   - Rimuove proiettile

2. **Proiettile Ranged vs Player**:
   - Verifica collisione circolare
   - Applica danno con invulnerabilità
   - Rimuove proiettile

3. **Walker Attack vs Player**:
   - Se in attack_range
   - Applica danno se cooldown permette

---

### 6. **Wave System** (`levels/waves.py`) - 170+ righe

**Configura le ondate (wave) di nemici per livello**

#### Level 1 (Tutorial):
```python
Wave 1: 1 Walker (health=2)
Wave 2: 2 Walker (health=3 default)
```

#### Level 2 (Intermediate):
```python
Wave 1: 1 Walker + 1 Ranged
Wave 2: 2 Jumper
Wave 3: 1 Walker + 1 Ranged + 1 Jumper (difficile!)
```

#### Level 3+ (Scalate):
- Difficoltà aumenta con il piano
- Mix di nemici variegato
- Salute scala dynamicamente
- Generato proceduralmente

#### Funzioni:
```python
get_waves_for_level(floor_number)      # Ritorna wave configurate/generate
generate_scaled_waves(floor_number)    # GenERa wave procedurali
get_boss_wave()                         # Wave del boss finale
```

**Scalamento Difficoltà:**
- Floor 1-2: Manuale
- Floor 3+: `difficulty = 1.0 + (floor - 3) * 0.15` (max 3.0)

---

### 7. **LevelState Integration** (Fase 4)

**Integrazione completa dei nemici nel game loop**

#### Nuovo nel __init__:
```python
self.enemy_manager = None
self.current_wave_index = 0
self.wave_complete = False
self.all_waves_complete = False
```

#### Nel __enter__:
```python
# Carica waves configurate
waves = get_waves_for_level(floor_number)
# Spawna prima wave
self._spawn_next_wave()
```

#### Nel update:
```python
# Aggiorna nemici
enemy_manager.update(dt, player, tilemap, projectiles)

# Raccogli loot
coins_collected = enemy_manager.collect_loot(player)

# Verifica wave completata
if enemy_count == 0 and not wave_complete:
    spawn_next_wave()
```

#### Nel render:
```python
enemy_manager.render(surface, camera)
enemy_manager.render_loot(surface, camera)
```

#### HUD Aggiornato:
- Conta nemici rimanenti
- Wave corrente / totale
- Dinamico e informativo

---

## 🎯 Equilibrio Ganghero

### Walker Enemy:
- **Health**: 3
- **Speed**: 2.5 * 1.2 (in chase)
- **Attack Range**: 50px
- **Attack Damage**: 1
- **Attack Cooldown**: 1s
- **Loot**: 1-5 monete

### Ranged Enemy:
- **Health**: 2 (fragile!)
- **Speed**: 1.5 (lento, immobile in chase)
- **Fire**: Ogni 2 secondi
- **Projectile Speed**: 250 px/sec
- **Projectile Damage**: 1
- **Loot**: 1-7 monete (50% bonus)

### Jumper Enemy:
- **Health**: 4 (resistente)
- **Speed**: 3.0 * 1.3 (in chase)
- **Jump Force**: -12 px/sec
- **Jump Range**: 150px
- **Jump Cooldown**: 1.2s
- **Loot**: 1-5 monete

### Difficoltà Scalamento:
```
Piano 1-2:   Manuale, facile
Piano 3-5:   Principalmente Walker
Piano 6-10:  Mix Walker/Ranged
Piano 11-15: Mix completo (Walker/Ranged/Jumper)
Piano 16-18: Heavy Ranged/Jumper, difficile!
```

---

## 🎨 AI Design

### Algoritmo IA Base:
```
ogni frame:
  1. Calcola distanza dal player
  2. Se distanza < aggro_range:
       STATE = CHASE
     Else:
       STATE = PATROL
  3. Esegui logica per STATE
  4. Applica gravità
  5. Risolvi collisioni
```

### Personalizzazioni Sottoclassi:
- **Walker**: Aggressivo in chase, attacca in range
- **Ranged**: Immobile in chase, spara
- **Jumper**: Veloce in chase, salta in range

---

## 💥 Damage Flow

### Player Spara Proiettile:
```
1. Player preme click
2. Projectile creato da gun_position
3. Update() loop:
   - Projectile si muove
   - EnemyManager verifica collisione
   - Se collisione: enemy.take_damage(1)
   - Projectile rimosso
4. Enemy render barra salute ridotta
```

### Nemico Attacca Player:
```
Walker:
  1. Se distanza < 50px
  2. player.take_damage(1)
  3. player.invulnerable = True (0.5s)
  4. Attack_cooldown = 1s

Ranged:
  1. Projectile creato con IA
  2. Se collisione con player
  3. player.take_damage(1)
  4. Projectile rimosso
```

### Loot System:
```
Enemy muore:
  1. drop_loot() genera tipo
  2. Posizionato a morte_position
  3. Render ogni frame come +coins
  4. Se player collide: collect_loot()
```

---

## 🕹️ Controlli (Fase 1-4)

| Input | Azione |
|-------|--------|
| **WASD/Frecce** | Movimento |
| **Spazio** | Salto |
| **Mouse** | Mira |
| **Click SX** | Spara proiettile |
| **ESC** | Torna all'Hub |
|**F** (debug) | Danno a player |
| **H** (debug) | Heal a player |
| **Y** (debug) | Completa livello |

---

## 📊 File Statistics

| File | Linee | Scopo |
|------|-------|-------|
| enemy.py | 380+ | Enemy base con IA |
| enemy_walker.py | 100+ | Walker specializzato |
| enemy_ranged.py | 140+ | Ranged specializzato |
| enemy_jumper.py | 100+ | Jumper specializzato |
| enemy_manager.py | 380+ | Manager centrale |
| waves.py | 170+ | Configurazione wave |
| level_state.py | +100 | Integrazione |

**Totale Fase 4**: 1400+ righe di combattimento impeccabile!

---

## 🐛 Debug Features

Quando DEBUG_MODE = True:
- **Freccia direzione**: Mostrata sopra nemici
- **Barra salute**: Visualizzata per ogni nemico
- **Wave info**: Stampate al load
- **Damage log**: Ogni colpo registrato
- **Loot log**: Raccolta registrata

---

## 🚀 Prossime Fasi

**Fase 5**: UI, Inventario e NPC
- Menu inventario avanzato
- Combinazione oggetti
- NPC e dialoghi
- Comprare upgrade dall'hub

**Fase 6**: Progressione e Boss
- Salvataggio gioco
- Loop di progressione fra piani
- Boss finale speciale
- Ending

---

## 📝 Note Tecniche

### Wave Management:
```python
# All'inizio del livello
waves = get_waves_for_level(floor)
spawn_wave(waves[0])

# Quando wave completata (enemy_count == 0)
if current_wave_index < len(waves):
    spawn_wave(waves[current_wave_index])
    current_wave_index++
else:
    all_waves_complete = True
```

### Collision Detection:
```python
# Proiettile vs Enemy (punto-rettangolo)
if enemy.rect.collidepoint(projectile.x, projectile.y):
    enemy.take_damage()

# Proiettile Nemico vs Player (circolare)
if projectile.check_collision_circle(player.rect):
    player.take_damage()

# Attack vs Player (distanza Manhattan)
distance = abs(dx) + abs(dy)
if distance < attack_range:
    player.take_damage()
```

### Memory Management:
- Nemici morti rimossi dalla lista attiva
- Loot raccolto rimosso dalla lista
- Nessuna memory leak

---

**✅ Fase 4 Completata! Sistema di Nemici e Combattimento Impeccabile** 💎

Ready for Fase 5: UI, Inventario e NPC!
