# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 07:55:50 2019

@author: ingri
"""

from flask import Flask, flash, request, session, redirect, render_template, url_for
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
    error=None
    correos = mongo.db.usuarios
    if request.method == 'POST':
        login_user = correos.find_one({'correo' : request.form['email']})
        print(login_user)

        if login_user:
            if request.form['pass'].encode('utf-8') == login_user['password'].encode('utf-8'):
            #session['username'] = request.form['username']
                return redirect(url_for('index'))
        else:
            error="Datos erroneos"
    return render_template('login.html', error=error)

@app.route('/register', methods=['POST', 'GET'])
def registrar():
    error=None #Esto es para tirar el error de que ya existe usuario que sale en el html (linea 212)
    if request.method == 'POST':
        if request.form['registrarse'] == 'Registrarse':
            usuarios = mongo.db.usuarios
            existing_user = usuarios.find_one({'correo' : request.form['email']}) #buscando si usuario ya está
            print(existing_user)

            if existing_user:
                error="Esta cuenta ya existe "
            elif existing_user is None: 
                usuarios.insert({'correo' : request.form['email'], 'password' : request.form['pass']})
                #session['username'] = request.form['username']
                return redirect(url_for('index'))
        elif 'ingresa' in request.form:
            print("estoy en boton ingresar")
            return redirect(url_for(login))
    return render_template('register.html', error=error)

@app.route('/about')
def about():
    return render_template('contacto.html')

@app.route('/shop-grid')
def shop_grid():
    return render_template('shop-grid.html')

@app.route('/single-product')
def single_product():
    return render_template('single-product.html')

if __name__ == '__main__':
    #app.secret_key = 'mysecret'
    app.run(debug=True)