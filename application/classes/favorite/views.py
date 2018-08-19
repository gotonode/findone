from flask import request, render_template
from flask_login import current_user

from application import app, login_required_with_role, Role
from application.classes.favorite.forms import FavoriteForm


@app.route("/profile/favorite/add", methods=["POST"])
@login_required_with_role(Role.Normal)
def add_favorite():
	form = FavoriteForm(request.form)

	source_id = int(current_user.id)
	target_id = int(form.target_id.data)

	if source_id == target_id:
		return render_template("error.html", errors=["Et voi lisätä itseäsi suosikkeihin."])
