from flask import Flask, flash, redirect, render_template, request, session, abort
from collections import namedtuple
import urllib.request, json

app = Flask(__name__)

# https://github.com/garethbjohnson/gutendex#api
catalog = "http://gutendex.com/books"

def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
def json2obj(data): return json.loads(data, object_hook=_json_object_hook)

def readCatalog(route):
	url = catalog + route
	with urllib.request.urlopen(url) as req:
		return json.loads(req.read().decode())

@app.route("/")
@app.route("/index")
def hello():
	return render_template("index.html")

@app.route("/test")
def test():
	return "success"

@app.route("/login")
def login():
	return render_template("wip.html")

@app.route("/bookshelf")
def bookshelf():
	return render_template("wip.html")

@app.route("/book/<int:id>")
def book(id):
	book = readCatalog("/{}".format(id))
	title = book["title"]
	return render_template("bookInfo.html", **locals())

@app.route("/search/<string:terms>")
def search(terms):
	books = readCatalog("?search=" + urllib.parse.quote(terms))["results"]
	title = "Search results"
	return render_template("searchResults.html", **locals())

if __name__ == "__main__":
	app.run()
