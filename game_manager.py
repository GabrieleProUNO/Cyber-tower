"""
GameManager: Gestore centralizzato dello stato del gioco.
Gestisce il loop principale, il cambio di stati e lo stato globale del giocatore.
"""

import pygame
import sys
from config import *


class GameManager:
    """
    Gestore principale del gioco. Coordina:
    - Loop principale a 60 FPS
    - Cambio tra stati (Menu, Hub, Livello, etc.)
    - Stato globale del giocatore (salute, monete, inventario, floor attuale)
    """

    def __init__(self):
        """Inizializza il GameManager e Pygame."""
        pygame.init()

        # Configurazione schermo
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        self.clock = pygame.time.Clock()

        # Stato del gioco
        self.running = True
        self.current_state = None
        self.states = {}  # Dizionario degli stati disponibili

        # Stato globale del giocatore (salvataggio leggero)
        self.player_state = {
            "current_floor": HUB_FLOOR,
            "health": PLAYER_MAX_HEALTH,
            "coins": 0,
            "inventory": [],
            "upgrades": {},  # Potenziamenti permanenti
        }

    def register_state(self, state_name, state_instance):
        """
        Registra uno stato nel gestore.

        Args:
            state_name: Nome dell'stato (e.g., STATE_MENU)
            state_instance: Istanza della classe dello stato
        """
        self.states[state_name] = state_instance

    def change_state(self, new_state_name):
        """
        Cambia lo stato attuale. Chiama __exit__ dello stato corrente
        e __enter__ del nuovo stato.

        Args:
            new_state_name: Nome dello stato verso cui cambiare
        """
        if new_state_name not in self.states:
            print(f"⚠️  Errore: Stato '{new_state_name}' non registrato!")
            return

        # Esci dallo stato attuale
        if self.current_state is not None:
            self.current_state.__exit__()

        # Cambia stato
        self.current_state = self.states[new_state_name]
        self.current_state.__enter__()

        print(f"✓ Cambio stato: {new_state_name}")

    def run(self):
        """
        Avvia il loop principale del gioco.
        Continua fino a quando running è False.
        """
        if self.current_state is None:
            print("❌ Errore: Nessuno stato iniziale impostato!")
            return

        print(f"🎮 Avvio gioco: {GAME_TITLE}")
        print(f"📊 Risoluzione: {SCREEN_WIDTH}x{SCREEN_HEIGHT} @ {FPS} FPS")

        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in secondi

            # Elaborazione eventi
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Aggiornamenti e rendering dello stato attuale
            self.current_state.handle_events(events)
            self.current_state.update(dt)
            self.current_state.render()

            # Refresh display
            pygame.display.flip()

        self.quit()

    def quit(self):
        """Termina il gioco e chiude Pygame."""
        print("👋 Chiusura gioco...")
        pygame.quit()
        sys.exit()

    def get_player_state(self):
        """Ritorna lo stato globale del giocatore."""
        return self.player_state

    def set_player_health(self, health):
        """Imposta la salute del giocatore."""
        self.player_state["health"] = max(0, min(health, PLAYER_MAX_HEALTH))

    def add_coins(self, amount):
        """Aggiunge monete al giocatore."""
        self.player_state["coins"] += amount
        print(f"💰 +{amount} monete! Totale: {self.player_state['coins']}")

    def set_current_floor(self, floor):
        """Imposta il piano attuale."""
        self.player_state["current_floor"] = floor
        print(f"📍 Floor {floor}")
