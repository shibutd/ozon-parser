import sys
import re
from pathlib import Path

import click

from app import db
from app.models import Category
from .utils import DataImporter, DatabaseSaver
from . import cmd_bp


@cmd_bp.cli.command()
@click.argument('path')
def import_data(path):
    """Import data from .json file saved by parser.
    """
    global_path = Path(path)
    if not global_path.exists() or not global_path.is_dir():
        click.echo('Directory does not exists: {}'.format(path))
        sys.exit()

    click.echo('Importing data...')

    data_importer = DataImporter(global_path)
    database_saver = DatabaseSaver(session=db.session)

    patterns = {
        'categories': 'parent*',
        'subcategories': 'sub*',
        'items': 'items*',
    }
    # Import parent categories
    click.echo('Importing parent categories...')

    for categories in data_importer.get_data_from_multiple_files(
            patterns['categories']):
        try:
            database_saver.save_categories_to_database(categories)
        except Exception as e:
            db.session.rollback()
            click.echo(
                'Error occured while importing categories: {}'
                .format(e)
            )
            sys.exit()

    # Import subcategories
    click.echo('Importing subcategories...')

    for subcategories in data_importer.get_data_from_multiple_files(
            patterns['subcategories']):
        parent_categories = Category.query.filter(
            Category.is_parent()).all()
        try:
            database_saver.save_subcategories_to_database(
                subcategories,
                parent_categories
            )
        except Exception as e:
            db.session.rollback()
            click.echo(
                'Error occured while importing subcategories: {}'
                .format(e)
            )
            sys.exit()

    # Import items
    click.echo('Importing items...')

    for file_name in data_importer.get_files_names(patterns['items']):
        # Get category's slug name from file's name
        category_slug = re.search(
            r'items_([a-zA-Z_]+)_',
            file_name
        ).group(1)
        # Find category with found slug
        items_category = Category.query.filter_by(
            slug=category_slug).first()

        if items_category:
            click.echo('Importing items category: %s' % items_category.name)

            items = data_importer.get_data_from_file(file_name)
            try:
                database_saver.save_items_to_database(
                    items,
                    items_category
                )
            except Exception as e:
                db.session.rollback()
                click.echo(
                    'Error occured while importing items "{0}": {1}'
                    .format(items_category, e)
                )
                sys.exit()

    click.echo('Data import finished.')
