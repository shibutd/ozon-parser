import os
import click
from flask_migrate import Migrate
from app import create_app, db
from app.models import Category, Subcategory, Item, Price


app = create_app(os.getenv('FLASK_CONFIG', 'dev'))
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db,
                Category=Category,
                Subcategory=Subcategory,
                Item=Item,
                Price=Price)


@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='Run tests under code coverage.')
def test(coverage):
    """Run the unit tests."""
    if coverage:
        import coverage
        COV = coverage.coverage(branch=True, include='app/*')
        COV.start()
    else:
        COV = None

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=1).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()
