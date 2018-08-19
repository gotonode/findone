from application import db
from application.models import Base
from sqlalchemy.sql import text


class Account(Base):
	"""Every authenticated user has an account, but not everyone has a profile."""

	__tablename__ = "Account"

	handle = db.Column(db.String(12), nullable=False, unique=True)

	email = db.Column(db.String(128), nullable=False, unique=True)
	password = db.Column(db.String(144), nullable=False)

	# Role can be (one of):
	#  - 'N' for normal user
	#  - 'M' for moderator
	#  - 'A' for administrator
	#
	# This defaults to 'N' (normal user).
	role = db.Column(db.CHAR(1), nullable=False, default='N', server_default='N')

	def __init__(self, email, handle, password):
		"""Creates a new account."""

		self.email = email
		self.handle = handle
		self.password = password

	def get_id(self):
		return self.id

	@staticmethod
	def is_active():
		return True

	@staticmethod
	def is_anonymous():
		return False

	@staticmethod
	def is_authenticated():
		return True

	def get_password(self):
		return self.password.decode('utf-8')

	@staticmethod
	def find_accounts_without_profiles():
		"""Finds accounts that do not have a profile."""

		# This database query could be simplified, but I'm learning how to use the HAVING statement.
		statement = text(
			'SELECT "Account".id, "Account".handle, "Account".email '
			'FROM "Account" '
			'LEFT JOIN "Profile" ON "Profile".id = "Account".id '
			'GROUP BY "Account".id HAVING COUNT("Profile".id) = 0;'
		)

		connection = db.engine.connect()

		result_set = connection.execute(statement)

		response = []

		for row in result_set:
			response.append({"id": row[0], "email": row[1], "handle": row[2]})

		connection.close()

		return response


class Login(db.Model):
	"""This table records all login events (successful or not)."""

	# Inheriting Base is not an option since this table never updates its rows.

	__tablename__ = "Login"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	date_created = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False)

	# Add db.ForeignKey("Account.id") in the future?
	account_id = db.Column(db.Integer, nullable=True)

	email = db.Column(db.String(128), nullable=True)

	successful = db.Column(db.Boolean, nullable=False)

	address = db.Column(db.String(128), nullable=False)
	user_agent = db.Column(db.String(256), nullable=False)  # Some User-Agent strings are quite long.

	def __init__(self, address, user_agent):
		"""When creating a login entry, the user's IP address and User-Agent are passed."""

		self.address = address
		self.user_agent = user_agent

	def success(self, account_id):
		"""Login succeeded."""

		self.successful = True
		self.account_id = account_id  # On a successful login, we store the account's ID.

	def failure(self, email):
		""""Login was a failure."""

		self.successful = False
		self.email = email  # On a failed login, we store the email address used.
