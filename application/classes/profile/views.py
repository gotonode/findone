import random
from datetime import datetime

from flask import render_template, request, redirect, url_for
from flask_login import current_user

from application import app, db, login_required_with_role, Role
from application.classes.account.models import Account

from application.classes.profile.forms import ProfileEditTextForm, ProfileEditInfoForm, TagForm, ProfileCreateForm, \
	ProfileEditSeekForm
from application.classes.profile.models import Profile, City

from application.classes.tags.models import Tag, Profile_Tag
from application.classes.message.forms import MessageForm


@app.route("/profile", methods=["GET"])
@login_required_with_role(Role.Normal)
def profile_view():
	"""Redirects the logged-in user to "/profile/<handle>"."""

	account = Account.query.filter_by(id=current_user.id).first()

	if not Profile.query.filter_by(id=account.id).first():
		return redirect(url_for("profile_create"))  # User doesn't have a profile yet.

	return redirect(url_for("profile_view_with_handle", handle=str(account.handle)))


@app.route("/profile/id/<handle>", methods=["GET"])
def profile_view_with_handle(handle):
	"""View a profile (based on the given handle); this is the only place a profile is rendered."""

	own_profile = False

	account = Account.query.filter_by(handle=handle).first()

	if not account:
		return render_template("error.html", errors=["Käyttäjätunnusta ei löydy."])

	profile = Profile.query.filter_by(id=account.id).first()

	if not profile:
		return render_template("error.html", errors=["Käyttäjä ei ole vielä luonut profiilia itselleen. Voit tarkistaa tilanteen myöhemmin."])

	if current_user.is_authenticated and current_user.id == account.id:
		own_profile = True

	if profile.birth_year:
		age = datetime.now().year - profile.birth_year
		profile.age = age

	if profile.city_id:
		city = City.query.filter_by(id=profile.city_id).first()
		profile.city = city.name

	form = MessageForm()

	if current_user and current_user.is_authenticated:
		if current_user.handle == handle:
			form = None

	seek = ""

	if profile.seek_friend:
		if seek:
			seek += ", "
		seek = "ystävää"

	if profile.seek_support:
		if seek:
			seek += ", "
		seek += "vertaistukea"

	if profile.seek_penpal:
		if seek:
			seek += ", "
		seek += "kirjekaveria"

	if profile.seek_partner:
		if seek:
			seek += ", "
		seek += "kumppania"

	if profile.seek_other:
		if seek:
			seek += ", "
		seek += "jotain muuta"

	if seek == "":
		seek = None

	tags = Tag.query.filter(Profile_Tag.tag_id == Tag.id, Profile_Tag.profile_id == account.id).order_by(Tag.name).all()

	return render_template("profile/view.html", form=form, account=account, profile=profile, tags=tags, seek=seek,
						   own_profile=own_profile)


@app.route("/profile/random", methods=["GET"])
def profile_view_random():
	"""Redirect to a pseudorandom profile."""

	profiles = Profile.query.all()

	if len(profiles) == 0:
		return "Not enough profiles to use this feature."

	rand_profile = random.choice(profiles)

	# If the user is logged in, we'll look for another profile to display to them than their own.
	if current_user.is_authenticated and len(profiles) > 1:  # So we won't end up in an infinite loop.
		while rand_profile.id == current_user.id:
			rand_profile = random.choice(profiles)

	handle = Account.query.filter_by(id=rand_profile.id).first().handle

	return redirect(url_for("profile_view_with_handle", handle=handle))


@app.route("/profile/edit", methods=["GET"])
@login_required_with_role(Role.Normal)
def profile_edit():
	"""Edit your own profile (GET)."""

	profile = Profile.query.filter_by(id=current_user.id).first()

	if not profile:
		return redirect(url_for("profile_create"))  # User doesn't have a profile yet.

	tags = Tag.query.filter(
		Profile_Tag.tag_id == Tag.id,
		Profile_Tag.profile_id == current_user.id) \
		.order_by(Tag.name).all()

	text_edit_form = ProfileEditTextForm()

	text_edit_form.title.data = profile.title
	text_edit_form.content.data = profile.content

	info_edit_form = ProfileEditInfoForm()

	gender = profile.gender

	if gender is None:
		gender = "-"  # A dash here is used to represent null, or no-value.

	info_edit_form.gender.data = gender

	birth_year = profile.birth_year

	if birth_year is None:
		birth_year = ""

	info_edit_form.birth_year.data = birth_year

	info_edit_form.city_id.choices = [(cities.id, cities.name) for cities in City.query.all()]

	empty_choice = (-1, "(tyhjä)")
	info_edit_form.city_id.choices.insert(0, empty_choice)

	info_edit_form.city_id.data = profile.city_id
	info_edit_form.city_id.default = profile.city_id

	seek_edit_form = ProfileEditSeekForm()

	return render_template("profile/edit.html",
						   profile=profile,
						   tags=tags,
						   profile_text_form=text_edit_form,
						   profile_info_form=info_edit_form,
						   profile_seek_form=seek_edit_form,
						   tag_form=TagForm())


@app.route("/profile/edit/content", methods=["POST"])
@login_required_with_role(Role.Normal)
def profile_edit_content_post():
	"""Edit your own profile's title and content (POST)."""

	form = ProfileEditTextForm(request.form)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())

	profile = db.session().query(Profile).filter_by(id=current_user.id).first()

	profile.title = form.title.data
	profile.content = form.content.data

	db.session().commit()

	return redirect(url_for("profile_edit", _anchor="content"))


@app.route("/profile/edit/info", methods=["POST"])
@login_required_with_role(Role.Normal)
def profile_edit_details_post():
	"""Edit your own profile's age, gender and location (POST)."""

	form = ProfileEditInfoForm(request.form)

	form.city_id.choices = [(cities.id, cities.name) for cities in City.query.all()]

	empty_choice = (-1, "(tyhjä)")
	form.city_id.choices.insert(0, empty_choice)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())
	profile = db.session().query(Profile).filter_by(id=current_user.id).first()

	birth_year = int(form.birth_year.data)
	gender = form.gender.data
	if gender == "-":  # This is not null. So we convert it.
		gender = None
	city_id = form.city_id.data
	if city_id == -1:  # If we get a negative, we'll turn it into null.
		city_id = None

	profile.birth_year = birth_year
	profile.gender = gender
	profile.city_id = city_id

	db.session().commit()

	return redirect(url_for("profile_edit", _anchor="details"))


@app.route("/profile/tags/add", methods=["POST"])
@login_required_with_role(Role.Normal)
def profile_tags_add():
	"""Add a tag to your profile."""

	form = TagForm(request.form)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())

	tag_name = form.tag.data

	tag = Tag.query.filter(Tag.name == tag_name).first()

	# If the tag doesn't exist in the system, it is first added. After that,
	# it is associated with the currently logged-in user's profile.

	if tag:
		user_id = tag.id

		profile_tag = Profile_Tag.query.filter_by(profile_id=current_user.id, tag_id=tag.id).first()

		if profile_tag:
			return render_template("error.html", errors=["Tämä merkki on jo profiilissasi."])

	else:
		new_tag = Tag(tag_name)
		db.session().add(new_tag)  # A new tag is born!
		db.session().commit()
		user_id = new_tag.id

	profile_tag = Profile_Tag(current_user.id, user_id)
	db.session().add(profile_tag)
	db.session().commit()

	return redirect(url_for("profile_edit", _anchor="tags"))


@app.route("/profile/tags/remove", methods=["POST"])
@login_required_with_role(Role.Normal)
def profile_tags_remove():
	"""Remove a tag from your profile."""

	tag_id = request.form["tag_id"]

	profile_tag = Profile_Tag.query.filter_by(tag_id=tag_id, profile_id=current_user.id).first()

	db.session().delete(profile_tag)
	db.session().commit()

	return redirect(url_for("profile_edit", _anchor="tags"))


@app.route("/create", methods=["GET"])
@login_required_with_role(Role.Normal)
def profile_create():
	"""Create user's profile (GET)."""

	profile = Profile.query.filter_by(id=current_user.id).first()

	if profile:
		# User already has a profile.
		return redirect(url_for("profile_edit"))

	form = ProfileCreateForm()

	form.city_id.choices = [(cities.id, cities.name) for cities in City.query.all()]

	form.gender.data = '-'

	# Add this at the beginning so that the user can choose "empty".
	empty_choice = (-1, "(tyhjä)")
	form.city_id.choices.insert(0, empty_choice)

	return render_template("profile/create.html", form=form)


@app.route("/create", methods=["POST"])
@login_required_with_role(Role.Normal)
def profile_create_post():
	"""Create user's profile (POST)."""

	profile = Profile.query.filter_by(id=current_user.id).first()

	if profile:
		# User already has a profile.
		return redirect(url_for("profile_edit"))

	form = ProfileCreateForm(request.form)

	form.city_id.choices = [(cities.id, cities.name) for cities in City.query.all()]

	empty_choice = (-1, "(tyhjä)")
	form.city_id.choices.insert(0, empty_choice)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())

	title = form.title.data
	content = form.content.data

	birth_year = int(form.birth_year.data)
	gender = form.gender.data
	if gender == "-":  # This is not null. So we convert it.
		gender = None
	city_id = form.city_id.data
	if city_id == -1:  # If we get a negative, we'll turn it into null.
		city_id = None

	account = Account.query.filter_by(id=current_user.id).first()

	profile = Profile(account_id=account.id,
					  title=title,
					  content=content,
					  birth_year=birth_year,
					  gender=gender,
					  city_id=city_id)
	db.session().add(profile)
	db.session().commit()

	return redirect(url_for("profile_view_with_handle", handle=account.handle))
