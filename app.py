from flask import Flask, flash, redirect, render_template, request, session, abort
import urllib.request, json
#from collections import namedtuple

app = Flask(__name__)

# https://github.com/garethbjohnson/gutendex#api
catalog = "http://gutendex.com/books"


# unused utility function to turn API result into an object
#def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())
#def json2obj(data): return json.loads(data, object_hook=_json_object_hook)


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
	abort(501) # server error: unimplemented


@app.route("/bookshelf")
def bookshelf():
	abort(501) # server error: unimplemented


@app.route("/book/<int:id>")
def book(id):
	book = readCatalog("/{}".format(id))
	title = book["title"]
	bookURL = "https://www.gutenberg.org/files/{0}/{0}-h/{0}-h.htm".format(id)
	return render_template("bookInfo.html", **locals())


@app.route("/book/<int:id>/read")
def readBook(id):
	bookURL = "https://www.gutenberg.org/files/{0}/{0}-h/{0}-h.htm".format(id)
	website = urllib.request.urlopen(bookURL)
	return website.read()


@app.route('/search', methods=['GET'])
def searchGET():
	return render_template("search.html", title="Search")


@app.route('/search', methods=['POST'])
def searchPOST():
	url = ""
	if (request.form.get('searchType') == "title"):
		url = "/search/title=" + urllib.parse.quote(request.form.get('terms'))
	elif (request.form.get('searchType') == "author"):
		url = "/search/author=" + urllib.parse.quote(request.form.get('terms'))
	elif (request.form.get('searchType') == "category"):
		url = "/search/category=" + urllib.parse.quote(request.form.get('terms'))

	if url:
		return redirect(url, code=303)
	else:
		abort(400) # client error: invalid form


@app.route("/search/title=<string:terms>")
def searchTitle(terms):
	results = readCatalog("?search=" + urllib.parse.quote(terms))["results"]
	title = "Search results"
	searchType = "title"

	# refine results to only include title matches
	books = [x for x in results if terms.lower() in x["title"].lower()]

	return render_template("search.html", **locals())


@app.route("/search/author=<string:terms>")
def searchAuthor(terms):
	results = readCatalog("?search=" + urllib.parse.quote(terms))["results"]
	title = "Search results"
	searchType = "author"

	# refine results to only include author matches
	books = []
	for book in results:
		if (book["authors"]):
			for author in book["authors"]:
				if (terms.lower() in author["name"].lower()):
					books.append(book)

	return render_template("search.html", **locals())


@app.route("/search/category=<string:terms>")
def searchCategory(terms):
	books = readCatalog("?topic=" + urllib.parse.quote(terms))["results"]
	title = "Search results"
	searchType = "category"

	return render_template("search.html", **locals())


if __name__ == "__main__":
	app.run()
