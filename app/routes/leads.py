from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from app.models import Lead, FollowUp, STAGES, PAKET_HARGA, FU_JADWAL, FU_TEMPLATES
from app import db
from datetime import date, timedelta

leads_bp = Blueprint('leads', __name__, url_prefix='/leads')

def buat_jadwal_fu(lead):
    """Generate 6 FU records untuk lead baru."""
    for i, hari in enumerate(FU_JADWAL):
        fu_ke   = i + 1
        jadwal  = date.today() + timedelta(days=hari)
        pesan   = FU_TEMPLATES[fu_ke](lead.nama)
        fu = FollowUp(lead_id=lead.id, fu_ke=fu_ke,
                      jadwal_kirim=jadwal, pesan=pesan)
        db.session.add(fu)

@leads_bp.route('/')
@login_required
def index():
    stage_filter = request.args.get('stage', '')
    q            = request.args.get('q', '')
    query        = Lead.query
    if stage_filter:
        query = query.filter_by(stage=stage_filter)
    if q:
        query = query.filter(
            (Lead.nama.ilike(f'%{q}%')) | (Lead.no_wa.ilike(f'%{q}%'))
        )
    leads = query.order_by(Lead.created_at.desc()).all()
    return render_template('leads/index.html',
                           leads=leads, stages=STAGES,
                           stage_filter=stage_filter, q=q)

@leads_bp.route('/tambah', methods=['GET', 'POST'])
@login_required
def tambah():
    if request.method == 'POST':
        paket = request.form.get('paket', '')
        harga = PAKET_HARGA.get(paket, 0)
        lead  = Lead(
            nama           = request.form.get('nama', '').strip(),
            no_wa          = request.form.get('no_wa', '').strip(),
            asal_iklan     = request.form.get('asal_iklan', 'Meta Ads'),
            jenis_naskah   = request.form.get('jenis_naskah', ''),
            tujuan         = request.form.get('tujuan', ''),
            deadline_klien = request.form.get('deadline_klien', ''),
            paket          = paket,
            harga          = harga,
            catatan        = request.form.get('catatan', ''),
            pic_id         = current_user.id,
        )
        db.session.add(lead)
        db.session.flush()   # get lead.id before commit
        buat_jadwal_fu(lead)
        db.session.commit()
        flash(f'Lead {lead.nama} ({lead.id}) berhasil ditambahkan. FU H+0 s/d H+7 sudah dijadwalkan.', 'success')
        return redirect(url_for('leads.detail', lead_id=lead.id))
    return render_template('leads/tambah.html', stages=STAGES, paket_list=list(PAKET_HARGA.keys()))

@leads_bp.route('/<lead_id>')
@login_required
def detail(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    return render_template('leads/detail.html', lead=lead, stages=STAGES,
                           paket_list=list(PAKET_HARGA.keys()),
                           paket_harga=PAKET_HARGA)

@leads_bp.route('/<lead_id>/update-stage', methods=['POST'])
@login_required
def update_stage(lead_id):
    lead  = Lead.query.get_or_404(lead_id)
    stage = request.form.get('stage')
    if stage in STAGES:
        lead.stage = stage
        if stage in ('Selesai', 'Lost'):
            for fu in lead.fu_records:
                if fu.status == 'Pending':
                    fu.status = 'Dibatalkan'
        if stage == 'Paket Dipilih':
            paket = request.form.get('paket', lead.paket)
            if paket:
                lead.paket = paket
                lead.harga = PAKET_HARGA.get(paket, lead.harga)
        db.session.commit()
        flash(f'Stage diupdate ke {stage}.', 'success')
    return redirect(url_for('leads.detail', lead_id=lead_id))

@leads_bp.route('/<lead_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    if request.method == 'POST':
        lead.nama           = request.form.get('nama', lead.nama).strip()
        lead.no_wa          = request.form.get('no_wa', lead.no_wa).strip()
        lead.asal_iklan     = request.form.get('asal_iklan', lead.asal_iklan)
        lead.jenis_naskah   = request.form.get('jenis_naskah', lead.jenis_naskah)
        lead.tujuan         = request.form.get('tujuan', lead.tujuan)
        lead.deadline_klien = request.form.get('deadline_klien', lead.deadline_klien)
        lead.catatan        = request.form.get('catatan', lead.catatan)
        paket = request.form.get('paket', lead.paket)
        if paket != lead.paket:
            lead.paket = paket
            lead.harga = PAKET_HARGA.get(paket, 0)
        db.session.commit()
        flash('Data lead berhasil diupdate.', 'success')
        return redirect(url_for('leads.detail', lead_id=lead_id))
    return render_template('leads/edit.html', lead=lead,
                           paket_list=list(PAKET_HARGA.keys()))
