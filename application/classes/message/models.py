from flask_login import current_user
from sqlalchemy import func

from application import db
from sqlalchemy.sql import text


class Message(db.Model):

	__tablename__ = "Message"

	id = db.Column(db.Integer, primary_key=True, autoincrement=True)

	conversation_id = db.Column(db.Integer, db.ForeignKey("Conversation.id"), nullable=False)

	source_id = db.Column(db.Integer, db.ForeignKey("Profile.id"), nullable=False)
	target_id = db.Column(db.Integer, db.ForeignKey("Profile.id"), nullable=False)

	date_created = db.Column(db.DateTime, default=func.now(), server_default=func.now(), nullable=False)

	content = db.Column(db.String(1024), nullable=False)

	has_source_deleted = db.Column(db.Boolean, default=False, server_default='f', nullable=False)
	has_target_deleted = db.Column(db.Boolean, default=False, server_default='f', nullable=False)

	read = db.Column(db.Boolean, default=False, server_default='f', nullable=False)

	__table_args__ = (db.CheckConstraint("source_id != target_id"),)  # Can't send a message to oneself.

	def __init__(self, conversation_id, source_id, target_id, content):
		self.conversation_id = conversation_id
		self.source_id = source_id
		self.target_id = target_id
		self.content = content

	@staticmethod
	def get_latest_message_in_conversation(conversation_id):
		statement = text('SELECT * FROM "Message" WHERE conversation_id=:conversation_id ORDER BY date_created DESC LIMIT 1;')

		connection = db.engine.connect()

		result_set = connection.execute(statement, conversation_id=conversation_id)

		response = []

		for row in result_set:

			own_message = False
			if row[2] == current_user.id:
				own_message = True

			response.append({"date_created": row[4], "content": row[5], "own_message": own_message})

		connection.close()

		return response[0]
