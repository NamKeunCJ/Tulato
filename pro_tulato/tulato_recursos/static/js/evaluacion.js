//VALIDACION TEST
$(document).ready(function() {
    $('#test-form').off('submit').on('submit', function(e) {
        e.preventDefault();
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function(response) {
                if (response === 'error') {
                    $('#alerta-pregunta').html('<div class="alert alert-danger">Debe agregar al menos una pregunta con sus respectivas respuestas y seleccionar una respuesta correcta.</div>');
                } else if (response === 'success') {
                    $('#alerta-pregunta').html('<div class="alert alert-success">El test ha sido creado y guardado exitosamente.</div>');
                }
            },
            error: function() {
                // Error en la solicitud AJAX
                $('#alerta-pregunta').html('<div class="alert alert-danger">Error en la solicitud.</div>');
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const MAX_PREGUNTAS = 10;
    const MAX_RESPUESTAS = 4;
    const preguntasContainer = document.querySelector('.preguntas-container');
    const agregarPreguntaBtn = document.getElementById('agregar-pregunta');

    let totalPreguntas = 0;

    if (agregarPreguntaBtn && preguntasContainer) {
        agregarPreguntaBtn.addEventListener('click', () => {
            if (totalPreguntas >= MAX_PREGUNTAS) return;

            const preguntaIndex = totalPreguntas;
            const preguntaDiv = document.createElement('div');
            preguntaDiv.classList.add('mb-4', 'pregunta');

            preguntaDiv.innerHTML = `
                <label class="form-label">Pregunta ${preguntaIndex + 1}</label>
                <input type="text" class="form-control mb-2" name="pregunta[]" required maxlength="300">
                <div class="respuestas"></div>
                <button type="button" class="btn btn-sm btn-outline-secondary agregar-respuesta">+ Añadir Respuesta</button>
                <button type="button" class="btn btn-sm btn-outline-danger eliminar-pregunta"><i class="bi bi-trash3-fill"></i> Eliminar Pregunta</button>
            `;

            preguntasContainer.appendChild(preguntaDiv);

            const respuestasDiv = preguntaDiv.querySelector('.respuestas');
            const btnAgregarRespuesta = preguntaDiv.querySelector('.agregar-respuesta');
            const btnEliminarPregunta = preguntaDiv.querySelector('.eliminar-pregunta');

            let respuestas = 0;

            btnAgregarRespuesta.addEventListener('click', () => {
                if (respuestas >= MAX_RESPUESTAS) return;

                const respuestaGroup = document.createElement('div');
                respuestaGroup.classList.add('input-group', 'mb-2');

                respuestaGroup.innerHTML = `
                    <div class="input-group-text">
                        <input type="radio" name="respuesta_correcta[${preguntaIndex}]" value="${respuestas}" required>
                    </div>
                    <input type="text" class="form-control" name="respuesta[${preguntaIndex}][]" placeholder="Respuesta ${respuestas + 1}" required>
                `;

                respuestasDiv.appendChild(respuestaGroup);
                respuestas++;
            });

            // 🔴 Eliminar esta pregunta
            btnEliminarPregunta.addEventListener('click', () => {
                preguntaDiv.remove();
                totalPreguntas--;

                // Renumerar preguntas visibles
                document.querySelectorAll('.pregunta').forEach((element, index) => {
                    const label = element.querySelector('label');
                    if (label) label.textContent = `Pregunta ${index + 1}`;
                });
            });

            totalPreguntas++;
        });
    }
});

//Text tarea profesional
var quill = new Quill('#editor-test', {
    theme: 'snow'
});
document.querySelector('form').addEventListener('submit', function() {
document.querySelector('#contexto').value = quill.root.innerHTML;
});

//Actualizar datos test
$(document).ready(function() {
    $('[id^="editTest-form_"]').off('submit').on('submit', function(e) {
        e.preventDefault();
        const testId = $(this).attr('id').split("_")[1]; // Extrae el ID del usuario

        if (this.checkValidity()) {
            const formData = new FormData(this);  // ⬅️ Esto captura todos los datos, incluyendo archivos

            $.ajax({
                type: 'POST',
                url: $(this).attr('action'),
                data: formData,
                contentType: false,     // ⬅️ No dejar que jQuery establezca el tipo
                processData: false,     // ⬅️ Evitar que intente convertir el FormData en string
                success: function(response) {
                    if (response === 'success') {
                        location.reload()
                    }else{
                        $(`#editTestContainer_${testId}`).html('<div class="alert alert-danger">El estado del test ha sido actualizado. <br>Debido a que ya existen registros asociados, solo es posible modificar el estado del test. Otros cambios no están permitidos para mantener la integridad de los datos.</div>');
                    }
                },
                error: function() {
                    $(`#editTestContainer_${testId}`).html('<div class="alert alert-danger">Error en la solicitud.</div>');
                }
            });
        } else {
            this.reportValidity();
        }
    });
});