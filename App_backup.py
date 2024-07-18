from flask import Flask, render_template, request, redirect, send_file, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Lot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(100), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)

class LotEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('lot.id'), nullable=False)
    nom_edition = db.Column(db.String(200), nullable=False)
    type_edition = db.Column(db.String(20), nullable=False)
    type_envoie = db.Column(db.String(100), nullable=False)
    nombre_page_destinataire = db.Column(db.Integer, nullable=False)
    nombre_destinataires = db.Column(db.Integer, nullable=False)
    nombre_page = db.Column(db.Integer, nullable=False)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_edition = db.Column(db.String(200), nullable=False)
    type_edition = db.Column(db.String(20), nullable=False)
    type_envoie = db.Column(db.String(100), nullable=False)
    nombre_page_destinataire = db.Column(db.Integer, nullable=False)
    nombre_destinataires = db.Column(db.Integer, nullable=False)
    nombre_page = db.Column(db.Integer, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/')
def index():
    lots = Lot.query.order_by(Lot.date_creation.desc()).all()
    return render_template('index.html', lots=lots)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception as e:
        return f'There was a problem deleting that task: {e}'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Todo.query.get_or_404(id)
    if request.method == 'POST':
        task.nom_edition = request.form['nom_edition']
        task.type_edition = request.form['type_edition']
        task.type_envoie = request.form['type_envoie']
        task.nombre_page_destinataire = request.form['nombre_page_destinataire']
        task.nombre_destinataires = request.form['nombre_destinataires']
        task.nombre_page = request.form['nombre_page']
        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'There was a problem updating that task: {e}'
    return render_template('update.html', task=task)

@app.route('/export-excel')
def export_excel():
    tasks = Todo.query.all()
    data = [{
        'Nom Edition': task.nom_edition,
        'Type Edition': task.type_edition,
        'Type d\'envoie': task.type_envoie,
        'Nombre Page par Destinataire': task.nombre_page_destinataire,
        'Nombre Destinataires': task.nombre_destinataires,
        'Nombre Page': task.nombre_page,
        'Date Created': task.date_created
    } for task in tasks]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Tasks')
        workbook = writer.book
        worksheet = writer.sheets['Tasks']
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        worksheet.set_column(0, len(df.columns) - 1, 20)
    output.seek(0)
    return send_file(output, as_attachment=True, download_name="tasks.xlsx")

@app.route('/ajouter-lot', methods=['GET', 'POST'])
def ajouter_lot():
    if request.method == 'POST':
        try:
            numero_lot = request.form.get('numero_lot')
            new_lot = Lot(numero=numero_lot)
            db.session.add(new_lot)
            db.session.flush()
            for key, value in request.form.items():
                if key.startswith('nom_edition_'):
                    index = key.split('_')[-1]
                    nom_edition = value
                    type_edition = request.form.get(f'type_edition_{index}')
                    type_envoie = request.form.get(f'type_envoie_{index}')
                    nombre_page_destinataire = request.form.get(f'nombre_page_destinataire_{index}')
                    nombre_destinataires = request.form.get(f'nombre_destinataires_{index}')
                    nombre_page = request.form.get(f'nombre_page_{index}')
                    new_entry = LotEntry(
                        lot_id=new_lot.id,
                        nom_edition=nom_edition,
                        type_edition=type_edition,
                        type_envoie=type_envoie,
                        nombre_page_destinataire=nombre_page_destinataire,
                        nombre_destinataires=nombre_destinataires,
                        nombre_page=nombre_page
                    )
                    db.session.add(new_entry)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)})
    return render_template('ajouter_lot.html')

if __name__ == "__main__":
    app.run(debug=True)

