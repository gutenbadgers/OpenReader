import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


# return database connection object
def get_db():
	if "db" not in g:
		g.db = sqlite3.connect(
			current_app.config["DATABASE"],
			detect_types=sqlite3.PARSE_DECLTYPES
		)
		g.db.row_factory = sqlite3.Row
	
	return g.db


# remove and clean up database connection
def _close_db(e=None):
	db = g.pop("db", None)

	if db is not None:
		db.close()


# create/reset the database
def _init_db():
	db = get_db()

	with current_app.open_resource("schema.sql") as s:
		db.executescript(s.read().decode("utf8"))


# tell Flask how to cleanup and register following cli command
def init_app(app):
	app.teardown_appcontext(_close_db)
	app.cli.add_command(_init_db_command)


# cli command to create/reset the database
@click.command("init-db")
@with_appcontext
def _init_db_command():
	"""Clear the existing data and create new tables."""
	_init_db()
	click.echo("Initialized the database.")
