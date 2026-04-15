"""
Configurazione delle wave (ondate) di nemici per ogni livello.

Formato:
level_N_waves = [
    [  # Wave 1
        {"type": "walker", "x": 100, "y": 200},
        {"type": "ranged", "x": 300, "y": 200},
    ],
    [  # Wave 2
        {"type": "jumper", "x": 150, "y": 250},
        ...
    ]
]
"""

# ============================================================================
# LIVELLO 1 - Tutorial (Facile)
# ============================================================================
level_1_waves = [
    # Wave 1: Introduzione ai walker
    [
        {"type": "walker", "x": 200, "y": 150, "health": 2},
    ],
    # Wave 2: Due walker
    [
        {"type": "walker", "x": 150, "y": 200},
        {"type": "walker", "x": 300, "y": 200},
    ],
]

# ============================================================================
# LIVELLO 2 - Intermediate (Medio)
# ============================================================================
level_2_waves = [
    # Wave 1: Mix di nemici
    [
        {"type": "walker", "x": 100, "y": 150},
        {"type": "ranged", "x": 350, "y": 150},
    ],
    # Wave 2: Jumper challenge
    [
        {"type": "jumper", "x": 200, "y": 200},
        {"type": "jumper", "x": 400, "y": 200},
    ],
    # Wave 3: Difficile - mix completo
    [
        {"type": "walker", "x": 80, "y": 250},
        {"type": "ranged", "x": 200, "y": 250},
        {"type": "jumper", "x": 350, "y": 250},
    ],
]

# ============================================================================
# LIVELLO 3+ - Template
# ============================================================================
def get_waves_for_level(floor_number):
    """
    Ritorna le wave per un livello.

    Args:
        floor_number: Numero del piano (1-18)

    Returns:
        Lista di wave
    """
    if floor_number == 1:
        return level_1_waves
    elif floor_number == 2:
        return level_2_waves
    else:
        # Genera wave scalate dalla difficoltà
        return generate_scaled_waves(floor_number)


def generate_scaled_waves(floor_number):
    """
    Genera wave scalate dalla difficoltà del piano.

    Args:
        floor_number: Numero del piano (3-18)

    Returns:
        Lista di wave generate
    """
    # Scala di difficoltà
    difficulty = min(1.0 + (floor_number - 3) * 0.15, 3.0)  # Max 3.0
    num_enemies_per_wave = max(2, int(2 + (floor_number - 3) * 0.5))

    waves = []

    # Crea 2-4 wave in base al piano
    num_waves = min(2 + (floor_number - 3) // 5, 4)

    for wave_idx in range(num_waves):
        wave = []

        # Randomizza tipi di nemico in base al piano
        for enemy_idx in range(num_enemies_per_wave):
            x = 100 + (enemy_idx * 150)
            y = 150 + (wave_idx * 50)

            # Bilanciamento tipi per difficoltà
            if floor_number < 5:
                # Principalmente walker
                enemy_type = "walker"
            elif floor_number < 10:
                # Mix di walker e ranged
                enemy_type = "walker" if enemy_idx % 2 == 0 else "ranged"
            elif floor_number < 15:
                # Mix completo
                types = ["walker", "ranged", "jumper"]
                enemy_type = types[enemy_idx % 3]
            else:
                # Difficile - mix con weight verso ranged e jumper
                types = ["ranged", "jumper", "ranged"]
                enemy_type = types[enemy_idx % 3]

            # Scala salute
            base_health = {
                "walker": 3,
                "ranged": 2,
                "jumper": 4,
            }
            health = max(1, int(base_health[enemy_type] * difficulty))

            wave.append({
                "type": enemy_type,
                "x": x,
                "y": y,
                "health": health,
            })

        waves.append(wave)

    return waves


# ============================================================================
# BOSS FINALE - Piano 18
# ============================================================================
boss_wave = [
    # Mini-boss: Ranged forte
    {
        "type": "ranged",
        "x": 640,
        "y": 300,
        "health": 8,
        "aggro_range": 500,
    }
]

def get_boss_wave():
    """Ritorna la wave del boss finale."""
    return [boss_wave]
