from flask import (
    Blueprint,
    abort,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for,
    jsonify,
)
from sqlalchemy import exc
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

    try:
        # query as a prefix, which allows us to access with a partial hash
        hc = HashChain.query.filter(HashChain.sha256.like(f"{sha256}%")).one()
    except exc.NoResultFound:
        flash("Your hash doesn't exist in the system!")
        return render_template("base.html")
    except exc.MultipleResultsFound:
        flash("Your hash needs more characters to find a unique hit!")
        return render_template("base.html")

    # If the letter hasn't been written yet
    if hc.letter is None:
        if g.user and g.user.sha256 == sha256:
            # If the user logged in under this hash, let them fill it
            return redirect(url_for("chainlink.fill", sha256=sha256))
        else:
            # Else it's an error
            flash("This hash is initialized, but its letter hasn't been filled yet!")

    # If the user is logged in and this is their hash, exposed the full bit
    # depth of it and its neighbours.
    parent = hc.parent.shart256
    if g.user and g.user.sha256.startswith(sha256):
        sha256 = g.user.sha256 # fill out the whole hash
        children = [child.sha256 for child in hc.children]
    else:
        children = [child.shart256 for child in hc.children]

    return render_template(
        "chainlink/view.html",
        parent=parent,
        children=children,
        sha256=sha256,
        letter=hc.letter,
    )


@bp.route("/fill/<sha256>", methods=("GET", "POST"))
def fill(sha256):
    """Fill a pending link"""
    hc = HashChain.query.filter_by(sha256=sha256).first_or_404()
    l = Letter.query.filter_by(hashchain_id=hc.id).one_or_none()

    # Starting values for the page's inputs. This is mainly used for error
    # handling, if a submission goes bad, the user doesn't lose their entered
    # text (there is probably a better way to achieve this)
    input_vals = {}

    if l is not None:
        # If the letter already exists, redirect to its view page
        flash("This hash is already filled!")
        return redirect(url_for("chainlink.view", sha256=sha256))
    elif request.method == "POST":
        error = None

        # resolve the veteran_id, if there is one
        if not request.form["veteran-hash"]:
            v_id = None
        else:
            v = HashChain.query.filter_by(sha256=request.form["veteran-hash"]).one_or_none()
            if v is None:
                error = "Your veteran hash could not be found in the system!"
            else:
                v_id = v.id

        # Report the error, or proceed with the new record
        if error:
            flash(error)
            input_vals |= request.form
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
            db.session.commit()

            return redirect(url_for("chainlink.view", sha256=sha256))

    return render_template("chainlink/fill.html", letter=hc.letter, **input_vals)

@bp.route("/api/make_child/<sha256>", methods=["POST"])
def api_make_child(sha256):
    """Create a new new child off the given hash"""

    hc = HashChain.query.filter_by(sha256=sha256).first_or_404()
    if hc.nchildren >= HashChain.MAX_DEGREE:
        return "<li>you have maxed out the number of child hashes!</li>"
    else:
        newhash = hc.make_child().sha256
        db.session.commit()
        return f"<li><a href='/view/{newhash}'>{newhash}</a></li>"