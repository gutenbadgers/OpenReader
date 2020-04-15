from flask import Flask
import urllib.request, json 

app = Flask(__name__)

# https://github.com/garethbjohnson/gutendex#api
with urllib.request.urlopen("http://gutendex.com/books/?search=dickens%20great") as url:
	data = json.loads(url.read().decode())
	print(data)

@app.route('/')
def hello_world():
	return 'Hello, world!'

if __name__ == '__main__':
	app.run()
