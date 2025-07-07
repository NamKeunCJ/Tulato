//BOTONES MAPA
function mostrarDimensiones(vereda, lat, lng) {
    // Cambiar ubicación del mapa
    const iframe = document.getElementById("mapaIframe");
    iframe.src = `https://maps.google.com/maps?q=${lat},${lng}&z=16&t=k&output=embed`;

    // Ocultar todos los botones específicos
    const todosBotones = document.querySelectorAll(".boton-vereda");
    todosBotones.forEach(btn => btn.style.display = "none");

    // Ocultar botones generales
    const botonesGenerales = document.querySelectorAll("#inicio_1_map > button:not(.boton-vereda):not(#boton-inicio)");
    botonesGenerales.forEach(btn => btn.style.display = "none");

    // Mostrar los botones específicos de la vereda seleccionada
    const ids = [`${vereda}-social`, `${vereda}-economico`, `${vereda}-ambiental`];
    ids.forEach(id => {
    const btn = document.getElementById(id);
    if (btn) btn.style.display = "block";
    });
}

function volverAlInicio() {
    // Restaurar mapa a coordenadas iniciales
    const iframe = document.getElementById("mapaIframe");
    iframe.src = "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d244288.6858243649!2d-78.95750641630411!3d1.5349239928085352!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x8e2cf3ed01eb17a1%3A0x7060d98bb5b209!2zUsOtbyBNaXJh!5e1!3m2!1ses!2sco!4v1746821585462!5m2!1ses!2sco";

    // Ocultar todos los botones específicos
    const todosBotones = document.querySelectorAll(".boton-vereda");
    todosBotones.forEach(btn => btn.style.display = "none");

    // Mostrar botones generales (menos el botón "Inicio" para que no se duplique)
    const botonesGenerales = document.querySelectorAll("#inicio_1_map > button:not(.boton-vereda):not(#boton-inicio)");
    botonesGenerales.forEach(btn => btn.style.display = "block");
}
//Ajax para informacion y botones ocultos
document.getElementById('form-determinantes').addEventListener('submit', async function (e) {
    volverAlInicio()
    e.preventDefault(); // Evita el envío normal del formulario

    const form = e.target;
    const formData = new FormData(form);

    const response = await fetch(form.action, {
        method: 'POST',
        body: formData
    });

    const html = await response.text(); // Esperamos HTML completo

    // Parsear solo la parte de resultados usando DOMParser
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    // Lista de clases que quieres actualizar
    const secciones = ['resultado-filtro', 'resultado-botones'];

    secciones.forEach(clase => {
        const nuevoContenido = doc.querySelector(`.${clase}`);
        const actual = document.querySelector(`.${clase}`);
        if (nuevoContenido && actual) {
        actual.innerHTML = nuevoContenido.innerHTML;
        }
    });
});

document.addEventListener('click', function(e) {
    const btn = e.target.closest('.descargar-btn');
    if (btn) {
        e.preventDefault();
        const id = btn.getAttribute('data-id');
        if (id) {
            window.open(`/gestion_informacion/descargar_info?id_info=${id}`, '_blank');
        }
    }
});

//PAUSA DEL VIDEO
document.addEventListener('DOMContentLoaded', function () {
    const modals = document.querySelectorAll('.modal');

    modals.forEach(modal => {
    modal.addEventListener('hidden.bs.modal', function () {
        const iframe = modal.querySelector('iframe.youtube-iframe');
        if (iframe) {
        // Usa postMessage para pausar el video
        iframe.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
        }
    });
    });
});