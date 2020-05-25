import urllib.request, urllib.error
import json

import openreader.cache as cache

_page_lines = 30

# https://github.com/garethbjohnson/gutendex#api
def _read_catalog(route):
	url = "http://gutendex.com/books" + route
	try:
		with urllib.request.urlopen(url) as req:
			return json.loads(req.read().decode("utf-8"))
	except urllib.error.HTTPError:
		return None


# https://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages
# returns bytes, not a string
def _read_PG(route, text=False):
	url = "https://www.gutenberg.org" + route
	try:
		with urllib.request.urlopen(url) as req:
			if text:
				return req.read().decode("utf-8")
			else:
				return req.read()
	except urllib.error.HTTPError:
		return None


# return book metadata
def get_info(id):
	return _read_catalog("/{}".format(id))


# return book cover. verified valid sizes: small, medium
def get_cover(id, size):
	return _read_PG("/cache/epub/{0}/pg{0}.cover.{1}.jpg".format(id, size))


# return book content
def get_content(id):
	if cache.contains(id):
		print("Returning cached item:", id)
		content = cache.get(id)
		if content:
			return content
		else:
			print("Failed to retrieve cached item. Fetching again.")

	#content = _read_PG("/files/{0}/{0}-h/{0}-h.htm".format(id))

	# if available, the -0 version is newer
	content = _read_PG("/files/{0}/{0}-0.txt".format(id), text=True)
	if not content:
		content = _read_PG("/files/{0}/{0}.txt".format(id), text=True)

	cache.add(id, content)
	return content
	

# return book content by page and number of pages
def get_content_page(id, page):
	full_book = get_content(id)
	if not full_book:
		return None

	lines = full_book.split("\n")
	first_index = max(_page_lines * (page-1), 0)
	last_index  = min(_page_lines * page, len(lines))

	#num_pages  = -(-len(lines) // _page_lines)

	if first_index < 0 or last_index > len(lines):
		return None

	page = lines[_page_lines * (page-1) : _page_lines * page]
	return "\n".join(page)


# return images referenced in book content
def get_content_image(id, filename):
	return _read_PG("/files/{0}/{0}-h/images/{1}".format(id, filename))


# return a list of book metadata
# Note: title and author search types artificially limit results to matches
def search(type, terms):
	if type == "title-author":
		return _read_catalog("?search=" + urllib.parse.quote(terms))["results"]
	elif type == "category":
		return _read_catalog("?topic=" + urllib.parse.quote(terms))["results"]
	else:
		return None
