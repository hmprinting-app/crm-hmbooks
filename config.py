import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'hmbooks-crm-dev-secret-2026')
    raw_db = os.environ.get('DATABASE_URL', 'sqlite:///hmbooks.db')
    SQLALCHEMY_DATABASE_URI = raw_db.replace('postgres://', 'postgresql://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FONNTE_TOKEN   = os.environ.get('FONNTE_TOKEN', '')
    FONNTE_API_URL = 'https://api.fonnte.com'
    WA_NUMBER      = os.environ.get('WA_NUMBER', '')
    ANTHROPIC_KEY  = os.environ.get('ANTHROPIC_API_KEY', '')
