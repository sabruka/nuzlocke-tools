import pickle
import uuid

import click as click

from nuzlocke import NuzlockeRun
from pokemon import Pokemon
from scraper_sv import scrape_mons


@click.group()
def cli():
    pass


@click.command()
@click.option("-s", "--seed", "seed", default=uuid.uuid4().hex, help="The seed to use to generate the run.")
@click.option("--allow-dupes", "allow_dupes", is_flag=True, default=False, help="Allow duplicate pokemon to be caught.")
@click.option("-o", "--order", "show_order", is_flag=True, default=False, help="Also print out the order of things to accomplish, along with suggested max. level restrictions.")
def generate(seed: str, allow_dupes: bool, show_order: bool):
    """
    Generates a new Nuzlocke run.
    """
    click.echo(f"Running generate_run with seed={seed}")
    NuzlockeRun(seed=seed, prevent_dupes=not allow_dupes, show_order=show_order).generate_run()


@click.command()
def scrape():
    """
    Extracts data from the internet about Pokemon and stores them in a file used for Nuzlocke runs.
    """
    scrape_mons()


@click.command()
@click.option("-n", "--name", "name", help="The name of the pokemon whose data we want to find..")
def get_mon_data(name: str):
    """
    Reads from the pokemon data file and prints out the data for that pokemon.
    """
    with open('./pokemon.data', 'rb') as file:
        pokemon: [Pokemon] = pickle.load(file)
        for p in pokemon:
            if p.get_name().lower() == name.lower():
                print(f"#{p.get_national_dex_number()} {p.get_name()}")
                print(f"{p.get_locations()}")
                return
    print(f"Could not find {name}: {[p.get_name() for p in pokemon]}")


cli.add_command(generate)
cli.add_command(scrape)
cli.add_command(get_mon_data)

if __name__ == '__main__':
    cli()
