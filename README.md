# OpenReader

An open-source e-reader for out-of-copyright books written in Python 3.

## Installation

For the simplest method, just do this:

```bash
pip install flask
```

For an isolated installation, the process is a bit more involved:

```bash
# First install the virtual pip environment handler
pip install virtualenv

# Next create a new virtual environment
virtualenv venv

# Activate the virtual environment in bash.
# There are other scripts for other shells, like activate.fish and .ps1
source venv/bin/activate

# Once inside venv, pip will install packages isolated from your system
pip install flask

# When you're done, exit the virtual environment
deactivate
```

## Usage

If you're using `virtualenv`, then first run `source venv/bin/activate`.

Execute `flask run`, then visit http://127.0.0.1:5000 in your browser.

With `virtualenv`, run `deactivate` or just kill the shell when you're done.

## Contributor Info

* Tabs, not spaces. That's what the tab key is for.

* Don't commit (even locally) if there are errors or warnings.

* Flask has a built-in development server that supports auto-reload on source change and shows an interactive debugger on errors. Run it with `FLASK_ENV=development flask run`.
