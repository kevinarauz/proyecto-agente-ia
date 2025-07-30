// JavaScript para la aplicación de IA con Agentes

// Inicializar AOS (Animate On Scroll)
AOS.init({
    duration: 800,
    easing: 'ease-in-out',
    once: true
});

// Variables globales
let loadingModal;
let chatBody;
let preguntaInput;
let enviarBtn;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    chatBody = document.getElementById('chatBody');
    preguntaInput = document.getElementById('preguntaInput');
    enviarBtn = document.getElementById('enviarBtn');
    
    // Event listeners
    document.getElementById('chatForm').addEventListener('submit', handleSubmit);
    preguntaInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    });
});

// Manejar envío del formulario
async function handleSubmit(e) {
    e.preventDefault();
    
    const pregunta = preguntaInput.value.trim();
    if (!pregunta) return;
    
    const modo = document.getElementById('modoSelect').value;
    const modelo = document.getElementById('modeloSelect').value;
    
    // Agregar mensaje del usuario al chat
    agregarMensaje(pregunta, 'usuario');
    
    // Limpiar input y deshabilitar botón
    preguntaInput.value = '';
    setLoading(true);
    
    try {
        const respuesta = await enviarPreguntaAPI(pregunta, modo, modelo);
        agregarMensaje(respuesta.respuesta, 'ia', respuesta.modo, respuesta.modelo_usado);
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Hubo un problema al procesar tu pregunta. Por favor, inténtalo de nuevo.',
            confirmButtonColor: '#007bff'
        });
    } finally {
        setLoading(false);
    }
}

// Enviar pregunta a la API
async function enviarPreguntaAPI(pregunta, modo, modelo) {
    const response = await fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            pregunta: pregunta,
            modo: modo,
            modelo: modelo
        })
    });
    
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
}

// Agregar mensaje al chat
function agregarMensaje(texto, tipo, modo = null, modeloUsado = null) {
    const mensajeDiv = document.createElement('div');
    
    if (tipo === 'usuario') {
        mensajeDiv.className = 'mensaje-usuario';
        mensajeDiv.innerHTML = `
            <i class="fas fa-user me-2"></i>
            ${texto}
        `;
    } else if (tipo === 'ia') {
        mensajeDiv.className = 'mensaje-ia';
        const modoIcon = modo === 'agente' ? 'fas fa-search' : 'fas fa-robot';
        const modoBadge = modo === 'agente' ? 
            '<span class="modo-badge modo-agente">Agente</span>' : 
            '<span class="modo-badge modo-simple">Simple</span>';
        
        const modeloBadge = modeloUsado ? 
            `<span class="modelo-badge">${modeloUsado === 'gemini-1.5-flash' ? '🧠 Gemini' : '🦙 Llama3'}</span>` : '';
        
        mensajeDiv.innerHTML = `
            <i class="${modoIcon} me-2"></i>
            ${texto}
            <div class="badges-container">
                ${modoBadge}
                ${modeloBadge}
            </div>
        `;
    }
    
    chatBody.appendChild(mensajeDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Controlar estado de carga
function setLoading(isLoading) {
    if (isLoading) {
        enviarBtn.disabled = true;
        preguntaInput.disabled = true;
        preguntaInput.blur(); // Quitar el foco del input antes de mostrar el modal
        loadingModal.show();
    } else {
        loadingModal.hide();
        enviarBtn.disabled = false;
        preguntaInput.disabled = false;
        // Dar un pequeño delay antes de enfocar para evitar conflictos con el modal
        setTimeout(() => {
            preguntaInput.focus();
        }, 100);
    }
}

// Enviar pregunta predefinida
function enviarPregunta(pregunta, modo) {
    document.getElementById('modoSelect').value = modo;
    preguntaInput.value = pregunta;
    
    // Trigger submit
    const event = new Event('submit');
    document.getElementById('chatForm').dispatchEvent(event);
}

// Ejecutar ejemplo de agente
async function ejemploAgente() {
    Swal.fire({
        title: '🤖 Demo del Agente',
        text: 'El agente ejecutará una búsqueda web de ejemplo. ¿Continuar?',
        icon: 'question',
        showCancelButton: true,
        confirmButtonColor: '#007bff',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, ejecutar',
        cancelButtonText: 'Cancelar'
    }).then(async (result) => {
        if (result.isConfirmed) {
            setLoading(true);
            
            try {
                const response = await fetch('/ejemplo-agente', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                
                // Agregar pregunta y respuesta al chat
                agregarMensaje(data.pregunta, 'usuario');
                agregarMensaje(data.respuesta, 'ia', data.modo);
                
                Swal.fire({
                    icon: 'success',
                    title: '¡Demo Completado!',
                    text: 'El agente ha ejecutado exitosamente una búsqueda web.',
                    confirmButtonColor: '#007bff'
                });
                
            } catch (error) {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error en Demo',
                    text: 'Hubo un problema al ejecutar el demo del agente.',
                    confirmButtonColor: '#007bff'
                });
            } finally {
                setLoading(false);
            }
        }
    });
}

// Limpiar chat
function limpiarChat() {
    Swal.fire({
        title: '🗑️ Limpiar Chat',
        text: '¿Estás seguro de que quieres limpiar toda la conversación?',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, limpiar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            // Limpiar solo los mensajes, mantener el mensaje del sistema
            const mensajes = chatBody.querySelectorAll('.mensaje-usuario, .mensaje-ia');
            mensajes.forEach(mensaje => mensaje.remove());
            
            Swal.fire({
                icon: 'success',
                title: '¡Chat Limpiado!',
                text: 'La conversación ha sido eliminada.',
                timer: 1500,
                showConfirmButton: false
            });
        }
    });
}

// Efectos adicionales
document.addEventListener('DOMContentLoaded', function() {
    // Efecto de escritura para el mensaje del sistema
    const mensajeSistema = document.querySelector('.mensaje-sistema');
    if (mensajeSistema) {
        mensajeSistema.style.opacity = '0';
        setTimeout(() => {
            mensajeSistema.style.transition = 'opacity 1s ease';
            mensajeSistema.style.opacity = '1';
        }, 500);
    }
    
    // Auto-focus en el input
    setTimeout(() => {
        preguntaInput.focus();
    }, 1000);
});

// Prevenir envío de formulario vacío
function validarInput() {
    const pregunta = preguntaInput.value.trim();
    enviarBtn.disabled = !pregunta || preguntaInput.disabled;
}

// Event listener para validación en tiempo real
document.addEventListener('DOMContentLoaded', function() {
    preguntaInput.addEventListener('input', validarInput);
    validarInput(); // Validación inicial
});
