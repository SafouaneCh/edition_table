from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func
import pandas as pd
import os
import zipfile
import base64
import plotly.graph_objects as go

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

# Route pour la page données d'édition
@app.route('/donnees-édition')
def donnees_edition():
    lots = Lot.query.all()
    return render_template('donnees_edition.html', lots=lots)

# Route pour obtenir les détails d'un lot
@app.route('/lot-details/<int:lot_id>', methods=['GET'])
def lot_details(lot_id):
    lot = Lot.query.get_or_404(lot_id)
    entries = LotEntry.query.filter_by(lot_id=lot_id).all()
    data = {
        'numero': lot.numero,
        'entries': [{
            'nom_edition': entry.nom_edition,
            'type_edition': entry.type_edition,
            'type_envoie': entry.type_envoie,
            'nombre_page_destinataire': entry.nombre_page_destinataire,
            'nombre_destinataires': entry.nombre_destinataires,
            'nombre_page': entry.nombre_page
        } for entry in entries]
    }
    return jsonify(data)

# Route pour ajouter un nouveau lot
@app.route('/ajouter-lot', methods=['GET', 'POST'])
def ajouter_lot():
    if request.method == 'POST':
        lot = Lot(numero=Lot.get_next_numero())
        db.session.add(lot)
        db.session.flush()  # Pour obtenir l'ID du lot

        entries = []
        entry_count = len([key for key in request.form.keys() if key.startswith('nom_edition_')])
        
        for i in range(1, entry_count + 1):
            nom_edition = request.form.get(f'nom_edition_{i}')
            type_edition = request.form.get(f'type_edition_{i}')
            type_envoie = request.form.get(f'type_envoie_{i}')
            nombre_page_destinataire_str = request.form.get(f'nombre_page_destinataire_{i}')
            nombre_destinataires_str = request.form.get(f'nombre_destinataires_{i}')
            nombre_pages_str = request.form.get(f'nombre_pages_{i}')

            if not all([nom_edition, type_edition, type_envoie, nombre_page_destinataire_str, nombre_destinataires_str, nombre_pages_str]):
                flash("Erreur: Tous les champs sont requis", 'error')
                return redirect(url_for('ajouter_lot'))

            try:
                nombre_page_destinataire = int(nombre_page_destinataire_str)
                nombre_destinataires = int(nombre_destinataires_str)
                nombre_page = int(nombre_pages_str)
            except ValueError:
                flash("Erreur: Les valeurs numériques sont invalides", 'error')
                return redirect(url_for('ajouter_lot'))

            entry = LotEntry(
                lot_id=lot.id,
                nom_edition=nom_edition,
                type_edition=type_edition,
                type_envoie=type_envoie,
                nombre_page_destinataire=nombre_page_destinataire,
                nombre_destinataires=nombre_destinataires,
                nombre_page=nombre_page
            )
            entries.append(entry)

        db.session.add_all(entries)

        try:
            db.session.commit()
            flash('Lot ajouté avec succès!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout du lot : {str(e)}", 'error')

    last_lot = Lot.query.order_by(Lot.id.desc()).first()
    return render_template('ajouter_lot.html', last_lot=last_lot)

# Route pour télécharger tous les lots
@app.route('/telecharger-tous-les-lots', methods=['GET'])
def telecharger_tous_les_lots():
    try:
        lots = Lot.query.all()
        data = []
        for lot in lots:
            entries = lot.entries.all()
            for entry in entries:
                data.append({
                    'Numéro du Lot': lot.numero,
                    'Nom Édition': entry.nom_edition,
                    'Type Édition': entry.type_edition,
                    'Type Envoi': entry.type_envoie,
                    'Nombre Pages Destinataire': entry.nombre_page_destinataire,
                    'Nombre Destinataires': entry.nombre_destinataires,
                    'Nombre Pages': entry.nombre_page,
                })
        df = pd.DataFrame(data)
        file_path = 'lots.xlsx'
        df.to_excel(file_path, index=False)

        # Vérifiez si le fichier a bien été créé
        if not os.path.exists(file_path):
            flash("Erreur: Le fichier n'a pas été créé.", 'error')
            return redirect(url_for('donnees_edition'))

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"Erreur lors du téléchargement des fichiers : {str(e)}", 'error')
        return redirect(url_for('donnees_edition'))

# Route pour télécharger un lot spécifique
@app.route('/telecharger-lot/<int:lot_id>', methods=['GET'])
def telecharger_lot(lot_id):
    try:
        lot = Lot.query.get_or_404(lot_id)
        entries = lot.entries.all()
        data = []
        for entry in entries:
            data.append({
                'Numéro du Lot': lot.numero,
                'Nom Édition': entry.nom_edition,
                'Type Édition': entry.type_edition,
                'Type Envoi': entry.type_envoie,
                'Nombre Pages Destinataire': entry.nombre_page_destinataire,
                'Nombre Destinataires': entry.nombre_destinataires,
                'Nombre Pages': entry.nombre_page,
            })
        df = pd.DataFrame(data)
        file_path = f'lot_{lot_id}.xlsx'
        df.to_excel(file_path, index=False)

        # Vérifiez si le fichier a bien été créé
        if not os.path.exists(file_path):
            flash("Erreur: Le fichier n'a pas été créé.", 'error')
            return redirect(url_for('donnees_edition'))

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        flash(f"Erreur lors du téléchargement du lot : {str(e)}", 'error')
        return redirect(url_for('donnees_edition'))

# Route pour télécharger les lots sélectionnés
@app.route('/telecharger-lots-selectionnes', methods=['POST'])
def telecharger_lots_selectionnes():
    try:
        # Récupérer les IDs des lots sélectionnés depuis le formulaire
        lot_ids = request.form.getlist('lots')
        
        if not lot_ids:
            flash("Aucun lot sélectionné pour le téléchargement.", 'warning')
            return redirect(url_for('donnees_edition'))

        # Préparer les fichiers Excel pour chaque lot sélectionné
        file_paths = []
        for lot_id in lot_ids:
            lot = Lot.query.get_or_404(lot_id)
            entries = lot.entries.all()
            data = []
            for entry in entries:
                data.append({
                    'Numéro du Lot': lot.numero,
                    'Nom Édition': entry.nom_edition,
                    'Type Édition': entry.type_edition,
                    'Type Envoi': entry.type_envoie,
                    'Nombre Pages Destinataire': entry.nombre_page_destinataire,
                    'Nombre Destinataires': entry.nombre_destinataires,
                    'Nombre Pages': entry.nombre_page,
                })
            df = pd.DataFrame(data)
            file_path = f'lot_{lot_id}.xlsx'
            df.to_excel(file_path, index=False)
            file_paths.append(file_path)

        # Créer un fichier ZIP contenant tous les fichiers Excel
        zip_file_path = 'lots_selectionnes.zip'
        with zipfile.ZipFile(zip_file_path, 'w') as zipf:
            for file_path in file_paths:
                zipf.write(file_path)
                os.remove(file_path)  # Supprimer le fichier après l'ajouter au ZIP

        # Vérifiez si le fichier ZIP a bien été créé
        if not os.path.exists(zip_file_path):
            flash("Erreur: Le fichier ZIP n'a pas été créé.", 'error')
            return redirect(url_for('donnees_edition'))

        return send_file(zip_file_path, as_attachment=True)

    except Exception as e:
        flash(f"Erreur lors du téléchargement des lots sélectionnés : {str(e)}", 'error')
        return redirect(url_for('donnees_edition'))

# Route pour la page de rapport
@app.route('/rapport')
def rapport():
    # Obtenir les données des lots par heure
    lots = Lot.query.with_entities(func.strftime('%Y-%m-%d %H:00:00', Lot.date_creation).label('hour'), func.count(Lot.id).label('count')).group_by(func.strftime('%Y-%m-%d %H:00:00', Lot.date_creation)).all()

    hours = [lot.hour for lot in lots]
    counts = [lot.count for lot in lots]

    # Créer le graphique
    fig = go.Figure()
    fig.add_trace(go.Bar(x=hours, y=counts))
    fig.update_layout(
        title='Nombre de Lots Créés par Heure',
        xaxis_title='Heure',
        yaxis_title='Nombre de Lots'
    )

    # Convertir le graphique en image PNG base64
    img_bytes = fig.to_image(format='png')
    img_base64 = base64.b64encode(img_bytes).decode('utf-8')

    return render_template('rapport.html', graph_img=img_base64)

if __name__ == '__main__':
    app.run(debug=True)






