from flask import (
	Blueprint, flash, g, redirect, render_template, request, url_for, abort
)
import urllib

from openreader.auth import login_required
from openreader.db import get_db
import openreader.catalog as catalog
import random

bp = Blueprint("books", __name__, static_folder="static")

@bp.route("/")
def index():

	booklist = []
	count = 0
	while count < 5:
		id = random.randint(1,4000)
		book = catalog.get_info(id)
		cover = catalog.get_cover(id, "medium")

		while not cover:
			id = random.randint(1,4000)
			book = catalog.get_info(id)

		booklist.append(book)
		count = count + 1

	return render_template("index.html", books=booklist)


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
	content = catalog.get_content(id)
	if content:
		return render_template("bookFull.html", content=content)
	else:
		return "Book not available!"

# Route to get book page
@bp.route("/book/<int:id>/read/<int:page>")
def readPage(id, page):
	body = catalog.get_content_page(id, page)

	if page == 1 and not body:
		return "Book not available!"

	if not body:	# failsafe to keep user from falling out of page ranges
		return redirect(url_for("books.readPage", id=id, page=1))

	return render_template("bookPage.html", **locals())


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

	if searchType not in ["title-author", "category"]:
		abort(400) # client error: invalid form

	url = url_for("books.searchResults", searchType=searchType,
		terms=request.form.get("terms"))
	return redirect(url, code=303)


@bp.route("/search/<string:searchType>/<string:terms>")
def searchResults(searchType, terms):
	if searchType not in ["title-author", "category"]:
		abort(400) # client error: invalid form

	books = catalog.search(searchType, terms)
	return render_template("search.html", **locals())

# Function to get the URL of the current page to be used in bookmarks.
@bp.route("/book/<int:id>/read/<int:page>/getbookmark")
@login_required
def getBookmark(id, page):
	pageURL = url_for("books.readPage", id=id, page=page)
	db = get_db()
	if not g: abort(400)

	db.execute(
		"INSERT INTO bookmark (book_id, user_id, page, implicit) VALUES(?, ?, ?, ?)",
		(id, g.user["id"], page, 1)
	)

	newURL = url_for("books.info", id=id)
	db.commit()
	return redirect(newURL)

@bp.route("/book/<int:id>/readbookmark")
@login_required
def send_to_bookmark(id):
	db = get_db()
	if not g: abort(400)

	# Retrieve bookmark info from row with highest bookmark_id
	thisBook = db.execute(
		"SELECT * FROM bookmark WHERE user_id = ? AND book_id = ? AND bookmark_id = (SELECT MAX(bookmark_id) FROM bookmark)",
	 	(g.user["id"], id)
	 ).fetchone()

	 # If case for no bookmarks
	if thisBook is None:
		newURL = url_for("books.info", id=id)
		return redirect(newURL)

	#Send user to the correct page
	page = thisBook[3]

	pageURL = url_for("books.readPage", id=id, page=page)

	return redirect(pageURL)
