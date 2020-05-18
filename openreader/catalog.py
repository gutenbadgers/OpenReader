import urllib.request, urllib.error
import json

# https://github.com/garethbjohnson/gutendex#api
def _read_catalog(route):
	url = "http://gutendex.com/books" + route
	try:
		with urllib.request.urlopen(url) as req:
			return json.loads(req.read().decode())
	except urllib.error.HTTPError:
		return None


# https://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages
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


# return book content
def get_content(id):
	return _read_PG("/files/{0}/{0}-h/{0}-h.htm".format(id))


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
