from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, GuestlistOpen, GuestlistAccepted, GuestlistDeclined
from . import db
import json
import sys

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='error')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/guest-list', methods=['GET', 'POST'])
@login_required
def guest_list():
    if request.method == 'POST':
        guest = request.form.get('guest')

        if len(guest) < 1:
            flash('Name is too short!', category='error')
        else:
            new_guest = GuestlistOpen(name=guest, user_id=current_user.id, count=1)
            db.session.add(new_guest)
            db.session.commit()
            flash('Guest added!', category='success')
    return render_template("guestlist.html", user=current_user)


@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})


@views.route('/guest-change', methods=['POST'])
def guest_open():
    guest = json.loads(request.data)
    guestId = guest['guestId']
    tableFrom = guest['tableFrom']
    tableTo = guest['tableTo']
    guest = getattr(sys.modules[__name__], tableFrom).query.get(guestId)
    print(guest)
    if guest:
        print('test')
        if guest.user_id == current_user.id:
            db.session.delete(guest)
            db.session.commit()
            guest = getattr(sys.modules[__name__], tableTo)(name=guest.name, user_id=current_user.id, count=1)
            db.session.add(guest)
            db.session.commit()

    return jsonify({})
