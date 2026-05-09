from flask import Blueprint, request, jsonify, current_app
from app.models import Lead, WAMessage
from app import db

webhooks_bp = Blueprint('webhooks', __name__, url_prefix='/webhooks')

@webhooks_bp.route('/wa-incoming', methods=['POST'])
def wa_incoming():
    """
    Fonnte webhook — menerima pesan WA masuk dari leads.
    Set di dashboard Fonnte: Webhook URL = https://domain.com/webhooks/wa-incoming
    """
    data   = request.get_json(silent=True) or request.form.to_dict()
    sender = str(data.get('sender', '')).strip()
    pesan  = str(data.get('message', '')).strip()

    if not sender or not pesan:
        return jsonify({'ok': False}), 400

    # Cari lead berdasarkan nomor WA
    no_wa_clean = sender.lstrip('+').lstrip('0')
    lead = Lead.query.filter(
        Lead.no_wa.contains(no_wa_clean[-8:])
    ).first()

    # Simpan pesan masuk
    msg = WAMessage(
        lead_id = lead.id if lead else None,
        arah    = 'in',
        pesan   = pesan,
    )
    db.session.add(msg)

    # Auto-create lead jika belum ada (CTWA baru)
    if not lead:
        from app.routes.leads import buat_jadwal_fu
        lead = Lead(nama=f'Lead {sender[-4:]}', no_wa=sender,
                    asal_iklan='CTWA - Meta Ads', catatan=pesan[:200])
        db.session.add(lead)
        db.session.flush()
        buat_jadwal_fu(lead)
        msg.lead_id = lead.id

    db.session.commit()
    return jsonify({'ok': True, 'lead_id': lead.id})
