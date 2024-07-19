# routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models import Lot, LotEntry

main_bp = Blueprint('main', __name__)

@main_bp.route('/ajouter-lot', methods=['GET', 'POST'])
def ajouter_lot():
    if request.method == 'POST':
        lot = Lot(numero=Lot.get_next_numero())
        db.session.add(lot)
        db.session.flush()  # Pour obtenir l'ID du lot
        for key, value in request.form.items():
            if key.startswith('nom_edition'):
                index = key.split('_')[-1]
                nom_edition = request.form.get(f'nom_edition_{index}')
                type_edition = request.form.get(f'type_edition_{index}')
                type_envoie = request.form.get(f'type_envoie_{index}')
                nombre_page_destinataire = int(request.form.get(f'nombre_page_destinataire_{index}'))
                nombre_destinataires = int(request.form.get(f'nombre_destinataires_{index}'))
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
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout du lot : {str(e)}", 'error')
    last_lot = Lot.query.order_by(Lot.id.desc()).first()
    return render_template('ajouter_lot.html', last_lot=last_lot)

@main_bp.route('/ajouter-lot', methods=['GET', 'POST'])
def ajouter_lot():
    if request.method == 'POST':
        lot = Lot(numero=Lot.get_next_numero())
        db.session.add(lot)
        db.session.flush()  # Pour obtenir l'ID du lot

        nom_edition = request.form.get('nom_edition')
        type_edition = request.form.get('type_edition')
        type_envoie = request.form.get('type_envoie')
        nombre_page_destinataire_str = request.form.get('nombre_page_destinataire')
        nombre_destinataires_str = request.form.get('nombre_destinataires')

        if nombre_page_destinataire_str and nombre_destinataires_str:
            nombre_page_destinataire = int(nombre_page_destinataire_str)
            nombre_destinataires = int(nombre_destinataires_str)
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
        else:
            flash("Erreur: Données manquantes pour l'entrée", 'error')
            return redirect(url_for('main.ajouter_lot'))

        try:
            db.session.commit()
            flash('Lot ajouté avec succès!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f"Erreur lors de l'ajout du lot : {str(e)}", 'error')

    last_lot = Lot.query.order_by(Lot.id.desc()).first()
    return render_template('ajouter_lot.html', last_lot=last_lot)