# -*- coding: utf-8 -*-
"""
Created on Mon Jul 22 07:55:50 2019

@author: ingri
"""

from flask import Flask, flash, request, session, redirect, render_template, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['SECRET_KEY']='secretkey'
app.config['MONGO_DBNAME'] = 'MercaDelivery'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/MercaDelivery'

mongo = PyMongo(app)
logueado=False
mi_carro=[]
mis_ordenes=[]
n_carrito=0
cantidad_pedidos=0
subtotal=0
categories=[]

def set_categorias():
    categ=mongo.db.categorias
    categories= list(categ.find({}))

def set_carrito():
    if 'username' in session:
        carro = mongo.db.carrito
        app.mi_carro=list(carro.find({'correo': session['username']}))
        app.n_carrito=len(app.mi_carro)

def set_ordenes():
    orden= mongo.db.ordenes
    mis_ordenes=list(orden.find({'correo': session['username']}))

    cantidad_pedidos=0
    #Esto es para saber la cantidad de pedidos que tiene
    for ordenes in mis_ordenes:
        if cantidad_pedidos < ordenes['numero']:
            cantidad_pedidos = ordenes['numero']

def set_subtotal():
    if 'username' in session:
        for elemento in mi_carro:
            precio = elemento['precio']
            cantidad= elemento['cantidad']
            subtotal = subtotal + (precio*cantidad)

#Pasa el carrito y las ordenes de la persona logueada a todas las paginas
@app.context_processor
def para_todos():
    return dict(logueado=logueado, carro=mi_carro, n_carro=n_carrito, orden=mis_ordenes, n_ordenes=cantidad_pedidos, categorias=categories, subtotal=subtotal)

@app.route('/')
def index():
    if 'username' in session:
        logueado=True
        set_carrito()
    categorias=list(mongo.db.categorias.find())
    productos=mongo.db.articulos
    articulos=list(productos.find({}))

    return render_template('index.html', categorias=categorias, articulos=articulos, logueado=logueado, carrito=app.mi_carro, carro=app.n_carrito)


@app.route('/logout')
def logout():
    logueado=False
    categorias=list(mongo.db.categorias.find())
    productos=mongo.db.articulos
    articulos=list(productos.find({}))

    return render_template('index.html', categorias=categorias, articulos=articulos, logueado=logueado)

@app.route('/login', methods=['POST','GET'])
def login():
    error=None
    correos = mongo.db.usuarios
    if request.method == 'POST':
        login_user = correos.find_one({'correo' : request.form['email']})
        print(login_user)

        if login_user:
            if request.form['pass'].encode('utf-8') == login_user['password'].encode('utf-8'):
                session['username'] = request.form['email']
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

    #Hago una listas de diccionario [{id: adkn, nombre: 'Piña', 'cantidad': 0, 'categoria': 'Frutas', 'descripcion':'algo', 'detalles':'algo mas ', 'precio': '1.05'}, {producto 2...}]
    catalogo = list(productos.find({})) 

    #Pasando la lista manejo la carga de los productos desde el html (Linea 230)
    return render_template('shop-grid.html', catalogo=catalogo, categorias=categorias,categoria_en_seleccion=categoria_en_seleccion, carrito=app.mi_carro, carro=app.n_carrito, logueado=logueado)

@app.route('/producto/<articulo>', methods=['POST', 'GET'])
def single_product(articulo):
    if 'username' in session:
        logueado = True
        set_carrito()
    productos=mongo.db.articulos
    catalogo_frutas = len(list(productos.find({'categoria':'Frutas'})))
    catalogo_verduras = len(list(productos.find({'categoria':'Verduras'})))
    mensaje=None
    display=productos.find_one({'nombre': articulo})
    print(catalogo_frutas, catalogo_verduras, display)

    if request.method == 'POST':
        if request.form['anadir'] == "Añadir al carrito":
            carrito=mongo.db.carrito
            carrito.insert({'correo' : session['username'], 'nombre' : articulo,'cantidad': int(request.form['qty']) ,'precio':display['precio']})
            mensaje="Ya fue agregado al carrito"

    return render_template('single-product.html', articulo=articulo, display=display , n_frutas=catalogo_frutas, n_verduras=catalogo_verduras, carrito=app.mi_carro, carro=app.n_carrito, logueado=logueado,mensaje=mensaje)

@app.route('/cart/')
def carrito():
    if 'username' in session:
        logueado=True
        set_carrito()
    categorias=list(mongo.db.categorias.find())
    productos=mongo.db.articulos
    articulos=list(productos.find({}))
    subtotal=0
    delivery=4.50
    car = mongo.db.carrito
    carrito = list(car.find({'correo':session['username']}))

    for item in carrito:
        subtotal= subtotal + float(item['precio']) * int(item['cantidad'])

    return render_template('cart.html', ccarrito=carrito, cant=len(carrito), categorias=categorias, articulos=articulos, carrito=app.mi_carro, carro=app.n_carrito, logueado=logueado, sub=subtotal, deli=delivery)

if __name__ == '__main__':
    app.run(debug=True)