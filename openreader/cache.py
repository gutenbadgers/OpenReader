import os
import shutil
import click
from flask import current_app
from flask.cli import with_appcontext

# Errors should be fatal, so don't catch

_path     = lambda: current_app.config["CACHE"]
_max_size = lambda: current_app.config["CACHESIZE"]
_path_to  = lambda f: os.path.join(_path(), f)
_exists   = lambda: os.path.isdir(_path())
_contents = lambda: [] if not _exists() else \
		[f for f in os.listdir(_path()) if os.path.isfile(_path_to(f))]
_size     = lambda: sum(os.path.getsize(_path_to(f)) for f in _contents())

def _clear():
	if os.path.exists(_path()):
		shutil.rmtree(_path())

def prune(extra_room=0):
	if extra_room >= _max_size():
		_clear()
		return

	while _contents() and _size() > _max_size() - extra_room:
		oldest = min(_contents(), key=lambda f: os.path.getctime(_path_to(f)))
		os.remove(_path_to(oldest))

def contains(name):
	return os.path.isfile(_path_to(name))

def get(name):
	if contains(name):
		with open(_path_to(name)) as f:
			return f.read()

def add(name, content):
	size = len(content.encode("utf-8"))

	if size > _max_size():
		return
	prune(size)

	if not os.path.exists(_path()):
		os.makedirs(_path())
	with open(_path_to(name), "w") as f:
		f.write(content)


def init_app(app):
	app.cli.add_command(_clear_cache_command)

@click.command("clear-cache")
@with_appcontext
def _clear_cache_command():
	"""Clear the existing cached files."""
	_clear()
	click.echo("Cleared the cache.")
