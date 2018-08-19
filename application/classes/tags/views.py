from application import app
from flask import render_template
from application.classes.tags.forms import TagSearchForm
from application.classes.tags.models import Tag


@app.route("/tags", methods=["GET"])
def tags_index():
	"""Constructs the tag cloud."""

	form = TagSearchForm()

	form.tag_id.choices = [(tags.get("id"), tags.get("name") + " (" + str(tags.get("count")) + ")") for tags in
						   Tag.get_tags_with_use_count(None)]

	return render_template("tags/cloud.html", form=form, tags=Tag.get_tags_with_use_count())
