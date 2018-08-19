from flask_wtf import FlaskForm
from wtforms import validators, SelectField


class TagSearchForm(FlaskForm):
	"""Used to search_with_tag with a specific tag on the tag cloud."""

	tag_id = SelectField("Kaikki merkit",
						 [validators.data_required(message="Epäkelpo merkki annettu.")],
						 choices=[],
						 coerce=int)

	class Meta:
		csrf = False  # This doesn't need XSS protection.
