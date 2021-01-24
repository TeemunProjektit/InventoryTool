from flask import render_template, request, redirect, session, flash
import pyodbc
import re
from app import app


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('index.html')

    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            global connection
            connection = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};\
                                SERVER=' + app.config['SERVER'] + ';\
                                DATABASE=' + app.config['DATABASE'] + ';\
                                UID=' + username + ';\
                                PWD=' + password + ';\
                                TRUSTED_CONNECTION=yes;')
            session['user'] = username

            return redirect('/inventory')

        except:
            flash("Incorrect username or password!")
            return render_template('index.html')


@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    if not session.get('user'):
        return redirect('/')

    if request.method == 'GET':
        cursor = connection.cursor()
        data = cursor.execute("SELECT office, product, name, SN, manufacturer, count FROM Inventory")
        data = cursor.fetchall()
        cursor.commit()
        cursor.close()
        return render_template('inventory.html', data=data)

    if request.method == 'POST':
        if request.form.get('Edit') == 'Edit':
            return redirect('/edit')
        elif request.form.get('Assign') == 'Assign':
            return redirect('/assign')
        elif request.form.get('Offices') == 'Helsinki':
            cursor = connection.cursor()
            data = cursor.execute("SELECT office, product, name, SN, manufacturer, count FROM Inventory WHERE "
                                  "office = 'Helsinki';")
            data = cursor.fetchall()
            cursor.commit()
            cursor.close()
            return render_template('inventory.html', data=data)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    if not session.get('user'):
        return redirect('/')

    if request.method == 'GET':
        cursor = connection.cursor()
        itemdata = cursor.execute("SELECT office, product, name, SN, manufacturer, count FROM inventory WHERE id=1")
        itemdata = cursor.fetchall()
        cursor.commit()
        cursor.close()

        cursor = connection.cursor()
        itemhistory = cursor.execute("SELECT action, office, product, name, SN, manufacturer, count, user, "
                                     "assignedto, comment, changedate FROM inventory_history WHERE SN=123 ")
        itemhistory = cursor.fetchall()
        cursor.commit()
        cursor.close()

        return render_template('edit.html', itemdata=itemdata, itemhistory=itemhistory)

    if request.method == "POST":
        cursor = connection.cursor()
        newdetails = request.form
        office = newdetails['office']
        product = newdetails['product']
        name = newdetails['name']
        sn = newdetails['SN']
        manufacturer = newdetails['manufacturer']
        count = newdetails['count']

        cursor.execute("UPDATE inventory SET office=?, product=?, name=?, sn=?, manufacturer=?,"
                       " count=? WHERE id=1", (office, product, name, sn, manufacturer, count))
        cursor.commit()
        cursor.close()
        return redirect('/inventory')


@app.route('/assign', methods=['GET', 'POST'])
def assign():
    if not session.get('user'):
        return redirect('/')

    if request.method == 'GET':
        cursor = connection.cursor()
        assigndata = cursor.execute("SELECT office, product, name, SN, manufacturer, count FROM inventory"
                                    " WHERE id = 1 ")
        assigndata = cursor.fetchall()
        cursor.commit()
        cursor.close()
        return render_template('assign.html', assigndata=assigndata)

    if request.method == 'POST':
        assigneddetails = request.form
        assignedto = assigneddetails['assignedto']
        comment = assigneddetails['comment']
        cursor = connection.cursor()
        cursor.execute(("UPDATE inventory SET assignedto=?, comment=? WHERE id=1"), (assignedto, comment))
        cursor.commit()
        cursor.close()
        return redirect('/inventory')


@app.route('/add', methods=['GET', 'POST'])
def add():
    if not session.get('user'):
        return redirect('/')

    if request.method == 'GET':
        return render_template('add.html')

    if request.method == 'POST':

        errors = False

        inventorydetails = request.form
        office = inventorydetails['office']
        product = inventorydetails['product']
        name = inventorydetails['name']
        sn = inventorydetails['SN']

        if len(sn) < 1:
            flash("SN cannot be blank!")
            errors = True

        manufacturer = inventorydetails['manufacturer']
        count = inventorydetails['count']

        if re.search("['a-z]", count):
            flash('Count must be numbers!')
            errors = True
            print(type(count))

        if errors:
            return render_template('add.html')

        else:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO inventory(office, product, name, SN, manufacturer, count)"
                           " VALUES(?, ?, ?, ?, ?, ?)", (office, product, name, sn, manufacturer, count))
            cursor.commit()
            cursor.close()

            return redirect('/inventory')


@app.route('/history', methods=['GET'])
def history():
    if request.method == 'GET':
        cursor = connection.cursor()
        history_data = cursor.execute("SELECT action, office, product, name, SN, manufacturer, count, username, "
                                      "assignedto, comment, changedate count FROM inventory_history")
        history_data = cursor.fetchall()
        cursor.commit()
        cursor.close()
        return render_template('history.html', history_data=history_data)


@app.route('/logout')
def logout():
    if not session.get('user'):
        return redirect('/')

    session.pop('user')
    return redirect('/')
