from flask import render_template, url_for, redirect, request
from application import login_required_with_role, db

from application import app, Role
from application.classes.account.models import Account, Login

from application.classes.tags.models import Tag, Profile_Tag


@app.route("/admin", methods=["GET"])
@login_required_with_role(Role.Admin)  # Requires an admin (administrator) account type.
def admin():
	"""Admin panel for viewing login events."""

	accounts = Account.find_accounts_without_profiles()
	return render_template("admin/admin.html", accounts=accounts, logins=Login.query.all())


@app.route("/mod", methods=["GET"])
@login_required_with_role(Role.Mod)  # Requires a mod (moderator) account type.
def mod():
	"""Mod panel for removing inappropriate tags."""

	tags = Tag.get_tags_with_use_count()
	return render_template("admin/mod.html", tags=tags)


@app.route("/mod/tag/delete", methods=["POST"])
@login_required_with_role(Role.Mod)
def mod_delete_tag():
	"""Mod is deleting a tag."""

	tag_id = request.form["tag_id"]

	tag = Tag.query.filter_by(id=tag_id).first()

	# Delete all tag associations (from table Profile_Tag) first.
	Profile_Tag.query.filter_by(tag_id=tag.id).delete()

	# And then delete the tag from the database completely.
	db.session().delete(tag)

	# Commit to these changes.
	db.session().commit()

	return redirect(url_for("mod"))
