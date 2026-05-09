from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models import Lead, FollowUp, STAGES
from app import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/leads/stage-counts')
@login_required
def stage_counts():
    counts = {s: Lead.query.filter_by(stage=s).count() for s in STAGES}
    return jsonify(counts)

@api_bp.route('/leads/<lead_id>/move', methods=['POST'])
@login_required
def move_stage(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    data = request.get_json()
    new_stage = data.get('stage')
    if new_stage in STAGES:
        lead.stage = new_stage
        if new_stage in ('Selesai', 'Lost'):
            for fu in lead.fu_records:
                if fu.status == 'Pending':
                    fu.status = 'Dibatalkan'
        db.session.commit()
        return jsonify({'ok': True, 'stage': lead.stage})
    return jsonify({'ok': False, 'error': 'Invalid stage'}), 400
