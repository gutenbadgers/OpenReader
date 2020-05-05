from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, abort
)
import urllib.request, urllib.error
import json

from werkzeug.exceptions import abort

from openreader.auth import login_required
from openreader.db import get_db

bp = Blueprint('books', __name__)


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


@bp.route("/")
def index():
	return render_template("index.html")


@bp.route("/bookshelf", methods=["GET", "POST"])
@login_required
def bookshelf():
	db = get_db()
	if (request.method == "GET"):
		book_ids = db.execute(
			"SELECT book_id FROM bookshelf WHERE user_id = ?",
			(g.user["id"],)
		).fetchall()
		books = [readCatalog("/{}".format(b["book_id"])) for b in book_ids]
		return render_template("bookshelf.html", books=books)
	
	action = request.form.get("action")
	book_id = request.form.get("book_id")
	user_id = g.user["id"]

	if not (action in ["add", "delete"] and book_id and user_id):
		abort(400) # client error: bad request

	prev_bookmark =  db.execute(
		"SELECT book_id FROM bookshelf WHERE book_id = ? AND user_id = ?",
		(book_id, user_id)
	).fetchone()

	if action == "delete" and prev_bookmark is not None:
		db.execute(
			"DELETE FROM bookshelf WHERE book_id = ? AND user_id = ?",
			(book_id, user_id)
		)

	if action == "add" and prev_bookmark is None:
		db.execute(
			"INSERT INTO bookshelf (book_id, user_id) VALUES (?, ?)",
			(book_id, user_id)
		)

	db.commit()
	return redirect(url_for("books.bookshelf"))


@bp.route("/book/<int:id>")
def info(id):
	db = get_db()
	res = readCatalog("/{}".format(id))
	logged_in = g.user and g.user["id"]
	bookmarked = None

	if (logged_in): # if logged in, check if the user has a bookmark already
		bookmarked =  db.execute(
			"SELECT book_id FROM bookshelf WHERE book_id = ? AND user_id = ?",
			(id, g.user["id"])
		).fetchone() is not None
	else:
		bookmarked = False

	return render_template("bookInfo.html", book=res, bookmarked=bookmarked)


@bp.route("/book/<int:id>/read")
def read(id):
	return readPG("/files/{0}/{0}-h/{0}-h.htm".format(id))


# verified valid sizes: small, medium
@bp.route("/book/<int:id>/cover/<string:size>")
def cover(id, size):
	try:
		return readPG("/cache/epub/{0}/pg{0}.cover.{1}.jpg".format(id, size))
	except urllib.error.HTTPError:
		img = 'noCover{}.jpg'.format(size.capitalize())
		return bp.send_static_file(img)


# images referenced in book content
@bp.route("/book/<int:id>/images/<string:imageName>")
def image(id, imageName):
	return readPG("/files/{0}/{0}-h/images/{1}".format(id, imageName))


@bp.route("/search", methods=["GET", "POST"])
def search():
	if request.method == "GET":
		return render_template("search.html")

	searchType = request.form.get("searchType")
	url = ""

	if searchType in ["title", "author", "category"]:
		url = "/search/{}/".format(searchType)
	else:
		abort(400) # client error: invalid form

	url += urllib.parse.quote(request.form.get("terms"))
	return redirect(url, code=303)


@bp.route("/search/title/<string:terms>")
def searchTitle(terms):
	results = readCatalog("?search=" + urllib.parse.quote(terms))["results"]

	# refine results to only include title matches
	books = [x for x in results if terms.lower() in x["title"].lower()]
	searchType = "title"
	return render_template("search.html", **locals())


@bp.route("/search/author/<string:terms>")
def searchAuthor(terms):
	results = readCatalog("?search=" + urllib.parse.quote(terms))["results"]

	# refine results to only include author matches
	books = []
	for book in results:
		if (book["authors"]):
			for author in book["authors"]:
				if (terms.lower() in author["name"].lower()):
					books.append(book)

	searchType = "author"
	return render_template("search.html", **locals())


@bp.route("/search/category/<string:terms>")
def searchCategory(terms):
	books = readCatalog("?topic=" + urllib.parse.quote(terms))["results"]

	searchType = "category"
	return render_template("search.html", **locals())
