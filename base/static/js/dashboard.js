document.addEventListener("DOMContentLoaded", () => {
    // Mostrar un mensaje de bienvenida
    Swal.fire({
        title: '¡Bienvenido!',
        text: 'Has ingresado al dashboard exitosamente.',
        icon: 'success',
        confirmButtonText: 'Aceptar'
    });

    // Animaciones y estilos para las tarjetas tipo Power BI
    const cards = document.querySelectorAll(".card");
    cards.forEach(card => {
        // Agrega clases Tailwind para fondo, borde y transición
        card.classList.add(
            "bg-gradient-to-br", "from-slate-800", "to-slate-700",
            "rounded-2xl", "shadow-xl", "transition", "duration-300",
            "hover:scale-105", "hover:shadow-2xl", "border", "border-slate-600",
            "p-6", "text-white", "relative", "overflow-hidden"
        );
        // Efecto de resplandor al pasar el mouse
        card.addEventListener("mouseover", () => {
            card.classList.add("ring-4", "ring-blue-400/40");
        });
        card.addEventListener("mouseout", () => {
            card.classList.remove("ring-4", "ring-blue-400/40");
        });
    });

    // Gráfico de Estaciones por Región - estilo Power BI
    const stationsCtx = document.getElementById('stationsChart').getContext('2d');
    new Chart(stationsCtx, {
        type: 'bar',
        data: {
            labels: ['Norte', 'Sur', 'Este', 'Oeste'],
            datasets: [{
                label: 'Estaciones',
                data: [12, 19, 7, 14],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.85)',   // azul
                    'rgba(16, 185, 129, 0.85)',   // verde
                    'rgba(245, 158, 11, 0.85)',   // amarillo
                    'rgba(239, 68, 68, 0.85)'     // rojo
                ],
                borderRadius: 12,
                barPercentage: 0.6,
                categoryPercentage: 0.6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Estaciones por Región',
                    color: '#fff',
                    font: { size: 18, weight: 'bold', family: 'Inter, sans-serif' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#cbd5e1', font: { family: 'Inter, sans-serif' } },
                    grid: { color: 'rgba(100,116,139,0.2)' }
                },
                y: {
                    ticks: { color: '#cbd5e1', font: { family: 'Inter, sans-serif' } },
                    grid: { color: 'rgba(100,116,139,0.2)' }
                }
            }
        }
    });

    // Gráfico de Auditorías por Mes - estilo Power BI
    const auditsCtx = document.getElementById('auditsChart').getContext('2d');
    new Chart(auditsCtx, {
        type: 'line',
        data: {
            labels: ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo'],
            datasets: [{
                label: 'Auditorías',
                data: [5, 10, 8, 15, 12],
                borderColor: '#38bdf8',
                backgroundColor: 'rgba(56, 189, 248, 0.15)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#fff',
                pointBorderColor: '#38bdf8',
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: 'Auditorías por Mes',
                    color: '#fff',
                    font: { size: 18, weight: 'bold', family: 'Inter, sans-serif' }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#cbd5e1', font: { family: 'Inter, sans-serif' } },
                    grid: { color: 'rgba(100,116,139,0.2)' }
                },
                y: {
                    ticks: { color: '#cbd5e1', font: { family: 'Inter, sans-serif' } },
                    grid: { color: 'rgba(100,116,139,0.2)' }
                }
            }
        }
    });
});
