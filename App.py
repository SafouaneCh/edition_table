from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from io import BytesIO
import pandas as pd

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
    lots = Lot.query.order_by(Lot.date_creation.desc()).all()
    for lot in lots:
        lot.entries = list(lot.entries)  # Convert to list if needed
    return render_template('index.html', lots=lots)

@app.route('/delete/<int:id>')
def delete(id):
    entry_to_delete = Entry.query.get_or_404(id)

    try:
        db.session.delete(entry_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f'There was a problem deleting that entry: {e}'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    entry = Entry.query.get_or_404(id)

    if request.method == 'POST':
        entry.nom_edition = request.form['nom_edition']
        entry.type_edition = request.form['type_edition']
        entry.type_envoie = request.form['type_envoie']
        entry.nombre_page_destinataire = request.form['nombre_page_destinataire']
        entry.nombre_destinataires = request.form['nombre_destinataires']
        entry.nombre_page = request.form['nombre_page']

        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'There was a problem updating that entry: {e}'

    return render_template('update.html', entry=entry)

@app.route('/export-excel')
def export_excel():
    entries = Entry.query.all()

    # Convert entries to a list of dictionaries
    data = [{
        'Nom Edition': entry.nom_edition,
        'Type Edition': entry.type_edition,
        'Type d\'envoie': entry.type_envoie,
        'Nombre Page par Destinataire': entry.nombre_page_destinataire,
        'Nombre Destinataires': entry.nombre_destinataires,
        'Nombre Page': entry.nombre_page,
        'Date Created': entry.date_creation
    } for entry in entries]

    # Create a Pandas DataFrame
    df = pd.DataFrame(data)

    # Create a BytesIO object
    output = BytesIO()

    # Write the DataFrame to an Excel file
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Entries')

        # Get the xlsxwriter workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Entries']

        # Add a header format
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })

        # Write the column headers with the defined format
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Set the column width
        worksheet.set_column(0, len(df.columns) - 1, 20)

    # Set up the Http response
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="entries.xlsx")

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

if __name__ == "__main__":
    app.run(debug=True)



