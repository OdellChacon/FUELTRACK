document.addEventListener("DOMContentLoaded", () => {
    const sidebar = document.getElementById("sidebar");
    if (sidebar) {
        sidebar.classList.add("fixed");
        sidebar.innerHTML = `
            <div class="sidebar-logo" style="text-align: center; margin-bottom: 0px;">
                <img src="/static/img/logo.png" alt="Logo" style="width: 200px; height: auto;">
            </div>
            <ul>
                <!-- Inicio -->
                <li><a href="/base/dashboard"><i class="bx bx-home"></i> Inicio</a></li>

                <!-- Modulos -->
                <li class="sidebar-section">Modulos</li>
                <li><a href="/estaciones/listar"><i class="bx bx-gas-pump"></i> Estaciones</a></li>
                <li><a href="/usuarios/listar"><i class="bx bx-group"></i> Usuarios</a></li>
                <li><a href="/gestion/"><i class="bx bx-briefcase"></i> Gestión</a></li> <!-- URL corregida -->
                <li><a href="/audit"><i class="bx bx-search-alt"></i> Auditoría</a></li>

                <!-- Opciones -->
                <li class="sidebar-section">Opciones</li>
                <li><a href="/profile"><i class="bx bx-user"></i> Perfil</a></li>
                <li><a href="/logout"><i class="bx bx-log-out"></i> Cerrar sesión</a></li>
            </ul>
        `;

        // Mejora de la animación de entrada
        sidebar.style.opacity = "0";
        sidebar.style.transform = "translateX(-50%) scale(0.9)";
        setTimeout(() => {
            sidebar.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            sidebar.style.opacity = "1";
            sidebar.style.transform = "translateX(0) scale(1)";
        }, 100);
    }
});
