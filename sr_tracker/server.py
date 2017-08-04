# -*- coding: utf-8 -*-
# !C://python//python.exe

import csv
import datetime
import json
import os
import sqlite3
import tempfile
from sqlite3 import dbapi2 as sqlite3

from flask import Flask, url_for, request, session, g, redirect, abort, \
    render_template, flash, Markup, send_from_directory, Response
from sqlalchemy import create_engine
from werkzeug.utils import secure_filename

app = Flask(__name__)
# api = Api(app)
app.debug = True

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'sr_tracker.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config.from_envvar('sr_tracker_SETTINGS', silent=True)

# Connect to DB
conn = sqlite3.connect('sr_tracker.db')
db_connect = create_engine('sqlite:///sr_tracker.db')

####Debug Printing
# DEBUG_PRINT = 0
DEBUG_PRINT = 1
DEBUG = 1

#########################################################################################
#	Global Variables								#
#########################################################################################
post_string = str('insert into incidents (SR_NUMBER, SITE_NAME, SITE_ID, SEVERITY, ISSUE, SERIAL_NUMBER, CREATE_DATE) \
                values (?, ?, ?, ?, ?, ?, ?)')
get_string = str('select ID_NUM, SR_NUMBER, SITE_NAME, SITE_ID, SEVERITY, ISSUE, SERIAL_NUMBER from incidents order \
                    by SR_NUMBER')

#########################################################################################
#	MAIN										#
#########################################################################################
# Purpose: Starts program

########****************OLD CODE*******REMOVE ME************************************#####
# # Print the page
# if ($loggedIN = "1"){
# #print $request->header(-cookie=>[$cookie1,$cookie2]);
# set_cookie();
# }else{
# print $request->header;
# }
# print $request->start_html("$owner\'s Request System");
# print $request->h3 ("$owner\'s Request System");

# if($action eq "post")	   {post_entry(); }
# elsif($action eq "Submit") {submit_entry(); }
# elsif($action eq "Admin") {admin_panel(); }
# elsif($action eq "Edit")    {login(); }
# elsif($action eq "Login")   {authenticate();}
# elsif($action eq "Request") {post_task();}
# elsif($action eq "Recall")  {recall_entry(); }
# elsif($action eq "Change")  {change_entry();}
# elsif($action eq "Update")  {update_entry(); }
# elsif($action eq "Kbase")   {kbase_display();}
# elsif($action eq "View Open"){display_requests();}
# elsif($action eq "View Closed"){kbase_display();}
# elsif($action eq "View Tasks") {task_display();}
# elsif($action eq "Report")  {report_panel();}
# else			   { display_requests(); }
########****************OLD CODE*******REMOVE ME************************************#####

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute(get_string)
    entries = cur.fetchall()
    if DEBUG_PRINT == 1:
        assert (str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")))
        flash(Markup(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")))
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    if DEBUG_PRINT == 1:
        assert (str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")))
        flash(Markup(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")))
    db.execute(post_string, [request.form['SR_Number'], request.form['Site_Name'], request.form['Site_ID'],
                             request.form['Severity'], request.form['Issue'], request.form['Serial_Number'],
                               str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")), ])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    file = request.files['file']
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    csvfile = open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'r')
    jsonfile = open(os.path.join(app.config['UPLOAD_FOLDER'], 'file.json'), 'w')
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        flash(Markup(filename))

        fieldnames = ("Oracle Service Request #", "Site Name: Site Name", "Site Name: Site ID", "Severity",
                      "Service Request Status", "Date/Time Opened", "Last Modified Date", "Next Customer Contact",
                      "Product Name", "Product ID", "SW Version (Oracle)", "Problem Summary", "Case Owner: Full Name",
                      "Contact Name: Full Name", "Site Name: SAM: Full Name")
        reader = csv.DictReader(csvfile, fieldnames)

        output = []

        def generator():
            for each in reader:
                row = {}
                for field in fieldnames:
                    row[field] = each[field]
                output.append(row)
            yield json.dumps(output)

        return Response(generator(),
                        mimetype="text/plain",
                        headers={"Content-Disposition":
                                     "attachment;filename=file.json"})

    return '''
       <!doctype html>
       <title>Upload new File</title>
       <h1>Upload new File</h1>
       <form method=post enctype=multipart/form-data action="{{ url_for('upload') }}">
         <p><input type=file name=file>
            <input type=submit value=Upload>
       </form>
       '''
