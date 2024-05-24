import os
import pickle
import re
import time

import requests as requests
from bs4 import BeautifulSoup

from pokemon import Pokemon

POKEMON_LIST_REGEX = r"(?<=\>)\d+ \w+(?=\<\/option\>)"
SCRAPE_DELAY_IN_MS = 0

TEST_POKEMON_NAME = None


def _millis_ts() -> int:
    return int(time.time() * 1000)


def scrape_mons(delete: bool, file: str):
    if os.path.isfile(file):
        if not delete:
            print(f"File {file} already exists, please delete the file manually before scraping again.")
            return
        else:
            os.remove(file)

    start = _millis_ts()
    print(f"Finding mons for Scarlet & Violet...")
    mons = find_mons()
    print(f"{len(mons)} mons found.")

    pokemon = []
    for mon in mons:
        pokemon.append(Pokemon(mon[0], mon[1]))

    if TEST_POKEMON_NAME:
        p = [p for p in pokemon if p.get_name() == TEST_POKEMON_NAME][0]
        get_mon_data(p, True)
        print(p)
        return

    print("Getting mon data...")
    read = 0
    total_mons = len(pokemon)
    time_est_start = _millis_ts()
    last_print = 0
    for p in pokemon:
        read_time = _millis_ts()
        get_mon_data(p)
        read += 1

        # Rate-limiting in case we get contacted about overuse.
        while _millis_ts() - read_time < SCRAPE_DELAY_IN_MS:
            pass

        percent = int((read / total_mons) * 100)
        if percent > 0 and percent % 10 == 0 and percent > last_print:
            elapsed_time_seconds = (_millis_ts() - time_est_start)/1000
            estimated_total_time = elapsed_time_seconds * (100 / percent)
            print(f"\t{percent}% done. Estimated total time: {'{:.2f}'.format(estimated_total_time)}s ({'{:.2f}'.format(estimated_total_time - elapsed_time_seconds)}s remaining).")
            last_print = percent
    print(f"{len(pokemon)} mons read in in {'{:.2f}'.format(float(_millis_ts() - start) / 1000)}s.")

    backfill_regions(pokemon)
    final_adjustments(pokemon)

    save_mon_data(pokemon)
    print(f"Mon data stored successfully in {DATA_FILE}!")


def final_adjustments(pokemon: [Pokemon]):
    print("Making final adjustments to pokemon location lists...")
    # Remove Zapdos from Poco Path (a bit unfair, innit?)
    _remove_from_location(pokemon, "Zapdos", "Poco Path")

    # Final adjustment -- mark pokemon as legendary
    print("\tMarking pokemon as legendary...")
    url = "https://www.serebii.net/pokemon/legendary.shtml"
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    # Note: For simplicity, we won't filter more. Some of these will just contain junk.
    links = [a.text for a in soup.findAll('a') if a and a.text and a.get("href") and (
            "/pokemon" in a.get("href")
            or "/pokedex" in a.get("href")
    )]
    for p in pokemon:
        if p.get_name() in links:
            p.set_legendary()


def _remove_from_location(pokemon: [Pokemon], mon_name: str, location: str):
    poke = [p for p in pokemon if p.get_name() == mon_name][0]
    if location in poke._locations:
        poke._locations.remove(location)


def save_mon_data(pokemon: list[Pokemon]):
    with open(DATA_FILE, 'wb') as file:
        pickle.dump(pokemon, file, pickle.HIGHEST_PROTOCOL)


def get_mon_data(pokemon: Pokemon, test_mode: bool = False):
    url = f'https://serebii.net/pokedex-sv/{pokemon.get_name().lower()}/'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    _parse_location_data_for_mon(pokemon, soup, test_mode)


def _parse_location_data_for_mon(pokemon: Pokemon, pokemon_data: BeautifulSoup, test_mode: bool = False):
    t = pokemon_data.findAll('table')
    location_table = [l for l in t if l and l.tr and l.tr.td and l.tr.td.h2 and "Locations" in l.tr.td.h2][0]
    specific_location_candidates = location_table.findAll('td')
    for candidate in specific_location_candidates:
        possible_location_links = candidate.findAll('a')
        location_names = [pll.get_text() for pll in possible_location_links if '/pokearth/' in str(pll)]
        for location_name in location_names:
            pokemon.add_location(location_name)


def backfill_regions(pokemon: [Pokemon]):
    print("Backfilling regions to fix inconsistencies...")
    url = f'https://www.serebii.net/pokearth/'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    region_forms = [f for f in soup.findAll('form') if f.get('name')]
    regions_to_backfill = ['paldea', 'kitakami', 'terarium']
    region_forms = [f for f in region_forms if f.get('name') in regions_to_backfill]
    # These options lead nowhere
    pages_to_exclude = [
        "Pokéarth: Paldea",
        "Pokéarth: Kitakami",
        "Pokéarth: Terarium (Blueberry Academy)"
    ]
    for region in region_forms:
        print(f"\tBackfilling {region.get('name')}...")
        options = [o.get('value') for o in region.findAll('option') if not any(page_to_exclude in o.get_text() for page_to_exclude in pages_to_exclude)]
        num_options = len(options)
        backfilled = 0
        last_percent = 0
        for option in options:
            backfill_location(option, pokemon)
            backfilled += 1
            percent_done = int(backfilled / num_options * 100)
            if percent_done > last_percent and percent_done % 5 == 0:
                print(f"\t\t{percent_done}% complete...")
                last_percent = percent_done
        print(f"\tFinished backfilling {region.get('name')}.")


def backfill_location(location_path: str, pokemon: [Pokemon]):
    url = f'https://www.serebii.net{location_path}'
    data = requests.get(url).text
    soup = BeautifulSoup(data, 'html.parser')
    location_name = soup.find("h1").get_text()
    all_pokemon_numbers = [int(a.img.get("alt")) for a in soup.findAll('a') if [img for img in a.findAll('img') if "/pokedex-sv/" in img.get("src") and img.get("alt").isnumeric()]]
    for p in pokemon:
        if p.get_national_dex_number() in all_pokemon_numbers:
            was_backfilled = p.add_location(location_name)
            if was_backfilled:
                print(f"\t\t\tLocation {location_name} was added to {p.get_name()}.")


def find_mons() -> list[(int, str)]:
    url = f'https://serebii.net/pokedex-sv/'
    data = requests.get(url).text
    matches = re.finditer(POKEMON_LIST_REGEX, data, re.MULTILINE)
    pokemon_list = []
    last_number = 0
    for match in matches:
        splits = match.group().split(" ")
        nat_dex_num = int(splits[0])
        name = splits[1]
        # Workaround since the first list is the total pokemon list in national dex order. The moment we "reset" lists
        # found then we know we finished scraping that particular list.
        if nat_dex_num > last_number:
            pokemon_list.append((nat_dex_num, name))
            last_number = nat_dex_num
        else:
            break
    return pokemon_list


if __name__ == '__main__':
    scrape_mons()