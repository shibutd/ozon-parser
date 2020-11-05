import sys

import click

from app import db
from .utils import ParserLaucher
from . import cmd_bp


@cmd_bp.cli.command()
@click.option('-p', '--parse',
              type=click.Choice(
                  ['categories', 'subcategories', 'items'],
                  case_sensitive=False
              ),
              help='Parser type.',
              required=True)
@click.option('-j', '--json',
              is_flag=True,
              help='Save parsing result to .json file.')
@click.option('-s', '--save',
              is_flag=True,
              help='Save parsing result to database.')
def launch_parser(parse, json, save):
    """Parse data from 'ozon.ru' and save result to db and .json file.
    """
    launcher = ParserLaucher(
        './parse_results',
        save_to_json=json,
        save_to_db=save,
        session=db.session
    )

    launcher_functions = {
        'categories': launcher.fetch_parent_categories,
        'subcategories': launcher.fetch_subcategories,
        'items': launcher.fetch_items
    }
    try:
        launcher_functions[parse]()
    except Exception as e:
        db.session.rollback()
        click.echo('Error occured while adding data: {}'.format(e))
        sys.exit()

    click.echo('Parsing finished successfully.')
