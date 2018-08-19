from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, validators, BooleanField
from wtforms.fields.html5 import EmailField


# Classes here are separated to avoid code repetition, but it perhaps decreases readability.
# Classes beginning with double underscore are "private" (guided, not enforceable).


class __Email:
	"""When the user needs to enter their email address; used uniformly."""

	__abstract__ = True

	email = EmailField("Sähköpostiosoite",
					   [validators.DataRequired(message="Virheellinen sähköpostiosoite."),
						validators.Email()])  # Email handles length as well.


class __Password:
	"""When the user's password is prompted (in cases where it is only asked once)."""

	__abstract__ = True

	password = PasswordField("Salasana",
							 [validators.Length(min=8,
												max=32,
												message="Salasana joko liian lyhyt tai liian pitkä.")])


class __Handle:
	"""The username or profile name, also known as the handle."""

	__abstract__ = True

	handle = StringField("Profiilinimi",
						 [validators.Length(min=4,
											max=12,
											message="Profiilinimi joko liian lyhyt tai liian pitkä.")])


class EmailForm(FlaskForm, __Email, __Password):
	"""Used where the user can change their email address."""

	class Meta:
		csrf = True


class LoginForm(FlaskForm, __Email, __Password):
	"""Used when the user is logging in."""

	class Meta:
		csrf = True


class PasswordForm(FlaskForm):
	"""This is used when the user wants to change their password."""

	# No need to validate length of current password?
	current_password = PasswordField("Nykyinen salasana")

	new_password = PasswordField("Uusi salasana", [
		validators.Length(min=8,
						  max=32,
						  message="Uusi salasana on joko liian lyhyt (alle 8 merkkiä) tai liian pitkä (yli 32 merkkiä).")
	])

	new_password2 = PasswordField("Uusi salasana (2)", [
		validators.EqualTo("new_password",
						   message="Salasanojen on oltava samat.")
	])

	class Meta:
		csrf = True


class DeleteForm(FlaskForm, __Handle):
	"""When the user wants to delete their account."""

	# We need to add delete_password here because it is already present on the same page (for HTML label).
	delete_password = PasswordField("Salasana",
									[validators.Length(min=8,
													   max=32,
													   message="Salasana joko liian lyhyt tai liian pitkä.")])

	# On modern browsers, the HTML tag "required" will enforce this,
	# but on unsupported browsers, this is displayed to the user.
	confirmation = BooleanField("",
								validators=[validators.DataRequired("Sinun pitää hyväksyä tunnuksesi poisto.")])

	class Meta:
		csrf = True


class RegisterForm(FlaskForm, __Handle, __Email, __Password):
	"""When a new user is registering for an account for the first time."""

	password2 = PasswordField("Salasana (uudelleen)",
							  [validators.Length(min=8,
												 max=32,
												 message="Uudelleenannettu salasana ei kelpaa."),
							   validators.EqualTo("password",
												  message="Salasanojen on oltava samat.")])

	confirmation = BooleanField("",
								validators=[
									validators.DataRequired("Sinun pitää hyväksyä käyttö- ja tietosuojaehdot.")])

	class Meta:
		csrf = True
