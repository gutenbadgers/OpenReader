from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, abort
)
import urllib

from openreader.auth import login_required
from openreader.db import get_db
import openreader.catalog as catalog

bp = Blueprint("books", __name__, static_folder="static")

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
		books = [catalog.get_info(b["book_id"]) for b in book_ids]
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
	res = catalog.get_info(id)
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
	return catalog.get_content(id)


@bp.route("/book/<int:id>/cover/<string:size>")
def cover(id, size):
	cover = catalog.get_cover(id, size)
	if not cover:
		img = 'noCover{}.jpg'.format(size.capitalize())
		return bp.send_static_file(img)
	return cover


# images referenced in book content
@bp.route("/book/<int:id>/images/<string:imageName>")
def image(id, imageName):
	return catalog.get_content_image(id, imageName)


@bp.route("/search", methods=["GET", "POST"])
def search():
	if request.method == "GET":
		return render_template("search.html")

	searchType = request.form.get("searchType")

	if searchType not in ["title", "author", "category"]:
		abort(400) # client error: invalid form

	url = "/search/{}/".format(searchType)
	url += urllib.parse.quote(request.form.get("terms"))
	return redirect(url, code=303)


@bp.route("/search/title/<string:terms>")
def searchTitle(terms):
	books = catalog.search("title", terms)
	searchType = "title"
	return render_template("search.html", **locals())


@bp.route("/search/author/<string:terms>")
def searchAuthor(terms):
	books = catalog.search("author", terms)	
	searchType = "author"
	return render_template("search.html", **locals())


@bp.route("/search/category/<string:terms>")
def searchCategory(terms):
	books = catalog.search("category", terms)
	searchType = "category"
	return render_template("search.html", **locals())
