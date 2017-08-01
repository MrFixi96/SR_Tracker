# -*- coding: utf-8 -*-
#!C://python//python.exe

from flask import Flask, url_for, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from sqlite3 import dbapi2 as sqlite3
import flask_jsonpify, sqlite3, os


# Connect to DB
conn = sqlite3.connect('sreq.db')
db_connect = create_engine('sqlite:///sreq.db')


# Instantiate app object
app = Flask(__name__)
api = Api(app)


# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'sr_tracker.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('sr_tracker_SETTINGS', silent=True)

####Debug Printing
#DEBUG=0
DEBUG=1


#########################################################################################
#	Global Variables								#
#########################################################################################


########****************OLD CODE*******REMOVE ME************************************#####
# Get the list of parameters passed by html form
# my $action = $request->param("action");
# my $name = $request->param("name");
# my $assetNumber = $request->param("assetNumber");
# my $errorType = $request->param("errorType");
# my $email = $request->param("email");
# my $description = $request->param("description");
# my $priorityLevel = $request->param("priorityLevel");
# my $OS = $request->param("OS");
# my $record = $request->param("record");
# my $status= $request->param("status");
# my $RegID= $request->param("RegID");
# my $assigned= $request->param("assigned");
# my $timeStart= $request->param("timeStart");
# my $timeStop= $request->param("timeStop");
# my $resolution= $request->param("resolution");
# my $owner = "IT Services";
# my $user= $request->param("pass");
# my $pass= $request->param("pass");
# my $loginID= $request->param("loginID");
# my $loggedIN = "0";
# my $cookie1;
# my $cookie2;
########****************OLD CODE*******REMOVE ME************************************#####


insert_script = "INSERT INTO incidents ( Name, Email, AssetTag, Priority, Status, ErrorType, Description, OS) VALUES ( ?, ?, ?, ?, ?, ?, ?, ?)"


#########################################################################################
#	MAIN										#
#########################################################################################
#Purpose: Starts program

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
    cur = db.execute('select ID_NUM, SR_NUMBER, SITE_NAME, SITE_ID, SEVERITY, ISSUE, SERIAL_NUMBER from incidents order by SR_NUMBER')
    entries = cur.fetchall()
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into incidents (ID_NUM, SR_NUMBER, SITE_NAME, SITE_ID, SEVERITY, ISSUE, SERIAL_NUMBER) values (?, ?, ?, ?, ?, ?, ?)',
               [request.form['title'], request.form['text']])
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

###Do we need to disconnect from DB?

if __name__ == '__main__':
     app.run(port='7000')
