document.addEventListener('DOMContentLoaded', () => {
    console.log('Usuarios JS cargado.');
});

function openModal(action) {
    const modal = document.getElementById("modalFormat");
    const modalTitle = document.getElementById("modalTitle");

    if (action === "import") {
        modalTitle.textContent = "Seleccione el formato de Importación";
        modal.setAttribute("data-action", "import");
    } else if (action === "export") {
        modalTitle.textContent = "Seleccione el formato de Exportación";
        modal.setAttribute("data-action", "export");
    }

    modal.classList.remove("hidden");
}

function closeModal() {
    document.getElementById("modalFormat").classList.add("hidden");
}

function handleAction(format) {
    const modal = document.getElementById("modalFormat");
    const action = modal.getAttribute("data-action");
    // Lista de formatos soportados por el backend
    const formatosSoportados = ["csv", "excel", "json", "xml", "pdf", "sql"];

    if (action === "import") {
        const input = document.createElement("input");
        input.type = "file";
        input.accept = getAcceptFormat(format);
        input.onchange = () => handleImport(input.files[0], format);
        input.click();
    } else if (action === "export") {
        if (!formatosSoportados.includes(format)) {
            alert("Formato no soportado para exportar.");
            return;
        }
        const exportUrl = `/usuarios/exportar/${format}/`;
        window.location.href = exportUrl;
    }
}

// Actualiza la función para recibir el formato (aunque el backend lo detecta por extensión)
function handleImport(file, formato) {
    const form = new FormData();
    form.append("csrfmiddlewaretoken", getCSRFToken());
    form.append("file", file);

    fetch("/usuarios/importar/", {
        method: "POST",
        body: form
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            response.text().then(text => alert("Error al importar el archivo: " + text));
        }
    })
    .catch(error => {
        alert("Hubo un error al procesar el archivo: " + error.message);
    });
}

function getAcceptFormat(format) {
    const formats = {
        csv: ".csv",
        excel: ".xls,.xlsx",
        sql: ".sql",
        json: ".json",
        xml: ".xml",
        pdf: ".pdf"
    };
    return formats[format] || "";
}

function getCSRFToken() {
    // Intenta obtener el token del input, si no existe, busca en cookies
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    if (input) return input.value;
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
}

// Hacer confirmDelete global para que funcione desde el HTML
window.confirmDelete = function(id) {
    console.log('Intentando eliminar usuario', id);
    Swal.fire({
        title: '¿Estás seguro?',
        text: "Esta acción no se puede deshacer.",
        icon: 'warning',
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        showCancelButton: true
    }).then((result) => {
        if (result.isConfirmed) {
            const csrftoken = getCSRFToken();
            fetch(`/usuarios/eliminar/${id}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                console.log('Respuesta fetch:', response);
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor');
                }
                return response.json();
            })
            .then(data => {
                console.log('Respuesta JSON:', data);
                if (data.success) {
                    const row = document.querySelector(`tr[data-id="${id}"]`);
                    if (row) row.remove();
                    Swal.fire({
                        title: 'Eliminado',
                        text: 'El registro ha sido eliminado.',
                        icon: 'success',
                        timer: 2000,
                        showConfirmButton: false,
                        toast: true,
                        position: 'top-end'
                    });
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: data.message,
                        icon: 'error',
                        timer: 2000,
                        showConfirmButton: false,
                        toast: true,
                        position: 'top-end'
                    });
                }
            })
            .catch(error => {
                console.error('Error en fetch:', error);
                Swal.fire({
                    title: 'Error',
                    text: 'Ocurrió un error al procesar la solicitud.',
                    icon: 'error',
                    timer: 2000,
                    showConfirmButton: false,
                    toast: true,
                    position: 'top-end'
                });
            });
        }
    });
};
