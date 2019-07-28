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
                usuarios.insert({'correo' : request.form['email'], 'password' : request.form['pass'],'tipo':'cliente'})
                #session['username'] = request.form['username']
                return redirect(url_for('index'))
        elif 'ingresa' in request.form:
            print("estoy en boton ingresar")
            return redirect(url_for(login))
    return render_template('register.html', error=error)

@app.route('/about')
def about():
    return render_template('contacto.html')

@app.route('/shop-grid', defaults={'categoria_en_seleccion':'Frutas'})
@app.route('/shop-grid/<categoria_en_seleccion>')
def shop_grid(categoria_en_seleccion):
    #catalogo_en_seleccion=
    catalogo = []
    productos=mongo.db.articulos
    categorias=list(mongo.db.categorias.find())
    categoria_en_seleccion=categoria_en_seleccion
    print(categoria_en_seleccion)

    #Hago una listas de diccionario [{id: adkn, nombre: 'Piña', 'cantidad': 0, 'categoria': 'Frutas', 'descripcion':'algo', 'detalles':'algo mas ', 'precio': '1.05'}, {producto 2...}]
    catalogo = list(productos.find({})) 

    #Pasando la lista manejo la carga de los productos desde el html (Linea 230)
    return render_template('shop-grid.html', catalogo=catalogo, categorias=categorias,categoria_en_seleccion=categoria_en_seleccion)

@app.route('/producto/<articulo>')
def single_product(articulo):
    productos=mongo.db.articulos
    catalogo_frutas = len(list(productos.find({'categoria':'Frutas'})))
    catalogo_verduras = len(list(productos.find({'categoria':'Verduras'})))
    
    display=productos.find_one({'nombre': articulo})
    print(catalogo_frutas, catalogo_verduras, display)

    return render_template('single-product.html', articulo=articulo, display=display ,n_frutas=catalogo_frutas, n_verduras=catalogo_verduras)

if __name__ == '__main__':
    app.run(debug=True)