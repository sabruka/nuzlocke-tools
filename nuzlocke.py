import pickle
from random import Random

from pokemon import Pokemon


class NuzlockeRun:
    def __init__(self, content_file: str, seed: str, prevent_dupes: bool = True, show_order: bool = False, allow_legendaries: bool = False):
        self._content_file = content_file
        self._seed = seed
        self._prevent_dupes = prevent_dupes
        self._show_order = show_order
        self._allow_legendaries = allow_legendaries

    def generate_run(self):
        print(f"Generating run for seed {self._seed}...")
        with open(f'./{self._content_file}', 'rb') as file:
            pokemon: [Pokemon] = pickle.load(file)
            print(f"Found {len(pokemon)} possible pokemon.")

            total_location_list = [p.get_locations() for p in pokemon]
            location_list = list(set([location for location_list in total_location_list for location in location_list]))
            location_list.sort()
            self._cleanup_locations(location_list)
            print(f"Found {len(location_list)} total locations.")

            r = Random()
            r.seed(self._seed)
            print()
            print(f"""===== NUZLOCKE RULES =====

1. If a pokemon faints, it is considered dead and must be released.
2. You must give a nickname to every pokemon you catch.
3. You may only catch the first pokemon you encounter on each route matching the one selected by the generator.
    3.1 You may catch the pre-evolution of the pokemon selected by the generator for a specific route.
4. If you fail to catch the first pokemon you encounter on a route, you may not catch any more pokemon on that route.
5. You may not use any items in battle.

Your goals:

1. Complete Victory Road [ ]
2. Complete Path of Legends [ ]
3. Complete Starfall Street [ ]
4. Defeat Arven, Nemona, and Cassiopeia [ ]
5. Complete The Way Home [ ]
6. Complete the Academy Ace Tournament [ ]

The pokemon selected for you are the following:
            """)

            all_pokemon_selected = []
            selected_pokemon_by_location: dict[str, Pokemon] = {}
            # TODO: This can be optimized in the scraping step.
            for location in location_list:
                candidates = []
                for p in pokemon:
                    if p not in candidates and location in p.get_locations():
                        candidates.append(p)
                if not self._allow_legendaries:
                    candidates = [c for c in candidates if not c.is_legendary()]

                if self._prevent_dupes:
                    candidates = [c for c in candidates if c not in all_pokemon_selected]

                selected_pokemon = r.choice(candidates) if candidates else None
                selected_pokemon_by_location[location] = selected_pokemon
                all_pokemon_selected.append(selected_pokemon)

            for location, pokemon in selected_pokemon_by_location.items():
                print(f"\t{location}: {pokemon.get_name() if pokemon else 'None!'} [ ]")

            if self._show_order:
                print()
                print("Recommended level caps are the following:")
                level_caps = self._get_level_caps()
                for key in level_caps:
                    print(f"\t{key}: {level_caps[key]}")

            print()
            print("Good luck!")

    def _get_level_caps(self) -> dict:
        return {
            "Cortando Gym (Bug)": 16,
            "Rock Path of Legends": 17,
            "Artazin Gym (Grass)": 18,
            "Flying Path of Titans": 20,
            "Dark Team Star Base": 22,
            "Levincia Gym (Electric)": 26,
            "Fire Team Star Base": 29,
            "Steel Path of Titans": 30,
            "Cascarrafa Gym (Water)": 32,
            "Poison Team Star Base": 34,
            "Medali Gym (Normal)": 39,
            "Montenevera Gym (Ghost)": 45,
            "Ground Path of Titans": 47,
            "Alfornada Gym (Psychic)": 48,
            "Glaseado Gym (Ice)": 51,
            "Fairy Team Star Base": 54,
            "Fighting Team Star Base": 60,
            "Pre-boss Team Star": 65,
            "Boss Team Star": 67,
            "Path of Titans Final Fight": 67,
            "Elite Four": 71,
        }

    def _cleanup_locations(self, location_list):
        # Some locations are bugged or are scrapped incorrectly.
        if "Alfornado Cavern" in location_list:
            location_list.remove("Alfornado Cavern")  # Groudon is incorrectly set in this non-existent cavern.
        if "PokÃ©mon League" in location_list:
            location_list.remove("PokÃ©mon League")  # Incorrect spelling of Pokemon League.
        if "Victory Road" in location_list:
            location_list.remove(" Savanna BiomeFixed: Savanna Biome") # ???
