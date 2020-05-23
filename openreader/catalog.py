import urllib.request, urllib.error
import json

import openreader.cache as cache

# https://github.com/garethbjohnson/gutendex#api
def _read_catalog(route):
	url = "http://gutendex.com/books" + route
	try:
		with urllib.request.urlopen(url) as req:
			return json.loads(req.read().decode())
	except urllib.error.HTTPError:
		return None


# https://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages
# returns bytes, not a string
def _read_PG(route):
	url = "https://www.gutenberg.org" + route
	try:
		with urllib.request.urlopen(url) as req:
			return req.read()
	except urllib.error.HTTPError:
		return None


# return book metadata
def get_info(id):
	return _read_catalog("/{}".format(id))


# return book cover. verified valid sizes: small, medium
def get_cover(id, size):
	return _read_PG("/cache/epub/{0}/pg{0}.cover.{1}.jpg".format(id, size))


# Extracts <head> from book
def get_head(str):
	head_1_index = str.find("<head>")
	head_2_index = str.find("</head>")
	return str[head_1_index:head_2_index + 7]


# return book content
def get_content(id):
	if cache.contains(id):
		print("returning cached item:", id)
		return cache.get(id)
	# content = _read_PG("/files/{0}/{0}.txt".format(id))
	content = _read_PG("/files/{0}/{0}-h/{0}-h.htm".format(id))
	cache.add(id, content)
	return content

# return book content by page
def get_content_page(id, page):
	full_book = get_content(id)
	# print(get_content(id))
	html_head = get_head(full_book)						# HTML <head> tag as a string
	book_page = []										# Array where each element = page
	space_count = 0										# Count of space characters to determine page breaks
	newline_count = 0									# Count of newline characters

	starting_index = full_book.find("<body>")
	# starting_index = 0
	slice_index = starting_index
	for i in range(starting_index, len(full_book)):
		# if full_book[i] == " ":
			# space_count += 1
		if full_book[i] == "\n":
			newline_count += 1

		# break document into a new page if there are 566 pages OR 50 new lines. Whichever comes first.
		# if space_count >= 566:							# This will determine how many words per page
			# book_page.append(full_book[slice_index:i])
			# slice_index = i
			# space_count = 0

		if newline_count >= 50:
			book_page.append(full_book[slice_index:i])
			slice_index = i
			newline_count = 0

	return [html_head, book_page[page - 1], len(book_page)]
	# return [book_page[page - 1], len(book_page)]


# return images referenced in book content
def get_content_image(id, filename):
	return _read_PG("/files/{0}/{0}-h/images/{1}".format(id, filename))


# return a list of book metadata
# Note: title and author search types artificially limit results to matches
def search(type, terms):
	if type == "title":
		results = _read_catalog("?search=" + urllib.parse.quote(terms))["results"]
		return [x for x in results if terms.lower() in x["title"].lower()]
	elif type == "author":
		results = _read_catalog("?search=" + urllib.parse.quote(terms))["results"]
		return [b for b in results if b["authors"] and
			True in (terms.lower() in a["name"].lower() for a in b["authors"])
		]
	elif type == "category":
		return _read_catalog("?topic=" + urllib.parse.quote(terms))["results"]
	else:
		return None
