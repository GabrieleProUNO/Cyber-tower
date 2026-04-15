"""
Inventory System: Gestisce l'inventario del giocatore.

Responsabilità:
- Aggiungere/rimuovere item
- Stackare item identici
- Combinazione item (crafting)
- Persistenza stato
"""

from items import Item, ItemType, RECIPES
from config import *


class Inventory:
    """
    Rappresenta l'inventario del giocatore.

    Metodologia:
    - Slot basato: MAX_INVENTORY_SLOTS slot disponibili
    - Stack automatico: Item identici si stackano automaticamente
    - Crafting: Due item possono combinarsi se ricetta esiste
    """

    def __init__(self, max_slots=MAX_INVENTORY_SLOTS):
        """
        Inizializza l'inventario.

        Args:
            max_slots: Numero massimo di slot
        """
        self.max_slots = max_slots
        self.slots = [None] * max_slots  # Lista di Item o None
        self.selected_slot = 0  # Slot selezionato

    def add_item(self, item):
        """
        Aggiunge un item all'inventario.

        Tenta di stackare con item identici prima di usare nuovo slot.

        Args:
            item: Item da aggiungere

        Returns:
            True se aggiunto, False se pieno
        """
        if not isinstance(item, Item):
            return False

        # ====== TENTA DI STACKARE ======
        if item.is_stackable():
            for slot in self.slots:
                if slot is not None and slot.item_type == item.item_type:
                    slot.quantity += item.quantity
                    print(f"📦 {item.get_name()} +{item.quantity} (stack)")
                    return True

        # ====== USA NUOVO SLOT ======
        for i, slot in enumerate(self.slots):
            if slot is None:
                self.slots[i] = item
                print(f"📦 {item.get_name()} aggiunto")
                return True

        print(f"❌ Inventario pieno! Non posso aggiungere {item.get_name()}")
        return False

    def remove_item_at_slot(self, slot_idx):
        """
        Rimuove un item da uno slot specifico.

        Args:
            slot_idx: Indice dello slot

        Returns:
            Item rimosso, o None
        """
        if slot_idx < 0 or slot_idx >= len(self.slots):
            return None

        item = self.slots[slot_idx]
        self.slots[slot_idx] = None
        return item

    def get_item_at_slot(self, slot_idx):
        """
        Ottiene l'item a uno slot.

        Args:
            slot_idx: Indice dello slot

        Returns:
            Item nello slot, o None
        """
        if slot_idx < 0 or slot_idx >= len(self.slots):
            return None
        return self.slots[slot_idx]

    def count_item_type(self, item_type):
        """
        Conta gli item di un tipo specifico.

        Args:
            item_type: Tipo di item

        Returns:
            Quantità totale
        """
        total = 0
        for slot in self.slots:
            if slot is not None and slot.item_type == item_type:
                total += slot.quantity if slot.is_stackable() else 1
        return total

    def consume_items(self, item_type, quantity):
        """
        Consuma (rimuove) una quantità di item.

        Utile per consumare risorse in crafting o attivare upgrade.

        Args:
            item_type: Tipo di item
            quantity: Quantità da consumare

        Returns:
            True se consumato con successo, False se non abbastanza
        """
        needed = quantity

        # Rimuovi dai slot in ordine
        for i, slot in enumerate(self.slots):
            if slot is None or slot.item_type != item_type:
                continue

            if slot.is_stackable():
                consumed = min(needed, slot.quantity)
                slot.quantity -= consumed
                needed -= consumed

                if slot.quantity <= 0:
                    self.slots[i] = None
            else:
                self.slots[i] = None
                needed -= 1

            if needed <= 0:
                print(f"✓ Consumato {quantity}x {Item(item_type).get_name()}")
                return True

        print(f"❌ Non abbastanza {Item(item_type).get_name()} ({self.count_item_type(item_type)}/{quantity})")
        return False

    def try_combine(self, slot1_idx, slot2_idx):
        """
        Tenta di combinare due item da due slot diversi.

        Args:
            slot1_idx: Indice primo slot
            slot2_idx: Indice secondo slot

        Returns:
            True se combinazione riuscita, False altrimenti
        """
        item1 = self.get_item_at_slot(slot1_idx)
        item2 = self.get_item_at_slot(slot2_idx)

        if item1 is None or item2 is None:
            return False

        # Verifica se combinabili
        result_type = item1.can_combine_with(item2)
        if result_type is None:
            print(f"❌ {item1.get_name()} non può combinarsi con {item2.get_name()}")
            return False

        # ====== COMBINA ======
        self.remove_item_at_slot(slot1_idx)
        self.remove_item_at_slot(slot2_idx)

        result_item = Item(result_type, 1)
        self.add_item(result_item)

        print(f"✨ {item1.get_name()} + {item2.get_name()} = {result_item.get_name()}!")
        return True

    def get_slots(self):
        """Ritorna la lista di slot."""
        return self.slots

    def get_used_slots(self):
        """Ritorna il numero di slot usati."""
        return sum(1 for slot in self.slots if slot is not None)

    def is_full(self):
        """Verifica se inventario pieno."""
        return self.get_used_slots() >= self.max_slots

    def get_value(self):
        """
        Calcola il valore totale dell'inventario in monete.

        Returns:
            Valore totale
        """
        total = 0
        for slot in self.slots:
            if slot is not None:
                total += slot.get_value()
        return total

    def clear(self):
        """Svuota l'inventario."""
        self.slots = [None] * self.max_slots
        self.selected_slot = 0

    def to_dict(self):
        """Serializza l'inventario (per salvataggio)."""
        data = []
        for slot in self.slots:
            if slot is None:
                data.append(None)
            else:
                data.append({
                    "type": slot.item_type,
                    "quantity": slot.quantity,
                })
        return data

    @staticmethod
    def from_dict(data):
        """Deserializza l'inventario."""
        inv = Inventory()
        for i, item_data in enumerate(data):
            if item_data is not None:
                item = Item(item_data["type"], item_data["quantity"])
                inv.slots[i] = item
        return inv

    def __repr__(self):
        """Debug string."""
        items = []
        for slot in self.slots:
            if slot is not None:
                items.append(str(slot))
        return f"Inventory({', '.join(items)})"
