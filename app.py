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

@app.route('/search', methods=['GET'])
def searchGet():
	return render_template("search.html", title="Search")

@app.route('/search', methods=['POST'])
def search():
	# Depending on which form is sent to this route (author or title), redirect to different routes
	if (request.form.get('termsTitle')):
		url = "/search/title=" + urllib.parse.quote(request.form.get('termsTitle'))
		return redirect(url, code=302)
	elif (request.form.get('termsAuthor')):
		url = "/search/author=" + urllib.parse.quote(request.form.get('termsAuthor'))
		return redirect(url, code=302)

@app.route("/search/title=<string:terms>")
def searchResultsTitle(terms):
	books = readCatalog("?search=" + urllib.parse.quote(terms))["results"]
	title = "Search results"

	bookTitles = []
	for i in books:
		if (terms.lower() in i["title"].lower()):								# Checks if search term is in each results title
			bookTitles.append(i["title"])										# Appends it to final results if so

	return render_template("searchResults.html", **locals())

@app.route("/search/author=<string:terms>")
def searchResultsAuthor(terms):
	books = readCatalog("?search=" + urllib.parse.quote(terms))["results"]
	title = "Search results"
	
	authors = []
	for i in books:
		for j in i["authors"]:
			if (terms.lower() in j["name"].lower()):						# Checks if search term is in each results author
				authors.append(j["name"])									# Appends it to final results if so

	return render_template("searchResults.html", **locals())

if __name__ == "__main__":
	app.run()
