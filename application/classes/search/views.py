from flask import render_template, request

from application import app
from application.classes.profile.models import Profile, City
from application.classes.tags.models import Tag
from application.classes.search.forms import SearchForm


@app.route("/search")
def search():
	form = SearchForm()

	users = Profile.query.all()

	return render_template("search/search.html", form=form, users=users, tag=None)


@app.route("/search/tag/<tag_id>", methods=["GET"])
def search_with_tag(tag_id):
	"""Used to search_with_tag for all profiles that have the given tag associated with them."""


	form = SearchForm()

	# min_age = request.args.get("min_age")
	# max_age = request.args.get("max_age")
	#
	# try:
	# 	min_age = int(min_age)
	# 	max_age = int(max_age)
	#
	# except ValueError:
	# 	return render_template("error.html", errors=["Ikä ei ole kokonaisluku."])
	#
	# if not form.validate():
	# 	return render_template("error.html", errors=form.errors.values())

#	if (min_age and min_age < 18) or (max_age and max_age < 18):
#		return render_template("error.html", errors=["Ikä ei voi olla alle 18."])

	tag = Tag.query.filter_by(id=tag_id).first()

	profiles_with_tag = Profile.find_profiles_which_have_tag(tag_id)



	# if min_age:
	# 	form.min_age.data = min_age
	#
	# if max_age:
	# 	form.max_age.data = max_age

	form.city_id.choices = [(cities.id, cities.name) for cities in City.query.all()]

	empty_choice = (-1, "(kaikki)")
	form.city_id.choices.insert(0, empty_choice)

	form.city_id.data = -1
	form.city_id.default = -1

	return render_template("search/search.html", form=form, users=profiles_with_tag, tag=tag)
