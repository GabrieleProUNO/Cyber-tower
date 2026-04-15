"""
Cyber-Tower: Echoes of Industry
Entry point del gioco.

Per avviare il gioco:
    python main.py
"""

from game_manager import GameManager
from config import *
from states.menu_state import MenuState
from states.hub_state import HubState
from states.level_state import LevelState
from states.inventory_state import InventoryState
from states.gameover_state import GameOverState


def main():
    """Funzione principale: inizializza e avvia il gioco."""

    # Crea il GameManager
    game = GameManager()

    # Istanzia gli stati
    menu_state = MenuState(game)
    hub_state = HubState(game)
    level_state = LevelState(game)
    inventory_state = InventoryState(game)
    gameover_state = GameOverState(game)

    # Registra gli stati nel game manager
    game.register_state(STATE_MENU, menu_state)
    game.register_state(STATE_HUB, hub_state)
    game.register_state(STATE_LEVEL, level_state)
    game.register_state(STATE_INVENTORY, inventory_state)
    game.register_state(STATE_GAMEOVER, gameover_state)

    # Imposta il primo stato (Menu Principale)
    game.change_state(STATE_MENU)

    # Avvia il loop principale del gioco
    game.run()


if __name__ == "__main__":
    main()
