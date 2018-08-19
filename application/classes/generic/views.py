from flask import render_template

from application import app


@app.route("/terms", methods=["GET"])
def terms():
	return render_template("terms.html")
