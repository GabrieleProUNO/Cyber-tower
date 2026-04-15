# 🏗️ Cyber-Tower: Echoes of Industry

Un action-platformer 2D in stile Metroidvania sviluppato in Python 3 con Pygame.

## 📋 Configurazione Rapida

### Installazione

```bash
# Clone il repository
git clone <repo-url>
cd Cyber-tower

# Installa le dipendenze
pip install -r requirements.txt
```

### Avvio del Gioco

```bash
python main.py
```

## 🎮 Panoramica del Gioco

- **Mondo**: Torre di 18 piani + 1 hub
- **Genere**: Action-Platformer 2D (ispirato a Hollow Knight)
- **Tema**: Cyberpunk + Rivoluzione Industriale
- **Stile Visivo**: Minimale 2D

### Meccaniche Principali

- Esplorare ampi livelli
- Combattere nemici e mini-boss
- Raccogliere monete e risorse
- Combinare oggetti per potenziamenti
- Progressione lineare (Piano 0 Hub → Piani 1-18)

## 📂 Struttura del Progetto

```
Cyber-Tower/
├── main.py                  # Entry point
├── config.py               # Costanti globali
├── game_manager.py         # Gestore stato del gioco
├── states/                 # Gestione stati (Menu, Hub, Livelli, etc.)
│   ├── base_state.py      # Classe base
│   ├── menu_state.py      # Menu principale
│   ├── hub_state.py       # Piano 0 (Hub)
│   ├── level_state.py     # Livelli attivi (Fase 3-4)
│   ├── inventory_state.py # Inventario (Fase 5)
│   └── gameover_state.py  # Game Over
├── entities/              # Entità di gioco (Player, Nemici, etc.)
│   └── player.py          # (Fase 2)
├── levels/                # Gestione livelli
│   └── tilemap.py         # (Fase 3)
├── ui/                    # Interfaccia utente
│   └── ui_manager.py      # (Fase 5)
└── assets/                # Risorse (immagini, suoni, font)
```

## 🎯 Fasi di Sviluppo

### ✅ Fase 1: Setup e Game State Manager
- ✓ Finestra Pygame a 60 FPS
- ✓ GameManager centralizzato
- ✓ Sistema di gestione stati
- ✓ Menu principale, Hub, Livelli, Inventario, GameOver

### 🔄 Fase 2: Player Controller
- [ ] Classe Player
- [ ] Movimento fluido (WASD)
- [ ] Salto e gravità
- [ ] Sistema di mira e sparo (mouse)
- [ ] Gestione salute (4 cuori)

### 🔄 Fase 3: Tilemap e Telecamera
- [ ] Sistema di caricamento livelli (CSV/Tiled)
- [ ] Camera che segue il player
- [ ] Collisioni con il tilemap

### 🔄 Fase 4: Nemici, IA e Combattimento
- [ ] Classe base Enemy
- [ ] Nemici base con IA semplice
- [ ] Mini-boss
- [ ] Logica proiettili e collisioni

### 🔄 Fase 5: UI, Inventario e NPC
- [ ] Visualizzazione salute/monete
- [ ] Sistema inventario
- [ ] Menu combinazione oggetti
- [ ] Sistema dialoghi NPC

### 🔄 Fase 6: Loop di Progressione
- [ ] Completamento livello
- [ ] Ritorno all'hub
- [ ] Salvataggio progressione
- [ ] Finale del gioco

## 🕹️ Controlli (Versione Finale)

- **WASD** o **Frecce**: Movimento
- **Spazio**: Salto
- **Mouse**: Mirare
- **Click sinistro**: Sparare
- **E**: Interagire
- **I**: Inventario
- **ESC**: Pausa/Menu
- **Frecce su/giù + Enter**: Navigazione menu

## 🎨 Stile Visivo

- **Risoluzione**: 1280x720
- **FPS**: 60
- **Sprites**: Minimali, 2D
- **Colori**: Cyberpunk (Cyan, Magenta) + Toni industriali

## 📝 Note di Sviluppo

- Codice organizzato in moduli OOP
- Ogni classe ha una responsabilità singola
- Commenti in italiano per chiarezza
- Facile da estendere con nuove meccaniche

## 🔧 Dipendenze

- **pygame**: Libreria per lo sviluppo di giochi 2D
- **numpy**: Operazioni numeriche (per future ottimizzazioni)

---

**Status**: 🚀 Fase 1 Completata (scegli di proseguire alla Fase 2)