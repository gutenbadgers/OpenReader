# Application factory and Python's package marker
import os
from flask import Flask

def create_app():
	# create and configure the app
	app = Flask(__name__, instance_relative_config=True)
	
	app.config.from_mapping(
		SECRET_KEY="dev",
		DATABASE=os.path.join(app.instance_path, "openreader.sqlite")
	)

	app.config.from_pyfile("config.py", silent=True)

	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	from . import db
	db.init_app(app)

	from . import auth
	app.register_blueprint(auth.bp)

	from . import books
	app.register_blueprint(books.bp)
	app.add_url_rule("/", endpoint="index")

	return app
