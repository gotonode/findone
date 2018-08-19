from flask_wtf import FlaskForm
from wtforms import validators, IntegerField


class FavoriteForm(FlaskForm):
	# TODO: Check that the ID is a positive integer (> 0).
	id = IntegerField("ID", [validators.DataRequired()])

	# No need to ask for the source's ID (it is the currently logged in user).

	class Meta:
		csrf = True
