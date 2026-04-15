"""
Game Progression: Gestisce il loop di progressione fra piani.

Responsabilità:
- Progressione fra piani
- Loop hub -> livello -> risultato
- Salvataggio automatico
- Tracking completamenti
- Ending screen
"""

from config import *


class GameProgression:
    """
    Gestisce il loop completo di progressione del gioco.

    Stato Machine:
    HUB → LEVEL → COMPLETED/FAILED → HUB/GAMEOVER → ...
    """

    STATE_HUB = "hub"
    STATE_LEVEL = "level"
    STATE_LEVEL_COMPLETE = "level_complete"
    STATE_BOSS_DEFEATED = "boss_defeated"
    STATE_GAME_WON = "game_won"
    STATE_GAME_OVER = "game_over"

    def __init__(self, game_manager, save_system):
        """
        Inizializza il sistema progressione.

        Args:
            game_manager: Oggetto GameManager
            save_system: Oggetto SaveSystem
        """
        self.game_manager = game_manager
        self.save_system = save_system
        self.current_state = self.STATE_HUB
        self.playtime = 0.0
        self.level_start_time = 0.0

    def on_level_complete(self, level_state):
        """
        Chiamato quando un livello è completato.

        Args:
            level_state: Stato del livello completato
        """
        current_floor = self.game_manager.player_state["current_floor"]
        coins_collected = getattr(level_state, "collected_coins", 0)
        level_time = level_state.level_time

        print(f"\n✅  LIVELLO {current_floor} COMPLETATO!")
        print(f"   Tempo: {level_time:.1f}s")
        print(f"   Monete: {coins_collected}")

        # Aggiorna stato globale
        self.game_manager.player_state["coins"] += coins_collected
        self.game_manager.player_state["completed_floors"].append(current_floor)

        # Salva salute prima di andare all'hub
        self.game_manager.set_player_health(level_state.player.health)

        # Salvataggio automatico
        self.save_system.autosave(self.game_manager, self.playtime)

        self.current_state = self.STATE_LEVEL_COMPLETE

    def on_boss_defeated(self, level_state):
        """
        Chiamato quando il boss è sconfitto.

        Args:
            level_state: Stato del livello boss
        """
        print(f"\n🏆 BOSS SCONFITTO!")

        # Bonus vittoria
        victory_bonus = 1000
        self.game_manager.add_coins(victory_bonus)

        # Aggiorna stato
        self.game_manager.player_state["health"] = level_state.player.health
        self.game_manager.player_state["completed_floors"].append(FINAL_FLOOR)

        # Salvataggio
        self.save_system.autosave(self.game_manager, self.playtime)

        self.current_state = self.STATE_BOSS_DEFEATED

    def on_game_completed(self):
        """Chiamato quando il gioco è completato (tutti piani + boss)."""
        print(f"\n🎉 GIOCO COMPLETATO!")
        print(f"   Tempo totale: {self.playtime:.1f}s")
        print(f"   Monete finali: {self.game_manager.player_state['coins']}")

        self.current_state = self.STATE_GAME_WON

    def on_player_died(self):
        """Chiamato quando il player muore."""
        print(f"\n💀 GAME OVER!")
        current_floor = self.game_manager.player_state["current_floor"]
        print(f"   Caduto al piano {current_floor}")

        self.current_state = self.STATE_GAME_OVER

    def go_to_next_floor(self):
        """Passa al piano successivo."""
        current_floor = self.game_manager.player_state["current_floor"]
        next_floor = current_floor + 1

        if next_floor > FINAL_FLOOR:
            print(f"❌ Floor fuori limite!")
            return False

        self.game_manager.set_current_floor(next_floor)
        print(f"📍 Passando al Piano {next_floor}...")

        return True

    def go_to_hub(self):
        """Ritorna all'hub."""
        self.game_manager.set_current_floor(HUB_FLOOR)
        self.current_state = self.STATE_HUB
        print(f"🏛️  Ritorno all'Hub...")

    def reset_to_hub(self):
        """Resetta a hub per ricominciare."""
        self.game_manager.player_state["current_floor"] = HUB_FLOOR
        self.game_manager.player_state["health"] = PLAYER_MAX_HEALTH
        self.current_state = self.STATE_HUB
        print(f"🔄 Reset all'Hub...")

    def update(self, dt):
        """Aggiorna il tempo totale."""
        self.playtime += dt

    def is_boss_floor(self):
        """Verifica se il piano attuale è il boss."""
        current_floor = self.game_manager.player_state["current_floor"]
        return current_floor == FINAL_FLOOR

    def is_game_won(self):
        """Verifica se il gioco è vinto."""
        return self.current_state == self.STATE_GAME_WON

    def is_game_over(self):
        """Verifica se il gioco è perso."""
        return self.current_state == self.STATE_GAME_OVER

    def get_completion_percentage(self):
        """
        Calcola la percentuale di completamento.

        Returns:
            Percentuale (0-100)
        """
        completed = len(self.game_manager.player_state.get("completed_floors", []))
        total = FINAL_FLOOR + 1  # 0-18 = 19 piani

        return int((completed / total) * 100)

    def get_stats(self):
        """
        Ritorna statistiche di gioco.

        Returns:
            Dizionario con statistiche
        """
        return {
            "playtime": self.playtime,
            "completed_floors": len(
                self.game_manager.player_state.get("completed_floors", [])
            ),
            "total_floors": FINAL_FLOOR + 1,
            "coins": self.game_manager.player_state["coins"],
            "health": self.game_manager.player_state["health"],
            "completion": self.get_completion_percentage(),
        }

    def format_playtime(self):
        """Formatta il tempo di gioco."""
        hours = int(self.playtime // 3600)
        minutes = int((self.playtime % 3600) // 60)
        seconds = int(self.playtime % 60)

        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
