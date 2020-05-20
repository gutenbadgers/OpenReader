import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext

def init_app(app):
	app.teardown_appcontext(_close_db)
	app.cli.add_command(_init_db_command)

def get_db():
	if "db" not in g:
		g.db = sqlite3.connect(
			current_app.config["DATABASE"],
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row
	
	return g.db

def _close_db(e=None):
	db = g.pop("db", None)

	if db is not None:
		db.close()

def _init_db():
	db = get_db()

	with current_app.open_resource("schema.sql") as s:
		db.executescript(s.read().decode("utf8"))
	
@click.command("init-db")
@with_appcontext
def _init_db_command():
	"""Clear the existing data and create new tables."""
	_init_db()
	click.echo("Initialized the database.")
