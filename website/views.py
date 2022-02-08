from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Guest, Group, AcceptedRatio, Food, Table
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

    #print(db.metadata.tables.keys())
    
    groupsList = Group.query.all()
    
    
    if request.method == 'POST':
        mode = request.form['submit']
        upload_csv = request.form.get("Upload CSV")
        
        if mode == 'Upload CSV':

            uploaded_file = request.files['file']
            if uploaded_file.filename != '':

                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.filename)
                uploaded_file.save(file_path)

                openCsv = pd.read_csv(file_path, usecols = ['guestlist_open', 'open_group'], sep=None, skip_blank_lines=True)
                acceptedCsv = pd.read_csv(file_path, usecols = ['guestlist_accepted', 'accepted_group'], sep=None, skip_blank_lines=True)
                declinedCsv = pd.read_csv(file_path, usecols = ['guestlist_declined', 'declined_group'], sep=None, skip_blank_lines=True)
                waitingCsv = pd.read_csv(file_path, usecols = ['guestlist_waiting', 'waiting_group'], sep=None, skip_blank_lines=True)

                #should not be necessary
                openCsv = openCsv[openCsv['guestlist_open'].notna()]
                acceptedCsv = acceptedCsv[acceptedCsv['guestlist_accepted'].notna()]
                declinedCsv = declinedCsv[declinedCsv['guestlist_declined'].notna()]
                waitingCsv = waitingCsv[waitingCsv['guestlist_waiting'].notna()]
                openCsv = openCsv[openCsv['open_group'].notna()]
                acceptedCsv = acceptedCsv[acceptedCsv['accepted_group'].notna()]
                declinedCsv = declinedCsv[declinedCsv['declined_group'].notna()]
                waitingCsv = waitingCsv[waitingCsv['waiting_group'].notna()]

                openCsv.rename(columns={'guestlist_open': 'name', 'open_group': 'group_id'}, inplace=True)
                acceptedCsv.rename(columns={'guestlist_accepted': 'name', 'accepted_group': 'group_id'}, inplace=True)
                declinedCsv.rename(columns={'guestlist_declined': 'name', 'declined_group': 'group_id'}, inplace=True)
                waitingCsv.rename(columns={'guestlist_waiting': 'name', 'waiting_group': 'group_id'}, inplace=True)

                openCsv['user_id']=current_user.id
                acceptedCsv['user_id']=current_user.id
                declinedCsv['user_id']=current_user.id
                waitingCsv['user_id']=current_user.id

                openCsv['invitation_sent']=False
                acceptedCsv['invitation_sent']=False
                declinedCsv['invitation_sent']=False
                waitingCsv['invitation_sent']=False

                openCsv['status_id']=1
                acceptedCsv['status_id']=2
                declinedCsv['status_id']=3
                waitingCsv['status_id']=4

                openCsv.to_sql('guest', con=db.engine, if_exists='append', index=False)
                acceptedCsv.to_sql('guest', con=db.engine, if_exists='append', index=False)
                declinedCsv.to_sql('guest', con=db.engine, if_exists='append', index=False)
                waitingCsv.to_sql('guest', con=db.engine, if_exists='append', index=False)

                os.remove(file_path)
        
        elif mode == 'add_guest' or mode =='add_guest_waiting':

            guest = request.form.get('guest')
            group = request.form.get('group')

            if len(guest) < 1:
                flash('Name is too short!', category='error')
            else:
                if mode == 'add_guest':
                    new_guest = Guest(name=guest, user_id=current_user.id, invitation_sent=False, group_id=group, status_id=1)
                else:
                    new_guest = GuestlistWaiting(name=guest, user_id=current_user.id, invitation_sent=False, status_id=4)
                db.session.add(new_guest)
                db.session.commit()
                flash('Guest added!', category='success')

    rowsOpen = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=1).count()
    rowsAcc = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=2).count()
    rowsDec = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=3).count()
    rowsWait = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=4).count()

    guestsOpen = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=1)
    guestsAccepted = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=2)
    guestsDeclined = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=3)
    guestsWaiting = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=4)

    return render_template("guestlist.html", guestsOpen=guestsOpen, guestsDeclined=guestsDeclined, guestsAccepted=guestsAccepted, guestsWaiting=guestsWaiting, user=current_user, rowsOpen=rowsOpen, rowsAcc=rowsAcc, rowsDec=rowsDec, rowsWait=rowsWait, groupsList=groupsList)

@views.route('/foodcalc', methods=['GET', 'POST'])
@login_required
def foodcalc():

    
    # db.session.commit()
    if not db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).first():
        ratio = 50
    else:
        ratio = db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).first().ratio


    if request.method == 'POST':
        mode = request.form['submit']

        if mode == 'submit_ratio':
            ratio = request.form.get('ratio', type=int)
            if not db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).first():
                ratio = AcceptedRatio(ratio=ratio, user_id=current_user.id)
                db.session.add(ratio)
                ratio=ratio.ratio
                print('if')
            else:
                db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).update({"ratio": ratio})
                print('else')
            db.session.commit()
        
        elif mode == 'add_food':
            food_name = request.form.get('food_name')
            food_price = request.form.get('food_price')
            amount_1 = request.form.get('amount_1')
            amount_2 = request.form.get('amount_2')
            amount_3 = request.form.get('amount_3')

            if len(food_name) < 1:
                flash('Pleace enter a name!', category='error')
            elif len(food_price) < 1:
                flash('Pleace enter a price!', category='error')
            elif len(amount_1) < 1:
                flash('Pleace enter an estimated amount for men!', category='error')
            elif len(amount_2) < 1:
                flash('Pleace enter an estimated amount for women!', category='error')
            elif len(amount_3) < 1:
                flash('Pleace enter an estimated amount for children!', category='error')          
            else:
                if mode == 'add_food':
                    new_food = Food(name=food_name, user_id=current_user.id, price=food_price, amount_1=amount_1, amount_2=amount_2, amount_3=amount_3)
                else:
                    print()
                db.session.add(new_food)
                db.session.commit()
                flash('Food added!', category='success')
            print('food added')

    male_guests = db.session.query(Guest).filter_by(user_id=current_user.id, group_id=1, status_id=2).count()
    male_guests = round(male_guests + db.session.query(Guest).filter_by(user_id=current_user.id, group_id=1, status_id=1).count() * ratio/100)
    female_guests = db.session.query(Guest).filter_by(user_id=current_user.id, group_id=2, status_id=2).count()
    female_guests = round(female_guests + db.session.query(Guest).filter_by(user_id=current_user.id, group_id=2, status_id=1).count() * ratio/100)
    child_guests = db.session.query(Guest).filter_by(user_id=current_user.id, group_id=3, status_id=2).count()
    child_guests = round(child_guests + db.session.query(Guest).filter_by(user_id=current_user.id, group_id=3, status_id=1).count() * ratio/100)

    return render_template("foodcalc.html", user=current_user, male_guests=male_guests, female_guests=female_guests, child_guests=child_guests, ratio=ratio)


@views.route('/table-overview', methods=['GET', 'POST'])
def table_overview():

    selected_guests = request.form.getlist('selected')
    selected_table = request.form.get('tables')
    print(selected_guests) 
    print('----')
    print(selected_table)


    if request.method == 'POST':
        mode = request.form['submit']

        if mode == 'add_table':
            table_name = request.form.get('table_name')
            max_guests = request.form.get('max_guests')

            new_table = Table(name=table_name, user_id=current_user.id, max_guests=max_guests)
            db.session.add(new_table)
            db.session.commit()
            flash('Table added!', category='success')

        elif mode == 'assign_table':
            for guest in selected_guests:
                print(guest)
                db.session.query(Guest).filter_by(user_id=current_user.id, id=guest).update({"table_id": selected_table})
                db.session.commit()


    tableList = Table.query.all()      
    guestsOpen = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=1)
    guestsAccepted = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=2)  

    return render_template("tables.html",user=current_user, tableList=tableList, guestsOpen=guestsOpen, guestsAccepted=guestsAccepted)


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


@views.route('/delete-food', methods=['POST'])
def delete_food():
    food = json.loads(request.data)
    foodId = food['foodId']
    food = Food.query.get(foodId)
    if food:
        if food.user_id == current_user.id:
            db.session.delete(food)
            db.session.commit()

    return jsonify({})


@views.route('/delete-table', methods=['POST'])
def delete_table():
    table = json.loads(request.data)
    tableId = table['tableId']
    table = Table.query.get(tableId)
    if table:
        if table.user_id == current_user.id:
            db.session.delete(table)
            db.session.commit()

    return jsonify({})


@views.route('/guest-change', methods=['POST'])
def guest_open():
    guest = json.loads(request.data)
    guestId = guest['guestId']
    new_status = guest['new_status']
    guest = Guest.query.get(guestId)
    if guest:
        if guest.user_id == current_user.id:
            guest.status_id = new_status
            db.session.commit()

    return jsonify({})

@views.route('/guest-delete', methods=['POST'])
def guest_del():
    guest = json.loads(request.data)
    guestId = guest['guestId']
    guest = Guest.query.get(guestId)

    if guest:
        if guest.user_id == current_user.id:
            db.session.delete(guest)
            db.session.commit()

    return jsonify({})


@views.route('/delete-all', methods=['POST'])
def delete_all():
    GuestlistAccepted.query.filter_by(user_id=current_user.id).delete()
    GuestlistOpen.query.filter_by(user_id=current_user.id).delete()
    GuestlistDeclined.query.filter_by(user_id=current_user.id).delete()
    GuestlistWaiting.query.filter_by(user_id=current_user.id).delete()
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
