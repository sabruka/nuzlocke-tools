class Pokemon:
    def __init__(self, national_dex_number: int, name: str, legendary: bool = False):
        self._national_dex_number = national_dex_number
        self._name = name
        self._locations = []
        self._is_legendary = False

    def __str__(self):
        return f"""#{self._national_dex_number}: {self._name}{' *LEGENDARY*' if self._is_legendary else ''}"""

    def get_national_dex_number(self) -> int:
        return self._national_dex_number

    def get_name(self) -> str:
        return self._name

    def get_family(self) -> str:
        return self._family

    def add_location(self, route: str) -> bool:
        if route not in self._locations:
            self._locations.append(route)
            return True
        return False

    def remove_location(self, route: str):
        if route in self._locations:
            self._locations.remove(route)

    def add_locations(self, routes: [str]):
        for route in routes:
            self.add_location(route)

    def is_in_location(self, route: str) -> bool:
        return route in self._locations

    def get_locations(self) -> [str]:
        return self._locations

    def add_family(self, family: str):
        self._family = family

    def set_legendary(self):
        self._is_legendary = True

    def is_legendary(self) -> bool:
        return self._is_legendary