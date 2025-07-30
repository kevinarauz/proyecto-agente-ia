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
    
    // Capturar tiempo de inicio
    const tiempoInicio = new Date();
    
    // Agregar mensaje del usuario al chat
    agregarMensaje(pregunta, 'usuario');
    
    // Limpiar input y deshabilitar botón
    preguntaInput.value = '';
    setLoading(true);
    
    try {
        updateLoadingProgress(80, 'Procesando resultados...');
        const respuesta = await enviarPreguntaAPI(pregunta, modo, modelo);
        
        // Capturar tiempo de finalización
        const tiempoFin = new Date();
        const duracion = ((tiempoFin - tiempoInicio) / 1000).toFixed(1);
        
        updateLoadingProgress(95, 'Finalizando respuesta...');
        
        // Extraer pasos intermedios y pensamientos si están disponibles
        let pasos = null;
        let pensamientos = null;
        
        if (respuesta.pasos_intermedios && respuesta.pasos_intermedios.length > 0) {
            pasos = respuesta.pasos_intermedios.map((paso, index) => {
                if (paso.action && paso.action_input) {
                    return `� <strong>Paso ${paso.step || index + 1}:</strong> ${paso.thought || paso.action}<br>
                            📥 <strong>Entrada:</strong> ${paso.action_input}<br>
                            � <strong>Resultado:</strong> ${paso.observation.substring(0, 200)}...`;
                }
                return `📊 <strong>Paso ${index + 1}:</strong> ${paso.toString().substring(0, 150)}...`;
            });
        }
        
        if (respuesta.pensamientos && respuesta.pensamientos.length > 0) {
            pensamientos = respuesta.pensamientos;
        } else if (!pasos) {
            // Si no hay pasos ni pensamientos, crear uno básico
            pensamientos = ['💭 Procesando consulta usando conocimiento base del modelo'];
        }
        
        // Crear metadata mejorada
        const metadata = {
            tiempoInicio: respuesta.metadata?.timestamp_inicio ? new Date(respuesta.metadata.timestamp_inicio * 1000) : tiempoInicio,
            tiempoFin: respuesta.metadata?.timestamp_fin ? new Date(respuesta.metadata.timestamp_fin * 1000) : tiempoFin,
            duracion: respuesta.metadata?.duracion || duracion,
            iteraciones: respuesta.metadata?.iteraciones || 0,
            busquedas: respuesta.metadata?.busquedas || 0
        };
        
        updateLoadingProgress(100, 'Completado!');
        agregarMensaje(respuesta.respuesta, 'ia', respuesta.modo, respuesta.modelo_usado, pasos, metadata, pensamientos);
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
function agregarMensaje(texto, tipo, modo = null, modeloUsado = null, pasos = null, metadata = null, pensamientos = null) {
    const mensajeDiv = document.createElement('div');
    const timestamp = new Date();
    const uniqueId = Date.now() + Math.random().toString(36).substr(2, 9);
    
    if (tipo === 'usuario') {
        mensajeDiv.className = 'mensaje-usuario';
        mensajeDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <i class="fas fa-user me-2"></i>
                    ${texto}
                </div>
                <small class="text-muted ms-2">${formatearTiempo(timestamp)}</small>
            </div>
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
        
        // Agregar proceso de pensamiento detallado si está disponible
        let procesoCompleto = '';
        if (pensamientos && pensamientos.length > 0) {
            procesoCompleto = `
                <div class="proceso-pensamiento mt-3">
                    <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#pensamiento-${uniqueId}" aria-expanded="false">
                        <i class="fas fa-brain me-1"></i>Ver proceso de pensamiento (${pensamientos.length} pasos)
                    </button>
                    <div class="collapse mt-2" id="pensamiento-${uniqueId}">
                        <div class="card card-body bg-light">
                            <h6 class="mb-3"><i class="fas fa-cogs me-1"></i>Proceso de razonamiento:</h6>
                            ${pensamientos.map((pensamiento, index) => `
                                <div class="paso-pensamiento mb-2 p-2 border-start border-3 border-primary">
                                    ${pensamiento}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        } else if (pasos && pasos.length > 0) {
            procesoCompleto = `
                <div class="proceso-pensamiento mt-3">
                    <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#pensamiento-${uniqueId}" aria-expanded="false">
                        <i class="fas fa-brain me-1"></i>Ver pasos técnicos (${pasos.length} pasos)
                    </button>
                    <div class="collapse mt-2" id="pensamiento-${uniqueId}">
                        <div class="card card-body bg-light">
                            <h6 class="mb-3"><i class="fas fa-cogs me-1"></i>Pasos técnicos ejecutados:</h6>
                            ${pasos.map((paso, index) => `
                                <div class="paso-pensamiento mb-2 p-2 border-start border-3 border-success">
                                    <strong>Paso ${index + 1}:</strong> ${paso}
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Agregar metadata de tiempo y rendimiento
        let metadataInfo = '';
        if (metadata) {
            metadataInfo = `
                <div class="metadata-info mt-2 p-2 bg-light rounded">
                    <div class="row text-muted small">
                        <div class="col-md-4">
                            <i class="fas fa-clock me-1"></i>
                            Iniciado: ${formatearTiempo(metadata.tiempoInicio)}
                        </div>
                        <div class="col-md-4">
                            <i class="fas fa-flag-checkered me-1"></i>
                            Completado: ${formatearTiempo(metadata.tiempoFin)}
                        </div>
                        <div class="col-md-4">
                            <i class="fas fa-stopwatch me-1"></i>
                            Duración: ${metadata.duracion}s
                        </div>
                    </div>
                    ${metadata.iteraciones !== undefined ? `
                        <div class="mt-1 small text-muted">
                            <i class="fas fa-layer-group me-1"></i>
                            Iteraciones: ${metadata.iteraciones} | 
                            <i class="fas fa-search me-1"></i>
                            Búsquedas: ${metadata.busquedas || 0}
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        mensajeDiv.innerHTML = `
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <i class="${modoIcon} me-2"></i>
                    ${texto}
                    ${procesoCompleto}
                    ${metadataInfo}
                </div>
                <small class="text-muted ms-2">${formatearTiempo(timestamp)}</small>
            </div>
            <div class="badges-container mt-2">
                ${modoBadge}
                ${modeloBadge}
            </div>
        `;
    }
    
    chatBody.appendChild(mensajeDiv);
    chatBody.scrollTop = chatBody.scrollHeight;
}

// Formatear tiempo en formato legible
function formatearTiempo(fecha) {
    return fecha.toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
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
            const tiempoInicio = new Date();
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
            const tiempoFin = new Date();
            const duracion = ((tiempoFin - tiempoInicio) / 1000).toFixed(1);
            
            updateLoadingProgress(90, 'Formateando respuesta...');
            
            // Extraer pasos intermedios si están disponibles
            let pasos = null;
            if (data.pasos_intermedios && data.pasos_intermedios.length > 0) {
                pasos = data.pasos_intermedios.map(paso => {
                    if (paso.action && paso.action_input) {
                        return `🔍 Ejecutó búsqueda: "${paso.action_input}"`;
                    } else if (paso.observation) {
                        return `📊 Obtuvo resultado: ${paso.observation.substring(0, 150)}...`;
                    }
                    return paso.toString().substring(0, 80) + '...';
                });
            }
            
            // Crear metadata para demo
            const metadata = {
                tiempoInicio: tiempoInicio,
                tiempoFin: tiempoFin,
                duracion: duracion,
                iteraciones: data.pasos_intermedios ? data.pasos_intermedios.length : 0,
                busquedas: data.pasos_intermedios ? data.pasos_intermedios.filter(p => p.action === 'web_search' || p.action === 'duckduckgo_search').length : 0
            };
            
            updateLoadingProgress(100, 'Demo completado!');
            agregarMensaje(data.pregunta, 'usuario');
            agregarMensaje(data.respuesta, 'ia', data.modo, data.modelo_usado, pasos, metadata);
            
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


