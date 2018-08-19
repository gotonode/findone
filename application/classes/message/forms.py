from flask_wtf import FlaskForm
from wtforms import validators, TextAreaField, IntegerField


class MessageForm(FlaskForm):
	message = TextAreaField("Viesti",
							[validators.Length(min=1, max=100,
											   message="Viestisi on joko liian lyhyt tai liian pitkä.")])

	# TODO: Check that the ID is a positive integer.
	target_id = IntegerField("ID", [validators.DataRequired()])

	class Meta:
		csrf = True
