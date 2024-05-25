import os
import pickle
import time

import requests as requests
from bs4 import BeautifulSoup

from pokemon import Pokemon


def _millis_ts() -> int:
    return int(time.time() * 1000)


def scrape_mons(delete: bool, file: str):
    if os.path.isfile(file):
        if not delete:
            print(f"File {file} already exists, please delete the file manually before scraping again.")
            return
        else:
            print(f"Deleting file {file} before scraping...")
            os.remove(file)

    start = _millis_ts()
    print(f"Finding locations for Scarlet & Violet...")
    locations = find_location_links()
    print(f"{len(locations)} locations found.")

    print(f"Getting Pokémon data per location...")
    pokemon_per_location = find_pokemon_per_location(locations)
    print(f"{len(pokemon_per_location)} locations with pokemon.")

    # pokemon_per_location is a dict keyed by locations and whose value is a list of pokemon. Instead I want a dict
    # keyed by the pokemon and a list of possible locations for each pokemon.
    locations_per_pokemon = {}
    for location, mons in pokemon_per_location.items():
        for mon in mons:
            if mon not in locations_per_pokemon:
                locations_per_pokemon[mon] = []
            locations_per_pokemon[mon].append(location)
    pokemon = []
    for mon, locations in locations_per_pokemon.items():
        p = Pokemon(0, mon)
        p.add_locations(locations)
        pokemon.append(p)

    print(f"{len(pokemon)} Pokémon found.")
    # TODO: Set national dex number.

    final_adjustments(pokemon)

    save_mon_data(pokemon, file)
    print(f"Mon data stored successfully in {file} in {'{:.2f}'.format(float(_millis_ts() - start) / 1000)}s.")


def find_location_links() -> list[str]:
    url = f'https://bulbapedia.bulbagarden.net/wiki/Category:Scarlet_and_Violet_locations'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    location_links = [a.get("href") for a in soup.findAll('a') if (
            a
            and a.get("href")
            and a.get("href").startswith("/wiki/")
            and ":" not in a.get("href")
            and "_Squad%27s_Base" not in a.get("href")
    )]

    print("\tRemoving invalid location links...")
    if "/wiki/Pok%C3%A9mon_Scarlet_and_Violet" in location_links:
        location_links.remove("/wiki/Pok%C3%A9mon_Scarlet_and_Violet")
    if "/wiki/Paldea" in location_links:
        location_links.remove("/wiki/Paldea")
    if "/wiki/Unova" in location_links:
        location_links.remove("/wiki/Unova")
    if "/wiki/Main_Page" in location_links:
        location_links.remove("/wiki/Main_Page")
    if "/wiki/Pok%C3%A9_Mart" in location_links:
        location_links.remove("/wiki/Pok%C3%A9_Mart")
    if "/wiki/Pok%C3%A9_Center" in location_links:
        location_links.remove("/wiki/Pok%C3%A9_Center")

    return location_links


def find_pokemon_per_location(locations) -> {str, list[str]}:
    pokemon_per_location = {}

    for location_link in locations:
        full_link = f"https://bulbapedia.bulbagarden.net{location_link}"
        data = requests.get(full_link).text
        soup = BeautifulSoup(data, 'html.parser')

        title = soup.find('span', {'class': 'mw-page-title-main'}).text

        pokemon_header = [h for h in soup.findAll("h2") for s in h.findAll("span") if h.span and s.text == "Pokémon"]
        if not pokemon_header:
            continue

        header_element = pokemon_header[0]
        pokemon_section = header_element.find_next_sibling()

        pokemon_in_location = []
        # Loop until next h2 header.
        while pokemon_section.name != "h2":
            if pokemon_section and pokemon_section.name == "table":
                pokemon_in_table = list(set([a.text for a in pokemon_section.findAll('a') if (
                        a
                        and a.text
                        and a.get("href")
                        and "_(Pok%C3%A9mon)" in a.get("href")
                )]))

            if len(pokemon_in_table) > 0:
                pokemon_in_location.extend(pokemon_in_table)
                pokemon_in_location = list(set(pokemon_in_location))

            pokemon_section = pokemon_section.find_next_sibling()

        pokemon_per_location[title] = pokemon_in_location
        print(f"\tFound {len(pokemon_in_location)} Pokémon for location {title}.")

    return pokemon_per_location


def final_adjustments(pokemon: [Pokemon]):
    print("Making final adjustments to pokemon location lists...")
    print("\tRemoving certain pokemon from certain locations...")
    # Remove Zapdos from Poco Path (a bit unfair, innit?)
    _remove_from_location(pokemon, "Zapdos", "Poco Path")
    _remove_from_location(pokemon, "Squawkabilly", "Cabo Poco")

    print("\tRemoving unfair or unobtainable Pokémon...")
    _remove_pokemon(pokemon, "Ash-Greninja")
    _remove_pokemon(pokemon, "Bloodmoon Beast")
    _remove_pokemon(pokemon, "the ogre")
    _remove_pokemon(pokemon, "Loyal Three's master")
    for poke in pokemon:
        if "Starmobile" in poke.get_name():
            _remove_pokemon(pokemon, poke.get_name())

    # TODO Final adjustment -- mark pokemon as legendary


def _remove_pokemon(pokemon: [Pokemon], to_remove: str):
    for p in pokemon:
        if p.get_name() == to_remove:
            print(f"\t\tRemoving {to_remove} from lists.")
            pokemon.remove(p)


def _remove_from_location(pokemon: [Pokemon], mon_name: str, location: str):
    print(f"\t\tRemoving {mon_name} from {location}.")
    poke_matches = [p for p in pokemon if p.get_name() == mon_name]
    for poke in poke_matches:
        if poke.is_in_location(location):
            poke.remove_location(location)


def save_mon_data(pokemon: list[Pokemon], file: str):
    with open(file, 'wb') as file:
        pickle.dump(pokemon, file, pickle.HIGHEST_PROTOCOL)