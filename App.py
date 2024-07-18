from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'  # Clé secrète pour les messages flash
db = SQLAlchemy(app)

# Modèles de données
class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    date_creation = db.Column(db.DateTime, default=db.func.current_timestamp())
    entries = db.relationship('Entry', backref='lot', lazy=True)

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    nom_edition = db.Column(db.String(100), nullable=False)
    type_edition = db.Column(db.String(50), nullable=False)
    type_envoie = db.Column(db.String(50), nullable=False)
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
        nom_edition = request.form['nom_edition']
        type_edition = request.form['type_edition']
        type_envoie = request.form['type_envoie']
        nombre_page_destinataire = int(request.form['nombre_page_destinataire'])
        nombre_destinataires = int(request.form['nombre_destinataires'])

        # Calcul du nombre de pages
        nombre_page = nombre_page_destinataire * nombre_destinataires

        # Création du nouveau lot et entrée associée
        lot = Lot()
        entry = Entry(
            nom_edition=nom_edition,
            type_edition=type_edition,
            type_envoie=type_envoie,
            nombre_page_destinataire=nombre_page_destinataire,
            nombre_destinataires=nombre_destinataires,
            nombre_page=nombre_page
        )

        lot.entries.append(entry)

        try:
            db.session.add(lot)
            db.session.commit()
            flash('Lot ajouté avec succès!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout du lot : {str(e)}", 'error')

    # Récupérer le dernier lot créé pour afficher le numéro
    last_lot = Lot.query.order_by(Lot.id.desc()).first()
    return render_template('ajouter_lot.html', last_lot=last_lot)

if __name__ == '__main__':
    app.run(debug=True)



