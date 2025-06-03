from flask import Flask, current_app, render_template, request, redirect, session, url_for, jsonify
from db import get_db_connection
import os


app = Flask(__name__)

# Configurar la clave secreta de la aplicación, utilizada para gestionar sesiones y cookies seguras
app.config['SECRET_KEY'] = 'unicesmag'
# Configurar los parámetros de la base de datos
app.config['DB_HOST'] = 'localhost'  # El host donde se encuentra la base de datos
app.config['DB_NAME'] = 'tulato'  # El nombre de la base de datos
app.config['DB_USER'] = 'postgres'  # El usuario de la base de datos
app.config['DB_PASSWORD'] = 'unicesmag'  # La contraseña del usuario de la base de datos

# Carpeta para guardar las imagenes
ruta_base = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(ruta_base, 'static','uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#Traer datos usuario
def datos_usuario(user_id):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''SELECT u.usuario_id, u.nombre, u.apellido, r.tipo as rol FROM usuario u 
                JOIN rol r ON u.rol_id = r.rol_id WHERE usuario_id = %s;''', (user_id,))
            user = cur.fetchone()  
    return user

###### IR A autenticacion_registro.py #####
from autenticacion_registro import aut_reg
app.register_blueprint(aut_reg, url_prefix='/autenticacion_registro')
###### IR A evaluacion_aprendizaje.py #####
from evaluacion_aprendizaje import eva_apre
app.register_blueprint(eva_apre, url_prefix='/evaluacion_aprendizaje')
###### IR A gestion_informacion.py #####
from gestion_informacion import ges_inf
app.register_blueprint(ges_inf, url_prefix='/gestion_informacion')
###### IR A mapa_interactivo.py #####
from mapa_interactivo import map_int
app.register_blueprint(map_int, url_prefix='/mapa_interactivo')
###### IR A sistema_reportes.py #####
from sistema_reportes import sis_rep
app.register_blueprint(sis_rep, url_prefix='/sistema_reportes')

# Página principal
@app.route('/')
@app.route('/index')
def index():
    # Obtener el ID de usuario de la sesión actual
    user_id = session.get('user_id')    
    # Verificar si el usuario ha iniciado sesión
    if user_id is not None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''SELECT u.usuario_id, u.nombre, u.apellido, r.tipo as rol FROM usuario u 
                    join rol r on u.rol_id=r.rol_id WHERE usuario_id=%s;''', (user_id,))
                user = cur.fetchone()  # Obtener el primer resultado de la consulta      
        # Si el usuario ha iniciado sesión, redirigir a la página principal
        return render_template('index.html',user=user) 
    else:
        return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)
