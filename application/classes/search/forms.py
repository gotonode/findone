from flask_wtf import FlaskForm
from wtforms import validators, IntegerField, RadioField, SelectField, StringField


class SearchForm(FlaskForm):
	min_age = IntegerField("Ikä (alaraja)",
						   [validators.NumberRange(min=18, max=100, message="Iän pitää olla väliltä 18-100.")])

	max_age = IntegerField("Ikä (yläraja)",
						   [validators.NumberRange(min=18, max=100, message="Iän pitää olla väliltä 18-100.")])

	gender = RadioField("Sukupuoli",
						[validators.DataRequired(message="Sukupuoli pitää antaa tai valita tyhjä.")],
						choices=[('all', 'kaikki'), ('women', 'naiset'), ('men', 'miehet')], default='-')

	city_id = SelectField("Kunta", [validators.DataRequired(message="Virheellinen kunta.")], choices=[], coerce=int)

	tag = StringField("Merkki")

	class Meta:
		csrf = False
