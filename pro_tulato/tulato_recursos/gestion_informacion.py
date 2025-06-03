from flask import Blueprint, flash, render_template, request, session, redirect, url_for, jsonify, current_app
from db import get_db_connection
import os
from werkzeug.utils import secure_filename

from app import datos_usuario

# Crear un Blueprint para las rutas hídricas
ges_inf = Blueprint('gestion_informacion', __name__, static_folder='static', template_folder='templates')

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'svg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Agregar Informacion
@ges_inf.route('/agregar_informacion', methods=['GET', 'POST'])
def agregar_informacion():    
    modulo =2
    menu_solo = 5
    user_id = session.get('user_id')    

    if user_id is None: 
        return redirect(url_for('index'))  
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            user=datos_usuario(user_id)
            if request.method == 'POST':         
                titulo = request.form.get('titulo')
                coordenadas = request.form.get('coordenadas')
                file = request.files.get('file')
                video = request.form.get('video') or None
                descripcion = request.form.get('descripcion')
                proyecto = request.form.get('proyecto') or None
                municipio = request.form.get('municipio') or None
                vereda = request.form.get('vereda') or None
                determinante = request.form.get('determinante') or None
                rol = request.form.get('rol') or None

                ruta_archivo = None
                print(municipio)
                print(vereda)
                print(determinante)
                if file and file.filename != '':
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join('static', 'uploads'))
                        filepath = os.path.join(upload_folder, filename)
                        file.save(filepath)
                        ruta_archivo = os.path.join('static', 'uploads', filename)
                    else:
                        return 'error' 

                if proyecto=="4" and (municipio is None or vereda is None or determinante is None):                    
                    return 'error'

                print(f""" Título: {titulo} Coordenadas: {coordenadas} Archivo: {ruta_archivo} Descripción: {descripcion} Proyecto: {proyecto} Municipio: {municipio} Vereda: {vereda} Determinante: {determinante} Rol: {rol} """)
                
                # Insertar el nuevo usuario y devolver el id insertado
                cur.execute("""
                    INSERT INTO contenido (titulo, descripcion, coordenada, imagen, video, rol_id, usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING contenido_id
                """, (titulo,descripcion,coordenadas,ruta_archivo,video,rol,user_id))

                # Obtener el id del nuevo usuario
                contenido_id = cur.fetchone()[0]
                conn.commit()

                # Insertar el nuevo usuario y devolver el id insertado
                cur.execute("""
                    INSERT INTO asociacion_contenido (contenido_id, determinante_id, vereda_id, municipio_id, proyecto_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (contenido_id,determinante,vereda,municipio,proyecto))
                conn.commit()


                return 'success' 
            else:  
                cur.execute('SELECT rol_id, tipo FROM rol')
                rol = cur.fetchall()            
                cur.execute('SELECT proyecto_id, nombre FROM proyecto')
                proyecto = cur.fetchall()
                cur.execute('SELECT municipio_id, nombre FROM municipio')
                municipio = cur.fetchall()
                cur.execute('SELECT m.municipio_id, m.nombre, v.vereda_id, v.nombre FROM vereda v join municipio m on m.municipio_id=v.municipio_id')
                vereda = cur.fetchall()
                cur.execute('SELECT determinante_id, tipo FROM determinante')
                determinante = cur.fetchall()

                return render_template('/gestion_informacion/agregar_informacion.html',
                    modulo=modulo, menu_solo=menu_solo,
                    proyecto=proyecto, municipio=municipio, vereda=vereda,
                    determinante=determinante, rol=rol, user=user)
            
##Editar Informacion
@ges_inf.route('/editar_informacion', methods=['GET', 'POST'])
def editar_informacion():
    modulo = 2
    menu_solo = 5
    user_id = session.get('user_id')    
    user_rol = session.get('user_rol')

    if user_id is None or user_rol not in [1, 2]:
        return redirect(url_for('index'))

    user = datos_usuario(user_id)

    with get_db_connection() as conn:
        with conn.cursor() as cur:

            if request.method == 'POST':
                form = request.form
                id_info = form.get('id_info')
                titulo = form.get('titulo')
                coordenadas = form.get('coordenadas')
                descripcion = form.get('descripcion')
                video = form.get('video') or None
                proyecto = form.get('proyecto') or None
                municipio = form.get('municipio') or None
                vereda = form.get('vereda') or None
                determinante = form.get('determinante') or None
                rol = form.get('rol') or None
                file = request.files.get('file')
                ruta_archivo = None



                if file and file.filename != '':
                    if allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        upload_folder = current_app.config.get('UPLOAD_FOLDER', os.path.join('static', 'uploads'))
                        filepath = os.path.join(upload_folder, filename)
                        file.save(filepath)
                        ruta_archivo = os.path.join('static', 'uploads', filename)
                        cur.execute("""UPDATE contenido SET imagen = %s WHERE contenido_id = %s""",(ruta_archivo, id_info))
                    else:
                        return 'error'

                if proyecto == "4" and (not municipio or not vereda or not determinante):
                    return 'error'

                cur.execute("""UPDATE contenido 
                               SET titulo = %s, descripcion = %s, coordenada = %s, video = %s, rol_id = %s
                               WHERE contenido_id = %s""",
                            (titulo, descripcion, coordenadas, video, rol, id_info))

                cur.execute("""UPDATE asociacion_contenido 
                               SET determinante_id = %s, vereda_id = %s, municipio_id = %s, proyecto_id = %s
                               WHERE contenido_id = %s""",
                            (determinante, vereda, municipio, proyecto, id_info))

                conn.commit()
                return 'success' 

            # --- GET: Renderizar datos ---
            cur.execute("""SELECT c.contenido_id, c.created_at, c.titulo, p.nombre as proyecto, 
                           m.nombre, v.nombre, d.tipo, r.tipo as receptor, u.correo as creador, c.status, 
                           c.coordenada, c.imagen, c.video, c.descripcion, 
                           p.proyecto_id, m.municipio_id, v.vereda_id, d.determinante_id, r.rol_id
                           FROM asociacion_contenido ac
                           LEFT JOIN contenido c ON c.contenido_id = ac.contenido_id
                           LEFT JOIN usuario u ON u.usuario_id = c.usuario_id
                           LEFT JOIN rol r ON r.rol_id = c.rol_id
                           LEFT JOIN determinante d ON d.determinante_id = ac.determinante_id
                           LEFT JOIN vereda v ON v.vereda_id = ac.vereda_id
                           LEFT JOIN municipio m ON m.municipio_id = ac.municipio_id
                           LEFT JOIN proyecto p ON p.proyecto_id = ac.proyecto_id""")
            edit_info = cur.fetchall()

            # Cargar selects (todos en bloque)
            cur.execute('SELECT rol_id, tipo FROM rol')
            rol = cur.fetchall()
            cur.execute('SELECT proyecto_id, nombre FROM proyecto')
            proyecto = cur.fetchall()
            cur.execute('SELECT municipio_id, nombre FROM municipio')
            municipio = cur.fetchall()
            cur.execute('''SELECT m.municipio_id, m.nombre, v.vereda_id, v.nombre 
                           FROM vereda v JOIN municipio m ON m.municipio_id = v.municipio_id''')
            vereda = cur.fetchall()
            cur.execute('SELECT determinante_id, tipo FROM determinante')
            determinante = cur.fetchall()

    return render_template('/gestion_informacion/editar_informacion.html',
                           modulo=modulo, menu_solo=menu_solo, user=user,
                           proyecto=proyecto, municipio=municipio, vereda=vereda,
                           determinante=determinante, rol=rol, edit_info=edit_info)
 


##Informacion Demas Proyectos##
@ges_inf.route("/proyectos")
def proyectos():
    modulo=2    
    num_pro=int(request.args.get("num_pro"))
    menu_solo=num_pro
    if menu_solo<=0 or menu_solo>4:
        print("Salio 6")
        return redirect(url_for('index')) 

    user_id = session.get('user_id')  
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if user_id is not None:
                # Solo buscamos el hash por el correo
                user=datos_usuario(user_id)

            cur.execute('''SELECT c.titulo, c.descripcion, c.coordenada, c.imagen, r.tipo, c.status,
                   p.nombre, m.nombre, v.nombre, d.tipo, c.video
            FROM asociacion_contenido ac
            left JOIN contenido c ON c.contenido_id = ac.contenido_id
            left JOIN rol r ON r.rol_id = c.rol_id
            left JOIN determinante d ON d.determinante_id = ac.determinante_id
            left JOIN vereda v ON v.vereda_id = ac.vereda_id
            left JOIN municipio m ON m.municipio_id = ac.municipio_id
            left JOIN proyecto p ON p.proyecto_id = ac.proyecto_id
            WHERE p.proyecto_id= %s;''', (num_pro,))
            informacion = cur.fetchall()
    if user_id is not None:
        return render_template('/gestion_informacion/proyectos.html',modulo=modulo,menu_solo=menu_solo,user=user, informacion=informacion)
    else:
        return render_template('/gestion_informacion/proyectos.html',modulo=modulo,menu_solo=menu_solo,informacion=informacion)