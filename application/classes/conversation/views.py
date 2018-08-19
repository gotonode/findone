from flask import render_template, jsonify, abort, request, redirect
from flask_login import current_user

from application import app, login_required_with_role, Role, db
from application.classes.conversation.models import Conversation
from application.classes.message.forms import MessageForm
from application.classes.message.models import Message


@app.route("/conversation/message_count.json", methods=["GET"])
@login_required_with_role(Role.Normal)
def conversations_get_new_message_count():
	new_message_count = Conversation.get_new_message_count()

	return jsonify(new_message_count)


@app.route("/conversations", methods=["GET"])
@login_required_with_role(Role.Normal)
def conversations_view():
	"""Returns the conversations view."""

	form = MessageForm()

	return render_template("conversation/list.html", form=form)


@app.route("/conversations/send", methods=["POST"])
@login_required_with_role(Role.Normal)
def message_send():
	form = MessageForm(request.form)

	if not form.validate():
		return render_template("error.html", errors=form.errors.values())

	target_id = form.target_id.data

	if target_id == current_user.id:
		# Cannot (and should not) send a message to self.
		abort(500)

	content = form.message.data.strip()

	if target_id > current_user.id:
		alpha = current_user.id
		beta = target_id
	elif target_id < current_user.id:
		alpha = target_id
		beta = current_user.id
	else:
		alpha = None
		beta = None
		# The two above cases are purely for the IDE.
		abort(500)

	conversation = Conversation.query.filter_by(alpha=alpha, beta=beta).first()

	if conversation:
		conversation_id = conversation.id
	else:
		new_conversation = Conversation(alpha=alpha, beta=beta)
		db.session().add(new_conversation)
		db.session().commit()
		conversation_id = Conversation.query.filter_by(alpha=alpha, beta=beta).first().id

	message = Message(conversation_id=conversation_id, source_id=current_user.id, target_id=target_id, content=content)

	db.session().add(message)
	db.session().commit()

	return redirect(request.referrer)


# return Response("ok", status=201, mimetype='application/json')


@app.route("/conversations/all.json", methods=["GET"])
@login_required_with_role(Role.Normal)
def conversations_get_json():
	conversations = Conversation.find_my_conversations()

	return jsonify(conversations)


@app.route("/conversation/id/<conversation_id>", methods=["GET"])
@login_required_with_role(Role.Normal)
def conversation_view_one(conversation_id):
	"""View a single conversation (between profiles A and B)."""

	conversation_check = Conversation.query.filter_by(id=conversation_id).first()

	# This checks to see if the current user is taking part in the conversation he/she
	# is requesting. You're only allowed to see your own conversations.
	if conversation_check.alpha != current_user.id and conversation_check.beta != current_user.id:
		abort(403)

	# TODO: Check that a conversation has a message and that the message in question hasn't been removed by the current user.

	conversation = Conversation.get_conversation(conversation_id)

	return jsonify(conversation)
