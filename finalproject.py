from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response
import random
import string
import httplib2
import json
import requests
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

# Connect to database and create db session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from database_setup import Grudget, Base, Grudge, User
engine = create_engine(
                'sqlite:///grudgebucketwithusers.db',
                connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Grudget Catalog"

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    with open('client_secrets.json', 'r') as file:
        CLIENT_ID = json.load(file)['web']['client_id']
    # Verify Anti Forgery State Token received from client
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store authorization code received from client
    code = request.data
    # Exchange authorization code with Google for a credentials object
    try:
        # Create a Flow object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # Exchange authorization code for a credentials token
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if access token is valid/working
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Handle error if access token is not valid
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if access token is for the right user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
                   json.dumps("Token's user ID doesn't match given user ID."),
                   401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if access token is for the right application
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
                   json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response
    # Verify if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store access token for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user details (name and email) from Google API
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    login_session['picture'] = data['picture']
    # Check if the user already exists in the database
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    # Send Response back to the client
    output = ''
    output += '<h1>Welcome '
    output += login_session['username']
    output += login_session['email']
    output += login_session['picture']
    output += '</h1>'
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    flash("createUserfunction with login_session was called")
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    flash("getUserFunction with user_id was called")
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


# Disconnect based on provider
@app.route('/logout')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showGrudgets'))
    else:
        flash("You were not logged in")
        return render_template('publicgrudgets.html')


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        response = redirect(url_for('showGrudgets'))
        flash("You are now logged out.")
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view the Grudge Buckets aka Grudgets and Grudges
@app.route('/grudget/<int:grudget_id>/grudge/JSON')
def grudgetGrudgeJSON(grudget_id):
    grudget = session.query(Grudget).filter_by(id=grudget_id).one()
    grudges = session.query(Grudge).filter_by(grudget_id=grudget.id).all()
    return jsonify(Grudge=[i.serialize for i in grudges])


@app.route('/grudget/<int:grudget_id>/grudge/<int:grudge_id>/JSON')
def grudgeJSON(grudget_id, grudge_id):
    grudge = session.query(Grudge).filter_by(id=grudge_id).one()
    return jsonify(grudge=Grudge.serialize)


@app.route('/grudget/JSON')
def grudgetsJSON():
    grudgets = session.query(Grudget).all()
    return jsonify(grudget=[g.serialize for g in grudgets])


# Home Page, show all grudgets - grudge categories
@app.route('/')
@app.route('/grudget/', methods=['GET'])
def showGrudgets():
    grudgets = session.query(Grudget).all()
    if 'username' not in login_session:
        flash("You are not logged in.")
        return render_template('publicgrudgets.html',
                               grudgets=grudgets, username=None)
    else:
        return render_template('grudgets.html',
                               grudgets=grudgets,
                               username=login_session['username'])


# Create a new grudge bucket aka grudget
@app.route('/grudget/new/', methods=['GET', 'POST'])
def newGrudget():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newGrudget = Grudget(name=request.form['name'],
                             user_id=login_session['user_id'])
        session.add(newGrudget)
        session.commit()
        return redirect(url_for('showGrudgets'))
    else:
        return render_template('newGrudget.html',
                               username=login_session['username'])


# Edit a grudge bucket - anyone logged in can edit
@app.route('/grudget/<int:grudget_id>/edit/', methods=['GET', 'POST'])
def editGrudget(grudget_id):
    editedGrudget = session.query(Grudget).filter_by(id=grudget_id).one()
    # user = session.query(User).filter_by(id=user_id).one()
    creator = getUserInfo(editedGrudget.user_id)
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if request.form['name']:
            editedGrudget.name = request.form['name']
            return redirect(url_for('showGrudgets'))
    else:
        return render_template('editGrudget.html',
                               grudget=editedGrudget,
                               username=login_session['username'])


# # Delete a grudge bucket - Protected
@app.route('/grudget/<int:grudget_id>/delete/', methods=['GET', 'POST'])
def deleteGrudget(grudget_id):
    grudgetToDelete = session.query(Grudget).filter_by(id=grudget_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if login_session['user_id'] == grudgetToDelete.user_id:
        if request.method == 'POST':
            session.delete(grudgetToDelete)
            session.commit()
            flash("Grudget deleted")
            return render_template('main.html',
                                   username=login_session['username'])
        else:
            return render_template('deleteGrudget.html',
                                   grudget=grudgetToDelete,
                                   username=login_session['username'])
    else:
        flash("You can edit this grudget but you cannot delete it.")
        return redirect('/')


# Show a grudge
@app.route('/grudget/<int:grudget_id>/')
@app.route('/grudget/<int:grudget_id>/grudge/')
def showGrudge(grudget_id):
    grudget = session.query(Grudget).filter_by(id=grudget_id).first()
    creator = getUserInfo(grudget.user_id)
    grudges = session.query(Grudge).filter_by(grudget_id=grudget_id).all()
    if 'username' not in login_session:
        return render_template('publicgrudges.html',
                               grudges=grudges,
                               id=grudget_id,
                               grudget=grudget,
                               creator=creator,
                               username=None)
    else:
        return render_template('showgrudge.html',
                               grudges=grudges,
                               id=grudget_id,
                               grudget=grudget,
                               creator=creator,
                               username=login_session['username'])


# Create a new grudge
@app.route('/grudget/<int:grudget_id>/grudge/new/', methods=['GET', 'POST'])
def newGrudge(grudget_id):
    if 'username' not in login_session:
        return redirect('/login')
    grudget = session.query(Grudget).filter_by(id=grudget_id).one()
    creator = getUserInfo(grudget.user_id)
    # user_id=login_session['user_id']
    # if login_session['user_id'] != grudget.user_id:
    #      flash("You cannot edit this grudge.")
    # return redirect('/')
    if request.method == 'POST':
            newGrudge = Grudge(
                name=request.form['name'],
                description=request.form['description'],
                processed=request.form['processed'],
                takeaway=request.form['takeaway'],
                grudget_id=grudget_id,
                user_id=login_session['user_id'])
            session.add(newGrudge)
            session.commit()
            return redirect(url_for('showGrudge',
                                    grudget=grudget,
                                    grudget_id=grudget_id,
                                    creator=creator))
    else:
        return render_template('newgrudge.html',
                               grudget_id=grudget_id,
                               creator=creator)


# # Edit a grudge - Protected
@app.route('/grudget/<int:grudget_id>/grudge/<int:grudge_id>/edit',
           methods=['GET', 'POST'])
def editGrudge(grudget_id, grudge_id):
    if 'username' not in login_session:
        return redirect('/login')
    grudget = session.query(Grudget).filter_by(id=grudget_id).first()
    grudge = session.query(Grudge).filter_by(id=grudge_id).first()
    editgrudge = session.query(Grudge).filter_by(id=grudge_id).one()
    if login_session['user_id'] != grudge.user_id:
        flash("You cannot edit this grudge")
        return redirect('/')
    if request.method == 'POST':
        if request.form['name']:
            editgrudge.name = request.form['name']
        if request.form['description']:
            editgrudge.description = request.form['description']
        if request.form['processed']:
            editgrudge.processed = request.form['processed']
        if request.form['takeaway']:
            editgrudge.takeaway = request.form['takeaway']
        session.add(editgrudge)
        session.commit()
        return redirect(url_for('showGrudge', grudget_id=grudget_id))
    else:
        return render_template('editgrudge.html',
                               grudget_id=grudget_id,
                               grudge_id=grudge_id,
                               grudge=editgrudge)


# # Delete a grudge - Protected -
@app.route('/grudget/<int:grudget_id>/grudge/<int:grudge_id>/delete',
           methods=['GET', 'POST'])
def deleteGrudge(grudget_id, grudge_id):
    if 'username' not in login_session:
        return redirect('/login')
    grudget = session.query(Grudget).filter_by(id=grudget_id).first()
    grudge = session.query(Grudge).filter_by(id=grudge_id).first()
    grudgeToDelete = session.query(Grudge).filter_by(id=grudge_id).one()
    if login_session['user_id'] != grudge.user_id:
        flash("You cannot delete this grudge")
        return redirect('/')
    if request.method == 'POST':
        session.delete(grudgeToDelete)
        session.commit()
        return redirect(url_for('showGrudge', grudget_id=grudget_id))
    else:
        return render_template('deletegrudge.html',
                               grudget_id=grudget_id,
                               grudge=grudgeToDelete)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
