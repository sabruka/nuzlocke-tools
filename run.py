import uuid

import click as click

from games import violet
from nuzlocke import NuzlockeRun


@click.group()
def cli():
    pass


@click.command()
@click.option("-s", "--seed", "seed", default=uuid.uuid4().hex, help="The seed to use to generate the run.")
@click.option("--secret", "secret", default=None, help="Use this if you only want to print out a subset of routes.")
@click.option("--allow-dupes", "allow_dupes", is_flag=True, default=False, help="Allow duplicate pokemon to be caught.")
@click.option("-o", "--order", "show_order", is_flag=True, default=False, help="Also print out the order of things to accomplish, along with suggested max. level restrictions.")
def generate_run(seed: str, secret: str, allow_dupes: bool, show_order: bool):
    """
    Generates a new Nuzlocke run.
    """
    click.echo(f"Running generate_run with seed={seed}")
    game = violet
    NuzlockeRun(seed=seed, game=game, secret=secret, dupes_clause=not allow_dupes, show_order=show_order).generate_run()


cli.add_command(generate_run)

if __name__ == '__main__':
    cli()
