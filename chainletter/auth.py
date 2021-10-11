import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

from .models.hashchain import HashChain

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        sha256 = request.form["sha256"]
        error = None
        hc = HashChain.query.filter_by(sha256=sha256).one_or_none()

        if hc is None:
            flash("Unknown hash.")
        else:
            session.clear()
            session["sha256"] = hc.sha256
            return redirect(url_for("chainlink.view", sha256=sha256))

    return render_template("auth/login.html")


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    sha256 = session.get("sha256")

    if sha256 is None:
        g.user = None
    else:
        hc = HashChain.query.filter_by(sha256=sha256).one_or_none()
        if hc is None:
            g.user = None
        else:
            g.user = hc.sha256


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
