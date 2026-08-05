"""Blueprint de la iniciativa."""
from flask import Blueprint, render_template

iniciativa_bp = Blueprint("iniciativa", __name__)


@iniciativa_bp.route("/iniciativa")
def iniciativa():
    """Página sobre la iniciativa."""
    return render_template("iniciativa.html")
