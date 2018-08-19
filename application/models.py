from application import db


class Base(db.Model):
	"""Used as an abstract class with other forms that need all three
	(id, date_created, date_modified) fields.
	"""

	__abstract__ = True

	id = db.Column(db.Integer, primary_key=True)

	date_created = db.Column(db.DateTime,
							 default=db.func.current_timestamp(),
							 server_default=db.func.current_timestamp())
	date_modified = db.Column(db.DateTime,
							  default=db.func.current_timestamp(),
							  server_default=db.func.current_timestamp(),
							  onupdate=db.func.current_timestamp())
