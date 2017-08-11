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
#########################################################################################
#	Flask App Config                                    								#
#########################################################################################
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
app.config.from_envvar('sr_tracker_SETTINGS', silent=True)

#########################################################################################
#	File Handling Global Variables								                        #
#########################################################################################
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

#########################################################################################
#   Debug Printing                                                                      #
#########################################################################################
# DEBUG_PRINT = 0
DEBUG_PRINT = 1
DEBUG = 1

#########################################################################################
#	Global Variables								                                    #
#########################################################################################
post_string = str('insert into incidents (SR_NUMBER, SITE_NAME, SITE_ID, SEVERITY, ISSUE, SERIAL_NUMBER, CREATE_DATE) \
                values (?, ?, ?, ?, ?, ?, ?)')
get_string = str('select ID_NUM, SR_NUMBER, SITE_NAME, SITE_ID, SEVERITY, ISSUE, SERIAL_NUMBER from incidents order \
                    by SR_NUMBER')

#########################################################################################
#	MAIN										                                        #
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

#########################################################################################
#   DB Functions
#########################################################################################

conn = sqlite3.connect('sr_tracker.db')
db_connect = create_engine('sqlite:///sr_tracker.db')


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


#########################################################################################
#   Show Entries
#########################################################################################

@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute(get_string)
    entries = cur.fetchall()
    if DEBUG_PRINT == 1:
        assert (str(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")))
        flash(Markup(datetime.datetime.now().strftime("%d/%m/%Y %H:%M")))
    return render_template('show_entries.html', entries=entries)


#########################################################################################
#   Add Entries
#########################################################################################

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


#########################################################################################
#   Login
#########################################################################################

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


#########################################################################################
#   Logout
#########################################################################################

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


#########################################################################################
#   File Handling Functions
#########################################################################################

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#************************
# URL: /uploads/filename
#************************

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

#************************
# URL: /uploads/
#************************

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

        fieldnames = ('Oracle Service Request #', "Site Name: Site Name", "Site Name: Site ID", "Severity",
                  "Service Request Status", "Date/Time Opened", "Last Modified Date", "Next Customer Contact",
                  "Product Name", "Product ID", "SW Version (Oracle)", "Problem Summary", "Case Owner: Full Name",
                  "Contact Name: Full Name", "Site Name: SAM: Full Name")
        
        #figure out row count for creating objects
        reader = csv.DictReader((line.replace('\0','') for line in csvfile), fieldnames)
        size=len(list(reader))
        #reset the file reader back to begining of file
        csvfile.seek(0, 0)
        reader = csv.DictReader((line.replace('\0','') for line in csvfile), fieldnames)
        
        if DEBUG_PRINT: print("Number of rows is " + str(size))

        #Initialize a list of objects for each row in the file
        instancelist = [SReq(fieldnames) for r in range(size)]

        #Process the rows and set the object attributes
        i = 0
        skip = 0
        if reader:
            for row in reader:
                if DEBUG_PRINT: print("loading row: " + str(row))
                for field, value in row.items():
                    if DEBUG_PRINT: print("loading field: object number " + str(i) + " " +  field + ":" + value)
                    if field == value:
                        skip = 1
                        continue
                    setattr(instancelist[i],str(field),str(value))
                if skip == 1:
                    skip = 0
                    continue
                i += 1

        #Print out our data to see if it worked
        if DEBUG_PRINT: 
            print("Finished loading object")
            for each in instancelist:
                each.print_vals()


            # output = []
            #
            # def generator():
            #     for each in reader:
            #         row = {}
            #         for field in sr.__dict__:
            #             row[field] = each[field]
            #         output.append(row)
            #    yield json.dumps(output)

            #return Response(generator(),
            #                 mimetype="text/plain",
            #                 headers={"Content-Disposition":
            #                              "attachment;filename=file.json"})




    return '''
       <!doctype html>
       <title>Upload new File</title>
       <h1>Upload new File</h1>
       <form method=post enctype=multipart/form-data action="{{ url_for('upload') }}">
         <p><input type=file name=file>
            <input type=submit value=Upload>
       </form>
       '''


#########################################################################################
#   Class: SReq
#########################################################################################

class SReq:
# sr_num, site_name, site_id, sev, status, create_date, modified_date, next_contact, product_name,
#                 serial_num, issue, case_owner, contact_name

    def __init__(self,fieldnames):
        #initialize attributes dynamically
        for field in fieldnames:
            setattr(self,field,"")

        self.description = "This is an object representing the data a SAM needs to know about a Service Request"
        self.author = "James Anderton (james.anderton@dell.com)"

    def describe(self, text):
        self.description = text

    def author(self, text):
        self.author = text

    def print_vals(self):
        for key, value in self.__dict__.items():
            print(str(key) + ":" + str(value))

        print("\n")

    def email(self):
        pass

    def create_url(self):
        pass

    def output_json_obj(self):
        obj = json.JSONEncoder(self.__dict__)
        return obj

    def output_json_file(self):
        output = []

        def generator():
            for each in self.__dict__:
                row = {}
                for field in self.__dict__.items():
                    row[field] = each[field]
                output.append(row)
            yield json.dumps(output)

        return Response(generator(),
                        mimetype="text/plain",
                        headers={"Content-Disposition":
                                     "attachment;filename=file.json"})

    def output_csv_file(self):
        pass
