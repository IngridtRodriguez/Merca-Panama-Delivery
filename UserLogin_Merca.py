# -*- coding: utf-8 -*-

from flask import Flask, flash, request, session, redirect, render_template, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)


app.config['SECRET_KEY']='secretkey'

#Configurando la base de datos con la que se conecta
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

#Para obtener las categorias en la base de datos
def set_categorias():
    categ=mongo.db.categorias
    categories= list(categ.find({}))

#Para obtener el carrito del usuario en la base de datos, si es que hay una sesión abierta
def set_carrito():
    if 'username' in session:
        carro = mongo.db.carrito
        app.mi_carro=list(carro.find({'correo': session['username']}))
        app.n_carrito=len(app.mi_carro)

#Para borrar producto del carrito
def del_carrito(product):
    if 'username' in session:
        temp = mongo.db.carrito
        temp.remove({'correo': session['username'], 'nombre': product})

#Obtiene las ordenes del usuario (No ha sido implementado)
def set_ordenes():
    orden= mongo.db.ordenes
    mis_ordenes=list(orden.find({'correo': session['username']}))

    cantidad_pedidos=0
    '''Esto es para saber la cantidad de pedidos que tiene el usuario
        En la base de datos, los ordenes se registran por artículo comprado
        Si una orden tiene multiples frutos o verduras, cada documento o "fila" tiene el mismo número de orden
    '''
    for ordenes in mis_ordenes:
        if cantidad_pedidos < ordenes['numero']:
            cantidad_pedidos = ordenes['numero']

#Obtener el subtotal a pagar, si es que hay una sesión abierta
def set_subtotal():
    if 'username' in session:
        for elemento in mi_carro:
            precio = elemento['precio']
            cantidad= elemento['cantidad']
            subtotal = subtotal + (precio*cantidad)


@app.context_processor
def para_todos():
    """
    Esta función se encarga de inyectar variables automaticamente en el contexto de los templates (html's).
    Pasa el subtotal (con un formato) de la persona logueada a todas las paginas
    Esto es fundamental para el caso del header.html, ya que el header tiene el icono de carrito
    Header.html se repite en todas las páginas, asi solo se programa un vez y solo es incluido en otro html (por ejemplo, index)
    """
    def get_subtotal(carrito):
        """
        El context processor get_subtotal hace que la variable llamada get_subtotal esté disponible en todos los templates.
        Además, lo pasa en un cierto formato (de dos puntos decimales). Desde un template se pasará de la siguiente forma:
        {{get_subtotal(carrito)}}

        :param carrito: Diccionario que se recupera de la base de datos con datos del carrito del usuario en sesión actualmente.
        
        :return: get_subtotal
        """

        if 'username' in session:
            subtotal=0
            for elemento in carrito:
                precio = elemento['precio']
                cantidad= elemento['cantidad']
                subtotal = subtotal + (precio*cantidad)
            return '{0:.2f}'.format(subtotal)
    return {'get_subtotal': get_subtotal}

#######COMENZANDO A ASIGNAR LAS RUTAS#########

@app.route('/')
def index():
    """
    Ruta de la pagina principal, se ingresa a ella escribiendo la ruta localhost/
    
    :return: template index.html con todos los artículos en la base de datos
    """

    #si hay un username en la variable sesión
    if 'username' in session:
        logueado=True
        set_carrito()
    #Aunque no haya user logueado, se muestra las categorias y se cargan en las opciones
    categorias=list(mongo.db.categorias.find())
    productos=mongo.db.articulos
    articulos=list(productos.find({}))

    return render_template('index.html', categorias=categorias, articulos=articulos, logueado=logueado, carrito=app.mi_carro, n_carro=app.n_carrito)

@app.route('/logout')
def logout():
    logueado=False
    categorias=list(mongo.db.categorias.find())
    productos=mongo.db.articulos
    articulos=list(productos.find({}))

    return render_template('index.html', categorias=categorias, articulos=articulos, logueado=logueado)


@app.route('/contacto')
def about():
    """
    Ruta de contacto. Se entra en ella poniendo en url localhost/contacto
    
    :return: template contacto.html
    """
    if 'username' in session:
        logueado = True
        set_carrito()
    categorias = list(mongo.db.categorias.find())
    productos = mongo.db.articulos
    articulos = list(productos.find({}))

    return render_template('contacto.html', categorias=categorias, articulos=articulos, logueado=logueado, carrito=app.mi_carro, n_carro=app.n_carrito)

@app.route('/login', methods=['POST','GET'])
def login():
    """
    Ruta para el inicio de sesión. Se ingresa a ella con localhost/login
    Se especifica los métodos utilizados ya que aquí se obtendrá datos si se presiona un submit
    La función login utiliza método POST para detectar los request a ingreso de datos. 
    
    :return: template login.html
    :return: error
    """
    #Mensaje de error que se pasará al html y será manejado con Jinja
    error=None
    #Base de datos, collection o tabla usuarios 
    correos = mongo.db.usuarios

    if request.method == 'POST':
        #Buscando el usuario con el correo que se metió en el input llamado email
        login_user = correos.find_one({'correo' : request.form['email']})

        #De existir el usuario se compara la contraseña de él con la contraseña en input llamado pass
        if login_user:
            if request.form['pass'].encode('utf-8') == login_user['password'].encode('utf-8'):
                session['username'] = request.form['email']
                return redirect(url_for('index'))
        #Si no se encontró al usuario se muestra un error en el html
        else:
            error="Datos erroneos"
    return render_template('login.html', error=error)

@app.route('/register', methods=['POST', 'GET'])
def registrar():
    """
    Ruta para el registro, se entra a ella con localhost/register
    Maneja entrada de datos, se especifica método POST
    
    :return: template register.html
    :return: error
    """
    error=None #Esto es para tirar el error de que ya existe usuario que sale en el html (linea 212)
    if request.method == 'POST':
        #Si se presiona el botón registrarse dentro de un form verifico si el usuario ya tiene cuenta
        if request.form['registrarse'] == 'Registrarse':
            usuarios = mongo.db.usuarios
            existing_user = usuarios.find_one({'correo' : request.form['email']})
            print(existing_user)

            if existing_user:
                error="Esta cuenta ya existe "
            #El usuario no existe todavia, se inserta a la base de datos
            elif existing_user is None: 
                usuarios.insert({'correo' : request.form['email'], 'password' : request.form['pass'],'tipo':'cliente'})
                #session['username'] = request.form['username']
                return redirect(url_for('index'))
        #En se presiona el botón de login, se redirige a la ruta login
        elif 'ingresa' in request.form:
            return redirect(url_for(login))
    return render_template('register.html', error=error)

@app.route('/shop-grid', defaults={'categoria_en_seleccion':'Frutas'})
@app.route('/shop-grid/<categoria_en_seleccion>')
def shop_grid(categoria_en_seleccion):
    """
    Ruta para catalogo, se ingresa a ella con localhost/shop-grid/. Por default abre las frutas
    Utiliza URL converter, lo que da la capacidad de crear un URL dinámico. 
    Es decir, se utiliza parte del URL como una variable de búsqueda de productos por categoría
    Por default la categoría en selección son las Frutas.

    :param categoria_en_seleccion: Variable Dinamica

    :return: template shop-grid.html
    :return: categoria_en_seleccion
    """
    catalogo = []
    productos=mongo.db.articulos
    categorias=list(mongo.db.categorias.find())

    #Hago una listas de diccionario [{id: adkn, nombre: 'Piña', 'cantidad': 0, 'categoria': 'Frutas', 'descripcion':'algo', 'detalles':'algo mas ', 'precio': '1.05'}, {producto 2...}]
    catalogo = list(productos.find({})) 

    #Pasando la lista manejo la carga de los productos desde el html (Linea 230)
    return render_template('shop-grid.html', catalogo=catalogo, categorias=categorias,categoria_en_seleccion=categoria_en_seleccion, carrito=app.mi_carro, n_carro=app.n_carrito, logueado=logueado)

@app.route('/producto/<articulo>', methods=['POST', 'GET'])
def single_product(articulo):
    """
    Ruta de los productos. Se ingresa a ella con localhost/producto/Piña o localhost/producto/Naranja o desde la página de catalogo
    Justo como con el catalogo, utiliza URL converter para pasar URL como variables (En este caso, el artículo)
    <articulo> se pasa desde el shop-grid donde se le dé click a un producto
    
    También utiliza método POST en caso de Añadir un producto al carrito
    
    :param articulo: Variable dinamica 
    
    :return: template single-product.html
    :return: articulo
    """
    if 'username' in session:
        logueado = True
        set_carrito()
    productos = mongo.db.articulos
    catalogo_frutas = len(list(productos.find({'categoria': 'Frutas'})))
    catalogo_verduras = len(list(productos.find({'categoria': 'Verduras'})))
    mensaje = None
    display = productos.find_one({'nombre': articulo}) #Aqui busco detalles del producto escogido en mongodb

    if request.method == 'POST':
        #Si se presiona boton añadir al carrito entonces se agrega al carrito del usuario en sesión y la cantidad que especifica en el input qty
        if request.form['anadir'] == "Añadir al carrito":
            carrito = mongo.db.carrito
            carrito.insert({'correo': session['username'], 'nombre': articulo, 'cantidad': int(request.form['qty']),
                            'precio': display['precio']})
            mensaje = "Ya fue agregado al carrito"

    return render_template('single-product.html', articulo=articulo, display=display, n_frutas=catalogo_frutas, n_verduras=catalogo_verduras, carrito=app.mi_carro, n_carro=app.n_carrito, logueado=logueado, mensaje=mensaje)

@app.route('/cart/')
def carrito():
    """
    Ruta para el carrito. Se entra a ella con localhost/cart
    Esta función se encarga de mostrar todos los artículos y cantidades guardadas en cierta sesión.
    Desde esta página se lleva a la pagina de pago al presionar un botón de tramitar.

    :return: template cart.html
    """
    if 'username' in session:
        logueado=True
    categorias=list(mongo.db.categorias.find())
    productos=mongo.db.articulos
    articulos=list(productos.find({}))
    subtotal=0
    delivery=4.50
    car = mongo.db.carrito
    carrito = list(car.find({'correo':session['username']})) #Trayendo el carrito del usuario

    for item in carrito:
        subtotal= subtotal + float(item['precio']) * int(item['cantidad'])

    return render_template('cart.html', ccarrito=carrito, cant=len(carrito), categorias=categorias, articulos=articulos, carrito=app.mi_carro, n_carro=app.n_carrito, logueado=logueado, sub=subtotal, deli=delivery)

@app.route('/pago', methods=['POST','GET'])
def checkout():
    """
    Esta función se encarga del pago de la orden del carrito.
    Tiene dos formularios: uno de actualización de datos y dirección de vivienda y otro de Pago
    Al actualizar datos de la dirección de vivienda se abre el Collection usuarios y edita estos campos.
    Al pagar la base de datos resta la cantidad de artículos disponibles en el Collection articulos y borra el carrito del usuario.

    :return: template checkout.html
    """
    direccion_agregada=None
    usuarios = mongo.db.usuarios
    existing_user = usuarios.find_one({'correo' : session['username']})
    sub=0
    car = mongo.db.carrito
    carrito = list(car.find({'correo':session['username']}))

    for item in carrito:
        sub= sub + float(item['precio']) * int(item['cantidad'])
    pago=None
    if request.method == 'POST':
        if 'guardar' in request.form:
            mongo.db.usuarios.update({'correo':session['username']},{"$set":{'nombre':request.form['Nombre'],'apellido':request.form['Apellido'], 'direccion':request.form['Direccion'], 'barriada':request.form['Barriada'] , 'telefono':request.form['Telefono']}})
            direccion_agregada=True
            return redirect(url_for('checkout'))

        #Si se presiona el botón pagar
        elif 'pagar' in request.form:
            for item in carrito:
                articulo=mongo.db.articulos.find_one({'nombre':item['nombre']})
                #Se actualiza la cantidad de articulos en la base de datos.
                #se obtiene cantidad de productos y se resta la cantidad que se pidió en el carrito
                mongo.db.articulos.update({'nombre':item['nombre']},{"$set":{'cantidad': (articulo['cantidad'] - item['cantidad']) }})
            mongo.db.carrito.remove({'correo':session['username']})
            pago=True
    return render_template('checkout.html', usuario=existing_user, subtotal=sub, carrito=carrito, pago=pago)

@app.route('/eliminar/<articulo>')
def eliminarcarrito(articulo):
    if 'username' in session:
        logueado=True
        del_carrito(articulo)

    categorias=list(mongo.db.categorias.find())
    productos=mongo.db.articulos
    articulos=list(productos.find({}))
    subtotal=0
    car = mongo.db.carrito
    carrito = list(car.find({'correo':session['username']}))
    for item in carrito:
        subtotal= subtotal + float(item['precio']) * int(item['cantidad'])
    return render_template('cart.html', ccarrito=carrito, cant=len(carrito), categorias=categorias, articulos=articulos, carrito=app.mi_carro, n_carro=app.n_carrito, logueado=logueado, sub=subtotal)

if __name__ == '__main__':
    app.run(debug=True)