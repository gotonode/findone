import os
from enum import Enum
from functools import wraps

from flask import Flask, got_request_exception
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path="/static")

import rollbar
import rollbar.contrib.flask


@app.before_first_request
def init_rollbar():
    rollbar.init(
        "4696f6afdcbc41399fd694550535b780",
        "development",
        root=os.path.dirname(os.path.realpath(__file__)),
        allow_logging_basic_config=False)

got_request_exception.connect(rollbar.contrib.flask.report_exception, app)

if os.environ.get("HEROKU"):
	# We're running on Heroku.
	app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")  # This is secretly stored on Heroku.
	app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
	app.config["SQLALCHEMY_ECHO"] = False

	# These are only when running on Heroku, and provide statistics for the developers
	# (things like database loads and slow queries).
	from scout_apm.flask import ScoutApm

	app.config['SCOUT_NAME'] = "findone"

	ScoutApm(app)
else:
	# We're running locally.
	app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")  # This is locally stored as an environment variable.

	# This is of format: "postgres://user:password@localhost:5432/database", and the
	# connection string is stored locally (the password is a secret).
	app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("LOCAL_DATABASE_URL")
	app.config["SQLALCHEMY_ECHO"] = True  # For debugging purposes.

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

bcrypt = Bcrypt(app)

db = SQLAlchemy(app)


class Role(Enum):
	"""These are used with the 'login_required_with_role' function."""

	Normal = 'N'  # Normal users, without admin and mod powers, but with a profile.
	Mod = 'M'  # Mod users, with mod powers but without a profile/account page.
	Admin = 'A'  # Admin user(s), with admin powers but without a profile/account page.


if os.environ.get("HEROKU"):
	# We're running on Heroku, so we'll add this for statistics.
	from scout_apm.flask.sqlalchemy import instrument_sqlalchemy

	instrument_sqlalchemy(db)


def login_required_with_role(role):
	"""Used instead of "login_required" when a specific role is needed."""

	role = role.value  # Because it's an enum, we'll get its value here.

	def wrapper(fn):
		@wraps(fn)
		def decorated_view(*args, **kwargs):
			if not current_user.is_authenticated:
				return login_manager.unauthorized()

			if current_user.role != role:
				return login_manager.unauthorized()

			return fn(*args, **kwargs)

		return decorated_view

	return wrapper


# The following imports are necessary. Do not remove them even if your environment/IDE claims that
# they are not needed. This does introduce a cyclomatic issue but in this instance it is by purpose.

import application.views
from application.classes.tags import models, views
from application.classes.account import models, views
from application.classes.profile import models, views
from application.classes.conversation import models, views
from application.classes.message import models
from application.classes.search import views
from application.classes.favorite import models, views
from application.classes.block import models, views
from application.classes.admin import views
from application.classes.debug import views
from application.classes.generic import views

# Do not remove the imports above. If your IDE automatically removes them, re-clone
# this repository from GitHub (or, if you know how, revert the changes).

from application.classes.account.models import Account

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth_login_get"
login_manager.login_message = "Tämä toiminto vaatii sisäänkirjautumisen."


@login_manager.user_loader
def load_user(user_id):
	"""Used by the session system."""

	return Account.query.get(user_id)


# This was causing random crashes on Heroku, and it seems the same issue is with other students.
# About every 5th or so GET request would result in a server error concerning an SSL issue.
# Will look into it on a later occasion.
#
# Update: Setting the workers to 1 fixed it. But is it good for production?
try:
	db.create_all()
except:
	pass
