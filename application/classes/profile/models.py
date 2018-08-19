from datetime import datetime
from sqlalchemy import text

from application import db

from application.models import Base


class Profile(Base):
	"""
	Not every account has a profile (such as those who have been banned
	and accounts for tasks such as administration and moderation).
	"""

	__tablename__ = "Profile"

	title = db.Column(db.String(64), nullable=False)
	content = db.Column(db.String(2048), nullable=False)

	birth_year = db.Column(db.Integer(), nullable=True)  # From 1900 to (current_year() - 18) or null.
	gender = db.Column(db.CHAR(1), nullable=True)  # Male ('M'), female ('F') or null.

	city_id = db.Column(db.Integer, db.ForeignKey("City.id"), nullable=True)  # The city's ID or null.

	seek_partner = db.Column(db.Boolean, default=False, server_default='f', nullable=False)
	seek_penpal = db.Column(db.Boolean, default=False, server_default='f', nullable=False)
	seek_other = db.Column(db.Boolean, default=False, server_default='f', nullable=False)
	seek_friend = db.Column(db.Boolean, default=False, server_default='f', nullable=False)
	seek_support = db.Column(db.Boolean, default=False, server_default='f', nullable=False)

	tags = db.relationship("Profile_Tag", backref="Profile", lazy=True)

	def __init__(self, account_id, title, content, birth_year, gender, city_id):
		"""When creating a new profile, almost all of the profile information must be given."""

		self.id = account_id  # Always the same as "Account.id".
		self.title = title
		self.content = content
		self.birth_year = birth_year
		self.gender = gender
		self.city_id = city_id

	@staticmethod
	def find_profiles_which_have_tag(tag_id):
		"""Used to find all profiles that have a specific tag associated with them."""

		# This is a rather complex query, but I managed to do everything necessary in only one.
		statement = text(
			'SELECT "Account".handle, "Profile".birth_year, "Profile".gender, "City".name AS "city", "Profile".title '
			'FROM "Profile" '
			'LEFT JOIN "Account" ON "Account".id = "Profile".id '
			'LEFT JOIN "City" ON "City".id = "Profile".city_id '
			'LEFT JOIN "Profile_Tag" ON "Profile_Tag".profile_id = "Profile".id '
			'GROUP BY "Profile".birth_year, "Account".handle, "Profile".gender, "City".name, "Profile_Tag".tag_id, "Profile".title '
			'HAVING "Profile_Tag".tag_id = :tag_id;')

		connection = db.engine.connect()

		result_set = connection.execute(statement, tag_id=tag_id)

		users = Profile.__construct_users(result_set)

		connection.close()

		return users

	@staticmethod
	def find_random_profiles():
		statement = text(
			'SELECT "Account".handle, "Profile".birth_year, "Profile".gender, "City".name AS "city", "Profile".title '
			'FROM "Profile" '
			'LEFT JOIN "Account" ON "Account".id = "Profile".id '
			'LEFT JOIN "City" ON "City".id = "Profile".city_id '
			'LEFT JOIN "Profile_Tag" ON "Profile_Tag".profile_id = "Profile".id '
			'GROUP BY "Profile".birth_year, "Account".handle, "Profile".gender, "City".name, "Profile".title '
			'ORDER BY random() LIMIT 9;')

		connection = db.engine.connect()

		result_set = connection.execute(statement)

		users = Profile.__construct_users(result_set)

		connection.close()

		return users

	@staticmethod
	def __construct_users(result_set):
		response = []

		for row in result_set:
			details = ""

			if row[1]:
				age = datetime.now().year - int(row[1])

				details = "~" + str(age) + " vuotta"
			else:
				age = None

			if row[2] == "M":
				gender = "mies"
			elif row[2] == "F":
				gender = "nainen"
			else:
				gender = None

			if gender:
				if len(details) > 0:
					details += ", "
				details += gender

			if row[3]:
				if len(details) > 0:
					details += ", "
				details += row[3]

			if not details:
				details = "(ei lisätietoja)"

			response.append(
				{"handle": row[0], "birth_year": row[1], "gender": gender, "city": row[3], "age": age, "title": row[4],
				 "details": details})

		return response


class City(db.Model):
	"""A simple structure to store cities name's."""

	__tablename__ = "City"

	# Cities are not added manually after the initial import, so no auto-increment needed.
	id = db.Column(db.Integer, primary_key=True, autoincrement=False)
	name = db.Column(db.String(128), nullable=False, unique=True)

	def __init__(self, name):
		self.name = name
