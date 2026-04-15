"""
Save System: Gestisce il salvataggio e caricamento del gioco.

Responsabilità:
- Serializzazione stato gioco
- Salvataggio su file JSON
- Caricamento stato
- Gestione save slot multipli
"""

import json
import os
import copy
from datetime import datetime
from config import *


class SaveData:
    """Rappresenta i dati salvati del gioco."""

    def __init__(self):
        """Inizializza i dati di salvataggio."""
        self.player_state = {
            "current_floor": HUB_FLOOR,
            "health": PLAYER_MAX_HEALTH,
            "max_health": PLAYER_MAX_HEALTH,
            "coins": 0,
            "inventory": [],
            "upgrades": {},
            "completed_floors": [],
        }
        self.timestamp = datetime.now().isoformat()
        self.playtime = 0.0  # Secondi
        self.version = "1.0"

    def to_dict(self):
        """Converte a dizionario per JSON."""
        return {
            "version": self.version,
            "timestamp": self.timestamp,
            "playtime": self.playtime,
            "player_state": self.player_state,
        }

    @staticmethod
    def from_dict(data):
        """Converte da dizionario JSON."""
        save = SaveData()
        save.version = data.get("version", "1.0")
        save.timestamp = data.get("timestamp", save.timestamp)
        save.playtime = data.get("playtime", 0.0)
        save.player_state = data.get("player_state", save.player_state)
        return save

    def __repr__(self):
        """Debug string."""
        floor = self.player_state["current_floor"]
        coins = self.player_state["coins"]
        time_hours = self.playtime // 3600
        time_mins = (self.playtime % 3600) // 60
        return f"SaveData(Floor {floor}, {coins}💰, {int(time_hours)}h{int(time_mins)}m)"


class SaveSystem:
    """Gestisce il salvataggio e caricamento del gioco."""

    SAVES_DIR = "saves"
    AUTOSAVE_FILE = "autosave.json"
    SLOT_FILE_TEMPLATE = "save_slot_{}.json"

    def __init__(self):
        """Inizializza il sistema di salvataggio."""
        # Crea cartella saves se non esiste
        if not os.path.exists(self.SAVES_DIR):
            os.makedirs(self.SAVES_DIR)
            print(f"✓ Cartella '{self.SAVES_DIR}' creata")

    def save_game(self, game_manager, playtime, slot=0):
        """
        Salva il gioco.

        Args:
            game_manager: GameManager con stato gioco
            playtime: Tempo di gioco in secondi
            slot: Numero slot salvataggio (0-4)

        Returns:
            True se salvataggio riuscito
        """
        save_data = SaveData()
        save_data.player_state = copy.deepcopy(game_manager.player_state)
        save_data.playtime = playtime

        filename = os.path.join(self.SAVES_DIR, self.SLOT_FILE_TEMPLATE.format(slot))

        try:
            with open(filename, 'w') as f:
                json.dump(save_data.to_dict(), f, indent=2)
            print(f"✅ Gioco salvato in slot {slot}: {save_data}")
            return True
        except Exception as e:
            print(f"❌ Errore salvataggio: {e}")
            return False

    def autosave(self, game_manager, playtime):
        """
        Salvataggio automatico.

        Args:
            game_manager: GameManager
            playtime: Tempo di gioco
        """
        save_data = SaveData()
        save_data.player_state = copy.deepcopy(game_manager.player_state)
        save_data.playtime = playtime

        filename = os.path.join(self.SAVES_DIR, self.AUTOSAVE_FILE)

        try:
            with open(filename, 'w') as f:
                json.dump(save_data.to_dict(), f, indent=2)
            print(f"💾 Autosave: {save_data}")
            return True
        except Exception as e:
            print(f"⚠️  Errore autosave: {e}")
            return False

    def load_game(self, slot=0):
        """
        Carica un gioco salvato.

        Args:
            slot: Numero slot da caricare

        Returns:
            SaveData caricato, o None se errore
        """
        filename = os.path.join(self.SAVES_DIR, self.SLOT_FILE_TEMPLATE.format(slot))

        if not os.path.exists(filename):
            print(f"⚠️  Nessun salvataggio nel slot {slot}")
            return None

        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            save_data = SaveData.from_dict(data)
            print(f"✅ Gioco caricato dal slot {slot}: {save_data}")
            return save_data
        except Exception as e:
            print(f"❌ Errore caricamento: {e}")
            return None

    def load_autosave(self):
        """
        Carica l'autosave.

        Returns:
            SaveData, o None se non esiste
        """
        filename = os.path.join(self.SAVES_DIR, self.AUTOSAVE_FILE)

        if not os.path.exists(filename):
            return None

        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            return SaveData.from_dict(data)
        except Exception as e:
            print(f"⚠️  Errore caricamento autosave: {e}")
            return None

    def get_save_slots(self):
        """
        Ritorna info di tutti i slot.

        Returns:
            Lista di (slot_num, SaveData o None)
        """
        slots = []
        for i in range(5):
            save_data = self.load_game(i)
            slots.append((i, save_data))
        return slots

    def delete_save(self, slot=0):
        """
        Elimina un salvataggio.

        Args:
            slot: Numero slot

        Returns:
            True se eliminato
        """
        filename = os.path.join(self.SAVES_DIR, self.SLOT_FILE_TEMPLATE.format(slot))

        try:
            if os.path.exists(filename):
                os.remove(filename)
                print(f"✓ Salvataggio slot {slot} eliminato")
                return True
        except Exception as e:
            print(f"❌ Errore eliminazione: {e}")

        return False

    def export_save(self, slot=0, export_path="save_export.json"):
        """
        Esporta un salvataggio.

        Args:
            slot: Numero slot
            export_path: Percorso esportazione

        Returns:
            True se esportato
        """
        save_data = self.load_game(slot)
        if save_data is None:
            return False

        try:
            with open(export_path, 'w') as f:
                json.dump(save_data.to_dict(), f, indent=2)
            print(f"✓ Salvataggio esportato in {export_path}")
            return True
        except Exception as e:
            print(f"❌ Errore esportazione: {e}")
            return False

    def import_save(self, slot=0, import_path="save_export.json"):
        """
        Importa un salvataggio.

        Args:
            slot: Numero slot destinazione
            import_path: Percorso importazione

        Returns:
            True se importato
        """
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
            save_data = SaveData.from_dict(data)

            filename = os.path.join(self.SAVES_DIR, self.SLOT_FILE_TEMPLATE.format(slot))
            with open(filename, 'w') as f:
                json.dump(save_data.to_dict(), f, indent=2)

            print(f"✓ Salvataggio importato nel slot {slot}")
            return True
        except Exception as e:
            print(f"❌ Errore importazione: {e}")
            return False
