from sqlalchemy import func

from application import db


class Block(db.Model):
	__tablename__ = "Block"

	source_id = db.Column(db.Integer, db.ForeignKey("Profile.id"), nullable=False)
	target_id = db.Column(db.Integer, db.ForeignKey("Profile.id"), nullable=False)

	date_created = db.Column(db.DateTime, default=func.now(), server_default=func.now(), nullable=False)

	__table_args__ = (db.PrimaryKeyConstraint("source_id", "target_id"),
					  db.CheckConstraint("source_id != target_id"),)  # Can't block oneself.

	def __init__(self, source_id, target_id):
		self.source_id = source_id
		self.target_id = target_id
