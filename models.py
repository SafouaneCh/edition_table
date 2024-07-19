# models.py
from extensions import db
from datetime import datetime
from sqlalchemy import func

class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(50), unique=True, nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    entries = db.relationship('LotEntry', backref='lot', lazy='dynamic')

    @classmethod
    def get_next_numero(cls):
        max_numero = db.session.query(func.max(cls.numero)).scalar()
        if max_numero:
            # Assuming the format is 'LOT-XXXXXX'
            max_num = int(max_numero.split('-')[1])
            next_num = max_num + 1
        else:
            next_num = 1
        return f'LOT-{next_num:06d}'

class LotEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    nom_edition = db.Column(db.String(200), nullable=False)
    type_edition = db.Column(db.String(20), nullable=False)
    type_envoie = db.Column(db.String(100), nullable=False)
    nombre_page_destinataire = db.Column(db.Integer, nullable=False)
    nombre_destinataires = db.Column(db.Integer, nullable=False)
    nombre_page = db.Column(db.Integer, nullable=False)