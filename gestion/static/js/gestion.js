document.addEventListener('DOMContentLoaded', function() {
    // window.gestionVars debe estar definido en el template antes de cargar este JS
    const vars = window.gestionVars || {};
    const consumoInput = document.getElementById('consumo-input');
    const nivelCombustible = document.getElementById('nivel-combustible');
    const autonomiaHrs = document.getElementById('autonomia-hrs');
    const necesario100 = document.getElementById('necesario-100');
    const porcentajeBarra = document.getElementById('porcentaje-barra');
    const vacio24 = document.getElementById('vacio-24');
    const real24 = document.getElementById('real-24');
    const vacio36 = document.getElementById('vacio-36');
    const real36 = document.getElementById('real-36');
    const vacio48 = document.getElementById('vacio-48');
    const real48 = document.getElementById('real-48');
    const vacio72 = document.getElementById('vacio-72');
    const real72 = document.getElementById('real-72');
    const vacio96 = document.getElementById('vacio-96');
    const real96 = document.getElementById('real-96');
    const capacidadAnteriorInput = document.getElementById('capacidad-anterior-input');
    const disponibleInput = document.getElementById('disponible-input');
    const nivelCombustibleInput = document.getElementById('nivel-combustible-input');
    const disponibleTarjeta = document.getElementById('disponible-tarjeta');
    const tanqueBaseInput = document.getElementById('tanque-base-input');
    const tanqueExternoInput = document.getElementById('tanque-externo-input');
    const totalTanqueDiv = document.getElementById('total-tanque');
    const iconoTanqueReserva = document.getElementById('icono-tanque-reserva');
    const iconoTanqueBase = document.getElementById('icono-tanque-base');
    const iconoTanqueExterno = document.getElementById('icono-tanque-externo');
    const capacidadMaximaReservaInput = document.getElementById('capacidad-maxima-reserva-input');

    // Datos base desde el backend (pasados como window.gestionVars)
    const capacidadAnterior = parseFloat(vars.capacidadAnterior) || 0;
    const suministros = (
        (parseFloat(vars.suministro_w19) || 0) +
        (parseFloat(vars.suministro_w20) || 0) +
        (parseFloat(vars.suministro_w21) || 0) +
        (parseFloat(vars.suministro_w22) || 0)
    );
    const hrsTotal = parseFloat(vars.hrsTotal) || 0;
    const totalTanque = parseFloat(vars.totalTanque) || 0;

    function updateCamposDependientes(consumo, capacidadAnteriorOverride) {
        consumo = parseFloat(consumo) || 0;
        let capacidad = typeof capacidadAnteriorOverride !== "undefined"
            ? parseFloat(capacidadAnteriorOverride) || 0
            : capacidadAnterior;
        const nivel = capacidad + suministros - (hrsTotal * consumo);
        const nivelPositivo = Math.max(nivel, 0);
        nivelCombustible.textContent = nivelPositivo.toFixed(0) + " Lts";
        const autonomia = consumo > 0 ? nivelPositivo / consumo : 0;
        autonomiaHrs.textContent = Math.round(autonomia);
        const necesario = totalTanque - nivelPositivo;
        necesario100.textContent = necesario.toFixed(0) + " Lts";
        const porcentaje = totalTanque > 0 ? (nivelPositivo * 100 / totalTanque) : 0;
        porcentajeBarra.textContent = porcentaje.toFixed(1) + "%";
        vacio24.textContent = (consumo * 24).toFixed(0);
        vacio36.textContent = (consumo * 36).toFixed(0);
        vacio48.textContent = (consumo * 48).toFixed(0);
        vacio72.textContent = (consumo * 72).toFixed(0);
        vacio96.textContent = (consumo * 96).toFixed(0);
        real24.textContent = (autonomia > 24 ? 0 : (24 * consumo - nivelPositivo)).toFixed(0);
        real36.textContent = (autonomia > 36 ? 0 : (36 * consumo - nivelPositivo)).toFixed(0);
        real48.textContent = (autonomia > 48 ? 0 : (48 * consumo - nivelPositivo)).toFixed(0);
        real72.textContent = (autonomia > 72 ? 0 : (72 * consumo - nivelPositivo)).toFixed(0);
        real96.textContent = (autonomia > 96 ? 0 : (96 * consumo - nivelPositivo)).toFixed(0);
    }
    if (consumoInput) {
        consumoInput.addEventListener('input', function() {
            updateCamposDependientes(consumoInput.value, capacidadAnteriorInput ? capacidadAnteriorInput.value : undefined);
        });
        updateCamposDependientes(consumoInput.value, capacidadAnteriorInput ? capacidadAnteriorInput.value : undefined);
        consumoInput.addEventListener('change', function() {
            const newConsumo = consumoInput.value;
            fetch(vars.urlActualizarConsumo, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": vars.csrfToken
                },
                body: JSON.stringify({ consumo: newConsumo })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    consumoInput.classList.add('border-green-500');
                    setTimeout(() => consumoInput.classList.remove('border-green-500'), 1000);
                } else {
                    consumoInput.classList.add('border-red-500');
                    setTimeout(() => consumoInput.classList.remove('border-red-500'), 1000);
                }
            });
        });
    }

    // NUEVO: Capacidad Anterior en tiempo real
    if (capacidadAnteriorInput) {
        capacidadAnteriorInput.addEventListener('input', function() {
            updateCamposDependientes(consumoInput ? consumoInput.value : 0, capacidadAnteriorInput.value);
        });
        capacidadAnteriorInput.addEventListener('change', function() {
            const newCapacidad = capacidadAnteriorInput.value;
            fetch(vars.urlActualizarCapacidad, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": vars.csrfToken
                },
                body: JSON.stringify({ capacidad_anterior: newCapacidad })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    capacidadAnteriorInput.classList.add('border-green-500');
                    setTimeout(() => capacidadAnteriorInput.classList.remove('border-green-500'), 1000);
                } else {
                    capacidadAnteriorInput.classList.add('border-red-500');
                    setTimeout(() => capacidadAnteriorInput.classList.remove('border-red-500'), 1000);
                }
            });
        });
    }

    // NUEVO: Disponible en tiempo real
    if (disponibleInput) {
        disponibleInput.addEventListener('input', function() {
            // Actualiza la tarjeta de disponible en tiempo real
            if (disponibleTarjeta) {
                disponibleTarjeta.textContent = (parseFloat(disponibleInput.value) || 0).toFixed(0) + " Lts";
            }
        });
        disponibleInput.addEventListener('change', function() {
            const newDisponible = disponibleInput.value;
            fetch(vars.urlActualizarDisponible, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": vars.csrfToken
                },
                body: JSON.stringify({ disponible: newDisponible })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    disponibleInput.classList.add('border-green-500');
                    setTimeout(() => disponibleInput.classList.remove('border-green-500'), 1000);
                } else {
                    disponibleInput.classList.add('border-red-500');
                    setTimeout(() => disponibleInput.classList.remove('border-red-500'), 1000);
                }
            });
        });
    }

    // NUEVO: Nivel en tiempo real
    if (nivelCombustibleInput) {
        nivelCombustibleInput.addEventListener('input', function() {
            // Si quieres recalcular otros campos, llama a updateCamposDependientes aquí
        });
        nivelCombustibleInput.addEventListener('change', function() {
            const newNivel = nivelCombustibleInput.value;
            fetch(vars.urlActualizarNivel, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": vars.csrfToken
                },
                body: JSON.stringify({ nivel_combustible: newNivel })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    nivelCombustibleInput.classList.add('border-green-500');
                    setTimeout(() => nivelCombustibleInput.classList.remove('border-green-500'), 1000);
                } else {
                    nivelCombustibleInput.classList.add('border-red-500');
                    setTimeout(() => nivelCombustibleInput.classList.remove('border-red-500'), 1000);
                }
            });
        });
    }

    // NUEVO: Tanque Base en tiempo real
    if (tanqueBaseInput) {
        tanqueBaseInput.addEventListener('input', function() {
            // Actualiza el total en tiempo real
            const base = parseFloat(tanqueBaseInput.value) || 0;
            const externo = tanqueExternoInput ? (parseFloat(tanqueExternoInput.value) || 0) : 0;
            if (totalTanqueDiv) {
                totalTanqueDiv.textContent = (base + externo).toFixed(0);
            }
            // Actualiza dependientes si lo deseas
        });
        tanqueBaseInput.addEventListener('change', function() {
            const newBase = tanqueBaseInput.value;
            fetch(vars.urlActualizarTanqueBase, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": vars.csrfToken
                },
                body: JSON.stringify({ tanque_base: newBase })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    tanqueBaseInput.classList.add('border-green-500');
                    setTimeout(() => tanqueBaseInput.classList.remove('border-green-500'), 1000);
                } else {
                    tanqueBaseInput.classList.add('border-red-500');
                    setTimeout(() => tanqueBaseInput.classList.remove('border-red-500'), 1000);
                }
            });
        });
    }

    // NUEVO: Tanque Externo en tiempo real
    if (tanqueExternoInput) {
        tanqueExternoInput.addEventListener('input', function() {
            // Actualiza el total en tiempo real
            const base = tanqueBaseInput ? (parseFloat(tanqueBaseInput.value) || 0) : 0;
            const externo = parseFloat(tanqueExternoInput.value) || 0;
            if (totalTanqueDiv) {
                totalTanqueDiv.textContent = (base + externo).toFixed(0);
            }
            // Actualiza dependientes si lo deseas
        });
        tanqueExternoInput.addEventListener('change', function() {
            const newExterno = tanqueExternoInput.value;
            fetch(vars.urlActualizarTanqueExterno, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": vars.csrfToken
                },
                body: JSON.stringify({ tanque_externo: newExterno })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    tanqueExternoInput.classList.add('border-green-500');
                    setTimeout(() => tanqueExternoInput.classList.remove('border-green-500'), 1000);
                } else {
                    tanqueExternoInput.classList.add('border-red-500');
                    setTimeout(() => tanqueExternoInput.classList.remove('border-red-500'), 1000);
                }
            });
        });
    }

    // NUEVO: Capacidad máxima tanque reserva en tiempo real
    if (capacidadMaximaReservaInput) {
        capacidadMaximaReservaInput.addEventListener('change', function() {
            const valor = capacidadMaximaReservaInput.value;
            fetch(window.gestionVars.urlActualizarCapacidadMaximaReserva, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": window.gestionVars.csrfToken
                },
                body: JSON.stringify({ capacidad_maxima_reserva: valor })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    capacidadMaximaReservaInput.classList.add('border-green-500');
                    setTimeout(() => capacidadMaximaReservaInput.classList.remove('border-green-500'), 1000);
                } else {
                    capacidadMaximaReservaInput.classList.add('border-red-500');
                    setTimeout(() => capacidadMaximaReservaInput.classList.remove('border-red-500'), 1000);
                }
            })
            .catch(() => {
                capacidadMaximaReservaInput.classList.add('border-red-500');
                setTimeout(() => capacidadMaximaReservaInput.classList.remove('border-red-500'), 1000);
            });
        });
    }

    // --- Bloqueo persistente de tanques con estado inicial ---
    function setBloqueoTanque(icon, input, bloqueado, colorBloqueado, colorNormal) {
        input.disabled = bloqueado;
        if (bloqueado) {
            icon.classList.remove(colorNormal);
            icon.classList.add(colorBloqueado, 'opacity-60');
            input.classList.add('border-red-500');
            icon.style.backgroundColor = "#f87171";
            icon.style.color = "#fff";
        } else {
            icon.classList.remove(colorBloqueado, 'opacity-60');
            icon.classList.add(colorNormal);
            input.classList.remove('border-red-500');
            icon.style.backgroundColor = "";
            icon.style.color = "";
        }
    }

    // Estado inicial desde window.gestionVars
    setBloqueoTanque(
        iconoTanqueReserva,
        disponibleInput,
        vars.tanqueReservaCondenado,
        'bg-gray-300', 'bg-purple-100'
    );
    setBloqueoTanque(
        iconoTanqueBase,
        tanqueBaseInput,
        vars.tanqueBaseCondenado,
        'bg-gray-300', 'bg-blue-100'
    );
    setBloqueoTanque(
        iconoTanqueExterno,
        tanqueExternoInput,
        vars.tanqueExternoCondenado,
        'bg-gray-300', 'bg-green-100'
    );

    // Click para alternar bloqueo, persistente vía backend
    if (iconoTanqueReserva && disponibleInput) {
        iconoTanqueReserva.addEventListener('click', function() {
            fetch(vars.urlToggleTanqueReserva, {
                method: "POST",
                headers: { "X-CSRFToken": vars.csrfToken }
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    setBloqueoTanque(
                        iconoTanqueReserva,
                        disponibleInput,
                        data.condenado,
                        'bg-gray-300', 'bg-purple-100'
                    );
                }
            });
        });
    }
    if (iconoTanqueBase && tanqueBaseInput) {
        iconoTanqueBase.addEventListener('click', function() {
            fetch(vars.urlToggleTanqueBase, {
                method: "POST",
                headers: { "X-CSRFToken": vars.csrfToken }
            })
            .then (r => r.json())
            .then(data => {
                if (data.success) {
                    setBloqueoTanque(
                        iconoTanqueBase,
                        tanqueBaseInput,
                        data.condenado,
                        'bg-gray-300', 'bg-blue-100'
                    );
                }
            });
        });
    }
    if (iconoTanqueExterno && tanqueExternoInput) {
        iconoTanqueExterno.addEventListener('click', function() {
            fetch(vars.urlToggleTanqueExterno, {
                method: "POST",
                headers: { "X-CSRFToken": vars.csrfToken }
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    setBloqueoTanque(
                        iconoTanqueExterno,
                        tanqueExternoInput,
                        data.condenado,
                        'bg-gray-300', 'bg-green-100'
                    );
                }
            });
        });
    }

    // Modal importar horas
    window.openModalImportarHoras = () => {
        document.getElementById('modalImportarHoras').classList.remove('hidden');
        document.getElementById('importHorasResumen').innerHTML = '';
        document.getElementById('fileHorasInput').value = '';
    };
    window.closeModalImportarHoras = () => {
        document.getElementById('modalImportarHoras').classList.add('hidden');
    };
    window.importarHorasTrabajo = () => {
        const fileInput = document.getElementById('fileHorasInput');
        const resumenDiv = document.getElementById('importHorasResumen');
        if (!fileInput.files.length) {
            resumenDiv.innerHTML = '<span class="text-red-500">Seleccione un archivo.</span>';
            return;
        }
        const form = new FormData();
        form.append('file', fileInput.files[0]);
        form.append('gestion_id', vars.gestionId);
        fetch(vars.urlImportarHorasDetalle, {
            method: 'POST',
            headers: {
                'X-CSRFToken': vars.csrfToken
            },
            body: form
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                let resumenHtml = '';
                if (data.resumen && data.resumen.length) {
                    resumenHtml = '<ul style="text-align:left;">';
                    data.resumen.forEach(linea => {
                        resumenHtml += '<li>' + linea + '</li>';
                    });
                    resumenHtml += '</ul>';
                }
                Swal.fire({
                    icon: 'success',
                    title: 'Importación exitosa',
                    html: resumenHtml || 'Horas importadas correctamente.',
                    confirmButtonText: 'OK',
                    customClass: {
                        popup: 'swal2-rounded swal2-shadow'
                    }
                }).then(() => {
                    location.reload();
                });
                resumenDiv.innerHTML = '';
                window.closeModalImportarHoras();
            } else {
                resumenDiv.innerHTML = '<span class="text-red-500">Error: ' + data.message + '</span>';
            }
        })
        .catch(error => {
            resumenDiv.innerHTML = '<span class="text-red-500">Error de red o servidor.</span>';
        });
    };

    // Modal pegar horas
    window.openModalPegarHoras = () => {
        document.getElementById('modalPegarHoras').classList.remove('hidden');
        document.getElementById('importPegarResumen').innerHTML = '';
        document.getElementById('textareaHoras').value = '';
    };
    window.closeModalPegarHoras = () => {
        document.getElementById('modalPegarHoras').classList.add('hidden');
    };
    window.enviarHorasPegadas = () => {
        const textarea = document.getElementById('textareaHoras');
        const resumenDiv = document.getElementById('importPegarResumen');
        const texto = textarea.value.trim();
        if (!texto) {
            resumenDiv.innerHTML = '<span class="text-red-500">Pegue los registros primero.</span>';
            return;
        }
        const form = new FormData();
        form.append('texto', texto);
        form.append('gestion_id', vars.gestionId);
        fetch(vars.urlImportarHorasPegar, {
            method: 'POST',
            headers: {
                'X-CSRFToken': vars.csrfToken
            },
            body: form
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                let resumenHtml = '';
                if (data.resumen && data.resumen.length) {
                    resumenHtml = '<ul style="text-align:left;">';
                    data.resumen.forEach(linea => {
                        resumenHtml += '<li>' + linea + '</li>';
                    });
                    resumenHtml += '</ul>';
                }
                Swal.fire({
                    icon: 'success',
                    title: 'Importación exitosa',
                    html: resumenHtml || 'Horas importadas correctamente.',
                    confirmButtonText: 'OK',
                    customClass: {
                        popup: 'swal2-rounded swal2-shadow'
                    }
                }).then(() => {
                    location.reload();
                });
                resumenDiv.innerHTML = '';
                window.closeModalPegarHoras();
            } else {
                resumenDiv.innerHTML = '<span class="text-red-500">Error: ' + data.message + '</span>';
            }
        })
        .catch(error => {
            resumenDiv.innerHTML = '<span class="text-red-500">Error de red o servidor.</span>';
        });
    };

    // NUEVO: Inputs de suministro y horas trabajo
    const semanas = [19, 20, 21, 22, 23];
    semanas.forEach(function(sem) {
        const suministroInput = document.getElementById('suministro-w' + sem);
        const horasInput = document.getElementById('horas-w' + sem);
        if (suministroInput) {
            suministroInput.addEventListener('input', function() {
                guardarSemana(sem);
            });
        }
        if (horasInput) {
            horasInput.addEventListener('input', function() {
                guardarSemana(sem);
            });
        }
    });
    function guardarSemana(sem) {
        const data = {
            semana: sem,
            suministro: parseFloat(document.getElementById('suministro-w' + sem).value) || 0,
            horas_trabajo: parseFloat(document.getElementById('horas-w' + sem).value) || 0
        };
        fetch(vars.urlActualizarSemana, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": vars.csrfToken
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            const suministroInput = document.getElementById('suministro-w' + sem);
            const horasInput = document.getElementById('horas-w' + sem);
            if (data.success) {
                suministroInput.classList.add('border-green-500');
                horasInput.classList.add('border-green-500');
                setTimeout(() => {
                    suministroInput.classList.remove('border-green-500');
                    horasInput.classList.remove('border-green-500');
                }, 500);
                updateCamposDependientes(consumoInput.value);
                // Actualiza el promedio diario en la tabla
                if (data.promedio_diario !== undefined) {
                    const promedioTd = document.getElementById('promedio-w' + sem);
                    if (promedioTd) promedioTd.textContent = parseFloat(data.promedio_diario).toFixed(2);
                }
            } else {
                suministroInput.classList.add('border-red-500');
                horasInput.classList.add('border-red-500');
                setTimeout(() => {
                    suministroInput.classList.remove('border-red-500');
                    horasInput.classList.remove('border-red-500');
                }, 1000);
            }
        });
    }
});
