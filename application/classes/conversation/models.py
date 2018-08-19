from flask_login import current_user
from sqlalchemy import func, text, UniqueConstraint, CheckConstraint

from application import db


class Conversation(db.Model):
	__tablename__ = "Conversation"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	date_created = db.Column(db.DateTime, default=func.now(), server_default=func.now(), nullable=False)

	alpha = db.Column(db.Integer, db.ForeignKey("Profile.id"), nullable=False)
	beta = db.Column(db.Integer, db.ForeignKey("Profile.id"), nullable=False)

	__table_args__ = (db.UniqueConstraint("alpha", "beta"), db.CheckConstraint("beta > alpha"),)

	def __init__(self, alpha, beta):
		"""An alpha is always less than beta, and never equal."""
		self.alpha = alpha
		self.beta = beta

	@staticmethod
	def get_new_message_count():
		return {"count": "123"}

	@staticmethod
	def find_my_conversations():
		statement = text(
			'SELECT "Conversation".id AS "conversation_id", "Conversation".date_created AS "conversation_started", '
			'(SELECT LEFT(content, 32) FROM "Message" WHERE "Message".conversation_id = "Conversation".id ORDER BY date_created DESC LIMIT 1) AS "latest_message",'
			'(SELECT date_created FROM "Message" WHERE "Message".conversation_id = "Conversation".id ORDER BY date_created DESC LIMIT 1) AS "date_created",'
			'(SELECT handle FROM "Account" WHERE id=4) AS "alpha",'
			'(SELECT handle FROM "Account" WHERE id=3) AS "beta"'
			'FROM "Conversation" WHERE alpha=:id OR beta=:id;')

		connection = db.engine.connect()

		result_set = connection.execute(statement, id=current_user.id)

		response = []

		for row in result_set:
			alpha = row["alpha"]
			beta = row["beta"]

			if alpha == current_user.handle:
				other_profile = beta
			else:
				other_profile = alpha

			response.append(
				{"conversation_id": row["conversation_id"],
				 "date_created": row["date_created"],
				 "other_profile": other_profile,
				 "latest_message": row["latest_message"]})

		connection.close()

		return response

	@staticmethod
	def get_conversation(conversation_id):
		statement = text('SELECT id, date_created AS "sent", content, '
						 '(SELECT "Account".handle FROM "Account" WHERE "Account".id = "Message".source_id) AS "source", '
						 '(SELECT "Account".handle FROM "Account" WHERE "Account".id = "Message".target_id) AS "target"'
						 'FROM "Message" WHERE conversation_id = :conversation_id ORDER BY date_created ASC;')

		connection = db.engine.connect()

		result_set = connection.execute(statement, conversation_id=conversation_id)

		response = []

		for row in result_set:
			if row["source"] == current_user.handle:
				own_message = True
			else:
				own_message = False

			response.append(
				{"id": row["id"], "sent": row["sent"], "content": row["content"], "own_message": own_message})

		connection.close()

		return response

	@staticmethod
	def __get_date_string(datetime):
		return str(datetime.hour) + ":" + str(datetime.minute) + ":" + str(datetime.second) \
			   + " " + str(datetime.day) + "." + str(datetime.month) + "." + str(datetime.year)
