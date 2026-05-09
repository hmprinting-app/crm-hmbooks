from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from app.models import FollowUp, Lead
from app import db
from datetime import date
import requests as req

followup_bp = Blueprint('followup', __name__, url_prefix='/followup')

def kirim_fonnte(no_wa, pesan):
    token = current_app.config.get('FONNTE_TOKEN', '')
    if not token:
        return False, 'FONNTE_TOKEN tidak dikonfigurasi'
    try:
        r = req.post(
            'https://api.fonnte.com/send',
            headers={'Authorization': token},
            json={'target': no_wa, 'message': pesan, 'countryCode': '62'},
            timeout=10
        )
        data = r.json()
        return data.get('status') is True, data.get('reason', '')
    except Exception as e:
        return False, str(e)

@followup_bp.route('/')
@login_required
def index():
    hari_ini  = date.today()
    pending   = FollowUp.query\
                .filter(FollowUp.jadwal_kirim <= hari_ini,
                        FollowUp.status == 'Pending')\
                .order_by(FollowUp.jadwal_kirim).all()
    mendatang = FollowUp.query\
                .filter(FollowUp.jadwal_kirim > hari_ini,
                        FollowUp.status == 'Pending')\
                .order_by(FollowUp.jadwal_kirim).limit(20).all()
    return render_template('followup/index.html',
                           pending=pending, mendatang=mendatang, hari_ini=hari_ini)

@followup_bp.route('/<int:fu_id>/kirim', methods=['POST'])
@login_required
def kirim(fu_id):
    fu   = FollowUp.query.get_or_404(fu_id)
    lead = fu.lead
    sukses, pesan_err = kirim_fonnte(lead.no_wa, fu.pesan)
    if sukses:
        from datetime import datetime
        fu.status      = 'Terkirim'
        fu.waktu_kirim = datetime.utcnow()
        db.session.commit()
        flash(f'FU-{fu.fu_ke} ke {lead.nama} berhasil dikirim via WA.', 'success')
    else:
        flash(f'Gagal kirim: {pesan_err}', 'error')
    return redirect(url_for('followup.index'))

@followup_bp.route('/<int:fu_id>/batalkan', methods=['POST'])
@login_required
def batalkan(fu_id):
    fu = FollowUp.query.get_or_404(fu_id)
    fu.status = 'Dibatalkan'
    db.session.commit()
    flash('FU dibatalkan.', 'success')
    return redirect(url_for('followup.index'))

@followup_bp.route('/blast-hari-ini', methods=['POST'])
@login_required
def blast_hari_ini():
    hari_ini = date.today()
    pending  = FollowUp.query.filter(
                   FollowUp.jadwal_kirim == hari_ini,
                   FollowUp.status == 'Pending').all()
    berhasil = gagal = 0
    from datetime import datetime
    for fu in pending:
        sukses, _ = kirim_fonnte(fu.lead.no_wa, fu.pesan)
        if sukses:
            fu.status      = 'Terkirim'
            fu.waktu_kirim = datetime.utcnow()
            berhasil += 1
        else:
            gagal += 1
    db.session.commit()
    flash(f'Blast selesai: {berhasil} terkirim, {gagal} gagal.', 'success')
    return redirect(url_for('followup.index'))
