from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Clé secrète pour les messages flash

db = SQLAlchemy(app)

# Modèles
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

# Création des tables dans la base de données
with app.app_context():
    db.create_all()

# Route pour la page d'accueil
@app.route('/')
def index():
    lots = Lot.query.all()
    return render_template('index.html', lots=lots)

# Route pour ajouter un nouveau lot
@app.route('/ajouter-lot', methods=['GET', 'POST'])
def ajouter_lot():
    if request.method == 'POST':
        print("POST request received") # Pour le débogage
        print(request.form) # Pour voir les données du formulaire
        lot = Lot(numero=Lot.get_next_numero())
        db.session.add(lot)
        db.session.flush()  # Pour obtenir l'ID du lot

        nom_edition = request.form.get('nom_edition')
        type_edition = request.form.get('type_edition')
        type_envoie = request.form.get('type_envoie')
        nombre_page_destinataire_str = request.form.get('nombre_page_destinataire')
        nombre_destinataires_str = request.form.get('nombre_destinataires')

        if not all([nom_edition, type_edition, type_envoie, nombre_page_destinataire_str, nombre_destinataires_str]):
            flash("Erreur: Tous les champs sont requis", 'error')
            return redirect(url_for('ajouter_lot'))

        try:
            nombre_page_destinataire = int(nombre_page_destinataire_str)
            nombre_destinataires = int(nombre_destinataires_str)
        except ValueError:
            flash("Erreur: Les valeurs numériques sont invalides", 'error')
            return redirect(url_for('ajouter_lot'))

        nombre_page = nombre_page_destinataire * nombre_destinataires

        entry = LotEntry(
            lot_id=lot.id,
            nom_edition=nom_edition,
            type_edition=type_edition,
            type_envoie=type_envoie,
            nombre_page_destinataire=nombre_page_destinataire,
            nombre_destinataires=nombre_destinataires,
            nombre_page=nombre_page
        )
        db.session.add(entry)

        try:
            db.session.commit()
            flash('Lot ajouté avec succès!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout du lot : {str(e)}", 'error')

    last_lot = Lot.query.order_by(Lot.id.desc()).first()
    return render_template('ajouter_lot.html', last_lot=last_lot)

if __name__ == '__main__':
    app.run(debug=True)