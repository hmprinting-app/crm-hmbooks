from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Lead, STAGES

pipeline_bp = Blueprint('pipeline', __name__, url_prefix='/pipeline')

@pipeline_bp.route('/')
@login_required
def index():
    kanban = {}
    for s in STAGES:
        kanban[s] = Lead.query.filter_by(stage=s)\
                       .order_by(Lead.created_at.desc()).all()
    return render_template('pipeline/kanban.html', kanban=kanban, stages=STAGES)
