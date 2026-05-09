from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Lead, FollowUp, STAGES
from app import db
from datetime import date
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    total_leads   = Lead.query.count()
    selesai       = Lead.query.filter_by(stage='Selesai').count()
    conv_rate     = round(selesai / total_leads * 100) if total_leads else 0

    revenue_done  = db.session.query(func.sum(Lead.harga))\
                    .filter(Lead.stage == 'Selesai').scalar() or 0
    revenue_pipe  = db.session.query(func.sum(Lead.harga))\
                    .filter(Lead.stage.notin_(['Selesai', 'Lost', 'New Lead'])).scalar() or 0

    fu_hari_ini   = FollowUp.query.filter(
                        FollowUp.jadwal_kirim == date.today(),
                        FollowUp.status == 'Pending').count()
    fu_terlambat  = FollowUp.query.filter(
                        FollowUp.jadwal_kirim < date.today(),
                        FollowUp.status == 'Pending').count()

    stage_counts  = {}
    for s in STAGES:
        stage_counts[s] = Lead.query.filter_by(stage=s).count()

    recent_leads  = Lead.query.order_by(Lead.created_at.desc()).limit(10).all()

    fu_pending    = FollowUp.query\
                    .filter(FollowUp.jadwal_kirim <= date.today(),
                            FollowUp.status == 'Pending')\
                    .order_by(FollowUp.jadwal_kirim).limit(10).all()

    return render_template('dashboard/index.html',
        total_leads   = total_leads,
        conv_rate     = conv_rate,
        revenue_done  = revenue_done,
        revenue_pipe  = revenue_pipe,
        fu_hari_ini   = fu_hari_ini,
        fu_terlambat  = fu_terlambat,
        stage_counts  = stage_counts,
        recent_leads  = recent_leads,
        fu_pending    = fu_pending,
        stages        = STAGES,
    )
