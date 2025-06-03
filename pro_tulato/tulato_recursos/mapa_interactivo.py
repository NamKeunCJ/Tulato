from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify

from db import get_db_connection
from app import datos_usuario

# Crear un Blueprint para las rutas hídricas
map_int = Blueprint('mapa_interactivo', __name__, static_folder='static',template_folder='templates')

# Página principal
@map_int.route('/tulato_inicio', methods=['GET', 'POST'])
def tulato_inicio():
    modulo=2
    menu_solo=4
    user_id = session.get('user_id')  
    # Verificar si el método de la solicitud es POST
    if request.method == 'POST':   
        # Veredas y sus determinantes
        veredas = {
            'Imbili': [
                request.form.get('imbili_social') is not None,
                request.form.get('imbili_economico') is not None,
                request.form.get('imbili_ambiental') is not None
            ],
            'Candelillas': [
                request.form.get('candelillas_social') is not None,
                request.form.get('candelillas_economico') is not None,
                request.form.get('candelillas_ambiental') is not None
            ],
            'Descolgadero': [
                request.form.get('descolgadero_social') is not None,
                request.form.get('descolgadero_economico') is not None,
                request.form.get('descolgadero_ambiental') is not None
            ]
        }

        determinantes_labels = ['Social', 'Económico', 'Ambiental']

        condiciones = ["c.status = %s"]
        valores = [True]

        subcondiciones = []

        for vereda, checks in veredas.items():
            determinantes_seleccionados = [determinantes_labels[i] for i, activo in enumerate(checks) if activo]
            if determinantes_seleccionados:
                subcondiciones.append("(v.nombre = %s AND d.tipo IN %s)")
                valores.append(vereda)
                valores.append(tuple(determinantes_seleccionados))

        if subcondiciones:
            condiciones.append('(' + ' OR '.join(subcondiciones) + ')')

        query = f'''
            SELECT c.titulo, c.descripcion, c.coordenada, c.imagen, r.tipo, c.status,
                   p.nombre, m.nombre, v.nombre, d.tipo, c.video
            FROM asociacion_contenido ac
            JOIN contenido c ON c.contenido_id = ac.contenido_id
            JOIN rol r ON r.rol_id = c.rol_id
            JOIN determinante d ON d.determinante_id = ac.determinante_id
            JOIN vereda v ON v.vereda_id = ac.vereda_id
            JOIN municipio m ON m.municipio_id = ac.municipio_id
            JOIN proyecto p ON p.proyecto_id = ac.proyecto_id
            WHERE {' AND '.join(condiciones)} ORDER BY v.nombre, d.tipo, c.created_at DESC;
        '''

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, valores)
                informacion = cur.fetchall()

    else:
        candelillas = [False, False, False]
        descolgadero = [False, False, False]
        imbili = [False, False, False]


    # Verificar si el usuario ha iniciado sesión
    if user_id is not None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                user=datos_usuario(user_id) 

        # Si el usuario ha iniciado sesión, redirigir a la página principal
        if request.method == 'POST': 
            return render_template('/mapa_interactivo/tulato_inicio.html',modulo=modulo, menu_solo=menu_solo, user=user, candelillas=veredas['Candelillas'],descolgadero=veredas['Descolgadero'],imbili=veredas['Imbili'],informacion=informacion)
        else:
            return render_template('/mapa_interactivo/tulato_inicio.html',modulo=modulo, menu_solo=menu_solo, user=user, candelillas=candelillas,descolgadero=descolgadero,imbili=imbili)
    else:
        if request.method == 'POST': 
            return render_template('/mapa_interactivo/tulato_inicio.html',modulo=modulo, menu_solo=menu_solo, candelillas=veredas['Candelillas'],descolgadero=veredas['Descolgadero'],imbili=veredas['Imbili'],informacion=informacion)
        else:
            return render_template('/mapa_interactivo/tulato_inicio.html',modulo=modulo, menu_solo=menu_solo, candelillas=candelillas,descolgadero=descolgadero,imbili=imbili)
        