from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify

from db import get_db_connection
from app import datos_usuario

# Crear un Blueprint para las rutas hídricas
sis_rep = Blueprint('sistema_reportes', __name__, static_folder='static',template_folder='templates')

# Página principal
@sis_rep.route('/visualizacion_dashboard')
def visualizacion_dashboardx():  
    modulo=2
    menu_solo=8
    user_id = session.get('user_id')  

    if user_id is None :
        return redirect(url_for('index'))

    user = datos_usuario(user_id)  
    print(user)
    with get_db_connection() as conn:
        with conn.cursor() as cur:  
            #Interacción Candelillas, Imbili, Descolgadero
            cur.execute('''select sum(v.cantidad), d.tipo, ve.nombre from visualizacion v
                join contenido c on v.contenido_id=c.contenido_id
                join asociacion_contenido ac on ac.contenido_id=c.contenido_id
                join determinante d on d.determinante_id=ac.determinante_id
                join vereda ve on ve.vereda_id=ac.vereda_id
                WHERE d.determinante_id != %s
                group by d.determinante_id, ve.nombre ''',(4,))
            interaccion_determinante = cur.fetchall()

            #Interacción general
            cur.execute('''select sum(v.cantidad), ve.nombre from visualizacion v
                join contenido c on v.contenido_id=c.contenido_id
                join asociacion_contenido ac on ac.contenido_id=c.contenido_id
                join vereda ve on ve.vereda_id=ac.vereda_id
                group by ve.nombre''')
            interaccion_general = cur.fetchall()

            # Test por resolver
            cur.execute("""
                SELECT t.test_id,  COALESCE(i.porcentaje, 0) AS porcentaje, COALESCE(i.intento, 0) AS intento
                FROM   test t
                LEFT JOIN (
                    SELECT  i.test_id, (i.puntaje * 100.0) / COUNT(p.pregunta_id) AS porcentaje, i.intento
                    FROM intento_test i
                    JOIN pregunta p ON p.test_id = i.test_id
                    WHERE i.usuario_id = %s
                    GROUP BY i.test_id, i.puntaje, i.intento
                ) i ON t.test_id = i.test_id
                WHERE 
                    t.status = %s;
            """, (user_id,True,))

            # Obtener todos los test que he realizado
            my_test = cur.fetchall()

            menor_igual_50 = 0
            mayor_50 = 0
            igual_0 = 0

            for row in my_test:
                if row[1] <= 50 and row[1] != 0:
                    menor_igual_50 += 1
                elif row[1] > 50:
                    mayor_50 += 1
                elif row[1] == 0:
                    igual_0 += 1

            test_realizados = [
                [igual_0, '(0%) '],
                [menor_igual_50, '<= 50%'],
                [mayor_50, '> 50%'],
            ]

            #Mis Descargas
            cur.execute('''select c.contenido_id, c.titulo, p.nombre, m.nombre, v.nombre, d.tipo, de.created_at, de.cantidad, c.status from descarga de
                JOIN contenido c on de.contenido_id=c.contenido_id 
				JOIN asociacion_contenido ac on ac.contenido_id=c.contenido_id
				left JOIN determinante d ON d.determinante_id = ac.determinante_id
	            left JOIN vereda v ON v.vereda_id = ac.vereda_id
	            left JOIN municipio m ON m.municipio_id = ac.municipio_id
	            left JOIN proyecto p ON p.proyecto_id = ac.proyecto_id
				WHERE d.determinante_id != %s and de.usuario_id=%s''',(4,user_id,))
            mis_descargas = cur.fetchall()

            #Seguimiento de Descargas de Información por Responsable
            cur.execute('''select c.contenido_id, c.titulo, p.nombre, m.nombre, v.nombre, d.tipo, u.correo, r.tipo, g.tipo,
                u.edad, ge.tipo, u.discapacidad, de.created_at, de.cantidad, c.status from descarga de
                JOIN contenido c on de.contenido_id=c.contenido_id 
                JOIN usuario u on de.usuario_id=u.usuario_id 
				LEFT JOIN rol r ON r.rol_id = u.rol_id				
				JOIN genero g on u.genero_id=g.genero_id 
				JOIN grupo_etnico ge on u.grupo_id=ge.grupo_id
				JOIN asociacion_contenido ac on ac.contenido_id=c.contenido_id
				left JOIN determinante d ON d.determinante_id = ac.determinante_id
	            left JOIN vereda v ON v.vereda_id = ac.vereda_id
	            left JOIN municipio m ON m.municipio_id = ac.municipio_id
	            left JOIN proyecto p ON p.proyecto_id = ac.proyecto_id 
                WHERE d.determinante_id != %s order by created_at desc''',(4,))
            seguimiento_descargas = cur.fetchall()

            #Comparativa de acierto y error por determinante
            cur.execute('''select g.determinante,ROUND((SUM(g.aciertos) * 100.0) / (SUM(g.aciertos) + SUM(g.errores)),2) as total_aciertos, ROUND((SUM(g.errores) * 100.0) / (SUM(g.aciertos) + SUM(g.errores)),2) as total_errores from
                (SELECT de.tipo as determinante,COUNT(p.pregunta_id) AS total_preguntas_respondidas, 
                it.puntaje as aciertos, COUNT(p.pregunta_id) - it.puntaje AS errores
                from determinante de
                join test t on de.determinante_id=t.determinante_id
                left join intento_test it on it.test_id=t.test_id
                left join usuario u on u.usuario_id=it.usuario_id
                join pregunta p on p.test_id=t.test_id group by de.tipo,it.puntaje) as g
                group by g.determinante order by g.determinante asc
            ''')
            acierto_error = cur.fetchall()

    return render_template('/sistema_reportes/dashboard.html',user=user,modulo=modulo,menu_solo=menu_solo,int_det=interaccion_determinante,int_gen=interaccion_general, test_realizados=test_realizados, mis_descargas=mis_descargas,seg_des=seguimiento_descargas, aci_err=acierto_error)