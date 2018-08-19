from datetime import datetime
import random
import string

from flask import url_for, redirect, render_template
from flask_login import current_user, logout_user, login_user
from sqlalchemy import text

from application import db, Role

from application import app
from application.classes.account.models import Account
from application.classes.profile.models import Profile, City
from application.classes.tags.models import Profile_Tag, Tag
from application.classes.conversation.models import Conversation
from application.classes.message.models import Message


@app.route("/project")
def project():
	accounts = Account.query.all()

	return render_template("debug/project.html", accounts=accounts)


@app.route("/reset", methods=["GET"])
def reset_no_users():
	reset(create_users=False)


@app.route("/debug/generate_messages", methods=["GET"])
def generate_messages():
	profiles = Profile.query.all()

	random.shuffle(profiles)  # A random order of profiles.

	id_list = []

	for profile in profiles:
		id_list.append(profile.id)

	for profile in profiles:
		while True:
			a = random.choice(id_list)
			if a != profile.id:
				break

		if profile.id > a:
			alpha = a
			beta = profile.id
		else:
			alpha = profile.id
			beta = a

		conversation_check = Conversation.query.filter_by(alpha=alpha, beta=beta).first()
		if not conversation_check:
			conversation = Conversation(alpha=alpha, beta=beta)

			db.session().add(conversation)
			db.session().commit()

	conversations = Conversation.query.all()

	count = random.randint(10, 100)

	for x in range(count):
		conversation = random.choice(conversations)

		content = generate_sentence(random.randint(1, 20))

		if random.randint(0, 1) == 0:
			# From alpha to beta.
			message = Message(conversation.id, conversation.alpha, conversation.beta, content)
		else:
			# From beta to alpha.
			message = Message(conversation.id, conversation.beta, conversation.alpha, content)

		db.session().add(message)

	db.session().commit()

	return redirect(url_for("project"))


@app.route("/reset/<create_users>", methods=["GET"])
def reset(create_users):
	db.reflect()
	db.drop_all()
	db.create_all()

	# Add the cities first.
	sql_file_cities = open("application/database/sql/cities.sql", 'r', encoding="UTF-8")
	execute_sql(sql_file_cities)

	# And now add the sample tags.
	sql_tags = open("application/database/sql/tags.sql", 'r', encoding="UTF-8")
	execute_sql(sql_tags)

	if create_users == str(1):
		# Create an admin, a mod and three normal accounts.
		debug_create_sample_user(Role.Admin)
		debug_create_sample_user(Role.Mod)
		debug_create_sample_users(count=3)

	try:
		if current_user and current_user.is_authenticated:
			logout_user()
	except:
		pass

	return redirect(url_for("project"))


def execute_sql(sql_file):
	sql_command = ""

	for line in sql_file:
		# Line is not a comment and contains something (besides '\r\n').
		if not line.startswith("/*") and line.strip('\r\n'):
			sql_command += line.strip('\r\n')
			if sql_command.endswith(";"):
				try:
					db.session().execute(text(sql_command))
					db.session().commit()

				except:
					raise

				sql_command = ""


def generate_sentence(word_count):
	content = ""

	for x in range(word_count):
		word_length = random.randint(2, 16)
		word = ''.join(random.SystemRandom().choice(string.ascii_letters) for _ in range(word_length))
		content = content + word + " "
		if random.randint(0, 10) == 0:  # Add a newline.

			# TODO: No periods on empty lines.

			if random.randint(0, 5) == 0:  # End the previous line with a character.
				content = content.strip() + "!"
			else:
				content = content.strip() + "."

			content = content + "\r\n"

			if random.randint(0, 3) == 0:  # Two newlines in a row.
				content = content + "\r\n"

	content = content.strip(" !.\t\n\r") + "."

	return content


def debug_create_sample_user(role=Role.Normal):
	handles = db.session().query(Account.handle).all()

	if role == Role.Admin:
		prefix = "admin"
		chars = 1
	elif role == Role.Mod:
		prefix = "mod"
		chars = 2
	else:
		prefix = "usr"
		chars = 7

	# Generate a random handle until an unused one is found.
	while True:
		rand = ''.join(random.SystemRandom().choice(string.digits) for _ in range(chars))
		handle = prefix + "-" + rand
		if handle not in handles:
			break

	email = handle + "@example.com"

	password = "$2b$12$Qcq5pJtH7mQGyhszAudBH.GfyZbKqMZEkyGL/8ZESmZLrZ3cvGcCu"  # The password is "88888888".

	account = Account(email=email, handle=handle, password=password)
	account.role = role.value

	db.session().add(account)
	db.session().commit()

	if role != Role.Normal:
		# Admins and mods don't have profiles, so we're done here.
		return redirect(url_for("index"))

	account = Account.query.filter_by(handle=handle).first()

	word_count = random.randint(10, 100)  # Generate this many random words.

	content = generate_sentence(word_count)

	title = "Test Profile"

	if random.randint(0, 6) == 0:
		birth_year = None
	else:
		year = random.randint(1900, datetime.now().year - 18)
		birth_year = int(year)

	if random.randint(0, 6) == 0:
		gender = None
	else:
		gender_random = random.randint(0, 1)
		if gender_random == 1:
			gender = 'M'
		else:
			gender = 'F'

	if random.randint(0, 6) == 0:
		city_id = None
	else:
		cities = City.query.all()
		city_id = random.choice(cities).id

	profile = Profile(account_id=account.id,
					  title=title,
					  content=content,
					  birth_year=birth_year,
					  gender=gender,
					  city_id=city_id)

	if random.randint(0, 3) == 0:
		profile.seek_friend = True
	if random.randint(0, 3) == 0:
		profile.seek_other = True
	if random.randint(0, 3) == 0:
		profile.seek_partner = True
	if random.randint(0, 3) == 0:
		profile.seek_penpal = True
	if random.randint(0, 3) == 0:
		profile.seek_support = True

	tags = Tag.query.all()

	tag_count = random.randint(0, int(len(tags) / 2))

	db.session().add(profile)
	db.session().commit()

	for x in range(tag_count):
		tag = random.choice(tags)
		tags.remove(tag)

		profile_tag = Profile_Tag(account.id, tag.id)

		db.session().add(profile_tag)

	db.session().commit()

	return redirect(url_for("index"))


@app.route("/debug/create_sample_user/<count>", methods=["GET"])
def debug_create_sample_users(count, role=Role.Normal):
	for x in range(int(count)):
		debug_create_sample_user(role=role)

	return redirect(url_for("project"))


@app.route("/login/id/<account_id>", methods=["GET"])
def auth_login_now(account_id):
	if current_user and current_user.is_authenticated:
		logout_user()

	account = Account.query.filter_by(id=account_id).first()

	login_user(account)

	if account.role == Role.Normal.value:
		profile = Profile.query.filter_by(id=current_user.id).first()

		if not profile:
			return redirect(url_for("profile_create"))
		else:
			return redirect(url_for("profile_view_with_handle", handle=account.handle))
	elif account.role == Role.Admin.value:
		return redirect(url_for("admin"))
	elif account.role == Role.Mod.value:
		return redirect(url_for("mod"))


@app.route("/login/random", methods=["GET"])
def auth_login_now_random():
	if current_user and current_user.is_authenticated:
		logout_user()

	accounts = Account.query.filter_by(role='N').all()

	account = random.choice(accounts)

	login_user(account)

	profile = Profile.query.filter_by(id=current_user.id).first()

	if not profile:
		return redirect(url_for("profile_create"))
	else:
		return redirect(url_for("profile_view_with_handle", handle=account.handle))
