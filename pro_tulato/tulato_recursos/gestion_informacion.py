import io
from flask import Blueprint, flash, render_template, request, send_file, session, redirect, url_for, jsonify, current_app

from db import get_db_connection
import os
from werkzeug.utils import secure_filename
from xhtml2pdf import pisa
from io import BytesIO
import base64
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
    user_id = session.get('user_id')    
    user_rol = session.get('user_rol')

    if user_id is None or user_rol not in [1, 2]:
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
                roles = request.form.getlist('rol')

                ruta_archivo = None
                
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
                
                elif not roles:
                    return 'exit'
                
                # Insertar el nuevo usuario y devolver el id insertado
                cur.execute("""
                    INSERT INTO contenido (titulo, descripcion, coordenada, imagen, video, usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING contenido_id
                """, (titulo,descripcion,coordenadas,ruta_archivo,video,user_id))

                # Obtener el id de la nueva informacion
                contenido_id = cur.fetchone()[0]
                conn.commit()

                # Insertar el nuevo contenido_rol y devolver el id insertado
                for rol_id in roles:
                    cur.execute("""
                        INSERT INTO contenido_rol (contenido_id, rol_id)
                        VALUES (%s, %s)
                    """, (contenido_id, rol_id))
                conn.commit()


                # Insertar el nuevo asociacion_contenido y devolver el id insertado
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
                cur.execute('SELECT determinante_id, tipo FROM determinante WHERE determinante_id != 4')
                determinante = cur.fetchall()

                return render_template('/gestion_informacion/agregar_informacion.html',
                    modulo=modulo, 
                    proyecto=proyecto, municipio=municipio, vereda=vereda,
                    determinante=determinante, rol=rol, user=user)
            
##Editar Informacion
@ges_inf.route('/editar_informacion', methods=['GET', 'POST'])
def editar_informacion():
    modulo = 2
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
                roles = form.getlist('rol')  # <-- Esto devuelve una lista de roles marcados
                file = request.files.get('file')
                status = form.get('status')
                
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
                               SET titulo = %s, descripcion = %s, coordenada = %s, video = %s
                               WHERE contenido_id = %s""",
                            (titulo, descripcion, coordenadas, video, id_info))
                
                if roles:
                    # Actualizar roles múltiples (checkboxes)
                    cur.execute("DELETE FROM contenido_rol WHERE contenido_id = %s", (id_info,))
                    for rol_id in roles:
                        cur.execute("INSERT INTO contenido_rol (contenido_id, rol_id) VALUES (%s, %s)", (id_info, rol_id))

                
                cur.execute("""UPDATE asociacion_contenido 
                               SET determinante_id = %s, vereda_id = %s, municipio_id = %s, proyecto_id = %s
                               WHERE contenido_id = %s""",
                            (determinante, vereda, municipio, proyecto, id_info))

                
                if status == 'on':
                    cur.execute("""UPDATE contenido SET status = %s WHERE contenido_id = %s""",(True, id_info))

                conn.commit()
                
                return 'success' 

            # --- GET: Renderizar datos ---
            cur.execute("""SELECT 
                    c.contenido_id, c.created_at, c.titulo, 
                    p.nombre AS proyecto, m.nombre, v.nombre, d.tipo, 
                    STRING_AGG(r.tipo, ', ') AS receptores,
                    u.correo AS creador, c.status, c.coordenada, 
                    c.imagen, c.video, c.descripcion, 
                    p.proyecto_id, m.municipio_id, v.vereda_id, d.determinante_id,
                    STRING_AGG(r.rol_id::text, ',') AS rol_ids
                FROM asociacion_contenido ac
                LEFT JOIN contenido c ON c.contenido_id = ac.contenido_id
                LEFT JOIN usuario u ON u.usuario_id = c.usuario_id
                LEFT JOIN contenido_rol cr ON cr.contenido_id = c.contenido_id
                LEFT JOIN rol r ON r.rol_id = cr.rol_id
                LEFT JOIN determinante d ON d.determinante_id = ac.determinante_id
                LEFT JOIN vereda v ON v.vereda_id = ac.vereda_id
                LEFT JOIN municipio m ON m.municipio_id = ac.municipio_id
                LEFT JOIN proyecto p ON p.proyecto_id = ac.proyecto_id
                GROUP BY 
                    c.contenido_id, c.created_at, c.titulo, p.nombre, 
                    m.nombre, v.nombre, d.tipo, u.correo, c.status, 
                    c.coordenada, c.imagen, c.video, c.descripcion, 
                    p.proyecto_id, m.municipio_id, v.vereda_id, d.determinante_id
                ORDER BY c.created_at desc;
            """)
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
            cur.execute('SELECT determinante_id, tipo FROM determinante WHERE determinante_id != 4')
            determinante = cur.fetchall()

    return render_template('/gestion_informacion/editar_informacion.html',
                           modulo=modulo,  user=user,
                           proyecto=proyecto, municipio=municipio, vereda=vereda,
                           determinante=determinante, rol=rol, edit_info=edit_info)
 
@ges_inf.route('/eliminar_informacion')
def eliminar_informacion():
    id_info=request.args.get('id_info')
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Ejecutar la consulta para actualizar el estado del proyecto a "false"
            cur.execute('''
                UPDATE contenido SET status = %s WHERE contenido_id = %s
            ''', (False, id_info,))
            
            # Confirmar los cambios en la base de datos
            conn.commit()
    
    # Redirigir de vuelta a la lista de proyectos
    return redirect(url_for('gestion_informacion.editar_informacion'))


##Informacion Demas Proyectos##
@ges_inf.route("/proyectos")
def proyectos():
    modulo=2    
    num_pro=int(request.args.get("num_pro"))
    if num_pro<=0 or num_pro>4:
        return redirect(url_for('index')) 

    user_id = session.get('user_id')
    user_rol = session.get('user_rol')
    print("rol: ", user_rol)
    cantidad = 1  
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if user_id is not None:
                # Solo buscamos el hash por el correo
                user=datos_usuario(user_id)                
                cur.execute("""SELECT a.contenido_id FROM asociacion_contenido a 
                                JOIN contenido c on c.contenido_id=a.contenido_id
                                JOIN contenido_rol cr on cr.contenido_id=c.contenido_id
                                JOIN rol r on r.rol_id=cr.rol_id
                                WHERE proyecto_id=%s and cr.rol_id=%s and c.status=%s""", (num_pro,user_rol,True))
                contenido_id = cur.fetchall()

                for contenido in contenido_id:
                    cantidad = 1
                    cur.execute("""SELECT cantidad FROM visualizacion WHERE usuario_id=%s AND contenido_id=%s""", (user_id, contenido[0]))
                    my_info = cur.fetchone()

                    if my_info is None:
                        cur.execute("""INSERT INTO visualizacion (cantidad, usuario_id, contenido_id) VALUES (%s, %s, %s)""", (cantidad, user_id, contenido[0]))
                    else:
                        cantidad += my_info[0]
                        cur.execute("""UPDATE visualizacion SET cantidad=%s WHERE usuario_id=%s AND contenido_id=%s""", (cantidad, user_id, contenido[0]))


                    
            cur.execute('''SELECT c.titulo, c.descripcion, c.coordenada, c.imagen, r.tipo, c.status,
                p.nombre, m.nombre, v.nombre, d.tipo, c.video, c.contenido_id
                FROM asociacion_contenido ac
                left JOIN contenido c ON c.contenido_id = ac.contenido_id
                left JOIN contenido_rol cr on cr.contenido_id=c.contenido_id
                left JOIN rol r on r.rol_id=cr.rol_id
                left JOIN determinante d ON d.determinante_id = ac.determinante_id
                left JOIN vereda v ON v.vereda_id = ac.vereda_id
                left JOIN municipio m ON m.municipio_id = ac.municipio_id
                left JOIN proyecto p ON p.proyecto_id = ac.proyecto_id
                WHERE p.proyecto_id= %s AND c.status=%s;''', (num_pro,True,))
            informacion = cur.fetchall()

    if user_id is not None:
        return render_template('/gestion_informacion/proyectos.html',modulo=modulo,menu_solo=num_pro,user=user, info=informacion)
    else:
        return render_template('/gestion_informacion/proyectos.html',modulo=modulo,menu_solo=num_pro,info=informacion)
    
@ges_inf.route("/descargar_info")
def descargar_info():
    id_info = request.args.get('id_info')
    user_id = session.get('user_id')

    if user_id is None:
        return redirect(url_for('index'))

    cantidad = 1
    print("USUARIO",user_id)
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Control de descargas
            cur.execute("""SELECT cantidad FROM descarga WHERE usuario_id=%s AND contenido_id=%s""", (user_id, id_info))
            my_info = cur.fetchone()

            if my_info is None:
                cur.execute("""INSERT INTO descarga (cantidad, usuario_id, contenido_id) VALUES (%s, %s, %s)""", (cantidad, user_id, id_info))
            else:
                cantidad += my_info[0]
                cur.execute("""UPDATE descarga SET cantidad=%s WHERE usuario_id=%s AND contenido_id=%s""", (cantidad, user_id, id_info))

            conn.commit()

            # Obtener la información del contenido
            cur.execute('''SELECT c.titulo, c.descripcion, c.coordenada, c.imagen, r.tipo, c.status,
                p.nombre, m.nombre, v.nombre, d.tipo, c.video, c.contenido_id
                FROM asociacion_contenido ac
                left JOIN contenido c ON c.contenido_id = ac.contenido_id
                left JOIN contenido_rol cr on cr.contenido_id=c.contenido_id
                left JOIN rol r on r.rol_id=cr.rol_id
                LEFT JOIN determinante d ON d.determinante_id = ac.determinante_id
                LEFT JOIN vereda v ON v.vereda_id = ac.vereda_id
                LEFT JOIN municipio m ON m.municipio_id = ac.municipio_id
                LEFT JOIN proyecto p ON p.proyecto_id = ac.proyecto_id
                WHERE c.contenido_id = %s''', (id_info,))
            info = cur.fetchone()

    # Asegúrate de que la ruta de la imagen es válida
    imagen_base64 = None
    if info[3]:  # info[3] es la ruta a la imagen
        ruta_imagen = os.path.join(current_app.root_path, info[3].lstrip("/"))  # elimina "/" inicial si existe
        if os.path.exists(ruta_imagen):
            with open(ruta_imagen, "rb") as image_file:
                imagen_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    # Construir la ruta absoluta correctamente
    ruta_logo = os.path.join(current_app.root_path, "static", "images", "logo.svg")

    # Verificar y convertir a base64
    logo_base64 = None
    if os.path.exists(ruta_logo):
        with open(ruta_logo, "rb") as f:
            logo_base64 = base64.b64encode(f.read()).decode("utf-8")
    # Renderizar la plantilla con la info
    rendered = render_template("gestion_informacion/contenido_pdf.html", info=info, imagen_base64=imagen_base64,logo_base64=logo_base64)


    # Generar el PDF
    pdf_io = BytesIO()
    pisa_status = pisa.CreatePDF(rendered, dest=pdf_io)
    pdf_io.seek(0)

    if pisa_status.err:
        return "Error al generar el PDF", 500

    return send_file(pdf_io, download_name="contenido.pdf", as_attachment=True)