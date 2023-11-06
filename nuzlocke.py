from random import Random

from game import Game


class NuzlockeRun:
    def __init__(self, seed: str, game: Game, dupes_clause: bool = True, secret: str = None, show_order: bool = False):
        self._seed = seed
        self._game = game
        self._dupes_clause = dupes_clause
        self._secret = secret
        self._show_order = show_order

    def generate_run(self):
        """
        Generates a list of routes along with the pokemon caught on each route, and prints it out.
        """
        r = Random()
        r.seed(self._seed)

        print(f"Generating run for game {self._game.get_name()} and seed {self._seed}...")
        print()
        print(f"""
===== NUZLOCKE RULES =====

1. If a pokemon faints, it is considered dead and must be released.
2. You must give a nickname to every pokemon you catch.
3. You may only catch the first pokemon you encounter on each route matching the one selected by the generator.
    3.1 You may catch the pre-evolution of the pokemon selected by the generator for a specific route.
4. If you fail to catch the first pokemon you encounter on a route, you may not catch any more pokemon on that route.
5. If you encounter a pokemon you have already caught, {"you may ignore it and try to catch the next pokemon you encounter" if self._dupes_clause else "you must catch it"}.
6. You may not use any items in battle.

Your goals:

1. Complete Victory Road [ ]
2. Complete Path of Legends [ ]
3. Complete Starfall Street [ ]
4. Defeat Arven, Nemona, and Cassiopeia [ ]
5. Complete The Way Home [ ]
6. Complete the Academy Ace Tournament [ ]

The pokemon selected for you are the following:
        """)

        selected_pokemon_by_route = {}
        for route in self._game.get_routes():
            candidates = sorted(list(set([p for p in self._game.get_pokemon_for_route(route)])), key=lambda p: p.get_name())
            if self._dupes_clause:
                families_selected = [p.get_family() for p in selected_pokemon_by_route.values()]
                candidates = [c for c in candidates if c.get_family() not in families_selected]
            if not candidates:
                selected_pokemon_by_route[route] = None
            else:
                selected_pokemon_by_route[route] = r.choice(candidates)

        for route, pokemon in selected_pokemon_by_route.items():
            if not self._secret or self._secret.lower() in route.lower():
                print(f"    {route}: {str(pokemon).title()} [ ]" if pokemon else f"{route}: None!")

        if self._show_order:
            print()
            print("Here is a suggestion for route order, along with maximum level restrictions:")
            path_and_max_levels = self._game.get_path_and_max_levels()
            for path, max_level in path_and_max_levels:
                print(f"    {path} (max level {max_level}) [ ]")

        print()
        print("Good luck!")
