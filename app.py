from flask import Flask, flash, redirect, render_template, request, session, abort
import urllib.request, json 

app = Flask(__name__)

# https://github.com/garethbjohnson/gutendex#api
catalog = "http://gutendex.com/books"

@app.route("/")
def hello():
	return render_template("hello.html", title = "OpenReader Test", name = "world")

@app.route("/search/<string:terms>")
def search(terms):
	url = catalog + "?search={}".format(urllib.parse.quote(terms))
	with urllib.request.urlopen(url) as req:
		return json.loads(req.read().decode())

if __name__ == "__main__":
	app.run()
