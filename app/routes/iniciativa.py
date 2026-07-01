from flask import Blueprint, render_template

iniciativa_bp = Blueprint('iniciativa', __name__)


@iniciativa_bp.route('/iniciativa')
def iniciativa():
    """Render the initiative information page."""
    return render_template('iniciativa.html')
