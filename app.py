import flask
from flask import Flask
from flask import render_template, request, redirect, session
from datetime import datetime    #se usa para respetar nombres incluyendo el time como variable de cambio
from flask import send_from_directory    #obtiene info directamente de la imagen
import os
from flaskext.mysql import MySQL         #extension para usar MySQL en flask
from flask_session import Session


app=Flask(__name__)   #primera aplicacion __name__
app.secret_key="cesan51"
mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'     #enlace a bd de MySQL
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sitio'
mysql.init_app(app)

@app.route('/')                    #se define como base de ruta principal
def inicio():
    return  render_template('sitio/index.html')


@app.route('/img/<imagen>')        #base de ruta para mostrar imagen almacenada
def imagenes(imagen):              #creacion de funcion con variable de almacenamiento variable
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img'),imagen)

@app.route('/css/<archivocss>')        #base de ruta para mostrar imagen almacenada
def css_link(archivocss):              #creacion de funcion con variable de almacenamiento variable
    print(archivocss)
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)


@app.route('/libros')               #creacion de ruta libros
def libros():
    conexion=mysql.connect()             #forma de muestra del almacenamiento
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()                    #agrega el proceso
    print(libros)

    return  render_template('sitio/libros.html',libros=libros)      #el render funciona para renderizar y ubicar el documento en la app


@app.route('/nosotros')
def nosotros():
    return  render_template('sitio/nosotros.html')


@app.route('/admin/')
def admin_index():
    if not 'login' in session:             #este if valida si existe una sesion iniciana y si no es asi devuelve al login
        return redirect("/admin/login") 
    return  render_template('/admin/index.html')


@app.route('/admin/login', methods=['POST','GET'])
def admin_login():
     return  render_template('admin/login.html')


@app.route('/admin/login/accede', methods=['POST','GET'])
def admin_login_post():
   
    _usuario=request.form['txtUsuario']
    _password=request.form['txtPassword']

    print(_usuario)
    print(_password)

    if _usuario=="admin" and _password=="123":
        session["login"]=True  
        session["usuario"]="Administrador"
        return redirect("/admin")

    return render_template("admin/login.html", mensaje="Acceso denegado")


@app.route('/admin/cerrar')
def admin_login_cerrar():
    session.clear()              #clerar es equivalente a limpiar las variables de sesion
    return redirect('/admin')


@app.route('/admin/libros')              #este incluye las conexiones a base de datos
def admin_libros():

    if not 'login' in session:             #este if valida si existe una sesion iniciana y si no es asi devuelve al login
        return redirect("/admin/login")



    conexion=mysql.connect()             #forma de muestra del almacenamiento
    cursor= conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros=cursor.fetchall()
    conexion.commit()                    #agrega el proceso
    print(libros)
    return  render_template('/admin/libros.html',libros=libros)


@app.route('/admin/libros/guardar', methods=['POST'])       #forma en la cual se almacena los datos en la bd
def admin_libros_guardar():

    _nombre=request.form['txtNombre']                       #nuevas variables que almacena los datos recogidos en un form
    _url=request.form['txtURL']
    _archivo=request.files['txtImagen']

    tiempo= datetime.now()                                  #esta evita nombres repetido añadiendo datatime
    horaActual=tiempo.strftime('%Y%H%M%S')

    if _archivo.filename!="":
        nuevoNombre=horaActual+"_"+_archivo.filename
        _archivo.save("templates/sitio/img/"+nuevoNombre)

    sql="INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL,%s,%s,%s);"       #se agregan los datos a la bd en su respectivo orden
    datos=(_nombre,nuevoNombre,_url)

    conexion=mysql.connect()
    cursor=conexion.cursor()
    cursor.execute(sql,datos)
    conexion.commit()

    print(_nombre)           #los print se usan para ver la ejecucion en la consola
    print(_url)
    print(_archivo)

    if not 'login' in session:             #este if valida si existe una sesion iniciana y si no es asi devuelve al login
        return redirect("/admin/login")
    return  redirect('/admin/libros')


@app.route('/admin/libros/borrar', methods=['POST'])      #se usa para crear el borrar desde la pagina libros a la bd
def admin_libros_borrar():
    _id=request.form['txtID']
    print(_id)

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT imagen FROM `libros` WHERE id=%s", (_id))
    libro=cursor.fetchall()
    conexion.commit()
    print(libro)       #este almacena y verifica los datos

    if os.path.exists("templates/sitio/img/"+str(libro[0][0])):    #Borrado de imagen temporal en img
        os.unlink("templates/sitio/img/"+str(libro[0][0]))         #pregunta si la ruta existe y se es asi se ejecuta el unlink

    conexion=mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id=%s",(_id))
    conexion.commit()   #eliminado absoluto del dato de la bd
    
    if not 'login' in session:             #este if valida si existe una sesion iniciana y si no es asi devuelve al login
        return redirect("/admin/login")
    return  redirect('/admin/libros')

 



if __name__=='__main__':   #esto significa que si aplicaipon se encuentra en la pagina principal va a correr la app
    app.run(debug= True)

