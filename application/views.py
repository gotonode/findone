import os

from flask import render_template
from flask_login import current_user

from application import app
from application.classes.profile.models import Profile


@app.route("/")
def index():
	"""The starting point, the root. Returns the 'index.html' file."""

	if current_user:
		users = Profile.find_random_profiles()
	else:
		users = None

	debug = True
	if os.environ.get("HEROKU"):
		debug = False

	return render_template("index.html", debug=debug, users=users)
