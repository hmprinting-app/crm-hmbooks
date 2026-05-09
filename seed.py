"""
Jalankan SEKALI di Railway Shell setelah deploy:
    python seed.py
"""
from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()

    if not User.query.filter_by(email='admin@hmbooks.id').first():
        u = User(name='Admin HM Books', email='admin@hmbooks.id', role='owner')
        u.set_password('hmbooks2026')
        db.session.add(u)
        db.session.commit()
        print('✅ Admin user dibuat: admin@hmbooks.id / hmbooks2026')
    else:
        print('ℹ️  Admin sudah ada.')
    print('✅ Seed selesai.')
