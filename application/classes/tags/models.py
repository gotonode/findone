from application import db
from sqlalchemy import PrimaryKeyConstraint, text
from sqlalchemy.sql import func


class Tag(db.Model):
	"""The structure used for the tags.
	Inheriting Base is not an option here since not all fields would be used.
	"""

	__tablename__ = "Tag"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	date_created = db.Column(db.DateTime, default=func.now(), server_default=func.now(), nullable=False)
	name = db.Column(db.String(32), nullable=False)

	tags = db.relationship("Profile_Tag", backref="Tag", lazy=True)

	def __init__(self, name):
		"""When a new tag is born, it is given a name. The name must be globally-unique."""

		self.name = name

	@staticmethod
	def get_tags_with_use_count(limit=50):
		"""Returns up to "limit" tags, with their ID's, names and how
		many times each of them have been associated to a profile.
		"""

		# This method returns a list containing each tag and how many times it has been applied (used).
		# Unused tags are listed as well since this function is used for different tasks.
		# By default, only the first 50 entries are given.

		statement = 'SELECT "Tag".id, "Tag".name, ' \
					'(SELECT COUNT("Profile_Tag".tag_id) FROM "Profile_Tag" ' \
					'WHERE "Profile_Tag".tag_id = "Tag".id) AS "count" ' \
					'FROM "Tag" ORDER BY "count" DESC'

		if limit:
			# If limit is not None (null), we'll add it here.
			statement = statement + " LIMIT :limit"

		statement = text(statement)

		connection = db.engine.connect()

		result_set = connection.execute(statement, limit=limit)

		response = []

		for row in result_set:
			response.append({"id": row[0], "name": row[1], "count": row[2]})

		connection.close()

		return response


class Profile_Tag(db.Model):
	"""The connection table, connecting Tag and Profile tables together."""

	__tablename__ = "Profile_Tag"

	profile_id = db.Column(db.Integer, db.ForeignKey("Profile.id"), nullable=False)
	tag_id = db.Column(db.Integer, db.ForeignKey("Tag.id"), nullable=False)

	# This timestamp might get removed at some point. Currently it is for statistics.
	# It's easy to imagine this table getting quite large (size-wise).
	date_created = db.Column(db.DateTime, default=func.now(), server_default=func.now(), nullable=False)

	# This table has a primary key consisting of the ID's of its parts ("profile_id" and "tag_id"),
	# meaning that a single tag can only be associated with a single profile once.
	__table_args__ = (PrimaryKeyConstraint("profile_id", "tag_id"), {},)

	def __init__(self, profile_id, tag_id):
		"""To attach a Tag to a Profile, it is done via this table.
		Both the profile's ID and the tag's ID must be given.
		"""

		self.profile_id = profile_id
		self.tag_id = tag_id
