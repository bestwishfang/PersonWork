import os
from app import create, models
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand


app = create()
manage = Manager(app)
migrate = Migrate(app, models)
app.secret_key = '123123'

manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manage.run()
