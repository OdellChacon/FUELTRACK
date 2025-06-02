document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loginForm");
    const username = document.getElementById("username");
    const password = document.getElementById("password");

    form.addEventListener("submit", (e) => {
        if (username.value.trim() === "" || password.value.trim() === "") {
            e.preventDefault();
            alert("Por favor, completa todos los campos.");
        }

        const csrfToken = getCookie('csrftoken'); // Obtener el token CSRF
        const headers = new Headers();
        headers.append("X-CSRFToken", csrfToken);

        // Si usas fetch para enviar el formulario:
        // fetch(form.action, { method: "POST", headers, body: new FormData(form) });

        // Si no usas JavaScript para enviar el formulario, no necesitas este paso.
    });

    username.addEventListener("focus", () => {
        username.style.borderColor = "#007BFF";
    });

    password.addEventListener("focus", () => {
        password.style.borderColor = "#007BFF";
    });

    // Crear contenedor de ondas
    const waveContainer = document.createElement("div");
    waveContainer.classList.add("wave-container");

    // Crear y añadir ondas
    for (let i = 0; i < 3; i++) {
        const wave = document.createElement("div");
        wave.classList.add("wave");
        waveContainer.appendChild(wave);
    }

    // Añadir el contenedor al body
    document.body.appendChild(waveContainer);

    // Seleccionar las ondas y ajustar dinámicamente su posición
    const waves = document.querySelectorAll('.wave');
    setInterval(() => {
        waves.forEach((wave, index) => {
            const offset = Math.sin(Date.now() / 1000 + index) * 10; // Movimiento sinusoidal
            wave.style.transform = `translateX(-50%) translateY(${offset}px)`;
        });
    }, 50);

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
