document.addEventListener("DOMContentLoaded", function () {
    const resolveButtons = document.querySelectorAll(".btn-resolve");

    resolveButtons.forEach((button) => {
      button.addEventListener("click", function (event) {
        event.preventDefault();

        const form = button.closest("form");
        const taskItem = button.closest(".task-item");
        const taskId = taskItem.dataset.taskId;

        fetch(form.action, {
          method: "POST",
          headers: {
            "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]")
              .value,
            "Content-Type": "application/json",
          },
          body: JSON.stringify({}),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              const resolveButton = taskItem.querySelector(".btn-resolve");
              if (resolveButton) {
                resolveButton.remove();
              }

              const resolvedList =
                document.querySelector(".tareas-resueltas");
              taskItem.remove();
              resolvedList.appendChild(taskItem);
            } else {
              alert(data.message);
            }
          })
          .catch((error) => {
            console.error("Error:", error);
          });
      });
    });
  });

  // Función para verificar el acceso al archivo
  function checkFileAccess(url, action) {
    console.log(`Intentando ${action} archivo: ${url}`);
    // Puedes añadir lógica de verificación adicional aquí
    return true; // Devuelve false si quieres cancelar la acción
  }

  // Función para manejar errores de archivo
  function handleFileError(error) {
    console.error("Error con el archivo:", error);
    // Usando SweetAlert2 para mostrar el error (si lo tienes implementado)
    if (typeof Swal !== "undefined") {
      Swal.fire({
        title: "Error",
        text: "No se pudo acceder al archivo. Puede que no exista o no tengas permisos.",
        icon: "error",
      });
    } else {
      alert("No se pudo acceder al archivo.");
    }
  }

  // Verificar si los enlaces a archivos funcionan
  document.addEventListener("DOMContentLoaded", function () {
    // Obtener el valor de DEBUG de Django y convertirlo a booleano JS
    const isDebug = "{{ settings.DEBUG|yesno:'true,false' }}" === "true";

    document.querySelectorAll('a[href*="/media/"]').forEach((link) => {
      link.addEventListener("click", function (e) {
        // Solo verificar en producción (cuando no esté en DEBUG)
        if (!isDebug) {
          fetch(this.getAttribute("href"), { method: "HEAD" })
            .then((response) => {
              if (!response.ok) {
                e.preventDefault();
                handleFileError("Archivo no encontrado");
              }
            })
            .catch((error) => {
              e.preventDefault();
              handleFileError(error);
            });
        }
      });
    });
  });