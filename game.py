from pokemon import Pokemon


class Game:
    def __init__(self, name: str, route_pokemon_map: dict[str, list[Pokemon]]):
        self._name = name
        self._route_pokemon_map = route_pokemon_map

    def get_name(self) -> str:
        return self._name

    def get_pokemon_for_route(self, route: str) -> list[Pokemon]:
        return self._route_pokemon_map[route]

    def get_routes(self) -> list[str]:
        return list(self._route_pokemon_map.keys())
