from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify

from db import get_db_connection
from app import datos_usuario

# Crear un Blueprint para las rutas hídricas
eva_apre = Blueprint('evaluacion_aprendizaje', __name__, static_folder='static',template_folder='templates')

# Agregar Test
@eva_apre.route('/agregar_test', methods=['GET', 'POST'])
def agregar_test():    
    modulo =2
    user_id = session.get('user_id')    
    user_rol = session.get('user_rol')

    if user_id is None or user_rol not in [1, 2]:
        return redirect(url_for('index'))
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            user=datos_usuario(user_id)
            if request.method == 'POST': 
                print(request.form)        
                # Obtener datos básicos del test
                nombre = request.form.get('nombre')
                contexto = request.form.get('contexto')
                determinante_id = int(request.form.get('determinante'))
                
                
                # Lista de preguntas
                preguntas = request.form.getlist('pregunta[]')
                if preguntas ==[]:
                    return 'error' 
                
                # Validar que todas las preguntas tengan respuestas válidas
                for i in range(len(preguntas)):
                    respuestas = request.form.getlist(f'respuesta[{i}][]')
                    if not respuestas:
                        return 'error'
                    if request.form.get(f'respuesta_correcta[{i}]') is None:
                        return 'error'
                
                # Insertar el nuevo test
                cur.execute("""
                    INSERT INTO test (nombre, descripcion, determinante_id)
                    VALUES (%s, %s, %s) RETURNING test_id
                """, (nombre,contexto, determinante_id))

                # Obtener el id del nuevo test
                test_id = cur.fetchone()[0]
                conn.commit()

                # Insertar preguntas y respuestas
                for i, pregunta in enumerate(preguntas):
                    respuestas = request.form.getlist(f'respuesta[{i}][]')
                    indice_correcta = int(request.form.get(f'respuesta_correcta[{i}]'))

                    cur.execute("""
                        INSERT INTO pregunta (enunciado, test_id)
                        VALUES (%s, %s) RETURNING pregunta_id
                    """, (pregunta, test_id))
                    pregunta_id = cur.fetchone()[0]
                    conn.commit()

                    for idx, respuesta in enumerate(respuestas):
                        es_correcta = int(idx == indice_correcta)
                        cur.execute("""
                            INSERT INTO opcion (respuesta, es_correcta, pregunta_id)
                            VALUES (%s, %s, %s)
                        """, (respuesta, es_correcta, pregunta_id))
                    conn.commit()

                return 'success'                
            else:  
                # Obtener todos los determinante
                cur.execute("""SELECT determinante_id, tipo from determinante""")
                determinantes = cur.fetchall()
                return render_template('/evaluacion_aprendizaje/agregar_test.html', modulo=modulo, user=user, determinantes=determinantes)

##Editar Test
@eva_apre.route('/editar_test', methods=['GET', 'POST'])
def editar_test():
    modulo = 2
    user_id = session.get('user_id')    
    user_rol = session.get('user_rol')

    if user_id is None or user_rol not in [1, 2]:
        return redirect(url_for('index'))

    user = datos_usuario(user_id)

    with get_db_connection() as conn:
        with conn.cursor() as cur:

            if request.method == 'POST':                
                test_id = request.form.get('id_test')
                nombre = request.form.get('nombre')
                descripcion = request.form.get('descripcion')
                determinante_id = request.form.get('determinante')
                estado = request.form.get('estado_test')
                print(f'estado {estado}')
                print(type(estado))
                print("determinante_id: ",determinante_id)
                # Obtener preguntas del test
                cur.execute("SELECT count(intento_test_id) FROM intento_test WHERE test_id = %s", (test_id,))
                existe_registros = cur.fetchone()
                print('existe_registros',existe_registros[0])

                if existe_registros[0]!=0:
                    # --- Actualizar Test ---
                    cur.execute("""
                        UPDATE test 
                        SET status = %s 
                        WHERE test_id = %s
                    """, (estado, test_id))

                    conn.commit()

                    return 'error'
                
                elif estado == 'False' and existe_registros[0]==0:
                    # Eliminar opciones de preguntas del test
                    cur.execute("""
                        DELETE FROM opcion 
                        WHERE pregunta_id IN (
                            SELECT pregunta_id FROM pregunta WHERE test_id = %s
                        )
                    """, (test_id,))

                    # Eliminar preguntas del test
                    cur.execute("""
                        DELETE FROM pregunta 
                        WHERE test_id = %s
                    """, (test_id,))

                    # Eliminar el test
                    cur.execute("""
                        DELETE FROM test 
                        WHERE test_id = %s
                    """, (test_id,))

                    conn.commit()
                    return 'success'
                    

                preguntas = {}
                correctas = {}

                for key, value in request.form.items():
                    if key.startswith('pregunta_'):
                        pregunta_id = key.replace('pregunta_', '')
                        preguntas[pregunta_id] = {'enunciado': value, 'opciones': {}}
                    elif key.startswith('opcion_'):
                        partes = key.split('_')
                        if len(partes) == 3:
                            _, pregunta_id, opcion_id = partes
                            if pregunta_id in preguntas:
                                preguntas[pregunta_id]['opciones'][opcion_id] = value
                    elif key.startswith('correcta_'):
                        pregunta_id = key.replace('correcta_', '')
                        correctas[pregunta_id] = value

                # --- Actualizar Test ---
                cur.execute("""
                    UPDATE test 
                    SET nombre = %s, descripcion = %s, status = %s, determinante_id = %s
                    WHERE test_id = %s
                """, (nombre, descripcion, estado, determinante_id, test_id))

                # --- Actualizar preguntas y opciones ---
                for pregunta_id, data in preguntas.items():
                    enunciado = data['enunciado']
                    cur.execute("""
                        UPDATE pregunta 
                        SET enunciado = %s 
                        WHERE pregunta_id = %s AND test_id = %s
                    """, (enunciado, pregunta_id, test_id))

                    opciones = data['opciones']
                    correcta = correctas.get(pregunta_id)

                    for opcion_id, texto in opciones.items():
                        es_correcta = 1 if opcion_id == correcta else 0
                        cur.execute("""
                            UPDATE opcion 
                            SET respuesta = %s, es_correcta = %s 
                            WHERE opcion_id = %s AND pregunta_id = %s
                        """, (texto, es_correcta, opcion_id, pregunta_id))

                conn.commit()

                return 'success'
            else:
                # Lista final de tests con preguntas y opciones
                tests_completos = []

                # Obtener todos los tests
                cur.execute("""SELECT t.test_id, t.nombre, t.descripcion, t.status, d.tipo, d.determinante_id FROM test t
                            join determinante d on d.determinante_id=t.determinante_id""")
                tests = cur.fetchall()

                # Obtener todos los determinante
                cur.execute("""SELECT determinante_id, tipo from determinante""")
                determinantes = cur.fetchall()

                for test in tests:
                    test_id, nombre, descripcion, status, determinante, determinante_id  = test

                    # Diccionario para almacenar el test y su contenido
                    test_dict = {
                        'test_id': test_id,
                        'nombre': nombre,
                        'descripcion': descripcion,
                        'status': status,   
                        'determinante': determinante, 
                        'determinante_id': determinante_id,                    
                        'preguntas': []
                    }

                    # Obtener preguntas del test
                    cur.execute("SELECT pregunta_id, enunciado FROM pregunta WHERE test_id = %s order by created_at asc", (test_id,))
                    preguntas = cur.fetchall()

                    for pregunta in preguntas:
                        pregunta_id, enunciado = pregunta

                        # Diccionario para cada pregunta
                        pregunta_dict = {
                            'pregunta_id': pregunta_id,
                            'enunciado': enunciado,
                            'opciones': []
                        }

                        # Obtener opciones de la pregunta
                        cur.execute("SELECT opcion_id, respuesta, es_correcta FROM opcion WHERE pregunta_id = %s", (pregunta_id,))
                        opciones = cur.fetchall()

                        for opcion in opciones:
                            opcion_id, respuesta, es_correcta = opcion
                            pregunta_dict['opciones'].append({
                                'opcion_id': opcion_id,
                                'respuesta': respuesta,
                                'es_correcta': es_correcta
                            })

                        # Agregar pregunta con opciones al test
                        test_dict['preguntas'].append(pregunta_dict)

                    # Agregar test completo a la lista
                    tests_completos.append(test_dict)
                
                return render_template('/evaluacion_aprendizaje/editar_test.html',
                            modulo=modulo, user=user, edit_test=tests_completos, determinantes=determinantes)


# Visualizar diferentes test y resolverlos
@eva_apre.route('/visualizar_tests', methods=['GET', 'POST'])
def visualizar_tests():    
    modulo =2
    menu_solo=5
    
    user_id = session.get('user_id')  

    if user_id is None:
        return redirect(url_for('index'))
    
    user=datos_usuario(user_id)

    #Extrae el id del test seleccionado
    test_id = request.args.get("test_id")
    if test_id is not None:
        test_id = int(test_id)


    with get_db_connection() as conn:
        with conn.cursor() as cur: 
            if test_id :
                menu_solo=6
                # Buscar test disponible
                cur.execute(""" SELECT t.test_id, t.nombre, t.descripcion, d.tipo FROM test t 
                    join determinante d on d.determinante_id=t.determinante_id WHERE t.test_id = %s AND t.status = %s""", (test_id,True,))
                # Obtener todos los test
                h_test = cur.fetchone()
                print(h_test)
                # Buscar test disponible
                cur.execute(""" SELECT p.pregunta_id, p.enunciado FROM pregunta p WHERE p.test_id = %s""", (test_id,))
                # Obtener todos los test
                h_pregunta = cur.fetchall()

                opciones=[]
                for pregunta in h_pregunta:
                    pregunta_id=pregunta[0]
                    # Buscar test disponible
                    cur.execute(""" SELECT o.opcion_id, o.respuesta, o.es_correcta FROM opcion o  WHERE o.pregunta_id = %s """, (pregunta_id,))
                    # Obtener todos los test
                    h_opcion = cur.fetchall()
                    opciones.append(h_opcion)

                return render_template('/evaluacion_aprendizaje/visualizar_tests.html', modulo=modulo, menu_solo=menu_solo, h_test=h_test, h_pregunta=h_pregunta, opciones=opciones,user=user, zip=zip)                
            else:  
                # Buscar test disponible
                cur.execute(""" select t.test_id, t.nombre , d.tipo FROM test t 
                    join determinante d on d.determinante_id=t.determinante_id where t.status=%s order by t.created_at desc""", (True,))
                # Obtener todos los test
                tests = cur.fetchall()

                # Buscar mis test
                cur.execute("""
                    select t.test_id, i.puntaje, i.intento from test t join intento_test i on i.test_id=t.test_id where i.usuario_id=%s and t.status=%s
                """, (user_id,True,))

                # Obtener todos los test que he realizado
                my_test = cur.fetchall()
                my_test_dict = {}
                for row in my_test:
                    key = row[0]
                    # Buscar mis test
                    cur.execute("""
                        select count(pregunta_id) from pregunta where test_id=%s
                    """, (row[0],))                        
                    # Obtener todos los test que he realizado
                    cantidad = cur.fetchone()
                    
                    if row[2]<3:
                        retroalimentacion=False
                    else:
                        retroalimentacion=True

                    value = {
                        'puntaje': (round((row[1]*100/cantidad[0]),2)),
                        'intento': row[2],
                        'retroalimentacion':retroalimentacion
                    }
                    my_test_dict[key] = value

                    print(my_test_dict)

                return render_template('/evaluacion_aprendizaje/visualizar_tests.html', modulo=modulo, menu_solo=menu_solo, tests=tests, my_test_dict=my_test_dict, user=user)

# Retroalimentacion del Test
@eva_apre.route('/retroalimentacion')
def retroalimentacion():    
    modulo =2
    menu_solo=7

    user_id = session.get('user_id')  
    if user_id is None:
        return redirect(url_for('index'))
    
    user=datos_usuario(user_id)
    #Extrae el id del test seleccionado
    test_id = int(request.args.get("test_id"))

    with get_db_connection() as conn:
        with conn.cursor() as cur: 
            if test_id :
                # Buscar test disponible
                cur.execute(""" SELECT t.test_id, t.nombre, t.descripcion FROM test t WHERE t.test_id = %s AND t.status = %s """, (test_id,True,))
                # Obtener todos los test
                r_test = cur.fetchone()
                # Buscar test disponible
                cur.execute(""" SELECT p.pregunta_id, p.enunciado FROM pregunta p WHERE p.test_id = %s""", (test_id,))
                # Obtener todos los test
                r_pregunta = cur.fetchall()

                opciones=[]
                for pregunta in r_pregunta:
                    pregunta_id=pregunta[0]
                    # Buscar test disponible
                    cur.execute(""" SELECT opcion_id, respuesta, es_correcta FROM opcion WHERE pregunta_id = %s AND es_correcta=%s""", (pregunta_id,1,))
                    # Obtener todos los test
                    r_opcion = cur.fetchone()
                    opciones.append(r_opcion)
                return render_template('/evaluacion_aprendizaje/visualizar_tests.html', modulo=modulo, menu_solo=menu_solo, r_test=r_test, r_pregunta=r_pregunta, opciones=opciones,user=user, zip=zip)                
            
# Guardar respuestas del test
@eva_apre.route('/guardar_respuestas', methods=['GET', 'POST'])
def guardar_respuestas():  
    user_id = session.get('user_id')  
    puntaje=0
    intento=1

    if user_id is None:
        return redirect(url_for('index'))

    with get_db_connection() as conn:
        with conn.cursor() as cur: 
            if request.method == 'POST':
                respuestas = []
                test_id = request.form.get('test_id')
                cur.execute("""
                    select i.intento from test t join intento_test i on i.test_id=t.test_id where i.usuario_id=%s and t.status=%s and t.test_id=%s
                """, (user_id,True,test_id,))

                # Obtener todos los test que he realizado
                my_test = cur.fetchone()
                
                if my_test is None:
                    print('entro')
                    intento=1

                    for key in request.form:
                        if key.startswith('pregunta_'):
                            pregunta_id = key.split('_')[1]
                            respuesta = request.form.get(key)
                            respuestas.append((pregunta_id, respuesta))

                    # Aquí podrías guardar las respuestas en la base de datos
                    for pregunta_id, respuesta in respuestas:
                        puntaje+= int(respuesta)
                    
                    # Ejemplo de inserción en base de datos (ajusta a tu modelo):
                    cur.execute("""
                        INSERT INTO intento_test (usuario_id, test_id, puntaje, intento)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, test_id, puntaje ,intento))

                    conn.commit()

                    return redirect(url_for('evaluacion_aprendizaje.visualizar_tests'))  
                else:
                    print('entro2')
                    intento+=my_test[0]

                    for key in request.form:
                        if key.startswith('pregunta_'):
                            pregunta_id = key.split('_')[1]
                            respuesta = request.form.get(key)
                            respuestas.append((pregunta_id, respuesta))

                    # Aquí podrías guardar las respuestas en la base de datos
                    for pregunta_id, respuesta in respuestas:
                        puntaje+= int(respuesta)

                    # Ejemplo de inserción en base de datos (ajusta a tu modelo):
                    cur.execute("""UPDATE intento_test SET puntaje=%s ,intento=%s where usuario_id=%s and test_id=%s""", (puntaje ,intento ,user_id, test_id ))
                    conn.commit()

                    return redirect(url_for('evaluacion_aprendizaje.visualizar_tests'))  
                