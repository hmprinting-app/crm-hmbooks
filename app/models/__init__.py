from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime, date, timedelta
import bcrypt
import uuid

# ---------------------------------------------------------------------------
# User (admin)
# ---------------------------------------------------------------------------
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    email      = db.Column(db.String(150), unique=True, nullable=False)
    password   = db.Column(db.LargeBinary, nullable=False)
    role       = db.Column(db.String(20), default='admin')  # owner / admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw):
        self.password = bcrypt.hashpw(raw.encode(), bcrypt.gensalt())

    def check_password(self, raw):
        return bcrypt.checkpw(raw.encode(), self.password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------------------------
# Lead
# ---------------------------------------------------------------------------
STAGES = [
    'New Lead',
    'Qualify',
    'Paket Dipilih',
    'Invoice Terkirim',
    'DP Masuk',
    'Produksi',
    'Selesai',
    'Lost',
]

PAKET_HARGA = {
    'Esensial'   : 2750000,
    'Akademik'   : 3750000,
    'Guru Besar' : 5500000,
}

class Lead(db.Model):
    __tablename__ = 'leads'
    id             = db.Column(db.String(20), primary_key=True,
                                default=lambda: 'HMB-' + uuid.uuid4().hex[:6].upper())
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    nama           = db.Column(db.String(150), nullable=False)
    no_wa          = db.Column(db.String(20), nullable=False)
    asal_iklan     = db.Column(db.String(50), default='Meta Ads')
    jenis_naskah   = db.Column(db.String(80))          # Disertasi/Tesis/KTI/dll
    tujuan         = db.Column(db.String(80))          # BKD / Jabfung / Keduanya
    deadline_klien = db.Column(db.String(50))
    stage          = db.Column(db.String(30), default='New Lead')
    paket          = db.Column(db.String(30))          # Esensial/Akademik/Guru Besar
    harga          = db.Column(db.BigInteger, default=0)
    catatan        = db.Column(db.Text)
    pic_id         = db.Column(db.Integer, db.ForeignKey('users.id'))
    pic            = db.relationship('User', backref='leads')
    fu_records     = db.relationship('FollowUp', backref='lead',
                                     cascade='all, delete-orphan')

    @property
    def fu_berikutnya(self):
        pending = [f for f in self.fu_records if f.status == 'Pending']
        if not pending:
            return None
        return min(pending, key=lambda f: f.jadwal_kirim)

    @property
    def stage_index(self):
        try:
            return STAGES.index(self.stage)
        except ValueError:
            return 0


# ---------------------------------------------------------------------------
# Follow-up
# ---------------------------------------------------------------------------
FU_JADWAL = [0, 1, 2, 3, 5, 7]   # H+ hari

FU_TEMPLATES = {
    1: lambda nama: f"""Halo Bapak/Ibu {nama} 👋

Terima kasih sudah menghubungi *HM Books Pustaka*! Kami spesialis konversi disertasi/tesis/KTI menjadi buku ber-ISBN untuk keperluan BKD & jabfung.

Apakah naskah Bapak/Ibu sudah siap kami bantu proses? 😊

– Tim HM Books Pustaka""",

    2: lambda nama: f"""Halo Bapak/Ibu {nama} 😊

Semoga hari ini menyenangkan! Kami ingin memastikan apakah ada pertanyaan mengenai proses penerbitan buku ISBN dari naskah Bapak/Ibu.

Kami siap bantu jelaskan paket dan prosesnya. Kapan waktu yang nyaman untuk diskusi? 🙏

– HM Books Pustaka""",

    3: lambda nama: f"""Halo Bapak/Ibu {nama} 🌟

Info penting: deadline pengajuan BKD semester ini semakin dekat. Banyak dosen sudah memulai proses lebih awal agar buku selesai tepat waktu.

Paket kami:
✅ *Esensial* — Rp 2.750.000 (14 hari kerja)
✅ *Akademik* — Rp 3.750.000 (21 hari kerja) ⭐
✅ *Guru Besar* — Rp 5.500.000 (14 hari priority)

Mau kami bantu pilihkan paket yang paling sesuai? 😊""",

    4: lambda nama: f"""Halo Bapak/Ibu {nama},

Kami memahami kesibukan Bapak/Ibu sebagai akademisi. Jika ada keraguan atau pertanyaan seputar proses penerbitan, kami dengan senang hati menjawab.

Boleh kami tanyakan, jenis naskah apa yang ingin Bapak/Ibu terbitkan? 🙏""",

    5: lambda nama: f"""Halo Bapak/Ibu {nama} 👋

FYI — kami baru saja selesai membantu beberapa dosen menerbitkan disertasi dan tesis sebagai buku ber-ISBN. Prosesnya lancar dan hasilnya memuaskan 📚

Jika tertarik memulai, cukup kirimkan naskah dalam format Word dan kami langsung proses. Tidak perlu menunggu sempurna dulu!

Ada pertanyaan? 😊""",

    6: lambda nama: f"""Halo Bapak/Ibu {nama},

Ini pesan terakhir dari kami — kami tidak ingin mengganggu terlalu sering 🙏

Jika suatu saat membutuhkan layanan penerbitan buku ISBN, kami selalu siap membantu. Simpan nomor kami ya!

Semoga karir akademik Bapak/Ibu terus berkembang 🌟

– HM Books Pustaka""",
}

class FollowUp(db.Model):
    __tablename__ = 'followups'
    id           = db.Column(db.Integer, primary_key=True)
    lead_id      = db.Column(db.String(20), db.ForeignKey('leads.id'), nullable=False)
    fu_ke        = db.Column(db.Integer)          # 1-6
    jadwal_kirim = db.Column(db.Date, nullable=False)
    status       = db.Column(db.String(20), default='Pending')  # Pending/Terkirim/Dibatalkan
    pesan        = db.Column(db.Text)
    waktu_kirim  = db.Column(db.DateTime)

    @property
    def label_hari(self):
        idx = self.fu_ke - 1
        if 0 <= idx < len(FU_JADWAL):
            return f'H+{FU_JADWAL[idx]}'
        return f'FU-{self.fu_ke}'

    @property
    def terlambat(self):
        return self.status == 'Pending' and self.jadwal_kirim < date.today()


# ---------------------------------------------------------------------------
# WA Message log
# ---------------------------------------------------------------------------
class WAMessage(db.Model):
    __tablename__ = 'wa_messages'
    id         = db.Column(db.Integer, primary_key=True)
    lead_id    = db.Column(db.String(20), db.ForeignKey('leads.id'))
    arah       = db.Column(db.String(5))    # in / out
    pesan      = db.Column(db.Text)
    waktu      = db.Column(db.DateTime, default=datetime.utcnow)
    status     = db.Column(db.String(20), default='sent')
