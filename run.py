import pickle
import uuid

import click as click

import bulbapedia_scraper_sv
import serebii_scraper_sv
from nuzlocke import NuzlockeRun
from pokemon import Pokemon


@click.group()
def cli():
    pass


@click.command()
@click.option("-f", "--file", "file", default="pokemon.data", help="The file to read the pokemon data from.")
@click.option("-s", "--seed", "seed", default=uuid.uuid4().hex, help="The seed to use to generate the run.")
@click.option("--allow-dupes", "allow_dupes", is_flag=True, default=False, help="Allow duplicate pokemon to be caught.")
@click.option("-o", "--order", "show_order", is_flag=True, default=False, help="Also print out the order of things to accomplish, along with suggested max. level restrictions.")
def generate(file: str, seed: str, allow_dupes: bool, show_order: bool):
    """
    Generates a new Nuzlocke run.
    """
    click.echo(f"Running generate_run with seed={seed}")
    NuzlockeRun(content_file=file, seed=seed, prevent_dupes=not allow_dupes, show_order=show_order).generate_run()


@click.command()
@click.option("-d", "--delete", "delete", is_flag=True, help="Delete the existing pokemon data file.")
@click.option("-f", "--file", "file", default="pokemon.data", help="The file to store the pokemon data in.")
@click.option("-s", "--source", "source", type=click.Choice(["serebii", "bulbapedia"]), default="serebii", help="The source to scrape from.")
def scrape(delete: bool, file: str, source):
    """
    Extracts data from the internet about Pokemon and stores them in a file used for Nuzlocke runs.
    """
    if source == "serebii":
        serebii_scraper_sv.scrape_mons(delete, file)
    elif source == "bulbapedia":
        bulbapedia_scraper_sv.scrape_mons(delete, file)


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
