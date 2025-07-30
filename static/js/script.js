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
let loadingTimer;
let startTime;

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
        updateLoadingProgress(80, 'Procesando resultados...');
        const respuesta = await enviarPreguntaAPI(pregunta, modo, modelo);
        
        updateLoadingProgress(95, 'Finalizando respuesta...');
        
        // Extraer pasos intermedios si están disponibles
        let pasos = null;
        if (respuesta.pasos_intermedios && respuesta.pasos_intermedios.length > 0) {
            pasos = respuesta.pasos_intermedios.map(paso => {
                if (paso.action && paso.action_input) {
                    return `Acción: ${paso.action} → "${paso.action_input}"`;
                } else if (paso.observation) {
                    return `Resultado: ${paso.observation.substring(0, 100)}...`;
                }
                return paso.toString().substring(0, 80) + '...';
            });
        }
        
        updateLoadingProgress(100, 'Completado!');
        agregarMensaje(respuesta.respuesta, 'ia', respuesta.modo, respuesta.modelo_usado, pasos);
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
    let endpoint = '/chat';
    if (modo === 'busqueda_rapida') {
        endpoint = '/busqueda-rapida';
    }
    
    const response = await fetch(endpoint, {
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
function agregarMensaje(texto, tipo, modo = null, modeloUsado = null, pasos = null) {
    const mensajeDiv = document.createElement('div');
    
    if (tipo === 'usuario') {
        mensajeDiv.className = 'mensaje-usuario';
        mensajeDiv.innerHTML = `
            <i class="fas fa-user me-2"></i>
            ${texto}
        `;
    } else if (tipo === 'ia') {
        mensajeDiv.className = 'mensaje-ia';
        let modoIcon = 'fas fa-robot';
        let modoBadge = '<span class="modo-badge modo-simple">Simple</span>';
        
        if (modo === 'agente' || modo === 'agente_general') {
            modoIcon = 'fas fa-search';
            modoBadge = '<span class="modo-badge modo-agente">Agente</span>';
        } else if (modo === 'busqueda_rapida' || modo === 'busqueda_directa') {
            modoIcon = 'fas fa-bolt';
            modoBadge = '<span class="modo-badge modo-busqueda">Búsqueda Rápida</span>';
        } else if (modo === 'simple_fallback' || modo === 'fallback_general') {
            modoIcon = 'fas fa-exclamation-triangle';
            modoBadge = '<span class="modo-badge modo-fallback">Fallback</span>';
        }
        
        const modeloBadge = modeloUsado ? 
            `<span class="modelo-badge">${modeloUsado === 'gemini-1.5-flash' ? '🧠 Gemini' : '🦙 Llama3'}</span>` : '';
        
        // Agregar cadena de pensamiento si está disponible
        let cadenaPensamiento = '';
        if (pasos && pasos.length > 0) {
            cadenaPensamiento = `
                <div class="cadena-pensamiento mt-2" style="font-size: 0.85em; opacity: 0.8; border-left: 2px solid #007bff; padding-left: 10px;">
                    <strong>🧠 Proceso de pensamiento:</strong>
                    <ul class="mb-0 mt-1">
                        ${pasos.map(paso => `<li>${paso}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        mensajeDiv.innerHTML = `
            <i class="${modoIcon} me-2"></i>
            ${texto}
            ${cadenaPensamiento}
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
function setLoading(isLoading, step = null, progress = 0) {
    if (isLoading) {
        enviarBtn.disabled = true;
        preguntaInput.disabled = true;
        preguntaInput.blur();
        
        // Reiniciar elementos del modal
        document.getElementById('loadingTitle').textContent = 'Procesando tu pregunta...';
        document.getElementById('loadingDescription').textContent = 'El agente está trabajando...';
        document.getElementById('loadingProgress').style.width = '0%';
        document.getElementById('timerValue').textContent = '0';
        document.getElementById('loadingSteps').style.display = 'none';
        
        // Iniciar timer
        startTime = Date.now();
        loadingTimer = setInterval(updateTimer, 100);
        
        loadingModal.show();
        
        // Simular progreso para mejor UX
        setTimeout(() => updateLoadingProgress(20, 'Conectando con el agente...'), 500);
        setTimeout(() => updateLoadingProgress(40, 'Analizando la pregunta...'), 1000);
        setTimeout(() => updateLoadingProgress(60, 'Ejecutando búsqueda web...'), 2000);
        
    } else {
        clearInterval(loadingTimer);
        loadingModal.hide();
        enviarBtn.disabled = false;
        preguntaInput.disabled = false;
        setTimeout(() => {
            preguntaInput.focus();
        }, 100);
    }
}

// Actualizar timer
function updateTimer() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    document.getElementById('timerValue').textContent = elapsed;
    
    // Mostrar pasos después de 3 segundos
    if (elapsed >= 3) {
        document.getElementById('loadingSteps').style.display = 'block';
    }
}

// Actualizar progreso de carga
function updateLoadingProgress(progress, step) {
    document.getElementById('loadingProgress').style.width = progress + '%';
    if (step) {
        document.getElementById('currentStep').textContent = step;
        document.getElementById('loadingSteps').style.display = 'block';
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

// Función para demo general del agente
async function demoGeneral() {
    try {
        const { value: tipoDemo } = await Swal.fire({
            title: '🌐 Demo Agente General',
            text: 'Selecciona qué tipo de información quieres que busque el agente:',
            icon: 'question',
            input: 'select',
            inputOptions: {
                'noticias': '📰 Noticias de IA',
                'bitcoin': '₿ Precio Bitcoin',
                'deportes': '⚽ Deportes recientes',
                'tech': '💻 Noticias OpenAI',
                'economia': '📈 Precio petróleo',
                'general': '🌐 Noticias generales'
            },
            inputPlaceholder: 'Selecciona una opción',
            showCancelButton: true,
            confirmButtonColor: '#007bff',
            cancelButtonColor: '#6c757d',
            confirmButtonText: '🚀 Ejecutar Demo',
            cancelButtonText: 'Cancelar'
        });

        if (tipoDemo) {
            setLoading(true);
            
            // Actualizar progreso específico para demo
            setTimeout(() => updateLoadingProgress(30, 'Preparando demo...'), 300);
            setTimeout(() => updateLoadingProgress(50, 'Ejecutando búsqueda especializada...'), 800);
            setTimeout(() => updateLoadingProgress(70, 'Analizando resultados...'), 1500);
            
            const response = await fetch('/agente-general', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    tipo: tipoDemo,
                    modelo: document.getElementById('modeloSelect').value
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            updateLoadingProgress(90, 'Formateando respuesta...');
            
            // Extraer pasos intermedios si están disponibles
            let pasos = null;
            if (data.pasos_intermedios && data.pasos_intermedios.length > 0) {
                pasos = data.pasos_intermedios.map(paso => {
                    if (paso.action && paso.action_input) {
                        return `Acción: ${paso.action} → "${paso.action_input}"`;
                    } else if (paso.observation) {
                        return `Resultado: ${paso.observation.substring(0, 100)}...`;
                    }
                    return paso.toString().substring(0, 80) + '...';
                });
            }
            
            updateLoadingProgress(100, 'Demo completado!');
            agregarMensaje(data.pregunta, 'usuario');
            agregarMensaje(data.respuesta, 'ia', data.modo, data.modelo_usado, pasos);
            
            const tipoEmoji = {
                'noticias': '📰', 'bitcoin': '₿', 'deportes': '⚽', 
                'tech': '💻', 'economia': '�', 'general': '🌐'
            };
            
            Swal.fire({
                icon: 'success',
                title: `${tipoEmoji[tipoDemo]} Demo Completado`,
                text: `El agente ha buscado información sobre ${data.tipo_demo} exitosamente.`,
                confirmButtonColor: '#007bff',
                timer: 3000
            });
        }
        
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'Hubo un problema al ejecutar el demo general.',
            confirmButtonColor: '#007bff'
        });
    } finally {
        setLoading(false);
    }
}


