from flask_wtf import FlaskForm
from wtforms import widgets, StringField, validators, TextAreaField, IntegerField, RadioField, SelectField, \
	SelectMultipleField


class __Info:
	"""Used to include the age, gender and city fields."""

	__abstract__ = True

	birth_year = IntegerField("Syntymävuosi",
							  [validators.DataRequired(message="Syntymävuosi pitää antaa."), validators.NumberRange(
								  min=1900,
								  max=2000,
								  message="Syntymävuoden pitää olla väliltä 1900-2000.")
							   ])

	gender = RadioField("Sukupuoli",
						[validators.DataRequired(message="Sukupuoli pitää antaa tai valita tyhjä.")],
						choices=[('M', 'mies'), ('F', 'nainen'), ('-', '(ei määritelty)')])

	city_id = SelectField("Kunta", [validators.DataRequired(message="Virheellinen kunta.")], choices=[], coerce=int)

	seek = SelectMultipleField("Etsin täältä",
							   choices=[("friend", "ystävää"), ("penpal", "kirjekaveria"), ("parter", "kumppania"),
										("support", "vertaistukea"), ("other", "jotain muuta")],
							   widget=widgets.ListWidget(prefix_label=False),
							   option_widget=widgets.CheckboxInput())


class __TitleAndContent:
	"""This includes fields for the title and content of a profile."""

	__abstract__ = True

	title = StringField("Otsikko", [validators.Length(min=8,
													  max=64,
													  message="Otsikko on joko liian lyhyt tai liian pitkä.")])

	content = TextAreaField("Sisältö", [validators.Length(
		min=32,
		max=2048,
		message="Leipäteksti on joko liian lyhyt tai liian pitkä.")])


class ProfileCreateForm(FlaskForm, __TitleAndContent, __Info):
	"""Used to create a profile (not to be confused with creating an account)."""

	class Meta:
		csrf = True


class ProfileEditTextForm(FlaskForm, __TitleAndContent):
	"""If the user wants to edit the title and/or content of their profile."""

	class Meta:
		csrf = True


class ProfileEditInfoForm(FlaskForm, __Info):
	"""When the user wants to change their age, gender or location."""

	class Meta:
		csrf = True


class ProfileEditSeekForm(FlaskForm):
	seek = SelectMultipleField("Etsin täältä",
							   choices=[("friend", "ystävää"), ("penpal", "kirjekaveria"), ("parter", "kumppania"),
										("support", "vertaistukea"), ("other", "jotain muuta")],
							   widget=widgets.ListWidget(prefix_label=False),
							   option_widget=widgets.CheckboxInput())

	class Meta:
		csrf = True


class TagForm(FlaskForm):
	"""Used to add new tags that associate with the user's profile."""

	tag = StringField("Uusi merkki", [validators.Length(
		min=2,
		max=20,
		message="Merkki on joko liian lyhyt (alle 3 merkkiä) tai liian pitkä (yli 20 merkkiä).")])

	class Meta:
		csrf = True
