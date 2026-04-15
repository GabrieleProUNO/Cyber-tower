"""
Classe base astratta per tutti gli stati del gioco.
Definisce l'interfaccia che ogni stato deve implementare.
"""

from abc import ABC, abstractmethod
import pygame


class BaseState(ABC):
    """
    Classe astratta base per tutti gli stati del gioco.

    Uno "stato" rappresenta una schermata o una sezione del gioco:
    - Menu principale
    - Hub (Piano 0)
    - Livello attivo
    - Inventario
    - GameOver

    Ogni stato ha un ciclo di vita:
    - __enter__: inizializzazione quando entra
    - handle_events: elaborazione degli input
    - update: logica di aggiornamento
    - render: disegno della schermata
    - __exit__: pulizia quando esce
    """

    def __init__(self, game_manager):
        """
        Inizializza lo stato.

        Args:
            game_manager: Riferimento al GameManager centrale
        """
        self.game_manager = game_manager
        self.screen = game_manager.screen
        self.clock = game_manager.clock

    def __enter__(self):
        """Chiamato quando lo stato viene attivato."""
        pass

    def __exit__(self):
        """Chiamato quando lo stato viene disattivato (cambio stato)."""
        pass

    @abstractmethod
    def handle_events(self, events):
        """
        Gestisce gli input dell'utente.

        Args:
            events: Lista degli eventi pygame
        """
        pass

    @abstractmethod
    def update(self, dt):
        """
        Aggiorna la logica dello stato.

        Args:
            dt: Delta time (tempo trascorso dall'ultimo frame in secondi)
        """
        pass

    @abstractmethod
    def render(self):
        """Disegna lo stato sullo schermo."""
        pass

    def change_state(self, new_state_name):
        """
        Richiede al GameManager di cambiare stato.

        Args:
            new_state_name: Nome dello stato a cui passare
        """
        self.game_manager.change_state(new_state_name)
