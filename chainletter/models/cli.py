import click
from flask.cli import with_appcontext
from flask.cli import AppGroup

from . import db
from .hashchain import HashChain

admin_cli = AppGroup('admin', help="admin commands")

@admin_cli.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    db.create_all()

    root = HashChain.make_root()
    db.session.add(root)
    db.session.commit()

    click.echo('Initialized the database.')


def init_app(app):
    """Register the command with the app"""
    app.cli.add_command(admin_cli)