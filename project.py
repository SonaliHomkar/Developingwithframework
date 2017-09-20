## import database and sqlalchemy for CRUD operations ##
from database_setup import Base,Restaurant,MenuItem,User
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
                newRestaurant = Restaurant(name = request.form['txtName'],user_id = login_session['user_id'])
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
                                   user_id = login_session['user_id'],
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

# a method to call the facebook server to run the api
@app.route('/fbconnect',methods=['POST'])
def fbconnect():
        
        if request.args.get('state') != login_session['state']:
                response = make_response(json.dumps('Invalid state parameter.'), 401)
                response.headers['Content-Type'] = 'application/json'
                return response
        access_token = request.data

        app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
        app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
        url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]

         # Use token to get user info from API
        userinfo_url = "https://graph.facebook.com/v2.8/me"
        '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
        '''
        token = result.split(',')[0].split(':')[1].replace('"', '')

        url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        # print "url sent for API access:%s"% url
        output = "API JSON result: %s" % result
        
        
        data = json.loads(result)
        login_session['provider'] = 'facebook'
        login_session['username'] = data["name"]
        #login_session['email'] = data["email"]
        login_session['facebook_id'] = data["id"]
        
        # The token must be stored in the login_session in order to properly logout
        login_session['access_token'] = token

        # Get user picture
        url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
        h = httplib2.Http()
        result = h.request(url, 'GET')[1]
        data = json.loads(result)

        login_session['picture'] = data["data"]["url"]

        # see if user exists
        '''
        user_id = getUserID(login_session['email'])
        if not user_id:
        '''
        user_id = createUser(login_session)
        login_session['user_id'] = user_id
        
        
        output = ''
        output += '<h1>Welcome, '
        output += login_session['username']

        output += '!</h1>'
        output += '<img src="'
        output += login_session['picture']
        output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

        flash("Now logged in as %s" % login_session['username'])
        return output

# Method to call FB server to disconnect and delete the token
@app.route('/fbdisconnect')
def fbdisconnect():
        facebook_id = login_session['facebook_id']
        access_token = login_session['access_token']
        url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
        del login_session['provider'] 
        del login_session['username'] 
        del login_session['facebook_id'] 
        del login_session['access_token'] 
        del login_session['picture']
        del login_session['user_id'] 
        return "you have been logged out"
    


# a method to call the google server to run the api
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
    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = getUserId(login_session['email'])
    if  not user_id:
            user_id = createUser(login_session)
            strUser = "New User"
    else:
            strUser = ("User Already exist")

    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += 'status : ' + strUser
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

def createUser(login_session):
        newUser = User(name=login_session['username'],
                       email=login_session['username']+"@yahoo.com",
                       picture=login_session['picture'])
        session.add(newUser)
        session.commit()
        user = session.query(User).filter_by(id=newUser.id).one()
        return user.id

def getUserInfo(user_id):
        user = session.query(User).filter_by(id=user_id).one()
        return user

def getUserId(email):
        try:
                user = session.query(User).filter_by(email=login_session['email']).one()
                return user.id
        except:
                return None

        
        
@app.route("/logout")
def logout():
        if login_session['provider'] == "google":
                gdisconnect()
        if login_session['provider'] == 'facebook':
                fbdisconnect()
        flash("you have been successfully logged out!!")
        return redirect(url_for('showLogin'))
                
                
                
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
