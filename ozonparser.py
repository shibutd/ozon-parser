import os
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler 
from app import create_app, db
from app.models import User, Category, Subcategory, Item
from app.parser_func import launch_parser


app = create_app(os.getenv('FLASK_CONFIG', 'dev'))
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Category=Category, Subcategory=Subcategory, Item=Item)


if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(launch_parser, 'interval', minutes=180)
    scheduler.start()
    app.run()
