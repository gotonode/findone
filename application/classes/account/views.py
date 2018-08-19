from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import desc

from application import app, db, bcrypt, login_required_with_role, Role

from application.classes.account.models import Account, Login
from application.classes.account.forms import LoginForm, RegisterForm, EmailForm, PasswordForm, DeleteForm

from application.classes.profile.models import Profile

from application.classes.tags.models import Profile_Tag


@app.route("/login", methods=["GET"])
def auth_login_get():
	"""Login functionality (GET)."""

	if current_user.is_authenticated:
		return redirect(url_for("index"))
	else:
		return render_template("account/login.html", form=LoginForm())


@app.route("/login", methods=["POST"])
def auth_login_post():
	"""Login functionality (POST)."""

	if current_user.is_authenticated:
		return redirect(url_for("index"))

	form = LoginForm(request.form)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())

	login = Login(request.environ["REMOTE_ADDR"], request.user_agent.string)

	account = Account.query.filter_by(email=form.email.data).first()

	error_template = render_template("error.html", errors=["Virheellinen käyttäjätunnus tai salasana."])

	if not account:  # Login fails.
		login.failure(form.email.data)  # If the login fails, we store the used email address.

		db.session().add(login)
		db.session().commit()

		return error_template

	password = form.password.data.strip()

	pass_okay = bcrypt.check_password_hash(account.password, password)

	if not pass_okay:
		login.failure(form.email.data)

		db.session().add(login)
		db.session().commit()

		return error_template

	login_user(account)

	login.success(account.id)  # If the login succeeds, we'll store the account's ID.

	db.session().add(login)
	db.session().commit()
	# TODO: Handle Flask's "next" URL parameter, if present.

	if account.role != 'N':
		return redirect(url_for("index"))
	else:
		profile = Profile.query.filter_by(id=current_user.id).first()
		if not profile:
			return redirect(url_for("profile_create"))  # User doesn't have a profile yet.

		return redirect(url_for("profile_view_with_handle", handle=account.handle))


@app.route("/logout", methods=["GET"])
@login_required
def auth_logout():
	"""Logout the current user (requires someone to be logged in)."""

	logout_user()
	return redirect(url_for("index"))


@app.route("/register", methods=["GET"])
def auth_register_get():
	"""Register for an account (GET)."""

	if current_user.is_authenticated:
		# User is logged-in and tried to register (GET).
		return redirect(url_for("index"))

	return render_template("account/register.html", form=RegisterForm())


@app.route("/register", methods=["POST"])
def auth_register_post():
	"""Register for an account (POST)."""

	if current_user.is_authenticated:
		# User is logged-in and tried to register (POST).
		return redirect(url_for("index"))

	form = RegisterForm(request.form)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())

	errors = []

	email = form.email.data.strip()

	if Account.query.filter_by(email=email).first():
		errors.append("Sähköpostiosoite on jo käytössä.")

	handle = form.handle.data.strip()

	if Account.query.filter_by(handle=handle).first():
		errors.append("Profiilinimi on jo käytössä.")

	if errors:
		return render_template("error.html", errors=errors)

	plaintext_password = str(form.password.data.strip())

	hashed_password = bcrypt.generate_password_hash(plaintext_password, 12).decode("utf-8")

	account = Account(email=email, handle=handle, password=hashed_password)

	db.session().add(account)
	db.session().commit()

	account = Account.query.filter_by(email=email).first()
	login_user(account)

	return redirect(url_for("profile_create"))


@app.route("/account", methods=["GET"])
@login_required_with_role(Role.Normal)
def account_edit():
	"""Edit user's account (GET)."""

	last_login = Login.query.filter_by(account_id=current_user.id).order_by(
		desc("date_created")).first()

	return render_template("account/edit.html",
						   email_form=EmailForm(),
						   password_form=PasswordForm(),
						   delete_form=DeleteForm(),
						   last_login=last_login)


@app.route("/account/edit/email", methods=["POST"])
@login_required_with_role(Role.Normal)
def account_edit_email():
	"""Change user's email address."""

	form = EmailForm(request.form)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())

	account = Account.query.filter_by(email=current_user.email).first()

	pass_okay = bcrypt.check_password_hash(account.password, form.password.data)

	if not pass_okay:
		return render_template("error.html", errors=["Nykyinen salasana on väärin."])

	account.email = form.email.data
	db.session().commit()

	return redirect(url_for("account_edit", _anchor="email_tab"))


@app.route("/account/edit/password", methods=["POST"])
@login_required_with_role(Role.Normal)
def account_edit_password():
	"""Change user's password."""

	form = PasswordForm(request.form)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())

	new_password = form.new_password.data.strip()
	current_password = form.current_password.data.strip()

	account = Account.query.filter_by(email=current_user.email).first()

	pass_okay = bcrypt.check_password_hash(account.password, current_password)

	if not pass_okay:
		return render_template("error.html", errors=["Nykyinen salasana on väärin."])

	hashed_password = bcrypt.generate_password_hash(new_password, 12).decode("utf-8")

	account.password = hashed_password

	db.session().commit()

	return redirect(url_for("account_edit", _anchor="password_tab"))


@app.route("/account/edit/delete", methods=["POST"])
@login_required_with_role(Role.Normal)  # Mods and admins cannot remove their accounts.
def account_edit_delete():
	"""Delete user's account (inc. profile, tags etc)."""

	form = DeleteForm(request.form)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())

	account = Account.query.filter_by(handle=form.handle.data).first()

	error_template = render_template("error.html", errors=["Virheellinen käyttäjätunnus tai salasana."])

	if not account:
		return error_template

	pass_okay = bcrypt.check_password_hash(account.password, form.delete_password.data)

	if not pass_okay:
		return error_template

	user_id = current_user.id

	logout_user()  # Must logout before we delete everything.

	# Delete user's tag associations (if it has any).
	db.session().query(Profile_Tag).filter_by(profile_id=user_id).delete()

	# Delete user's profile (if it has one).
	db.session().query(Profile).filter_by(id=user_id).delete()

	# Delete user's account.
	db.session().query(Account).filter_by(id=user_id).delete()

	# Commit all the changes above.
	db.session().commit()

	# Return to the index. Add a message confirming the delete?
	return redirect(url_for("index"))
