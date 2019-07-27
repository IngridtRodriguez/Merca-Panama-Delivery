# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 07:55:50 2019

@author: ingri
"""

from flask import Flask, request, session, redirect, render_template, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'MercaDelivery'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/MercaDelivery'

mongo = PyMongo(app)

@app.route('/')
def index():
    #if 'username' in session:
    #   return 'You are logged in as ' + session['username']
    return render_template('index.html')

@app.route('/login', methods=['POST','GET'])
def login():
    correos = mongo.db.usuarios
    login_user = correos.find_one({'correo' : request.form['email']})

    if login_user:
        if request.form['pass'].encode('utf-8') == login_user['password'].encode('utf-8'):
            #session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

#@app.route('/register', methods=['POST', 'GET'])
#def iniciar_sesion():
#    return render_template('login.html')

@app.route('/register', methods=['POST', 'GET'])
def registrar():
    if request.method == 'POST':
        if request.form['registrarse'] == 'Registrarse':
            print("entré a registrarse")
            users = mongo.db.users
            existing_user = users.find_one({'correo' : request.form['email']})
    
            if existing_user is None:
                users.insert({'correo' : request.form['correo'], 'password' : request.form['pass']})
                #session['username'] = request.form['username']
                return redirect(url_for('index'))
            return 'That username already exists!'
    
    return render_template('register.html')

if __name__ == '__main__':
    #app.secret_key = 'mysecret'
    app.run(debug=True)