import sys
import csv
from collections import Counter
import click
from flask import Blueprint
from . import db
from app.models import Category, Subcategory, Item, Price


cmd_bp = Blueprint('cmd', __name__)


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True


@cmd_bp.cli.command()
@click.argument('path')
def import_data(path):
    """Import data from .csv file."""
    print('Importing products...', file=sys.stdout)

    try:
        csvfile = open(path, 'r')
    except FileNotFoundError:
        print('File not found: {}'.format(path), file=sys.stdout)
        sys.exit()

    c = Counter()
    reader = csv.DictReader(csvfile, delimiter=';')

    for row in reader:
        # proceeding categories
        category, created = get_or_create(
            db.session,
            Category,
            name=row['category']
        )
        c['categories'] += 1
        if created:
            c['categories_created'] += 1

        # proceeding subcategories
        subcategory, created = get_or_create(
            db.session,
            Subcategory,
            name=row['subcategory'],
            category_id=category.id
        )
        c['subcategories'] += 1
        if created:
            c['subcategories_created'] += 1

        # proceeding items
        item, created = get_or_create(
            db.session,
            Item,
            name=row['item'],
            external_id=row['external_id'],
            subcategory_id=subcategory.id,
        )
        c['items'] += 1
        if created:
            c['items_created'] += 1

        # proceeding prices
        for price in row["prices"].split("|"):
            db.session.add(
                Price(value=price, item_id=item.id))
            db.session.commit()

    print(
        "Categories processed={0} (created={1})".format(
            c["categories"], c["categories_created"]),
        file=sys.stdout
    )
    print(
        "Subcategories processed={0} (created={1})".format(
            c["subcategories"], c["subcategories_created"]),
        file=sys.stdout
    )
    print(
        "Items processed={0} (created={1})".format(
            c["items"], c["items_created"]),
        file=sys.stdout
    )

    csvfile.close()
