
console.log("Entro JS")

//Mostrarse cuando se cargue
window.addEventListener('load', function () {
    document.body.classList.remove('oculto');
});

// Función reutilizable para validar hCaptcha
function validarHcaptcha(containerId, callback) {
    const response = hcaptcha.getResponse();
    console.log('Hacpchat response',response)
    if (response && response.trim() !== '') {
        console.log(`#${containerId}`)
        callback(); // Ejecuta la lógica si el captcha es válido
    } else {
        $(`#${containerId}`).html('<div class="alert alert-danger mt-3">Por favor completa el hCaptcha.</div>');
    }
}

//RECUPERAR CONTRASEÑA
$(document).ready(function() {
    $('#recuperar-form').off('submit').on('submit', function(e) {
        e.preventDefault();

        if (this.checkValidity()) {
            validarHcaptcha('alertRecuperar', () => {
                $.ajax({
                    type: 'POST',
                    url: $(this).attr('action'),
                    data: $(this).serialize(),
                    success: function(response) {
                        if (response === 'success') {
                            console.log("success")
                            $('#alertRecuperar').html(`
                                <div class="alert alert-success">
                                    <h6 class="text-center fw-bold mb-3 mt-3">¡Contraseña temporal enviada!</h6>
                                    <div class="justify-content-center" style="text-align: justify;">
                                        <small>
                                            Hemos enviado una contraseña temporal a tu correo electrónico. 
                                            Inicia sesión con ella y recuerda cambiarla por una nueva inmediatamente.
                                        </small>
                                    </div>
                                </div>
                            `);
                        } else if (response === 'error') {
                            console.log("error")
                            $('#alertRecuperar').html(`
                                <div class="alert alert-danger">
                                    <h6 class="text-center fw-bold mb-3 mt-3">¡Error!</h6>
                                    <div class="justify-content-center" style="text-align: justify;">
                                        <small>
                                            El correo electrónico no está registrado. 
                                            Por favor, verifica que esté escrito correctamente
                                            o regístralo para crear una nueva cuenta.
                                        </small>
                                    </div>
                                </div>
                            `);
                        }
                    },
                    error: function() {
                        $('#alertRecuperar').html('<div class="alert alert-danger">Error en la solicitud.</div>');
                    }
                });
            });
        } else {
            console.log("hcapcha")
            this.reportValidity();
        }
    });
});


//INICIO DE SESION
$(document).ready(function() {
    // Primero, eliminamos cualquier evento submit previo registrado
    $('#login-form').off('submit').on('submit', function(e) {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function(response) {
                if (response === 'error') {
                    console.log("error");
                    // Alerta por si el correo y contraseña están mal
                    $('#alertContainer').html('<div class="alert alert-danger">Verifica tu correo o contraseña.</div>');
                } else if (response === 'success') {
                    window.location.href = '/index';
                }
            },
            error: function() {
                // Error en la solicitud AJAX
                $('#alertContainer').html('<div class="alert alert-danger">Error en la solicitud.</div>');
            }
        });
    });
});

//REGISTRO
$(document).ready(function() {
    $('#register-form').off('submit').on('submit', function(event) {
        event.preventDefault();

        if (this.checkValidity()) {
            validarHcaptcha('registerContainer', () => {
                $.ajax({
                    type: 'POST',
                    url: $(this).attr('action'),
                    data: $(this).serialize(),
                    success: function(response) {
                        if (response === 'success') {
                            $('#registerContainer').html('<div class="alert alert-success">Se ha creado la cuenta de manera exitosa.</div>');
                        } else if (response === 'exist') {
                            $('#registerContainer').html('<div class="alert alert-danger">Los datos ya existen.</div>');
                        }
                    },
                    error: function() {
                        $('#registerContainer').html('<div class="alert alert-danger">Error en la solicitud.</div>');
                    }
                });
            });
        } else {
            this.reportValidity();
        }
    });
});

//Guardar datos Perfil
$(document).ready(function() {
    $('#perfil-form').off('submit').on('submit', function(event) {
        event.preventDefault();

        if (this.checkValidity()) {
            validarHcaptcha('perfilContainer', () => {
                $.ajax({
                    type: 'POST',
                    url: $(this).attr('action'),
                    data: $(this).serialize(),
                    success: function(response) {
                        if (response === 'success') {
                            $('#perfilContainer').html('<div class="alert alert-success">Se han guardado sus datos de manera exitosa.</div>');
                        }
                    },
                    error: function() {
                        $('#perfilContainer').html('<div class="alert alert-danger">Error en la solicitud.</div>');
                    }
                });
            });
        } else {
            this.reportValidity();
        }
    });
});

//Guardar datos usuario
$(document).ready(function() {
    // Primero, eliminamos cualquier evento submit previo registrado
    $('[id^="usuario-form_"]').off('submit').on('submit', function(e) {
        e.preventDefault();
        const userId = $(this).attr('id').split("_")[1]; // Extrae el ID del usuario
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            success: function(response) {
                if (response === 'error') {
                    console.log("error");
                    // Alerta por si el correo y contraseña están mal
                    $(`#usuarioContainer_${userId}`).html(`<div class="alert alert-danger">El sistema ya alcanzó el número limite permitido de administradores máximos.<br>
                        Si actualizaste el correo, por favor recarga la página para ver los cambios.</div`);
                } else if (response === 'success') {
                    location.reload()
                }else if (response === 'exist') {
                    $(`#usuarioContainer_${userId}`).html(`<div class="alert alert-danger">Lo sentimos, no cuentas con los permisos necesarios para realizar esta acción.</div`);
                }
            },
            error: function() {
                // Error en la solicitud AJAX
                $(`#usuarioContainer_${userId}`).html('<div class="alert alert-danger">Error en la solicitud.</div>');
            }
        });
    });
});

//Guardar datos informacion
$(document).ready(function() {
    $('#informacion-form').off('submit').on('submit', function(event) {
        event.preventDefault();

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
                        $('#informacionContainer').html('<div class="alert alert-success">Se ha guardado la información de manera exitosa.</div>');
                    }else{
                        $('#informacionContainer').html('<div class="alert alert-danger">Tipo de archivo no permitido. <br> Solo se permiten imágenes (.jpg, .jpeg, .png, .svg, .gif).</div>');
                    }
                },
                error: function() {
                    $('#informacionContainer').html('<div class="alert alert-danger">Error en la solicitud.</div>');
                }
            });
        } else {
            this.reportValidity();
        }
    });
});

//Actualizar datos informacion
$(document).ready(function() {
    $('[id^="editInfo-form_"]').off('submit').on('submit', function(e) {
        e.preventDefault();
        const infoId = $(this).attr('id').split("_")[1]; // Extrae el ID del usuario

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
                        $(`#editInfoContainer_${infoId}`).html('<div class="alert alert-danger">Tipo de archivo no permitido. <br> Solo se permiten imágenes (.jpg, .jpeg, .png, .svg, .gif).</div>');
                    }
                },
                error: function() {
                    $(`#editInfoContainer_${infoId}`).html('<div class="alert alert-danger">Error en la solicitud.</div>');
                }
            });
        } else {
            this.reportValidity();
        }
    });
});

//filtros informacion
document.addEventListener('DOMContentLoaded', function () {
    const proyectoSelect = document.querySelector('.proyecto');
    const municipioSelect = document.querySelector('.municipio');
    const veredaSelect = document.querySelector('.vereda');
    const determinanteSelect = document.querySelector('.determinante');


    // Oculta todas las veredas al cargar
    Array.from(veredaSelect.options).forEach(opt => opt.hidden = true);

    function toggleUbicacionFields() {
        const selectedProyecto = proyectoSelect.value;
        const enable = selectedProyecto === '4';

        municipioSelect.disabled = !enable;
        veredaSelect.disabled = !enable;
        determinanteSelect.disabled = !enable;

        if (!enable) {
        municipioSelect.selectedIndex = 0;
        veredaSelect.selectedIndex = 0;
        determinanteSelect.selectedIndex = 0;
        }
    }

    proyectoSelect.addEventListener('change', toggleUbicacionFields);
    toggleUbicacionFields(); // Llamada inicial

    municipioSelect.addEventListener('change', () => {
        const muni = municipioSelect.value;
        veredaSelect.selectedIndex = 0;

        Array.from(veredaSelect.options).forEach(opt => {
        if (!opt.value) {
            opt.hidden = false;
            return;
        }
        opt.hidden = opt.dataset.municipio !== muni;
        });

        // Al cambiar municipio, también forzamos deshabilitar determinante
        determinanteSelect.disabled = true;
        determinanteSelect.selectedIndex = 0;
    });

    veredaSelect.addEventListener('change', function () {
        if (veredaSelect.value) {
        determinanteSelect.disabled = false;
        } else {
        determinanteSelect.disabled = true;
        determinanteSelect.selectedIndex = 0;
        }
    });
});

document.addEventListener('DOMContentLoaded', function () {
    var quill = new Quill('#editor_agregar_info', {
        theme: 'snow'
    });

    document.querySelector('form').addEventListener('submit', function () {
        document.querySelector('#descripcion').value = quill.root.innerHTML;
    });
});

/*Text tarea profesional
var quill = new Quill('#editor', {
    theme: 'snow',
    modules: {
        toolbar: [
        ['bold', 'italic', 'underline'],
        [{'list': 'ordered'}, {'list': 'bullet'}],
        ['link']
        ]
    }
});
document.querySelector('form').addEventListener('submit', function () {
    // Sanitizar el contenido antes de enviarlo
    var contenidoSeguro = DOMPurify.sanitize(quill.root.innerHTML);
    document.querySelector('#descripcion').value = contenidoSeguro;
});*/

//VISUALIZACION DE CONTRASEÑA OJITO
document.getElementById('togglePassword').addEventListener('click', function () {
    const passwordInput = document.getElementById('password_usu');
    const icon = document.getElementById('toggleIcon');
    console.log("OJITO")
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    icon.classList.toggle('bi-eye');
    icon.classList.toggle('bi-eye-slash');
});
