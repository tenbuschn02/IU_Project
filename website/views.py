from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, GuestlistOpen, GuestlistAccepted, GuestlistDeclined, GuestlistWaiting
from . import db
import os
from flask import current_app
import pandas as pd
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
    print(db.metadata.tables.keys())
    rowsOpen = db.session.query(GuestlistOpen).count()
    rowsAcc = db.session.query(GuestlistAccepted).count()
    rowsDec = db.session.query(GuestlistDeclined).count()
    rowsWait = db.session.query(GuestlistWaiting).count()
    
    if request.method == 'POST':
        mode = request.form['submit']
        upload_csv = request.form.get("upload_csv")
        
        if mode == 'upload_csv':

            uploaded_file = request.files['file']
            if uploaded_file.filename != '':

                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.filename)
                uploaded_file.save(file_path)

                openCsv = pd.read_csv(file_path, usecols = ['guestlist_open'], sep=None, skip_blank_lines=True)
                acceptedCsv = pd.read_csv(file_path, usecols = ['guestlist_accepted'], sep=None, skip_blank_lines=True)
                declinedCsv = pd.read_csv(file_path, usecols = ['guestlist_declined'], sep=None, skip_blank_lines=True)
                waitingCsv = pd.read_csv(file_path, usecols = ['guestlist_waiting'], sep=None, skip_blank_lines=True)

                #should not be necessary
                openCsv = openCsv[openCsv['guestlist_open'].notna()]
                acceptedCsv = acceptedCsv[acceptedCsv['guestlist_accepted'].notna()]
                declinedCsv = declinedCsv[declinedCsv['guestlist_declined'].notna()]
                waitingCsv = waitingCsv[waitingCsv['guestlist_waiting'].notna()]

                print(acceptedCsv)

                openCsv.rename(columns={'guestlist_open': 'name'}, inplace=True)
                acceptedCsv.rename(columns={'guestlist_accepted': 'name'}, inplace=True)
                declinedCsv.rename(columns={'guestlist_declined': 'name'}, inplace=True)
                waitingCsv.rename(columns={'guestlist_waiting': 'name'}, inplace=True)

                

                print(acceptedCsv)

                openCsv['user_id']=current_user.id
                acceptedCsv['user_id']=current_user.id
                declinedCsv['user_id']=current_user.id
                waitingCsv['user_id']=current_user.id

                openCsv['count']=1
                acceptedCsv['count']=1
                declinedCsv['count']=1
                waitingCsv['count']=1

                openCsv.to_sql('guestlist_open', con=db.engine, if_exists='append', index=False)
                acceptedCsv.to_sql('guestlist_accepted', con=db.engine, if_exists='append', index=False)
                declinedCsv.to_sql('guestlist_declined', con=db.engine, if_exists='append', index=False)
                waitingCsv.to_sql('guestlist_waiting', con=db.engine, if_exists='append', index=False)

                os.remove(file_path)
        
        elif mode == 'add_guest' or mode =='add_guest_waiting':

            guest = request.form.get('guest')

            if len(guest) < 1:
                flash('Name is too short!', category='error')
            else:
                if mode == 'add_guest':
                    new_guest = GuestlistOpen(name=guest, user_id=current_user.id, count=1)
                else:
                    new_guest = GuestlistWaiting(name=guest, user_id=current_user.id, count=1)
                db.session.add(new_guest)
                db.session.commit()
                flash('Guest added!', category='success')


    return render_template("guestlist.html", user=current_user, rowsOpen=rowsOpen, rowsAcc=rowsAcc, rowsDec=rowsDec, rowsWait=rowsWait)

@views.route('/foodcalc', methods=['GET', 'POST'])
@login_required
def foodcalc():
    return render_template("foodcalc.html", user=current_user)


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
    if guest:
        if guest.user_id == current_user.id:
            db.session.delete(guest)
            db.session.commit()
            guest = getattr(sys.modules[__name__], tableTo)(name=guest.name, user_id=current_user.id, count=1)
            db.session.add(guest)
            db.session.commit()

    return jsonify({})

@views.route('/guest-delete', methods=['POST'])
def guest_del():
    guest = json.loads(request.data)
    guestId = guest['guestId']
    tableFrom = guest['tableFrom']
    guest = getattr(sys.modules[__name__], tableFrom).query.get(guestId)

    if guest:
        if guest.user_id == current_user.id:
            db.session.delete(guest)
            db.session.commit()

    return jsonify({})



# @application.route('upload.html',methods = ['POST'])
# def upload_route_summary():
#     if request.method == 'POST':

#         # Create variable for uploaded file
#         f = request.files['fileupload']  

#         #store the file contents as a string
#         fstring = f.read()
#         print(fstring)
        
#         #create list of dictionaries keyed by header row
#         #csv_dicts = [{k: v for k, v in row.items()} for row in csv.DictReader(fstring.splitlines(), skipinitialspace=True)]

#         #do something list of dictionaries
#     return "success"
