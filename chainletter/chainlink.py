from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)
from sqlalchemy.sql.selectable import HasSuffixes
from werkzeug.exceptions import abort

from .auth import login_required
from .models import db
from .models.hashchain import HashChain
from .models.letter import Letter
from chainletter.models import hashchain

bp = Blueprint("chainlink", __name__)


@bp.route("/")
def index():
    return render_template("chainlink/index.html")


@bp.route("/view/<sha256>")
def view(sha256):
    """Browse a filled link"""
    hc = HashChain.query.filter_by(sha256=sha256).first_or_404()

    # If the letter hasn't been written yet
    if hc.letter is None:
        if g.user and g.user.sha256 == sha256:
            # If the user logged in under this hash, let them fill it
            return redirect(url_for("chainlink.fill", sha256=sha256))
        else:
            # Else it's an error
            flash(
                "This hash is initialized, but its letter hasn't been filled yet!"
            )

    return render_template("chainlink/view.html", sha256=sha256, hc=hc)


@bp.route("/fill/<sha256>", methods=("GET", "POST"))
def fill(sha256):
    """Fill a pending link"""
    hc = HashChain.query.filter_by(sha256=sha256).first_or_404()
    l = Letter.query.filter_by(hashchain_id=hc.id).one_or_none()
    if l is not None:
        # If the letter already exists, redirect to its view page
        return redirect(url_for("chainlink.view", sha256=sha256))
    elif request.method == "POST":
        error = None

        # resolve the veteran_id, if there is one
        if not request.form["veteran-hash"]:
            v_id = None
        else:
            v = HashChain.query.filter_by(sha256=sha256).one_or_none()
            if v is None:
                error = "Your veteran hash could not be found in the system!"
            else:
                v_id = v.id

        # Report the error, or proceed with the new record
        if error:
            flash(error)
        else:
            l = Letter(
                hc.id,
                request.remote_addr,
                request.form["username"],
                request.form["home"],
                request.form["message"],
                v_id,
            )

            db.session.add(l)
            hc.make_child()
            db.session.commit()

            return redirect(url_for("chainlink.view", sha256=sha256))

    return render_template("chainlink/fill.html", letter=hc.letter)
