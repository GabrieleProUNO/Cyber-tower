# 🎮 FASE 2: Player Controller - Documentazione

## 📋 Cosa è stato implementato

### 1. **Classe Player** (`entities/player.py`)
#### Responsabilità:
- ✅ Movimento fluido (WASD/Frecce)
- ✅ Gravità e salto realistico
- ✅ Sistema di mira con mouse
- ✅ Sparo di proiettili
- ✅ Gestione della salute (4 cuori)
- ✅ Invulnerabilità post-danno
- ✅ Collisioni base (bordi schermo, ground level)
- ✅ Rendering con visualizzazione salute

#### Attributi Principali:
```python
self.vx, self.vy          # Velocità
self.health               # Salute (0-4)
self.is_grounded          # True se tocca terra
self.coyote_timer         # Permette salto dopo aver lasciato piattaforma
self.invulnerable         # Immunità temporanea post-danno
self.aim_x, self.aim_y    # Direzione di mira (normalizzata)
```

#### Metodi Pubblici:
- `handle_input(keys, mouse_pos)` - Elabora input
- `update(dt)` - Aggiorna fisica
- `render(surface)` - Disegna
- `take_damage(damage)` - Subisce danno
- `heal(amount)` - Guarisce
- `is_alive()` - Verifica se vivo
- `get_gun_position()` - Posizione bocca tubo
- `get_aim_direction()` - Direzione di mira

#### Fisica Implementata:
- **Accelerazione**: Il movimento è smorzato (non istantaneo)
- **Frizione**: Velocità decresce quando nessun input
- **Gravità**: Accelerazione verso il basso costante
- **Salto**: Impulso verticale negativo, con coyote time di 0.1s
- **Velocità Massima**: 10 pixel/sec (PLAYER_MAX_SPEED)
- **Limite Gravità**: Massima velocità in caduta

---

### 2. **Classe Projectile** (`entities/projectile.py`)
#### Responsabilità:
- ✅ Movimento lineare uniforme
- ✅ Collision detection circolare
- ✅ Lifetime automatico
- ✅ Rendering con effetto scia
- ✅ Distruzione fuori schermo

#### Attributi Principali:
```python
self.x, self.y            # Posizione (float)
self.vx, self.vy          # Velocità
self.radius               # Raggio collider (5 pixel)
self.lifetime             # Tempo massimo di vita
self.age                  # Età attuale
self.damage               # Danno inflitto
```

#### Metodi Pubblici:
- `update(dt)` - Aggiorna posizione
- `render(surface)` - Disegna
- `is_alive()` - Controlla se attivo
- `get_rect()` - Rettangolo per collision detection
- `check_collision_circle(other_rect)` - Collisione circolare-rettangolo

#### Velocità Proiettile:
- **Velocità Standard**: 500 pixel/sec
- **Lifetime**: 10 secondi
- **Danno**: 1 punto (configurabile)

---

### 3. **Integrazione in LevelState** (`states/level_state.py`)
#### Nuove Funzionalità:
- ✅ Spawn del Player all'inizio del livello
- ✅ Controlli Player integrati
- ✅ Sistema di sparo (click sinistro)
- ✅ Gestione proiettili (lista dinamica)
- ✅ Cooldown tra spari
- ✅ Collision detection (da Fase 3)
- ✅ HUD con salute/monete/piano
- ✅ Schermata di game over (salute = 0)
- ✅ Schermata di completamento livello (test con Y)

#### Cooldown Sparo:
- **Delay**: 0.15 secondi tra spari (6.67 spari/sec max)

#### Comandi di Debug (quando DEBUG_MODE = True):
```
F - Infliggi 1 danno al player
H - Guarisci il player di 1 punto
Y - Completa il livello (test)
```

---

## 🕹️ Controlli Implementati

### Movimento
| Input | Azione |
|-------|--------|
| **W** o **↑** | Movimento su |
| **A** o **←** | Movimento sinistra |
| **S** o **↓** | Movimento giù |
| **D** o **→** | Movimento destra |

### Salto
| Input | Azione |
|-------|--------|
| **Spazio** | Salta (solo se a terra o con coyote time) |

### Mira e Sparo
| Input | Azione |
|-------|--------|
| **Mouse** | Mira verso il cursore |
| **Click SX** | Spara un proiettile |

### Menu/Debug
| Input | Azione |
|-------|--------|
| **ESC** | Torna all'Hub |
| **F** | Danno (debug) |
| **H** | Heal (debug) |
| **Y** | Completa livello (test) |

---

## 🎯 Meccaniche Implementate

### 1. **Movimento Fluido**
- Accelerazione graduale in 4 direzioni (non binario)
- Frizione per rallentamento naturale
- Velocità massima di 10 px/sec
- Nessun cambio istantaneo di direzione

### 2. **Gravità e Salto**
- Gravità costante: 0.5 px/sec²
- Forza salto: -15 px/sec (verso l'alto)
- Coyote Time: 0.1 secondi (puoi saltare dopo aver lasciato una piattaforma)
- Invulnerable timer: 0.5 secondi dopo danno

### 3. **Mira e Sparo**
- Mira segue il mouse in tempo reale
- Tubo di mira visualizzato graficamente
- Proiettili sparati dalla bocca del tubo
- Velocità proiettile: 500 px/sec
- Cooldown: 150ms tra spari

### 4. **Salute**
- 4 punti vita (cuori)
- Visualizzati sopra il player
- Danno da nemici (implementato nei metodi)
- Guarigione disponibile
- Invulnerabilità temporanea (lampeggio rosso)

### 5. **Collisioni Semplici**
- **Bordi schermo**: Player non esce dai bordi
- **Ground level**: Piattaforma base a y=620px
- **Tetto**: Limite superiore a y=0
- **Proiettili**: Collision detection circolare

---

## 📊 Equilibrio Gameplay

### Movimento
- **Accelerazione**: 0.8 px/frame - Movimento responsivo ma fluido
- **Frizione**: 0.85 - Rallenta naturalmente
- **Velocità Max**: 10 px/sec - Velocità media

### Salto
- **Forza Salto**: -15 px/sec - Altezza ragionevole (~75px)
- **Gravità**: 0.5 px/sec² - Caduta naturale

### Sparo
- **Velocità**: 500 px/sec - Rapida ma non istantanea
- **Cooldown**: 150ms - ~6-7 spari/sec
- **Danno**: 1 punto - Base per nemici

---

## 🔧 Configurazione (config.py)

```python
# Movimento
GRAVITY = 0.5
PLAYER_MAX_SPEED = 10
PLAYER_ACCELERATION = 0.8
PLAYER_FRICTION = 0.85
PLAYER_JUMP_FORCE = -15

# Salute
PLAYER_MAX_HEALTH = 4

# Debug
DEBUG_MODE = True
```

Modifica questi valori in `config.py` per bilanciare il gameplay.

---

## 🧪 Come Testare

```bash
python main.py
```

1. Clicca "Inizia Gioco" dal menu
2. Clicca "Inizia Livello" dall'hub
3. Usa **WASD/Frecce** per muoverti
4. Premi **Spazio** per saltare
5. Muovi il **mouse** per mirare
6. **Click sinistro** per sparare
7. Premi **F** per simulare danno
8. Premi **Y** per completare il livello (test)

---

## 🐛 Note Tecniche

### Precision Handling
- Posizione del player in interi (Rect)
- Posizione proiettili in float (per fluidità)
- Delta time sempre capped a 100ms di sicurezza

### Memory Management
- Proiettili rimossi dalla lista quando scaduti
- Nessuna memory leak
- Sprite groups per ottimizzazione futura

### Physics Accuracy
- Movimento indipendente da FPS (dt-based)
- Gravità costante e prevedibile
- Salto sempre alla stessa altezza

---

## 🚀 Prossime Fasi

**Fase 3**: Tilemap e Telecamera
- Caricamento livelli da file
- Collisioni precise con piattaforme
- Camera che segue il player

**Fase 4**: Nemici e Combattimento
- Classe Enemy base
- IA semplice
- Damage ragdoll
- Mini-boss

**Fase 5**: UI e Inventario
- Menu inventario avanzato
- Combinazione oggetti
- Dialoghi NPC

---

**✅ Fase 2 Completata! Pronto per Fase 3** 🚀
