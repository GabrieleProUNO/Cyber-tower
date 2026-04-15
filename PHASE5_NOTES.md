# 🎮 FASE 5: Inventario, NPC e UI - Documentazione

## 📋 Cosa è stato implementato

### 1. **Sistema Item** (`items.py`) - 330+ righe

#### Item Types Disponibili:
```python
COIN - Valuta di base (stackabile)
HEALTH_POTION - Guarigione (stackabile)
SCRAP_METAL - Materiale crafting (stackabile)
ENERGY_CORE - Risorsa rara (stackabile)
BLUEPRINT - Progetto tecnico (non-stackabile)
UPGRADE_DAMAGE - +1 danno (non-stackabile)
UPGRADE_SPEED - +2 velocità (non-stackabile)
UPGRADE_HEALTH - +1 max salute (non-stackabile)
KEY - Chiave speciale (non-stackabile)
```

#### Proprietà Item:
- **Name**: Nome leggibile
- **Description**: Descrizione per HUD
- **Icon**: Emoji icona
- **Stackable**: Se può essere stackato
- **Rarity**: common/uncommon/rare/epic
- **Value**: Valore in monete

#### Rarity Colors:
```
Common    → Bianco
Uncommon  → Verde
Rare      → Cyan
Epic      → Magenta
```

#### Ricette Combinazione:
```python
SCRAP_METAL + ENERGY_CORE → UPGRADE_DAMAGE
SCRAP_METAL + SCRAP_METAL → BLUEPRINT
ENERGY_CORE + BLUEPRINT → UPGRADE_SPEED
```

#### WorldItem:
- Item caduto nel mondo
- Animazione su/giù (bob)
- Timeout dopo 30 secondi
- Rendering con icona colorata

---

### 2. **Sistema Inventario** (`inventory.py`) - 280+ righe

#### Metodologia:
- **Slot-Based**: 12 slot massimi (MAX_INVENTORY_SLOTS)
- **Auto-Stack**: Item identici si stackano automaticamente
- **Crafting**: Combina due item se ricetta esiste

#### Metodi Pubblici:
```python
add_item(item)              # Aggiunge item, auto-stack
remove_item_at_slot(idx)    # Rimuove da slot
get_item_at_slot(idx)       # Ottiene item a slot
count_item_type(type)       # Conta tipo item
consume_items(type, qty)    # Consuma risorse (crafting)
try_combine(slot1, slot2)   # Combina due item
get_value()                 # Valore totale monete
is_full()                   # Check se pieno
to_dict() / from_dict()     # Serializzazione
```

#### Workflow Inventario:
```
1. Item caduto nel mondo → WorldItem
2. Player vicino:
   a. Raccolto automaticamente
   b. Aggiunto all'inventario
   c. Se stackabile e identico: stack
   d. Altrimenti: nuovo slot
3. Player apre inventario (I)
4. Seleziona due item (↑↓)
5. Premi C per combinare
6. Se ricetta esiste: item combinato
7. Slot liberati, nuovo item aggiunto
```

#### Persistenza:
```python
inv_data = inventory.to_dict()
# Salva inventory_data...
inv_restored = Inventory.from_dict(inv_data)
```

---

### 3. **Sistema NPC** (`npc.py`) - 380+ righe

#### Classe Dialog:
```python
Dialog(lines, options)
- lines: Lista di righe di dialogo
- options: Dict {label → siguiente_dialog}
- get_current_line(): Riga attuale
- next_line(): Avanza
- is_complete(): Finito?
```

#### NPC Base:
```python
NPC(name, x, y, dialog, shop_items)
- start_conversation(player): Inizia dialogo
- advance_dialog(): Avanza riga
- end_conversation(): Termina
- render(surface, camera): Disegna
- render_dialog(surface): HUD dialogo
- render_shop(surface): Menu negozio
- buy_item(idx, coins): Acquista
- is_near_player(player): Verifica distanza
```

#### Shop:
```python
ShopItem(item_type, price, quantity)
- can_buy(player_coins): Check denaro
- buy(): Acquista item
```

#### NPCs Predefiniti:
1. **Commerciante** (400, 600)
   - Vende: Health Potion, Upgrade Damage/Speed/Health
   
2. **Anziano Saggio** (300, 600)
   - Solo dialogo (supporto narrativo)
   
3. **Mastro Fucina** (600, 600)
   - Vende: Scrap Metal, Energy Core (crafting resources)

#### Dialogo Flow:
```
1. Player si avvicina NPC
2. Pressa E: Conversa
3. Legge riga dialogo
4. Pressa E: Avanza riga
5. Completo: Dialogo termina
6. NPC con shop mostra opzioni
```

---

### 4. **UI Manager** (`ui/ui_manager.py`) - 350+ righe

#### Responsabilità:
- ✅ HUD principale (durante livello)
- ✅ Interfaccia inventario
- ✅ Dialoghi NPC
- ✅ Menu shop
- ✅ Statistiche hub
- ✅ Font management

#### HUD Principale:
```
Top-Left:
  ❤️  Salute: 3/4
  💰 Monete: 42
  📍 Piano: 1
  Nemici: 3
  Wave: 1/2

Top-Right:
  ⏱️  23.5s

Bottom-Right:
  I: Inventario | E: Interagisci | ESC: Pausa
```

#### Inventario UI:
```
┌─────────────────────────────────────┐
│ 🎒 INVENTARIO                        │
│ Slot: 5/12 | Valore: 240 💰         │
├─────────────────────────────────────┤
│ [1] 💰 Moneta x12                   │
│ [2] 🧪 Pozione Guarigione x3        │
│ [3] ⚙️  Rottame Metallico            │
│ [4] ⚡ Core Energetico               │
│ [5] 📋 Progetto Tecnico               │
│ e altri...                           │
├─────────────────────────────────────┤
│ ↑↓: Seleziona | C: Combina | I: Chiudi│
└─────────────────────────────────────┘
```

#### Shop UI:
```
┌──────────── 🛍️ NEGOZIO ───────────────┐
│ 🧪 Pozione Guarigione - 50💰         │
│ 💥 Upgrade Danno - 200💰             │
│ ⚡ Upgrade Velocità - 200💰          │
│ ❤️  Upgrade Salute - 250💰           │
└─────────────────────────────────────┘
```

---

## 🎯 **Flusso di Gioco (Fase 1-5)**

### Nel Livello:
```
Update Loop:
  1. Nemico muore → drop_loot()
  2. WorldItem caduto nel mondo
  3. Player raccogli → add_item()
  4. Inventario aggiornato

HUD:
  - Mostra salute, monete, nemici
  - Hint controlli inventario
```

### Nel Loot:
```
Enemy.die():
  loot = drop_loot()  # Dict con type/amount
  if loot:
    world_item = WorldItem(...)
    manager.loot_items.add(world_item)

WorldItem.update():
  if collide_player:
    item = world_item.get_item()
    inventory.add_item(item)
    loot_items.remove(world_item)
```

### Nel Crafting:
```
Player preme I:
  show_inventory = True
  
↑↓ per selezionare slot:
  selected_slot = (selected_slot ± 1) % 12
  
C per combinare:
  item1 = inventory[slot1]
  item2 = inventory[slot2]
  
  result_type = item1.can_combine_with(item2)
  if result_type:
    inventory.remove(slot1)
    inventory.remove(slot2)
    inventory.add(Item(result_type))
    print("✨ Crafting success!")
```

### Nell'Hub - Shop:
```
Player interagisce con NPC:
  npc.start_conversation()
  render_dialog(surface)
  
Se shop disponibile:
  render_shop(surface)
  
Player seleziona item:
  E: Acquista
  Item aggiunto inventario
  Monete decurtate
```

---

## 📊 **Equilibrio Economico**

### Monete Guadagnate:
```
Enemy Kills:
  Walker:    1-5 monete
  Ranged:    1-7 monete (50% bonus)
  Jumper:    1-5 monete

Loot Rari:   50-100 monete
```

### Costi Shop:
```
Health Potion:        50 💰
Upgrade Damage:      200 💰
Upgrade Speed:       200 💰
Upgrade Health:      250 💰
```

### Valori Crafting:
```
SCRAP_METAL: 10 💰
ENERGY_CORE: 100 💰
BLUEPRINT:   75 💰
UPGRADE_*:   200-250 💰
```

**Bilancio**: Player guadagna sufficiente per comprare 1-2 upgrade per livello

---

## 🎨 **Design UI**

### Font Hierarchy:
```
font_large (48px)  - Titoli sezioni
font_normal (32px) - HUD principale
font_small (24px)  - Dettagli inventario
font_tiny (20px)   - Controlli hint
```

### Color Scheme:
```
Primary:   CYAN     - Focus/HP
Alert:     RED      - Danno/Nemici
Positive:  GREEN    - Azioni
Rarity:    MAGENTA  - Epic items
```

### Overlay Transparency:
```
Inventario: 180 alpha (semi-trasparente)
Menu:       200 alpha (più scuro)
```

---

## 🕹️ **Controlli Fase 5**

| Input | Azione |
|-------|--------|
| **I** | Toggle Inventario |
| **↑↓** | Seleziona slot inventario |
| **C** | Combina item selezionati |
| **E** | Interagisci NPC / Avanza dialogo |
| **Click** | Compra da shop NPC |

---

## 🚀 **Integration Points**

### LevelState:
```python
# Nel __init__
self.inventory = Inventory()
self.ui_manager = UIManager()
self.npcs = []  # (non nel livello diretto)

# Nel update
if PRESSED[pygame.K_i]:
  ui_manager.toggle_inventory()

if ui_manager.show_inventory:
  if PRESSED[pygame.K_c]:
    inventory.try_combine(slot1, slot2)

# Nel render
ui_manager.render_main_hud(surface, player, self)
if ui_manager.show_inventory:
  ui_manager.render_inventory(surface, inventory, coins)
```

### HubState:
```python
# Nel __init__
self.npcs = [
  create_merchant(),
  create_elder(),
  create_forge_master(),
]

# Nel update
for npc in npcs:
  if npc.is_near_player(player) and PRESSED[pygame.K_e]:
    npc.start_conversation()

# Nel render
for npc in npcs:
  npc.render(surface, camera)
  if npc.is_talking:
    npc.render_dialog(surface)
  if npc.shop_items:
    npc.render_shop(surface)
```

---

## 📝 **File Statistics**

| File | Linee | Scopo |
|------|-------|-------|
| items.py | 330+ | Sistema item e ricette |
| inventory.py | 280+ | Inventario e crafting |
| npc.py | 380+ | NPC, dialoghi, shop |
| ui_manager.py | 350+ | Gestione UI |

**Totale Fase 5**: 1340+ righe di interfaccia!

---

## 🐛 **Debug Features**

- **Inventario Lista**: Stampato quando aggiunto/consumato
- **Crafting Log**: Mostra combinazioni riuscite/fallite
- **NPC Dialogo**: Stampato ogni riga
- **Shop Transaction**: Logato acquisti

---

## 🎁 **Prossime Fasi**

**Fase 6**: Progressione e Boss
- Salvataggio gioco
- Progressione fra piani
- Boss finale specializzato
- Ending cinematico

---

**✅ Fase 5 Completata! Sistema Inventario e NPC Impeccabile** 💎

Ready for Fase 6: Progressione e Finale!
