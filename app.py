from flask import Flask, redirect, render_template, request, abort
import urllib.request, urllib.error
import json

app = Flask(__name__)


# https://github.com/garethbjohnson/gutendex#api
def readCatalog(route):
	url = "http://gutendex.com/books" + route
	with urllib.request.urlopen(url) as req:
		return json.loads(req.read().decode())


# https://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages
def readPG(route):
	url = "https://www.gutenberg.org" + route
	with urllib.request.urlopen(url) as req:
		return req.read()


@app.route("/")
@app.route("/index")
def index():
	return render_template("index.html")


@app.route("/login")
def login():
	abort(501) # server error: unimplemented


@app.route("/bookshelf")
def bookshelf():
	abort(501) # server error: unimplemented


@app.route("/book/<int:id>")
def bookInfo(id):
	book = readCatalog("/{}".format(id))
	title = "Info: " + book["title"]
	return render_template("bookInfo.html", **locals())


@app.route("/book/<int:id>/read")
def bookRead(id):
	return readPG("/files/{0}/{0}-h/{0}-h.htm".format(id))


# verified valid sizes: small, medium
@app.route("/book/<int:id>/cover/<string:size>")
def bookCover(id, size):
	try:
		return readPG("/cache/epub/{0}/pg{0}.cover.{1}.jpg".format(id, size))
	except urllib.error.HTTPError:
		img = 'noCover{}.jpg'.format(size.capitalize())
		return app.send_static_file(img)


# images referenced in book content
@app.route("/book/<int:id>/images/<string:imageName>")
def bookImage(id, imageName):
	return readPG("/files/{0}/{0}-h/images/{1}".format(id, imageName))


@app.route('/search', methods=['GET'])
def search():
	return render_template("search.html", title="Search")


@app.route('/search', methods=['POST'])
def searchPOST():
	searchType = request.form.get('searchType')
	url = ""

	if searchType in ["title", "author", "category"]:
		url = "/search/{}/".format(searchType)
	else:
		abort(400) # client error: invalid form

	url += urllib.parse.quote(request.form.get('terms'))
	return redirect(url, code=303)


@app.route("/search/title/<string:terms>")
def searchTitle(terms):
	results = readCatalog("?search=" + urllib.parse.quote(terms))["results"]

	# refine results to only include title matches
	books = [x for x in results if terms.lower() in x["title"].lower()]

	title = "Search results"
	searchType = "title"
	return render_template("search.html", **locals())


@app.route("/search/author/<string:terms>")
def searchAuthor(terms):
	results = readCatalog("?search=" + urllib.parse.quote(terms))["results"]

	# refine results to only include author matches
	books = []
	for book in results:
		if (book["authors"]):
			for author in book["authors"]:
				if (terms.lower() in author["name"].lower()):
					books.append(book)

	title = "Search results"
	searchType = "author"
	return render_template("search.html", **locals())


@app.route("/search/category/<string:terms>")
def searchCategory(terms):
	books = readCatalog("?topic=" + urllib.parse.quote(terms))["results"]

	title = "Search results"
	searchType = "category"
	return render_template("search.html", **locals())


if __name__ == "__main__":
	app.run()
