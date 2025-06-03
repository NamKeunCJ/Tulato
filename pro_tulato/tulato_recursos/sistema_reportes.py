from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify

from db import get_db_connection

# Crear un Blueprint para las rutas hídricas
sis_rep = Blueprint('sistema_reportes', __name__, static_folder='static',template_folder='templates')

# Página principal
@sis_rep.route('/inicio_sesion')
def index():    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM genero WHERE genero_id = %s;', (2,))
            genero = cur.fetchone()
    return render_template('/sistema_reportes/inicio_sesion.html',genero=genero)