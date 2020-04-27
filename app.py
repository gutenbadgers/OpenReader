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

@app.route('/search', methods=['GET'])
def searchGet():
	return render_template("search.html", title="Search")

@app.route('/search', methods=['POST'])
def search():
	# Depending on which form is sent to this route, redirect to different routes
	print(request.form.get("terms"))
	if (request.form.get('searchType') == "title"):
		url = "/search/title=" + urllib.parse.quote(request.form.get('terms'))
		return redirect(url, code=302)
	elif (request.form.get('searchType') == "author"):
		url = "/search/author=" + urllib.parse.quote(request.form.get('terms'))
		return redirect(url, code=302)
	elif (request.form.get('searchType') == "category"):
		url = "/search/category=" + urllib.parse.quote(request.form.get('terms'))
		return redirect(url, code=302)
	# no else. It won'd do anything unless they pick one.

@app.route("/search/title=<string:terms>")
def searchResultsTitle(terms):
	results = readCatalog("?search=" + urllib.parse.quote(terms))["results"]
	title = "Search results"
	searchType = "title"
	
	# refine results to only include title matches
	books = [x for x in results if terms.lower() in x["title"].lower()] 			

	return render_template("searchResults.html", **locals())

@app.route("/search/author=<string:terms>")
def searchResultsAuthor(terms):
	results = readCatalog("?search=" + urllib.parse.quote(terms))["results"]
	title = "Search results"
	searchType = "author"
	books = []

	# refine results to only include author matches
	for book in results:
		if (book["authors"]):
			for author in book["authors"]:
				if (terms.lower() in author["name"].lower()):
					books.append(book)					

	return render_template("searchResults.html", **locals())

@app.route("/search/category=<string:terms>")
def searchResultsCategory(terms):
	books = readCatalog("?topic=" + urllib.parse.quote(terms))["results"]
	title = "Search results"
	searchType = "category"

	return render_template("searchResults.html", **locals())

if __name__ == "__main__":
	app.run()
