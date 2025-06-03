import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from argon2 import PasswordHasher, exceptions as argon2_exceptions
from db import get_db_connection
from app import datos_usuario

# Crear un Blueprint para las rutas hídricas
aut_reg = Blueprint('autenticacion_registro', __name__, static_folder='static',template_folder='templates')

# inicio de sesion
@aut_reg.route('/inicio_sesion', methods=['GET', 'POST'])
def index(): 
    modulo=1          
    # Verificar si el método de la solicitud es POST
    if request.method == 'POST':         
        email = request.form['email_usu']  # Obtener el correo del usuario desde el formulario
        password = request.form['password_usu']  # Obtener la contraseña del usuario desde el formulario 
        ph = PasswordHasher()                      
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Solo buscamos el hash por el correo
                cur.execute('SELECT usuario_id, rol_id, contraseña FROM usuario WHERE correo=%s;', (email,))
                user = cur.fetchone()  # Obtener el primer resultado de la consulta        

        if user is not None:
            user_id,rol_id, hashed_password = user  # El hash ya está guardado en la base de datos

            try:
                # Verificar contraseña con Argon2id
                ph.verify(hashed_password, password)

                session.permanent = True
                session['user_id'] = user_id  # Guardar el ID del usuario en la sesión
                session['user_rol'] = rol_id  

                return 'success'
            except argon2_exceptions.VerifyMismatchError:
                return 'error'  # Contraseña incorrecta
        else:
            return 'error'  # Usuario no encontrado
    else:
        return render_template('/autenticacion_registro/inicio_sesion.html', modulo=modulo)
    
#Cerrar Sesion        
@aut_reg.route('/logout')
def logout():
    # Borrar la información de la sesión
    session.clear()
    # Redireccionar a la página de inicio o a donde prefieras
    return redirect(url_for('index'))  

# registrarse
@aut_reg.route('/registro', methods=['GET', 'POST'])
def registro(): 
    modulo=1 
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Verificar si el método de la solicitud es POST
            if request.method == 'POST':         
                email = request.form['email']  # Obtener el correo del usuario desde el formulario
                nombre = request.form['nombre']  # Obtener el nombre del usuario desde el formulario
                apellido = request.form['apellido']  # Obtener el apellido del usuario desde el formulario
                password = request.form['password']  # Obtener la contraseña del usuario desde el formulario 
                genero = request.form['genero']  # Obtener el genero del usuario desde el formulario
                edad = request.form['edad']  # Obtener el edad del usuario desde el formulario
                discapacidad = request.form['discapacidad']  # Obtener el discapacidad del usuario desde el formulario
                grupo_etnico = request.form['grupo_etnico']  # Obtener el grupo_etnico del usuario desde el formulario

                if discapacidad == "":
                    discapacidad="No Aplica"

                ph = PasswordHasher() 
                password_encrip = ph.hash(password)   
                cur.execute('SELECT usuario_id FROM usuario WHERE correo=%s ;', (email,))
                user_exis = cur.fetchone()             
                if user_exis is not None:
                    # Si el usuario ya existe, devolver 'exist'
                    return 'exist' 
                else:                     
                    # Si el usuario no existe, insertar el nuevo usuario en la base de datos
                    cur.execute("""
                        INSERT INTO usuario (nombre, apellido, correo, contraseña, genero_id, edad, discapacidad, grupo_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (nombre, apellido, email, password_encrip, genero, edad, discapacidad, grupo_etnico))
                    conn.commit()
                    return 'success' 
            else:              
                cur.execute('SELECT genero_id, tipo FROM genero')
                genero = cur.fetchall()
                cur.execute('SELECT grupo_id, tipo FROM grupo_etnico')
                grupo = cur.fetchall()
                return render_template('/autenticacion_registro/registro.html',modulo=modulo,genero=genero,grupo=grupo)
            
#RECUPERAR CONTRASEÑA        
@aut_reg.route('/recuperar_password', methods=['GET', 'POST'])
def recuperar_password():
    modulo=1
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Verificar si el método de la solicitud es POST
            if request.method == 'POST':         
                email = request.form['email']  # Obtener el correo del usuario desde el formulario
                cur.execute('SELECT usuario_id, nombre, apellido FROM usuario WHERE correo=%s ;', (email,))
                user_exis = cur.fetchone()            
                if user_exis is not None:
                    caracteres = string.ascii_uppercase + string.digits
                    codigo = ''.join(random.choices(caracteres, k=8))
                    ph = PasswordHasher() 
                    password_encrip = ph.hash(codigo)
                    redaccion_correo(codigo,email,user_exis[1],user_exis[2])
                    # Solo buscamos el hash por el correo
                    cur.execute('UPDATE usuario set contraseña=%s WHERE usuario_id=%s;', (password_encrip,user_exis[0]))
                    conn.commit()

                    print("CODIGO", codigo)
                    # Si el correo si existe, devolver 'success'
                    return 'success' 
                else:  
                    return 'error'
            else:
                return render_template('/autenticacion_registro/recuperar_password.html',modulo=modulo)

#REDACCION MENSAJE CORREO
def redaccion_correo(codigo, email, nombre, apellido):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    correo_emisor = 'proyecto4tulato@gmail.com'
    contrasena_emisor = 'kxogeenkiyvxsyne'  # Usa contraseña de aplicación de Gmail

    mensaje = MIMEMultipart('related')  # Para incluir imágenes embebidas
    mensaje['From'] = correo_emisor
    mensaje['To'] = email
    mensaje['Subject'] = 'Recuperación de contraseña TULATO'

    # Parte alternativa para HTML
    mensaje_alternativo = MIMEMultipart('alternative')
    mensaje.attach(mensaje_alternativo)

    cuerpo_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; background-color: #0a3e2f; margin: 0; padding: 30px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 3px solid #EBAC06;">
                <div style="text-align: center; margin-bottom: 20px;">
                    <img src="cid:logo_nav" alt="Logo fondo" style="max-width: 300px;">
                </div>
                <h2 style="color: #0a3e2f; text-align: center; margin-bottom: 20px;">Recuperación de contraseña</h2>
                <p style="color: #333;">Hola {nombre} {apellido},</p>
                <p style="color: #333;">Has solicitado recuperar tu contraseña. Aquí tienes tu nueva contraseña temporal:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <span style="display: inline-block; background-color: #EBAC06; color: #0a3e2f; padding: 12px 30px; font-size: 24px; font-weight: bold; border-radius: 8px; letter-spacing: 2px;">
                    {codigo}
                    </span>
                </div>
                <p style="color: #555;">Te recomendamos iniciar sesión y cambiarla inmediatamente para mantener tu cuenta segura.</p>
                <p style="margin-top: 30px;">Saludos,<br><strong>Soporte TULATO</strong></p>
                <div style="text-align: start; margin-top: 10px;">
                    <img src="cid:logo_nav" alt="Logo nav" style="max-width: 90px;">
                </div>
            </div>
        </body>
    </html>
    """

    mensaje_alternativo.attach(MIMEText(cuerpo_html, 'html'))
    # Ruta absoluta al logo
    ruta_base = os.path.dirname(os.path.abspath(__file__))
    ruta_logo = os.path.join(ruta_base, 'static', 'images', 'logo.png')
    # Adjuntar imagen inferior
    with open(ruta_logo, 'rb') as img:
        img_mime = MIMEImage(img.read())
        img_mime.add_header('Content-ID', '<logo_nav>')
        img_mime.add_header('Content-Disposition', 'inline', filename='TULATO.png')  # <- Esta línea es clave
        mensaje.attach(img_mime)

    try:
        servidor = smtplib.SMTP(smtp_server, smtp_port)
        servidor.starttls()
        servidor.login(correo_emisor, contrasena_emisor)
        servidor.sendmail(correo_emisor, email, mensaje.as_string())
        servidor.quit()
        print("Correo enviado correctamente")
    except Exception as e:
        print("Error al enviar el correo:", e)


# EDITAR PERFIL
@aut_reg.route('/edit_perfil', methods=['GET', 'POST'])
def edit_perfil(): 
    modulo=2
    menu_solo=5
    # Obtener el ID de usuario de la sesión actual
    user_id = session.get('user_id')    
    # Verificar si el usuario ha iniciado sesión
    if user_id is None: 
        return redirect(url_for('index'))  
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Solo buscamos el hash por el correo
            cur.execute('''SELECT u.usuario_id, u.nombre, u.apellido, r.tipo as rol, u.correo, u.edad, g.tipo as genero, u.discapacidad, ge.tipo as grupo_etnico, u.genero_id, u.grupo_id FROM usuario u 
                join rol r on u.rol_id=r.rol_id 
                join genero g on u.genero_id=g.genero_id 
                join grupo_etnico ge on u.grupo_id=ge.grupo_id WHERE usuario_id=%s;''', (user_id,))
            user = cur.fetchone()  # Obtener el primer resultado de la consulta 

            # Verificar si el método de la solicitud es POST
            if request.method == 'POST':         
                nombre = request.form['nombre']  # Obtener el nombre del usuario desde el formulario
                apellido = request.form['apellido']  # Obtener el apellido del usuario desde el formulario
                password = request.form['password']  # Obtener la contraseña del usuario desde el formulario 
                genero = request.form['genero']  # Obtener el genero del usuario desde el formulario
                edad = request.form['edad']  # Obtener el edad del usuario desde el formulario
                discapacidad = request.form['discapacidad']  # Obtener el discapacidad del usuario desde el formulario
                grupo_etnico = request.form['grupo_etnico']  # Obtener el grupo_etnico del usuario desde el formulario
                print("Genero: ",genero)
                if discapacidad == "":
                    discapacidad="No Aplica"
                if password != "":
                    ph = PasswordHasher() 
                    password_encrip = ph.hash(password)
                    # actualizar datos
                    cur.execute(""" UPDATE usuario SET contraseña = %s WHERE usuario_id = %s """,
                        (password_encrip, user_id))
                    conn.commit()

                # actualizar datos
                cur.execute(""" UPDATE usuario SET nombre = %s, apellido = %s, genero_id = %s, edad = %s, discapacidad = %s, grupo_id = %s 
                            WHERE usuario_id = %s """,
                    (nombre, apellido, genero, edad, discapacidad, grupo_etnico, user_id))
                conn.commit()
                return 'success' 
            else:              
                cur.execute('SELECT genero_id, tipo FROM genero')
                genero = cur.fetchall()
                cur.execute('SELECT grupo_id, tipo FROM grupo_etnico')
                grupo = cur.fetchall()
                return render_template('/autenticacion_registro/editar_perfil.html',modulo=modulo,menu_solo=menu_solo,genero=genero,grupo=grupo, user=user)
            

# EDITAR USUARIO ROLES
@aut_reg.route('/edit_usuario', methods=['GET', 'POST'])
def edit_usuario(): 
    modulo=2
    menu_solo=5
    # Obtener el ID de usuario y ID rol de la sesión actual
    user_id = session.get('user_id')    
    user_rol = session.get('user_rol')  
    # Verificar si el usuario ha iniciado sesión
    if user_id is not None and (user_rol == 1 or user_rol == 2):     
        with get_db_connection() as conn:
            with conn.cursor() as cur:
            
                user=datos_usuario(user_id)
                
                cur.execute('''SELECT u.usuario_id, u.nombre, u.apellido, u.correo, r.tipo as rol, u.edad, g.tipo as genero, u.discapacidad, ge.tipo as grupo_etnico, u.rol_id FROM usuario u 
                    join rol r on u.rol_id=r.rol_id 
                    join genero g on u.genero_id=g.genero_id 
                    join grupo_etnico ge on u.grupo_id=ge.grupo_id''')
                edit_usu = cur.fetchall()  # Obtener el primer resultado de la consulta 

                cur.execute('select count(rol_id) from usuario where rol_id=2;')
                cant_administradores_max= cur.fetchone()  # Obtener Cantidad de administradores maximos

                # Verificar si el método de la solicitud es POST
                if request.method == 'POST':      
                    id_usuario = int(request.form['id_usu'])  # Obtener el id usuario del usuario desde el formulario
                    email = request.form['email']  # Obtener el email del usuario desde el formulario
                    rol = int(request.form['rol'])  # Obtener el rol del usuario desde el formulario

                    cur.execute('SELECT rol_id FROM usuario where usuario_id=%s;',(id_usuario,))
                    rol_actual = cur.fetchone()  # Obtener el primer resultado de la consulta 
                        
                    print( user[3] ,": ", rol_actual[0])
                    if (rol_actual[0] == 2 or rol == 2) and user[3] == 'Administrador': 
                        return 'exist'
                    else:
                        if rol == 2 and cant_administradores_max[0] ==3:
                            cur.execute(""" UPDATE usuario SET correo= %s WHERE usuario_id = %s """, (email, id_usuario))
                            conn.commit()
                            return 'error' 
                        else:  
                            if id_usuario!=user_id:
                                # actualizar datos
                                cur.execute(""" UPDATE usuario SET correo= %s, rol_id= %s
                                            WHERE usuario_id = %s """, (email, rol, id_usuario))
                                conn.commit()
                                return 'success'                            
                            else:       
                                # actualizar datos
                                cur.execute(""" UPDATE usuario SET correo= %s
                                            WHERE usuario_id = %s """, (email, id_usuario))
                                conn.commit()
                                return 'success'        
                else:              
                    cur.execute('SELECT rol_id, tipo FROM rol')
                    rol = cur.fetchall()
                    return render_template('/autenticacion_registro/editar_usuario.html',modulo=modulo,menu_solo=menu_solo,rol=rol, edit_usu=edit_usu, user=user)
    else:        
        return redirect(url_for('index'))  