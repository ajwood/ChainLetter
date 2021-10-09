from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from .auth import login_required
from .models import db
from .models.hashchain import HashChain

bp = Blueprint('chainlink', __name__)

@bp.route("/")
def index():
    return render_template('chainlink/index.html')

@bp.route("/link/<sha256>")
def link(sha256):
    hc = HashChain.query.filter_by(sha256=sha256).first_or_404()
    return render_template(
        "chainlink/link.html",
        sha256=sha256,
        )
