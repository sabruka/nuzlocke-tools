from typing import Optional

from pokemon import Pokemon


class Game:
    def __init__(self, name: str, route_pokemon_map: dict[str, list[Pokemon]], path_and_max_levels: tuple[str, int] = None):
        self._name = name
        self._route_pokemon_map = route_pokemon_map
        self._path_and_max_levels = path_and_max_levels

    def get_name(self) -> str:
        return self._name

    def get_path_and_max_levels(self) -> tuple[str, int]:
        return self._path_and_max_levels

    def get_pokemon_for_route(self, route: str) -> list[Pokemon]:
        return self._route_pokemon_map[route]

    def get_routes(self) -> list[str]:
        return list(self._route_pokemon_map.keys())
