from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Note, Guest, Group, AcceptedRatio, Food, Table, Costs
from . import db
import os
from flask import current_app, send_file
import pandas as pd
import json
import sys
import logging
import io

views = Blueprint('views', __name__)

# Acquire the logger for a library (azure.mgmt.resource in this example)
logger = logging.getLogger('azure.mgmt.resource')

# Set the desired logging level
logger.setLevel(logging.DEBUG)


# Welcome page
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():

    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note is too short!', category='danger')
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')

    return render_template("home.html", user=current_user)


# Maintaining the guest list. Containing four lists of guests related to the status of their invitation (Waiting list, Pending, accepted, declined)
@views.route('/guest-list', methods=['GET', 'POST'])
@login_required
def guest_list():

    #print(db.metadata.tables.keys())
    
    groupsList = Group.query.all()
    
    
    if request.method == 'POST':
        mode = request.form['submit']
        upload_csv = request.form.get("Upload CSV")
        
        if mode == 'Upload CSV':

            # Use uploaded CSV to create guest list
            uploaded_file = request.files['file']
            name, extension = os.path.splitext(uploaded_file.filename)

            if uploaded_file.filename == '':
                flash('Please select a file first', category='danger')
            elif extension != '.csv':
                flash('Uploaded file most be from type csv', category='danger')
            else:
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], uploaded_file.filename)
                uploaded_file.save(file_path)


                try:
                    openCsv = pd.read_csv(file_path, usecols = ['guestlist_open', 'open_group'], sep=None, skip_blank_lines=True, encoding="latin1")
                    acceptedCsv = pd.read_csv(file_path, usecols = ['guestlist_accepted', 'accepted_group'], sep=None, skip_blank_lines=True, encoding="latin1")
                    declinedCsv = pd.read_csv(file_path, usecols = ['guestlist_declined', 'declined_group'], sep=None, skip_blank_lines=True, encoding="latin1")
                    waitingCsv = pd.read_csv(file_path, usecols = ['guestlist_waiting', 'waiting_group'], sep=None, skip_blank_lines=True, encoding="latin1")

                    # Remove na
                    openCsv = openCsv[openCsv['guestlist_open'].notna()]
                    acceptedCsv = acceptedCsv[acceptedCsv['guestlist_accepted'].notna()]
                    declinedCsv = declinedCsv[declinedCsv['guestlist_declined'].notna()]
                    waitingCsv = waitingCsv[waitingCsv['guestlist_waiting'].notna()]
                    openCsv = openCsv[openCsv['open_group'].notna()]
                    acceptedCsv = acceptedCsv[acceptedCsv['accepted_group'].notna()]
                    declinedCsv = declinedCsv[declinedCsv['declined_group'].notna()]
                    waitingCsv = waitingCsv[waitingCsv['waiting_group'].notna()]

                    # Check group columns for correct ids
                    for line in openCsv['open_group']:
                        if not 1 <= line <=3:
                            raise TypeError()
                    for line in acceptedCsv['accepted_group']:
                        if not 1 <= line <=3:
                            raise TypeError
                    for line in declinedCsv['declined_group']:
                        if not 1 <= line <=3:
                            raise TypeError
                    for line in waitingCsv['waiting_group']:
                        if not 1 <= line <=3:
                            raise TypeError
                
                # Wrong group id
                except TypeError as te:
                    flash('Group Ids in uploaded file must be either 1 (male), 2 (female) or 3 (child)', category='danger')
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(te).__name__, te.args)
                    print(message)

                # All other execptions, most probably wrong column name 
                except ValueError as va:
                    flash('Wrong column names in uploaded file, please use the template', category='danger')
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(va).__name__, va.args)
                    print(message)

                except Exception as ex:
                    flash('An error occurred', category='danger')
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)

                else:

                    # Rename the columns
                    openCsv.rename(columns={'guestlist_open': 'name', 'open_group': 'group_id'}, inplace=True)
                    acceptedCsv.rename(columns={'guestlist_accepted': 'name', 'accepted_group': 'group_id'}, inplace=True)
                    declinedCsv.rename(columns={'guestlist_declined': 'name', 'declined_group': 'group_id'}, inplace=True)
                    waitingCsv.rename(columns={'guestlist_waiting': 'name', 'waiting_group': 'group_id'}, inplace=True)

                    # Add User Id column
                    openCsv['user_id']=current_user.id
                    acceptedCsv['user_id']=current_user.id
                    declinedCsv['user_id']=current_user.id
                    waitingCsv['user_id']=current_user.id

                    # Add invitations sent column (not used yet)
                    openCsv['invitation_sent']=False
                    acceptedCsv['invitation_sent']=False
                    declinedCsv['invitation_sent']=False
                    waitingCsv['invitation_sent']=False

                    # Add status id
                    openCsv['status_id']=1
                    acceptedCsv['status_id']=2
                    declinedCsv['status_id']=3
                    waitingCsv['status_id']=4

                    # Write to sqllite db
                    openCsv.to_sql('guest', con=db.engine, if_exists='append', index=False)
                    acceptedCsv.to_sql('guest', con=db.engine, if_exists='append', index=False)
                    declinedCsv.to_sql('guest', con=db.engine, if_exists='append', index=False)
                    waitingCsv.to_sql('guest', con=db.engine, if_exists='append', index=False)

                    # delete uploaded file
                    os.remove(file_path)
    
        elif mode == 'add_guest' or mode =='add_guest_waiting':

            # Add manually created guest either to waiting list or to pending list
            guest = request.form.get('guest')
            group = request.form.get('group')

            exists = db.session.query(Guest).filter_by(user_id=current_user.id, name=guest).first()
            if exists:
                flash('A Guest with this name already exists!', category='danger')
            else:
                if len(guest) < 1:
                    flash('Name is too short!', category='danger')
                else:
                    if mode == 'add_guest':
                        new_guest = Guest(name=guest, user_id=current_user.id, invitation_sent=False, group_id=group, status_id=1)
                    else:
                        new_guest = Guest(name=guest, user_id=current_user.id, invitation_sent=False, group_id=group, status_id=4)
                    db.session.add(new_guest)
                    db.session.commit()
                    flash('Guest added!', category='success')

    # get the amount of guests per status to show on website (guest list)
    rowsOpen = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=1).count()
    rowsAcc = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=2).count()
    rowsDec = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=3).count()
    rowsWait = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=4).count()

    # Get all guests per status to show on website (guest list)
    guestsOpen = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=1)
    guestsAccepted = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=2)
    guestsDeclined = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=3)
    guestsWaiting = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=4)

    return render_template("guestlist.html", guestsOpen=guestsOpen, guestsDeclined=guestsDeclined, guestsAccepted=guestsAccepted, guestsWaiting=guestsWaiting, user=current_user, rowsOpen=rowsOpen, rowsAcc=rowsAcc, rowsDec=rowsDec, rowsWait=rowsWait, groupsList=groupsList)


# Calculation tool for food amount and costs
@views.route('/foodcalc', methods=['GET', 'POST'])
@login_required
def foodcalc():

    # Define the ratio of accepted invitations (default value 80%)
    if not db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).first():
        ratio = 80
    else:
        ratio = db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).first().ratio


    if request.method == 'POST':
        mode = request.form['submit']

        if mode == 'submit_ratio':
            # Addapt the expected share of accepted invitations
            ratio = request.form.get('ratio', type=int)
            if not db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).first():
                ratio = AcceptedRatio(ratio=ratio, user_id=current_user.id)
                db.session.add(ratio)
                ratio=ratio.ratio
            else:
                db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).update({"ratio": ratio})
            db.session.commit()
        
        elif mode == 'add_food':
            # Add new food to the food list
            food_name = request.form.get('food_name')
            food_price = request.form.get('food_price')
            amount_1 = request.form.get('amount_1')
            amount_2 = request.form.get('amount_2')
            amount_3 = request.form.get('amount_3')

            if len(food_name) < 1:
                flash('Pleace enter a name!', category='danger')
            elif len(food_price) < 1:
                flash('Pleace enter a price!', category='danger')
            elif len(amount_1) < 1:
                flash('Pleace enter an estimated amount for men!', category='danger')
            elif len(amount_2) < 1:
                flash('Pleace enter an estimated amount for women!', category='danger')
            elif len(amount_3) < 1:
                flash('Pleace enter an estimated amount for children!', category='danger')          
            else:
                if mode == 'add_food':
                    new_food = Food(name=food_name, user_id=current_user.id, price=food_price, amount_1=amount_1, amount_2=amount_2, amount_3=amount_3)
                else:
                    print()
                db.session.add(new_food)
                db.session.commit()
                flash('Food added!', category='success')
            print('food added')

    # get amount of guests per group to show on website and use for calculation for expected amount of needed food
    male_guests = db.session.query(Guest).filter_by(user_id=current_user.id, group_id=1, status_id=2).count()
    male_guests = round(male_guests + db.session.query(Guest).filter_by(user_id=current_user.id, group_id=1, status_id=1).count() * ratio/100)
    female_guests = db.session.query(Guest).filter_by(user_id=current_user.id, group_id=2, status_id=2).count()
    female_guests = round(female_guests + db.session.query(Guest).filter_by(user_id=current_user.id, group_id=2, status_id=1).count() * ratio/100)
    child_guests = db.session.query(Guest).filter_by(user_id=current_user.id, group_id=3, status_id=2).count()
    child_guests = round(child_guests + db.session.query(Guest).filter_by(user_id=current_user.id, group_id=3, status_id=1).count() * ratio/100)

    return render_template("foodcalc.html", user=current_user, male_guests=male_guests, female_guests=female_guests, child_guests=child_guests, ratio=ratio)


# Maintaining a list of tables. Uses guest list to assign guest to a table
@views.route('/table-overview', methods=['GET', 'POST'])
@login_required
def table_overview():

    selected_guests = request.form.getlist('selected')
    selected_table = request.form.get('tables')

    if request.method == 'POST':
        mode = request.form['submit']

        if mode == 'add_table':
            # Add a new table to the list of tables, including maximum amount of guests
            table_name = request.form.get('table_name')
            max_guests = request.form.get('max_guests', type=int)

            if max_guests < 1:
                flash('Minimum quantity of 1 required', category='danger')
            elif len(table_name) < 1:
                flash('Please enter a table name', category='danger')
            else:
                new_table = Table(name=table_name, user_id=current_user.id, max_guests=max_guests)
                db.session.add(new_table)
                db.session.commit()
                flash('Table added!', category='success')

        elif mode == 'assign_table':
            # Assign the selected table to all selected guests
            for guest in selected_guests:
                guestAmount = db.session.query(Guest).filter_by(table_id=selected_table).count()
                max_guests = db.session.query(Table.max_guests).filter_by(id=selected_table).scalar()
                db.session.commit()

                print('-------')
                print(guestAmount)
                print(max_guests)
                print('-------')
                if guestAmount < max_guests:
                    db.session.query(Guest).filter_by(user_id=current_user.id, id=guest).update({"table_id": selected_table})
                    db.session.commit()
                    flash('Guest assign to table', category='success')
                else:
                    flash('Table already full', category='danger')

        elif mode == 'unassign':
            # unassign a guest from a table --> puts him back to list of guests without assigned tables
            for guest in selected_guests:
                db.session.query(Guest).filter_by(user_id=current_user.id, id=guest).update({"table_id": None})


    # Get list of tables, guest with pending and accepted invitation status and the amount of guests to show on website (page table overview)
    tableList = Table.query.all()      
    guestsOpen = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=1, table_id = None)
    guestsAccepted = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=2, table_id = None)  
    rowsOpen = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=1, table_id = None).count()
    rowsAcc = db.session.query(Guest).filter_by(user_id=current_user.id, status_id=2, table_id = None).count()

    return render_template("tables.html",user=current_user, tableList=tableList, guestsOpen=guestsOpen, guestsAccepted=guestsAccepted, rowsOpen=rowsOpen, rowsAcc=rowsAcc)


# financial overview
# Showing data added manually and data from food calculator
@views.route('/finances', methods=['GET', 'POST'])
@login_required
def finances():

     # Get the ratio of accepted invitations (default value 80%)
    if not db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).first():
        ratio = AcceptedRatio(ratio=80, user_id=current_user.id)
        db.session.add(ratio)
        db.session.commit()
        ratio = ratio.ratio
    else:
        ratio = db.session.query(AcceptedRatio).filter_by(user_id=current_user.id).first().ratio

    if request.method == 'POST':
        mode = request.form['submit']
        
        if mode == 'add_cost':
            # Add cost manually
            cost_name = request.form.get('cost_name')
            cost_price = request.form.get('cost_price')

            if len(cost_name) < 1:
                flash('Pleace enter a name!', category='danger')
            elif len(cost_price) < 1:
                flash('Pleace enter a price!', category='danger')        
            else:
                new_cost = Costs(name=cost_name, user_id=current_user.id, price=cost_price)
                db.session.add(new_cost)
                db.session.commit()
                flash('Cost added!', category='success')
            print('cost added')

    # Get amount of guests per group to display on website and to calculate the costs
    male_guests = db.session.query(Guest).filter_by(user_id=current_user.id, group_id=1, status_id=2).count()
    male_guests = round(male_guests + db.session.query(Guest).filter_by(user_id=current_user.id, group_id=1, status_id=1).count() * ratio/100)
    female_guests = db.session.query(Guest).filter_by(user_id=current_user.id, group_id=2, status_id=2).count()
    female_guests = round(female_guests + db.session.query(Guest).filter_by(user_id=current_user.id, group_id=2, status_id=1).count() * ratio/100)
    child_guests = db.session.query(Guest).filter_by(user_id=current_user.id, group_id=3, status_id=2).count()
    child_guests = round(child_guests + db.session.query(Guest).filter_by(user_id=current_user.id, group_id=3, status_id=1).count() * ratio/100)

    foods = db.session.query(Food).filter_by(user_id=current_user.id).all()
    costs = db.session.query(Costs).filter_by(user_id=current_user.id).all()
    db.session.commit()
  
    # Calculate the total costs (food and manually added costs)
    sum=0
    for food in foods:
        sum = sum + food.price * (food.amount_1 * male_guests + food.amount_2 * female_guests + food.amount_3 * child_guests)

    for cost in costs:
        sum = sum + cost.price

    return render_template("finances.html", user=current_user, male_guests=male_guests, female_guests=female_guests, child_guests=child_guests, ratio=ratio, sum=sum)


# Auxiliary page to delete a note
@views.route('/delete-note', methods=['POST'])
@login_required
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

# Auxiliary page to delete a food
@views.route('/delete-food', methods=['POST'])
@login_required
def delete_food():
    food = json.loads(request.data)
    foodId = food['foodId']
    food = Food.query.get(foodId)
    if food:
        if food.user_id == current_user.id:
            db.session.delete(food)
            db.session.commit()

    return jsonify({})

# Auxiliary page to delete a cost
@views.route('/delete-cost', methods=['POST'])
@login_required
def delete_cost():
    cost = json.loads(request.data) 
    costId = cost['costId']
    cost = Costs.query.get(costId)
    if cost:
        if cost.user_id == current_user.id:
            db.session.delete(cost)
            db.session.commit()

    return jsonify({})

# Auxiliary page to delete a table
@views.route('/delete-table', methods=['POST'])
@login_required
def delete_table():
    table = json.loads(request.data)
    tableId = table['tableId']
    table = Table.query.get(tableId)
    if table:
        if table.user_id == current_user.id:
            for guest in table.guest:
                guest.table_id = None
            db.session.delete(table)
            db.session.commit()

    return jsonify({})

# Auxiliary page to change the status of a guest (e.g. from pending to accepted)
@views.route('/guest-change', methods=['POST'])
@login_required
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

# Auxiliary page to delete a guest
@views.route('/guest-delete', methods=['POST'])
@login_required
def guest_del():
    guest = json.loads(request.data)
    guestId = guest['guestId']
    guest = Guest.query.get(guestId)

    if guest:
        if guest.user_id == current_user.id:
            db.session.delete(guest)
            db.session.commit()

    return jsonify({})

# Auxiliary page to delete all guests
@views.route('/delete-all', methods=['POST'])
@login_required
def delete_all():
    Guest.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({})

# Auxiliary page to get the csv template
@views.route('/get-template', methods=['GET','POST'])
@login_required
def get_template():
    print('get template')
    csv_dir  = "./static/files"
    csv_file = "GuestListTemplate.csv"
    csv_path = os.path.join(csv_dir, csv_file)
    send = send_file(csv_path, mimetype='text/csv', attachment_filename='GuestListTemplate.csv', as_attachment=True)
    print(send)
    return send

