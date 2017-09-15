## import database and sqlalchemy for CRUD operations ##
from database_setup import Base,Restaurant,MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask,render_template, request, redirect, url_for,flash, jsonify

# code added on 13 sept for login
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
import httplib2
import json
import requests
import string
import random

CLIENT_ID = json.loads(
        open('client_secrets.json','r').read())['web']['client_id']
# end code added on 13 sept for login

app = Flask(__name__)

## create session and connect to database ##
engine = create_engine('sqlite:///restaurantNew.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# display all restaurants
@app.route('/')
@app.route('/restaurants/')
def restaurantList():
        restaurantQuery = session.query(Restaurant).all()
        return render_template('restaurantList.html',restuarant=restaurantQuery)

# create a new restaurant
@app.route('/restaurants/new/', methods = ['GET','POST'])
def newRestaurant():
        if request.method == 'POST':
                newRestaurant = Restaurant(name = request.form['txtName'])
                session.add(newRestaurant)
                session.commit()
                flash("New Restaurant added!!")
                return redirect(url_for('restaurantList'))
        else:        
                return render_template('newRestaurant.html')

# edit Restaurant
@app.route('/restaurants/<int:restaurant_id>/edit/', methods = ['GET','POST'])
def editRestaurant(restaurant_id):
        editRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        if request.method == 'POST':
                editRestaurant.name = request.form['txtName']
                session.add(editRestaurant)
                session.commit()
                flash("Restaurant edited successfully!!")
                return redirect(url_for('restaurantList'))
        else:
                return render_template('editRestaurant.html',i=editRestaurant)

# delete Restaurant
@app.route('/restaurants/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
        deleteRestaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
        if request.method == 'POST':
                session.delete(deleteRestaurant)
                session.commit()
                flash("Restaurant deleted successfully")
                return redirect(url_for('restaurantList'))
        else:
                return render_template('deleteRestaurant.html',i=deleteRestaurant)

        

# display menu of selected restaurant
@app.route('/restaurants/<int:restaurant_id>/')
def restaurantMenu(restaurant_id):
        restaurantId = session.query(Restaurant).filter_by(id = restaurant_id).one()
        Menuitems = session.query(MenuItem).filter_by(restaurant_id = restaurantId.id).all()
        return render_template('menu.html',restaurant=restaurantId,items=Menuitems)

# Task 1 : Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/new/', methods=['GET','POST'])
def newMenuItem(restaurant_id):
        if request.method == 'POST':
                newItem = MenuItem(name = request.form['txtName'],
                                   restaurant_id=restaurant_id,
                                   description = request.form['txtdescription'],
                                   price = request.form['txtprice'],
                                   course = request.form['txtcourse'])
                session.add(newItem)
                session.commit()
                flash("New Menu Item created!!!")
                return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
        else:
                return render_template('newMenuItem.html',restaurant_id=restaurant_id)        

# Task 1 : Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/edit/', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
        editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
        if request.method == 'POST':
                editedItem.name = request.form['txtName']
                session.add(editedItem)
                session.commit()
                flash("Menu Item edited!!!")
                return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
        else:
                return render_template('editMenuItem.html',restaurant_id=restaurant_id,menu_id=menu_id,i=editedItem)
        return "page to edit a menu item ..."

# Task 1 : Create route for newMenuItem function here
@app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/delete/', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id, menu_id):
        deletedItem = session.query(MenuItem).filter_by(id=menu_id).one()
        if request.method == 'POST':
                session.delete(deletedItem)
                session.commit()
                flash("Menu Item Deleted!!!")
                return redirect(url_for('restaurantMenu',restaurant_id=restaurant_id))
        else:
                return render_template('deleteMenuItem.html',restaurant_id=restaurant_id,menu_id=menu_id,i=deletedItem)
        return "page to delete a menu item ..."


# Making an API endpoint(get request) to get the menu of spectified restaurant
@app.route('/restaurants/<int:restaurant_id>/menu/JSON')
def restaurantMenuJason(restaurant_id):
        restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
        items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
        return jsonify(MenuItems=[i.serialize for i in items])

# Making an API endpoint to get the single menu ITem
@ app.route('/restaurants/<int:restaurant_id>/<int:menu_id>/menu/JSON')
def menuItemJason(restaurant_id,menu_id):
        items = session.query(MenuItem).filter_by(id=menu_id).one()
        return jsonify(MenuItems=[items.serialize])

# Making a login page ---code added on 13 Sept
@ app.route('/login')
def showLogin():
        state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                        for x in xrange(32))
        login_session['state'] = state
        return render_template('login.html',STATE = state)

@app.route('/gconnect',methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
            response = make_response(json.dumps('Invalid state parameter'),401)
            response.headers['Content-Type'] = 'application/json'
            return response
    # Obtain authorization code
    code = request.data
    try:
            oauth_flow = flow_from_clientsecrets('client_secrets.json',scope = '')
            oauth_flow.redirect_uri = 'postmessage'
            credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
            response = make_response(json.dumps('Failed to upgrade' +
                                                'the authorization code'),401)
            response.headers['Content-Type'] = 'application/json'
            return response

    # check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url,'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
            response = make_response(json.dumps(result.get('error')),501)
            response.headers['Content-Type'] = 'application/json'
            return response
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
            response = make_response(json.dumps("Token's user id" +
                                                "doesn't match given" +
                                                "user id"), 401)
            response.headers['Content-Type'] = 'application/json'
            return response


    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
            response = make_response(json.dumps("Token's clinet id" +
                                                "doesn't match " +
                                                "app's id"),401)
            print "Token's id doesn't match app's id"
            response.headers['Content-Type'] = 'application/json'
            return response

    # check to see if the user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

                
@app.route("/gdisconnect")
def gdisconnect():
        access_token = login_session.get('access_token')
        if access_token is None:
                response = make_response(json.dumps("Current user is already" +
                                                            "not connected"),401)
                response.headers['Content-Type'] = 'application/json'
                return response
        
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]
        
        if result['status'] == '200':
                del login_session['access_token']
                del login_session['gplus_id']
                del login_session['username']
                del login_session['picture'] 
                del login_session['email']

                response = make_response(json.dumps('Successfully disconnected'),
                                         200)
                response.headers['Content-Type'] = 'application/json'
                return response
        else:
                response = make_response(json.dumps('Failed to revoke token for '+
                                                    'a given user'), 400)
                response.headers['Content-Type'] = 'application/json'
                return response
# --end Making a login page ---code added on 13 Sept

if __name__ == "__main__":
        app.secret_key = 'super_secret_key'
        app.debug = True
        app.run(host = '0.0.0.0', port = 5000)
