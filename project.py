## import database and sqlalchemy for CRUD operations ##
from database_setup import Base,Restaurant,MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask import Flask,render_template, request, redirect, url_for,flash, jsonify
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
                newItem = MenuItem(name = request.form['txtName'],restaurant_id=restaurant_id)
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

if __name__ == "__main__":
        app.secret_key = 'super_secret_key'
        app.debug = True
        app.run(host = '0.0.0.0', port = 5000)
