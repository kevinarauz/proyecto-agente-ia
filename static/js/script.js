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

// Estado global para razonamiento en tiempo real
let currentThinkingSteps = [];
let currentThinkingContainer = null;
let agentExecutionTimer = null;
let agentStartTime = null;

// Función para mostrar razonamiento en tiempo real con información del AgentExecutor
function mostrarRazonamientoTiempoReal(modeloSeleccionado, pregunta) {
    if (!modeloSeleccionado) return;
    
    // Crear contenedor temporal para el razonamiento
    const chatBody = document.getElementById('chatBody');
    const tempContainer = document.createElement('div');
    tempContainer.className = 'message ia-message mb-3';
    tempContainer.innerHTML = `
        <div class="thinking-real-time bg-info bg-opacity-10 border border-info rounded p-3">
            <div class="d-flex justify-content-between align-items-center mb-2">
                <h6 class="mb-0"><i class="fas fa-brain me-1"></i>Razonamiento en tiempo real - AgentExecutor</h6>
                <button class="btn btn-sm btn-outline-info" onclick="toggleRazonamiento()" title="Ocultar/Mostrar razonamiento">
                    <i class="fas fa-eye"></i>
                </button>
            </div>
            <div id="thinking-steps"></div>
            <div class="thinking-indicator">
                <div class="spinner-border spinner-border-sm text-info me-2" role="status"></div>
                <small class="text-muted">Procesando...</small>
            </div>
        </div>
    `;
    
    chatBody.appendChild(tempContainer);
    chatBody.scrollTop = chatBody.scrollHeight;
    currentThinkingContainer = tempContainer;
    agentStartTime = new Date();
    razonamientoOculto = false; // Reset del estado
    
    // Agregar primera fase del agente
    setTimeout(() => {
        agregarPasoRazonamientoTiempoReal("� Iniciando sistema de agentes de IA", "inicio");
    }, 200);
    
    setTimeout(() => {
        agregarPasoRazonamientoTiempoReal("⚡ > Entering new AgentExecutor chain...", "agente");
    }, 500);
    
    setTimeout(() => {
        agregarPasoRazonamientoTiempoReal(`🔍 Analizando consulta: "${pregunta}"`, "analisis");
    }, 800);
    
    // Detección de tipo de consulta
    const esConsultaNoticias = pregunta.toLowerCase().includes('noticias') || pregunta.toLowerCase().includes('hoy') || pregunta.toLowerCase().includes('actualidad');
    const internetHabilitado = document.getElementById('permitirInternet').checked;
    
    if (esConsultaNoticias && internetHabilitado) {
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("📰 Detectada consulta de información actual", "deteccion");
        }, 1200);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("🤖 I'll do my best to help!", "agente");
        }, 1600);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("💭 Thought: User is asking for today's news...", "pensamiento");
        }, 2000);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("🔧 Action: web_search", "accion");
        }, 2500);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("� Action Input: \"noticias de hoy\"", "input");
        }, 3000);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("🌐 🔍 Búsqueda web avanzada: noticias de hoy", "busqueda");
        }, 3500);
        
        // Simular progreso de búsqueda más realista para 30 minutos
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("⏳ Procesando múltiples fuentes... (puede tomar hasta 30 minutos)", "info");
        }, 4000);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("✅ DuckDuckGo: Resultados obtenidos", "resultado");
        }, 5000);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("📊 Procesando múltiples fuentes de noticias...", "procesamiento");
        }, 6000);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("🔄 Analizando y sintetizando información encontrada...", "analisis");
        }, 8000);
        
        // Agregar indicadores de progreso cada 30 segundos para consultas largas (30 minutos)
        if (esConsultaNoticias && internetHabilitado) {
            const intervalos = [15, 30, 60, 120, 180, 300, 450, 600, 900, 1200, 1500, 1800]; // Hasta 30 minutos
            intervalos.forEach((segundos, index) => {
                setTimeout(() => {
                    const minutos = Math.floor(segundos / 60);
                    const segsRestantes = segundos % 60;
                    const tiempoFormato = minutos > 0 ? `${minutos}m ${segsRestantes}s` : `${segundos}s`;
                    
                    if (segundos <= 300) { // Primeros 5 minutos
                        agregarPasoRazonamientoTiempoReal(`⏱️ Progreso: ${tiempoFormato} - Búsqueda profunda en curso...`, "progreso");
                    } else if (segundos <= 900) { // 5-15 minutos
                        agregarPasoRazonamientoTiempoReal(`🔍 Progreso: ${tiempoFormato} - Analizando múltiples fuentes...`, "progreso");
                    } else { // 15-30 minutos
                        agregarPasoRazonamientoTiempoReal(`🧠 Progreso: ${tiempoFormato} - Procesamiento avanzado...`, "progreso");
                    }
                }, segundos * 1000);
            });
        }
        
    } else if (internetHabilitado) {
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("🤖 Evaluando si requiere búsqueda web", "evaluacion");
        }, 1200);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("💭 Thought: Analyzing query for web search necessity", "pensamiento");
        }, 1800);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("🧠 Preparando respuesta usando conocimiento base", "preparacion");
        }, 2500);
    } else {
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("� Modo offline: Consultando base de conocimientos", "offline");
        }, 1200);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal(`🤖 Procesando con ${modeloSeleccionado}`, "modelo");
        }, 1800);
    }
}

// Función mejorada para agregar pasos de razonamiento con tipos
function agregarPasoRazonamientoTiempoReal(paso, tipo = "general") {
    if (!currentThinkingContainer) return;
    
    const tiempoActual = new Date();
    const tiempoTranscurrido = agentStartTime ? ((tiempoActual - agentStartTime) / 1000).toFixed(1) : 0;
    
    const stepsContainer = currentThinkingContainer.querySelector('#thinking-steps');
    const stepElement = document.createElement('div');
    
    // Diferentes estilos según el tipo
    let claseCSS = 'thinking-step mb-1 p-2 border-start border-3 bg-white rounded-end';
    let iconoTipo = '';
    
    switch(tipo) {
        case 'inicio':
            claseCSS += ' border-primary';
            iconoTipo = '🚀';
            break;
        case 'agente':
            claseCSS += ' border-success';
            iconoTipo = '⚡';
            break;
        case 'pensamiento':
            claseCSS += ' border-warning';
            iconoTipo = '💭';
            break;
        case 'accion':
            claseCSS += ' border-danger';
            iconoTipo = '🔧';
            break;
        case 'busqueda':
            claseCSS += ' border-info';
            iconoTipo = '🌐';
            break;
        case 'resultado':
            claseCSS += ' border-success';
            iconoTipo = '✅';
            break;
        case 'fin':
            claseCSS += ' border-dark';
            iconoTipo = '🏁';
            break;
        case 'error':
            claseCSS += ' border-danger';
            iconoTipo = '❌';
            break;
        case 'progreso':
            claseCSS += ' border-warning';
            iconoTipo = '⏱️';
            break;
        case 'info':
            claseCSS += ' border-secondary';
            iconoTipo = '💡';
            break;
        case 'think':
            claseCSS += ' border-purple';
            iconoTipo = '💭';
            break;
        case 'razonamiento':
            claseCSS += ' border-primary';
            iconoTipo = '🧠';
            break;
        default:
            claseCSS += ' border-info';
            iconoTipo = '📋';
    }
    
    stepElement.className = claseCSS;
    
    // Formateo especial para contenido <think>
    let contenidoFormateado = paso;
    if (tipo === 'think' || paso.includes('<think>')) {
        // Resaltar contenido de pensamiento interno
        contenidoFormateado = `<div class="think-content p-2 bg-light rounded mt-1">
            <small class="text-muted"><i class="fas fa-brain"></i> Razonamiento interno DeepSeek R1:</small>
            <div class="mt-1" style="font-style: italic; color: #6c757d;">${paso}</div>
        </div>`;
    } else if (paso.includes('Thought:')) {
        // Formatear pensamientos del agente
        contenidoFormateado = `<div class="thought-content">
            <span style="color: #28a745; font-weight: bold;">💭 ${paso}</span>
        </div>`;
    } else if (paso.includes('Action Input:')) {
        // Formatear inputs de acciones
        contenidoFormateado = `<div class="action-input-content">
            <span style="color: #dc3545; font-weight: bold;">📝 ${paso}</span>
        </div>`;
    }
    
    stepElement.innerHTML = `
        <div class="d-flex justify-content-between align-items-start">
            <div class="flex-grow-1">
                <small class="text-muted">[+${tiempoTranscurrido}s]</small><br>
                <div style="font-family: 'Courier New', monospace; font-size: 0.9em;">${contenidoFormateado}</div>
            </div>
            <small class="text-muted ms-2">${iconoTipo}</small>
        </div>
    `;
    
    stepsContainer.appendChild(stepElement);
    currentThinkingContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

// Función para finalizar razonamiento en tiempo real con mensaje del agente
function finalizarRazonamientoTiempoReal() {
    if (currentThinkingContainer) {
        // Agregar mensajes finales del agente
        const tiempoTotal = agentStartTime ? ((new Date() - agentStartTime) / 1000).toFixed(1) : 0;
        
        // Agregar paso final del agente
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal("🏁 > Finished chain.", "fin");
        }, 100);
        
        setTimeout(() => {
            agregarPasoRazonamientoTiempoReal(`✅ Agente completado en ${tiempoTotal}s`, "exito");
        }, 300);
        
        setTimeout(() => {
            const indicator = currentThinkingContainer.querySelector('.thinking-indicator');
            if (indicator) {
                indicator.innerHTML = `
                    <small class="text-muted"><i class="fas fa-check-circle text-success me-1"></i>AgentExecutor chain completado (${tiempoTotal}s)</small>
                `;
            }
            
            // Cambiar el título para indicar que el proceso terminó
            const titleElement = currentThinkingContainer.querySelector('h6');
            if (titleElement) {
                titleElement.innerHTML = `<i class="fas fa-brain me-1"></i>AgentExecutor chain completado (${tiempoTotal}s)`;
            }
            
            // Agregar borde de finalización
            const thinkingDiv = currentThinkingContainer.querySelector('.thinking-real-time');
            if (thinkingDiv) {
                thinkingDiv.classList.remove('bg-info', 'border-info');
                thinkingDiv.classList.add('bg-success', 'bg-opacity-10', 'border-success');
            }
        }, 500);
        
        // Solo limpiar las variables de control, mantener visible
        currentThinkingSteps = [];
        agentExecutionTimer = null;
        // currentThinkingContainer = null; // Mantener visible para el usuario
    }
}

// Variable global para estado de razonamiento
let razonamientoOculto = false;
let contenedorRazonamientoOriginal = null;

// Nueva función para ocultar/mostrar el razonamiento manualmente
function toggleRazonamiento() {
    if (!currentThinkingContainer) return;
    
    // Encontrar el botón para actualizar el icono
    const toggleButton = currentThinkingContainer.querySelector('button');
    const thinkingContent = currentThinkingContainer.querySelector('#thinking-steps');
    const thinkingIndicator = currentThinkingContainer.querySelector('.thinking-indicator');
    
    if (razonamientoOculto) {
        // Mostrar razonamiento
        if (thinkingContent) thinkingContent.style.display = 'block';
        if (thinkingIndicator) thinkingIndicator.style.display = 'block';
        razonamientoOculto = false;
        
        // Actualizar icono del botón
        if (toggleButton) {
            toggleButton.innerHTML = '<i class="fas fa-eye"></i>';
            toggleButton.title = 'Ocultar razonamiento';
        }
        
        // Restaurar pensamientos si los tenemos guardados
        if (pensamientosDefinitivos.length > 0 && thinkingContent && thinkingContent.children.length === 0) {
            pensamientosDefinitivos.forEach((pensamiento, index) => {
                const stepElement = document.createElement('div');
                stepElement.className = 'thinking-step mb-1 p-2 border-start border-3 border-success bg-white rounded-end';
                stepElement.innerHTML = `
                    <small class="text-muted">Paso ${index + 1}</small><br>
                    <strong>${pensamiento}</strong>
                `;
                thinkingContent.appendChild(stepElement);
            });
        }
        
        // Scroll al final
        currentThinkingContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
    } else {
        // Ocultar razonamiento
        if (thinkingContent) thinkingContent.style.display = 'none';
        if (thinkingIndicator) thinkingIndicator.style.display = 'none';
        razonamientoOculto = true;
        
        // Actualizar icono del botón
        if (toggleButton) {
            toggleButton.innerHTML = '<i class="fas fa-eye-slash"></i>';
            toggleButton.title = 'Mostrar razonamiento';
        }
    }
}

// Nueva función para ocultar el razonamiento manualmente (legacy)
function ocultarRazonamiento() {
    if (currentThinkingContainer && currentThinkingContainer.parentNode && !razonamientoOculto) {
        toggleRazonamiento();
    }
}

// Función auxiliar para formatear tiempo
function formatearTiempo(timestamp) {
    if (!timestamp) return 'N/A';
    
    // Si es un timestamp de JavaScript (milisegundos)
    if (typeof timestamp === 'number' && timestamp > 1000000000000) {
        return new Date(timestamp).toLocaleTimeString();
    }
    // Si es un objeto Date
    else if (timestamp instanceof Date) {
        return timestamp.toLocaleTimeString();
    }
    // Si es un string
    else if (typeof timestamp === 'string') {
        return new Date(timestamp).toLocaleTimeString();
    }
    
    return 'N/A';
}

// Variable global para almacenar los pensamientos definitivos
let pensamientosDefinitivos = [];

// Función para mostrar el proceso de razonamiento real del agente
function mostrarProcesoRazonamientoReal(pensamientos, modelo) {
    if (!pensamientos || pensamientos.length === 0) return;
    
    // Guardar los pensamientos definitivos
    pensamientosDefinitivos = [...pensamientos];
    
    // Actualizar el contenedor existente con los pensamientos reales
    if (currentThinkingContainer) {
        const stepsContainer = currentThinkingContainer.querySelector('#thinking-steps');
        if (stepsContainer) {
            // NO limpiar los pasos simulados, solo agregar los reales o reemplazar si es necesario
            const pasosExistentes = stepsContainer.querySelectorAll('.thinking-step').length;
            
            // Si ya hay pasos y son menos que los pensamientos reales, reemplazar todo
            if (pasosExistentes > 0 && pasosExistentes !== pensamientos.length) {
                stepsContainer.innerHTML = '';
            }
            
            // Agregar pensamientos reales solo si el contenedor está vacío o necesita actualización
            if (stepsContainer.children.length === 0) {
                pensamientos.forEach((pensamiento, index) => {
                    const stepElement = document.createElement('div');
                    stepElement.className = 'thinking-step mb-1 p-2 border-start border-3 border-success bg-white rounded-end';
                    stepElement.innerHTML = `
                        <small class="text-muted">Paso ${index + 1}</small><br>
                        <strong>${pensamiento}</strong>
                    `;
                    stepsContainer.appendChild(stepElement);
                });
            }
            
            // Actualizar el título
            const titleElement = currentThinkingContainer.querySelector('h6');
            if (titleElement) {
                const esDeepSeek = modelo === 'deepseek-r1:8b';
                titleElement.innerHTML = `<i class="fas fa-brain me-1"></i>${esDeepSeek ? 'Razonamiento DeepSeek R1' : 'Proceso de razonamiento del agente'}`;
            }
            
            // Remover el indicador de "Procesando..." 
            const thinkingIndicator = currentThinkingContainer.querySelector('.thinking-indicator');
            if (thinkingIndicator) {
                thinkingIndicator.style.display = 'none';
            }
            
            // Scroll al final
            currentThinkingContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    loadingModal = new bootstrap.Modal(document.getElementById('loadingModal'));
    chatBody = document.getElementById('chatBody');
    preguntaInput = document.getElementById('preguntaInput');
    enviarBtn = document.getElementById('enviarBtn');
    
    // Event listeners
    document.getElementById('chatForm').addEventListener('submit', handleSubmit);
    document.getElementById('modeloSelect').addEventListener('change', actualizarMensajeBienvenida);
    document.getElementById('permitirInternet').addEventListener('change', manejarCambioInternet);
    document.getElementById('modoSelect').addEventListener('change', validarModoInternet);
    preguntaInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    });
    
    // Validación en tiempo real del input
    preguntaInput.addEventListener('input', validarInput);
    validarInput(); // Validación inicial
    
    // Actualizar mensaje inicial
    actualizarMensajeBienvenida();
    validarModoInternet();
    
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
        if (preguntaInput) {
            preguntaInput.focus();
        }
    }, 1000);
});

// Función para actualizar el mensaje de bienvenida según el modelo seleccionado
function actualizarMensajeBienvenida() {
    const modeloSelect = document.getElementById('modeloSelect');
    const textoBienvenida = document.getElementById('textoBienvenida');
    
    if (!modeloSelect || !textoBienvenida) return;
    
    const modeloSeleccionado = modeloSelect.value;
    const modeloTexto = modeloSelect.options[modeloSelect.selectedIndex].text;
    
    let mensaje = '';
    
    switch(modeloSeleccionado) {
        case 'llama3':
            mensaje = '¡Hola! Soy tu asistente de IA con Llama3 8B. Excelente para conversaciones generales y tareas diversas.';
            break;
        case 'deepseek-coder':
            mensaje = '¡Hola! Soy tu asistente de IA con DeepSeek Coder. Especializado en programación, código y desarrollo.';
            break;
        case 'deepseek-r1:8b':
            mensaje = '¡Hola! Soy tu asistente de IA con DeepSeek R1 8B. Modelo de razonamiento avanzado para análisis profundo.';
            break;
        case 'phi3':
            mensaje = '¡Hola! Soy tu asistente de IA con Microsoft Phi-3. Modelo compacto y eficiente para respuestas rápidas.';
            break;
        case 'gemma:2b':
            mensaje = '¡Hola! Soy tu asistente de IA con Google Gemma 2B. Modelo ligero y rápido para consultas directas.';
            break;
        case 'gemini-1.5-flash':
            mensaje = '¡Hola! Soy tu asistente de IA con Google Gemini 1.5 Flash. Capacidades avanzadas para tareas complejas.';
            break;
        default:
            mensaje = `¡Hola! Soy tu asistente de IA con ${modeloTexto}. Puedo responder preguntas y ayudarte con diversas tareas.`;
    }
    
    mensaje += ' Puedo responder preguntas básicas';
    
    // Agregar información sobre búsqueda web según la configuración
    const permitirInternet = document.getElementById('permitirInternet');
    if (permitirInternet && permitirInternet.checked) {
        mensaje += ' o usar búsqueda web para información actual.';
    } else {
        mensaje += ' usando mi conocimiento base (búsqueda web deshabilitada).';
    }
    
    textoBienvenida.textContent = mensaje;
}

// Función para manejar cambio en el toggle de internet
function manejarCambioInternet() {
    const permitirInternet = document.getElementById('permitirInternet');
    const labelInternet = document.getElementById('labelInternet');
    const estadoWeb = document.getElementById('estadoWeb');
    const estadoWebTexto = document.getElementById('estadoWebTexto');
    const modoSelect = document.getElementById('modoSelect');
    
    if (permitirInternet.checked) {
        labelInternet.innerHTML = '<i class="fas fa-wifi me-1"></i>Permitir búsqueda web';
        labelInternet.className = 'form-check-label text-success';
        
        if (estadoWeb) {
            estadoWeb.className = 'alert alert-success py-1 px-2 mb-0';
            estadoWeb.style.fontSize = '0.8em';
        }
        if (estadoWebTexto) {
            estadoWebTexto.innerHTML = '<i class="fas fa-globe me-1"></i>Web habilitada - Puede buscar información actual';
        }
    } else {
        labelInternet.innerHTML = '<i class="fas fa-wifi-slash me-1"></i>Solo conocimiento base';
        labelInternet.className = 'form-check-label text-warning';
        
        if (estadoWeb) {
            estadoWeb.className = 'alert alert-warning py-1 px-2 mb-0';
            estadoWeb.style.fontSize = '0.8em';
        }
        if (estadoWebTexto) {
            estadoWebTexto.innerHTML = '<i class="fas fa-database me-1"></i>Solo base de datos - Sin acceso a internet';
        }
        
        // Si está deshabilitado internet, forzar modo simple
        if (modoSelect.value !== 'simple') {
            modoSelect.value = 'simple';
            Swal.fire({
                icon: 'info',
                title: 'Modo Cambiado',
                text: 'Al deshabilitar internet, se cambió automáticamente a Chat Simple.',
                timer: 2000,
                showConfirmButton: false
            });
        }
    }
    
    validarModoInternet();
    actualizarMensajeBienvenida(); // Actualizar mensaje cuando cambie la configuración
}

// Función para validar que el modo sea compatible con la configuración de internet
function validarModoInternet() {
    const permitirInternet = document.getElementById('permitirInternet');
    const modoSelect = document.getElementById('modoSelect');
    
    // Deshabilitar opciones que requieren internet si está deshabilitado
    const opciones = modoSelect.options;
    for (let i = 0; i < opciones.length; i++) {
        const opcion = opciones[i];
        if (opcion.value !== 'simple') {
            opcion.disabled = !permitirInternet.checked;
            if (!permitirInternet.checked) {
                opcion.style.color = '#6c757d';
                if (opcion.value === 'agente') {
                    opcion.text = '🔍 Agente con Búsqueda Web (Deshabilitado)';
                } else if (opcion.value === 'busqueda_rapida') {
                    opcion.text = '⚡ Búsqueda Rápida (Deshabilitado)';
                }
            } else {
                opcion.style.color = '';
                if (opcion.value === 'agente') {
                    opcion.text = '🔍 Agente con Búsqueda Web';
                } else if (opcion.value === 'busqueda_rapida') {
                    opcion.text = '⚡ Búsqueda Rápida';
                }
            }
        }
    }
}

// Manejar envío del formulario
async function handleSubmit(e) {
    e.preventDefault();
    
    const pregunta = preguntaInput.value.trim();
    if (!pregunta) return;
    
    const modo = document.getElementById('modoSelect').value;
    const modelo = document.getElementById('modeloSelect').value;
    const permitirInternet = document.getElementById('permitirInternet').checked;
    
    // Verificar si el modo requiere internet pero está deshabilitado
    if (!permitirInternet && (modo === 'agente' || modo === 'busqueda_rapida')) {
        Swal.fire({
            icon: 'warning',
            title: 'Búsqueda web deshabilitada',
            text: 'Has deshabilitado la búsqueda web. Se usará Chat Simple para esta consulta.',
            confirmButtonColor: '#007bff'
        });
        document.getElementById('modoSelect').value = 'simple';
        return;
    }
    
    // Capturar tiempo de inicio
    const tiempoInicio = new Date();
    
    // Agregar mensaje del usuario al chat
    agregarMensaje(pregunta, 'usuario');
    
    // Mostrar razonamiento en tiempo real específico para agentes
    const esAgente = (modo === 'agente' || (!permitirInternet && (modo === 'agente' || modo === 'busqueda_rapida')));
    if (esAgente || permitirInternet) {
        mostrarRazonamientoTiempoReal(modelo, pregunta);
    }
    
    // Limpiar input y deshabilitar botón
    preguntaInput.value = '';
    setLoading(true);
    
    try {
        updateLoadingProgress(80, 'Procesando resultados...');
        const respuesta = await enviarPreguntaAPI(pregunta, modo, modelo, permitirInternet);
        
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
            busquedas: respuesta.metadata?.busquedas || 0,
            internetHabilitado: permitirInternet
        };
        
        updateLoadingProgress(100, 'Completado!');
        
        // Finalizar razonamiento en tiempo real
        finalizarRazonamientoTiempoReal();
        
        // Mostrar el proceso de razonamiento real del agente
        if (pensamientos && pensamientos.length > 0) {
            mostrarProcesoRazonamientoReal(pensamientos, respuesta.modelo_usado);
        }
        
        agregarMensaje(respuesta.respuesta, 'ia', respuesta.modo, respuesta.modelo_usado, pasos, metadata, pensamientos);
    } catch (error) {
        console.error('Error:', error);
        
        // Finalizar razonamiento en tiempo real en caso de error
        finalizarRazonamientoTiempoReal();
        
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
async function enviarPreguntaAPI(pregunta, modo, modelo, permitirInternet = true) {
    let endpoint = '/chat';
    
    // Detección inteligente de tipo de consulta
    const preguntaLower = pregunta.toLowerCase();
    
    // Consultas de clima -> usar endpoint optimizado
    if ((preguntaLower.includes('clima') || preguntaLower.includes('weather') || 
         preguntaLower.includes('temperatura') || preguntaLower.includes('temp')) && 
        permitirInternet) {
        endpoint = '/clima-actual';
        console.log('🌤️ Detectada consulta de clima, usando endpoint optimizado');
    }
    // Búsquedas rápidas
    else if (modo === 'busqueda_rapida') {
        endpoint = '/busqueda-rapida';
    }
    
    // Forzar modo simple si internet está deshabilitado
    if (!permitirInternet && modo !== 'simple') {
        modo = 'simple';
    }
    
    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            pregunta: pregunta,
            modo: modo,
            modelo: modelo,
            permitir_internet: permitirInternet
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
        
        // Función para obtener el badge del modelo con icono correcto
        function getModeloBadge(modelo) {
            if (!modelo) return '';
            
            switch(modelo) {
                case 'llama3':
                    return '<span class="modelo-badge">🦙 Llama3</span>';
                case 'deepseek-coder':
                    return '<span class="modelo-badge">💻 DeepSeek</span>';
                case 'deepseek-r1:8b':
                    return '<span class="modelo-badge">🧮 DeepSeek R1</span>';
                case 'phi3':
                    return '<span class="modelo-badge">🔬 Phi-3</span>';
                case 'gemma:2b':
                    return '<span class="modelo-badge">💎 Gemma</span>';
                case 'gemini-1.5-flash':
                    return '<span class="modelo-badge">🧠 Gemini</span>';
                default:
                    return `<span class="modelo-badge">🤖 ${modelo}</span>`;
            }
        }
        
        const modeloBadge = getModeloBadge(modeloUsado);
        
        // Badge para indicar si se usó internet - MEJORADO
        let internetBadge = '';
        if (metadata && metadata.hasOwnProperty('internetHabilitado')) {
            if (metadata.internetHabilitado) {
                if (metadata.busquedas > 0) {
                    internetBadge = '<span class="modo-badge" style="background-color: #28a745; color: white;">🌐 Web Usada</span>';
                } else if (modo === 'agente' || modo === 'busqueda_rapida') {
                    internetBadge = '<span class="modo-badge" style="background-color: #17a2b8; color: white;">🌐 Web Disponible</span>';
                } else {
                    internetBadge = '<span class="modo-badge" style="background-color: #6c757d; color: white;">🌐 Web Disponible</span>';
                }
            } else {
                internetBadge = '<span class="modo-badge" style="background-color: #ffc107; color: #212529;">📚 Solo Base de Datos</span>';
            }
        }
        
        // Agregar proceso de pensamiento detallado si está disponible
        let procesoCompleto = '';
        if (pensamientos && pensamientos.length > 0) {
            // Verificar si es DeepSeek R1 para mostrar razonamiento especial
            const esDeepSeekR1 = modeloUsado === 'deepseek-r1:8b';
            const tipoRazonamiento = esDeepSeekR1 ? 'razonamiento avanzado' : 'proceso de pensamiento completo';
            const icono = esDeepSeekR1 ? 'fas fa-brain' : 'fas fa-cogs';
            const colorBorde = esDeepSeekR1 ? 'border-info' : 'border-primary';
            
            procesoCompleto = `
                <div class="proceso-pensamiento mt-3">
                    <button class="btn btn-sm btn-outline-${esDeepSeekR1 ? 'info' : 'primary'}" type="button" data-bs-toggle="collapse" data-bs-target="#pensamiento-${uniqueId}" aria-expanded="false">
                        <i class="${icono} me-1"></i>Ver ${tipoRazonamiento} (${pensamientos.length} pasos)
                    </button>
                    <div class="collapse mt-2" id="pensamiento-${uniqueId}">
                        <div class="card card-body ${esDeepSeekR1 ? 'bg-info bg-opacity-10' : 'bg-light'}">
                            <h6 class="mb-3"><i class="${icono} me-1"></i>${esDeepSeekR1 ? 'Razonamiento DeepSeek R1:' : 'Proceso de razonamiento del agente:'}</h6>
                            ${pensamientos.map((pensamiento, index) => `
                                <div class="paso-pensamiento mb-2 p-2 border-start border-3 ${colorBorde}">
                                    <small class="text-muted">Paso ${index + 1}</small><br>
                                    <strong>${pensamiento}</strong>
                                </div>
                            `).join('')}
                            ${esDeepSeekR1 ? '<small class="text-muted mt-2"><i class="fas fa-info-circle me-1"></i>Este es el proceso de razonamiento paso a paso del modelo DeepSeek R1</small>' : 
                              '<small class="text-muted mt-2"><i class="fas fa-info-circle me-1"></i>Este proceso muestra cómo el agente analizó tu consulta paso a paso</small>'}
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
            const duracionTexto = metadata.duracion_formateada || `${metadata.duracion}s`;
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
                            Duración: ${duracionTexto}
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
                    ${metadata.tipo_consulta ? `
                        <div class="mt-1 small text-muted">
                            <i class="fas fa-tag me-1"></i>
                            Tipo: ${metadata.tipo_consulta}
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
                ${internetBadge}
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
        
        // Determinar el modo actual para mostrar mensajes apropiados
        const modoSelect = document.getElementById('modoSelect');
        const modeloSelect = document.getElementById('modeloSelect');
        const permitirInternet = document.getElementById('permitirInternet');
        const modo = modoSelect ? modoSelect.value : 'simple';
        const modelo = modeloSelect ? modeloSelect.value : '';
        const internetHabilitado = permitirInternet ? permitirInternet.checked : false;
        
        // Reiniciar elementos del modal
        document.getElementById('loadingTitle').textContent = 'Procesando tu pregunta...';
        
        // Ajustar descripción según el modo y modelo
        if (modelo === 'deepseek-r1:8b') {
            document.getElementById('loadingDescription').textContent = 'DeepSeek R1 está razonando paso a paso...';
        } else if (modo === 'agente' && internetHabilitado) {
            document.getElementById('loadingDescription').textContent = 'El agente está trabajando con búsqueda web...';
        } else if (modo === 'busqueda_rapida' && internetHabilitado) {
            document.getElementById('loadingDescription').textContent = 'Realizando búsqueda rápida en web...';
        } else {
            document.getElementById('loadingDescription').textContent = 'Procesando con conocimiento base...';
        }
        
        document.getElementById('loadingProgress').style.width = '0%';
        document.getElementById('timerValue').textContent = '0';
        document.getElementById('loadingSteps').style.display = 'none';
        
        // Iniciar timer
        startTime = Date.now();
        loadingTimer = setInterval(updateTimer, 100);
        
        loadingModal.show();
        
        // Simular progreso para mejor UX con mensajes específicos
        if (modelo === 'deepseek-r1:8b') {
            // Proceso de razonamiento simulado para DeepSeek R1
            setTimeout(() => updateLoadingProgress(15, '🔍 Analizando pregunta inicial...'), 500);
            setTimeout(() => updateLoadingProgress(30, '🧠 Identificando conceptos clave...'), 1200);
            setTimeout(() => updateLoadingProgress(45, '📚 Accediendo a conocimiento base...'), 2000);
            setTimeout(() => updateLoadingProgress(60, '🔗 Conectando información relevante...'), 3000);
            setTimeout(() => updateLoadingProgress(75, '📝 Estructurando respuesta...'), 4000);
            setTimeout(() => updateLoadingProgress(90, '🔄 Validando coherencia...'), 5000);
        } else if (modo === 'agente' && internetHabilitado) {
            setTimeout(() => updateLoadingProgress(20, 'Conectando con el agente...'), 500);
            setTimeout(() => updateLoadingProgress(40, 'Analizando la pregunta...'), 1000);
            setTimeout(() => updateLoadingProgress(60, 'Ejecutando búsqueda web...'), 2000);
        } else if (modo === 'busqueda_rapida' && internetHabilitado) {
            setTimeout(() => updateLoadingProgress(30, 'Preparando búsqueda rápida...'), 500);
            setTimeout(() => updateLoadingProgress(60, 'Consultando fuentes web...'), 1000);
            setTimeout(() => updateLoadingProgress(80, 'Procesando resultados...'), 1500);
        } else {
            setTimeout(() => updateLoadingProgress(20, 'Conectando con el modelo...'), 500);
            setTimeout(() => updateLoadingProgress(40, 'Analizando la pregunta...'), 1000);
            setTimeout(() => updateLoadingProgress(60, 'Procesando respuesta...'), 2000);
        }
        
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

// Efectos adicionales ya están consolidados en el DOMContentLoaded principal

// Prevenir envío de formulario vacío
function validarInput() {
    const pregunta = preguntaInput.value.trim();
    enviarBtn.disabled = !pregunta || preguntaInput.disabled;
}

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

// Función para consulta rápida de clima
async function consultarClimaRapido() {
    try {
        setLoading(true);
        
        Swal.fire({
            title: 'Consultando clima...',
            text: 'Obteniendo información meteorológica de Quito',
            icon: 'info',
            allowOutsideClick: false,
            showConfirmButton: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        const response = await fetch('/clima-actual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pregunta: '¿Cuál es el clima actual en Quito?',
                modelo: document.getElementById('modeloSelect').value
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }

        Swal.close();
        
        // Agregar pregunta y respuesta al chat
        agregarMensaje('¿Cuál es el clima actual en Quito?', 'usuario');
        agregarMensaje(data.respuesta, 'ia', data.modo, data.modelo_usado, [], data.metadata, data.pensamientos || []);

        // Mostrar notificación de éxito
        Swal.fire({
            icon: 'success',
            title: '🌤️ Clima Consultado',
            text: 'Información meteorológica obtenida exitosamente.',
            confirmButtonColor: '#007bff',
            timer: 2000
        });

    } catch (error) {
        console.error('Error:', error);
        Swal.close();
        Swal.fire({
            icon: 'error',
            title: 'Error al consultar clima',
            text: 'No se pudo obtener la información meteorológica.',
            confirmButtonColor: '#007bff'
        });
    } finally {
        setLoading(false);
    }
}

// ========================
// CONTROL DE MODELOS
// ========================

async function refreshModelsStatus() {
    const container = document.getElementById('modelsStatusContainer');
    container.innerHTML = `
        <div class="col-12 text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Verificando estado de modelos...</span>
            </div>
            <p class="mt-2 text-muted">Actualizando estado de modelos...</p>
        </div>
    `;

    try {
        // Obtener estado general y modelos en ejecución de Ollama
        const [statusResponse, runningResponse] = await Promise.all([
            fetch('/api/models/status'),
            fetch('/api/models/ollama/running')
        ]);
        
        const statusData = await statusResponse.json();
        const runningData = await runningResponse.json();
        
        if (statusResponse.ok) {
            displayModelsStatus(statusData, runningData);
        } else {
            throw new Error(statusData.error || 'Error al obtener estado de modelos');
        }
    } catch (error) {
        console.error('Error:', error);
        container.innerHTML = `
            <div class="col-12 text-center">
                <div class="alert alert-danger" role="alert">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Error al verificar estado de modelos: ${error.message}
                </div>
            </div>
        `;
    }
}

function displayModelsStatus(data, runningData) {
    const container = document.getElementById('modelsStatusContainer');
    
    let html = '';
    
    // Ollama Status con control individual
    html += `
        <div class="col-lg-6 mb-3">
            <div class="card h-100">
                <div class="card-header ${data.ollama.available ? 'bg-success' : 'bg-danger'} text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-cube me-2"></i>
                        Ollama
                        <span class="badge ${data.ollama.available ? 'bg-light text-success' : 'bg-light text-danger'} ms-2">
                            ${data.ollama.available ? 'Online' : 'Offline'}
                        </span>
                        ${runningData.ollama_available && runningData.running_count > 0 ? 
                            `<span class="badge bg-warning text-dark ms-1">${runningData.running_count} ejecutándose</span>` : ''}
                    </h6>
                </div>
                <div class="card-body p-3">
                    ${data.ollama.available ? `
                        <div class="mb-2">
                            <small class="text-muted">Control Individual de Modelos:</small>
                        </div>
                        <div class="models-list" style="max-height: 200px; overflow-y: auto;">
                            ${(runningData.models || data.ollama.models).map(model => {
                                const modelName = model.name || model.name;
                                const isRunning = model.is_running || false;
                                const size = model.size ? formatSize(model.size) : 'N/A';
                                
                                return `
                                    <div class="d-flex justify-content-between align-items-center py-2 border-bottom">
                                        <div class="d-flex align-items-center">
                                            <div class="status-indicator me-2">
                                                <i class="fas fa-circle ${isRunning ? 'text-success' : 'text-secondary'}" 
                                                   title="${isRunning ? 'Modelo en ejecución' : 'Modelo detenido'}"></i>
                                            </div>
                                            <div>
                                                <small class="d-block fw-bold" title="${modelName}">
                                                    ${modelName.length > 20 ? modelName.substring(0, 20) + '...' : modelName}
                                                </small>
                                                <small class="text-muted">${size}</small>
                                            </div>
                                        </div>
                                        <div class="d-flex gap-1">
                                            ${isRunning ? `
                                                <button class="btn btn-outline-danger btn-sm" 
                                                        onclick="controlOllamaModel('${modelName}', 'stop')"
                                                        title="Detener modelo">
                                                    <i class="fas fa-stop"></i>
                                                </button>
                                            ` : `
                                                <button class="btn btn-outline-success btn-sm" 
                                                        onclick="controlOllamaModel('${modelName}', 'run')"
                                                        title="Ejecutar modelo">
                                                    <i class="fas fa-play"></i>
                                                </button>
                                            `}
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                        <div class="d-flex gap-1 mt-3">
                            <button class="btn btn-outline-warning btn-sm" onclick="controlOllama('stop')">
                                <i class="fas fa-power-off"></i> Detener Ollama
                            </button>
                            <button class="btn btn-outline-info btn-sm" onclick="refreshModelsStatus()">
                                <i class="fas fa-sync"></i> Actualizar
                            </button>
                        </div>
                    ` : `
                        <p class="text-muted mb-2">Ollama no está ejecutándose</p>
                        <button class="btn btn-outline-success btn-sm" onclick="controlOllama('start')">
                            <i class="fas fa-play"></i> Iniciar Ollama
                        </button>
                    `}
                </div>
            </div>
        </div>
    `;
    
    // LM Studio Status
    html += `
        <div class="col-lg-3 mb-3">
            <div class="card h-100">
                <div class="card-header ${data.lmstudio.available ? 'bg-success' : 'bg-warning'} text-white">
                    <h6 class="mb-0">
                        <i class="fas fa-desktop me-2"></i>
                        LM Studio
                        <span class="badge ${data.lmstudio.available ? 'bg-light text-success' : 'bg-light text-warning'} ms-2">
                            ${data.lmstudio.available ? 'Online' : 'Offline'}
                        </span>
                    </h6>
                </div>
                <div class="card-body p-3">
                    ${data.lmstudio.available ? `
                        <div class="mb-2">
                            <small class="text-muted">Modelos cargados (${data.lmstudio.models.length}):</small>
                        </div>
                        <div class="models-list" style="max-height: 120px; overflow-y: auto;">
                            ${data.lmstudio.models.map(model => `
                                <div class="py-1 border-bottom">
                                    <div class="d-flex align-items-center">
                                        <i class="fas fa-circle text-success me-2"></i>
                                        <small class="text-truncate" title="${model.id}">
                                            ${model.id.length > 15 ? model.id.substring(0, 15) + '...' : model.id}
                                        </small>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                        <div class="mt-2">
                            <button class="btn btn-outline-warning btn-sm" onclick="controlLMStudio('stop')">
                                <i class="fas fa-stop"></i> Info
                            </button>
                        </div>
                    ` : `
                        <p class="text-muted mb-2">LM Studio no está ejecutándose</p>
                        <button class="btn btn-outline-success btn-sm" onclick="controlLMStudio('start')">
                            <i class="fas fa-play"></i> Info
                        </button>
                    `}
                </div>
            </div>
        </div>
    `;
    
    // Google Gemini Status
    html += `
        <div class="col-lg-3 mb-3">
            <div class="card h-100">
                <div class="card-header ${data.gemini.available ? 'bg-success' : 'bg-secondary'} text-white">
                    <h6 class="mb-0">
                        <i class="fab fa-google me-2"></i>
                        Google Gemini
                        <span class="badge ${data.gemini.available ? 'bg-light text-success' : 'bg-light text-secondary'} ms-2">
                            ${data.gemini.available ? 'Configurado' : 'No configurado'}
                        </span>
                    </h6>
                </div>
                <div class="card-body p-3">
                    ${data.gemini.available ? `
                        <div class="d-flex align-items-center mb-2">
                            <i class="fas fa-circle text-success me-2"></i>
                            <small class="text-success">API Key configurada</small>
                        </div>
                        <small class="text-muted">Modelo: Gemini-1.5-Flash</small>
                    ` : `
                        <p class="text-muted mb-2">API Key no configurada</p>
                        <small class="text-muted">Añadir GOOGLE_API_KEY al archivo .env</small>
                    `}
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

function formatSize(size) {
    if (typeof size === 'number') {
        const units = ['B', 'KB', 'MB', 'GB', 'TB'];
        let i = 0;
        while (size >= 1024 && i < units.length - 1) {
            size /= 1024;
            i++;
        }
        return `${size.toFixed(1)} ${units[i]}`;
    }
    return size || 'N/A';
}

async function controlOllamaModel(modelName, action) {
    try {
        // Mostrar indicador de carga para el botón específico
        const buttons = document.querySelectorAll(`button[onclick*="${modelName}"]`);
        buttons.forEach(btn => {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        });

        const response = await fetch(`/api/models/ollama/individual/${encodeURIComponent(modelName)}/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Mostrar notificación de éxito
            Swal.fire({
                icon: 'success',
                title: `Modelo ${modelName}`,
                text: data.message,
                timer: 2000,
                showConfirmButton: false,
                toast: true,
                position: 'top-end'
            });
            
            // Actualizar estado después de un breve delay
            setTimeout(refreshModelsStatus, 1500);
        } else {
            throw new Error(data.error || `Error al ${action === 'run' ? 'ejecutar' : 'detener'} modelo`);
        }
    } catch (error) {
        console.error('Error:', error);
        
        // Restaurar botones
        const buttons = document.querySelectorAll(`button[onclick*="${modelName}"]`);
        buttons.forEach(btn => {
            btn.disabled = false;
            btn.innerHTML = action === 'run' ? '<i class="fas fa-play"></i>' : '<i class="fas fa-stop"></i>';
        });
        
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message,
            confirmButtonColor: '#007bff'
        });
    }
}

async function controlOllama(action) {
    try {
        const response = await fetch(`/api/models/ollama/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            Swal.fire({
                icon: 'success',
                title: 'Ollama',
                text: data.message,
                confirmButtonColor: '#007bff'
            });
            
            // Actualizar estado después de 2 segundos
            setTimeout(refreshModelsStatus, 2000);
        } else {
            throw new Error(data.error || 'Error al controlar Ollama');
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message,
            confirmButtonColor: '#007bff'
        });
    }
}

async function controlLMStudio(action) {
    try {
        const response = await fetch(`/api/models/lmstudio/${action}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            Swal.fire({
                icon: 'info',
                title: 'LM Studio',
                html: `
                    <p>${data.message}</p>
                    <div class="text-start mt-3">
                        <strong>Instrucciones:</strong>
                        <ol class="mt-2">
                            ${data.instructions.map(instruction => `<li>${instruction}</li>`).join('')}
                        </ol>
                    </div>
                `,
                confirmButtonColor: '#007bff'
            });
            
            // Actualizar estado después de unos segundos
            setTimeout(refreshModelsStatus, 3000);
        } else {
            throw new Error(data.error || 'Error al controlar LM Studio');
        }
    } catch (error) {
        console.error('Error:', error);
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: error.message,
            confirmButtonColor: '#007bff'
        });
    }
}

// Cargar estado de modelos al inicializar la página
document.addEventListener('DOMContentLoaded', function() {
    // Cargar estado inicial después de un breve delay
    setTimeout(refreshModelsStatus, 1000);
    
    // Auto-actualizar cada 10 segundos si está visible la sección
    setInterval(() => {
        const modelsSection = document.getElementById('modelsStatusContainer');
        if (modelsSection && isElementInViewport(modelsSection)) {
            refreshModelsStatus();
        }
    }, 10000);
});

// Función para verificar si un elemento está visible en viewport
function isElementInViewport(el) {
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// ========================
// CONSOLA OLLAMA
// ========================

// Agregar línea a la consola Ollama
function addOllamaConsoleLine(text, type = 'output') {
    const console = document.getElementById('ollamaConsoleOutput');
    const timestamp = new Date().toLocaleTimeString();
    
    let className = '';
    let prefix = '';
    
    switch(type) {
        case 'command':
            className = 'text-info';
            prefix = `[${timestamp}] $ ollama `;
            break;
        case 'success':
            className = 'text-success';
            prefix = `[${timestamp}] ✓ `;
            break;
        case 'error':
            className = 'text-danger';
            prefix = `[${timestamp}] ✗ `;
            break;
        case 'warning':
            className = 'text-warning';
            prefix = `[${timestamp}] ⚠ `;
            break;
        default:
            className = 'text-light';
            prefix = `[${timestamp}] `;
    }
    
    const line = document.createElement('div');
    line.className = `console-line ${className}`;
    line.innerHTML = `${prefix}${text}`;
    
    console.appendChild(line);
    console.scrollTop = console.scrollHeight;
}

// Ejecutar comando Ollama predefinido
async function executeOllamaCommand(command) {
    addOllamaConsoleLine(command, 'command');
    
    try {
        const response = await fetch('/api/ollama/console', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addOllamaConsoleLine(data.output, 'success');
            
            // Si fue comando serve, actualizar estado de modelos
            if (command === 'serve') {
                setTimeout(refreshModelsStatus, 2000);
            }
            // Si fue comando ps o list, actualizar estado también
            else if (command === 'ps' || command === 'list') {
                setTimeout(refreshModelsStatus, 1000);
            }
        } else {
            addOllamaConsoleLine(data.output || data.error, 'error');
        }
        
    } catch (error) {
        addOllamaConsoleLine(`Error de conexión: ${error.message}`, 'error');
    }
}

// Ejecutar comando personalizado
async function executeCustomOllamaCommand() {
    const input = document.getElementById('ollamaCommandInput');
    const command = input.value.trim();
    
    if (!command) {
        addOllamaConsoleLine('Por favor, ingresa un comando', 'warning');
        return;
    }
    
    // Limpiar input
    input.value = '';
    
    // Ejecutar comando
    await executeOllamaCommand(command);
}

// Mostrar acciones para modelos
async function showOllamaModelActions() {
    try {
        addOllamaConsoleLine('Obteniendo lista de modelos...', 'command');
        
        const response = await fetch('/api/ollama/models-for-actions');
        const data = await response.json();
        
        if (!data.available || data.models.length === 0) {
            addOllamaConsoleLine('No hay modelos disponibles o Ollama no está ejecutándose', 'warning');
            return;
        }
        
        const { value: selectedModel } = await Swal.fire({
            title: '🦙 Seleccionar Modelo',
            text: 'Elige un modelo para ejecutar o detener:',
            input: 'select',
            inputOptions: data.models.reduce((options, model) => {
                options[model] = model;
                return options;
            }, {}),
            inputPlaceholder: 'Selecciona un modelo',
            showCancelButton: true,
            confirmButtonText: 'Continuar',
            cancelButtonText: 'Cancelar',
            inputValidator: (value) => {
                if (!value) {
                    return 'Debes seleccionar un modelo';
                }
            }
        });
        
        if (selectedModel) {
            const { value: action } = await Swal.fire({
                title: `🔧 Acción para ${selectedModel}`,
                text: '¿Qué acción quieres realizar?',
                input: 'select',
                inputOptions: {
                    'run': '▶️ Ejecutar modelo (run)',
                    'stop': '⏹️ Detener modelo (stop)',
                    'show': 'ℹ️ Mostrar información (show)'
                },
                inputPlaceholder: 'Selecciona una acción',
                showCancelButton: true,
                confirmButtonText: 'Ejecutar',
                cancelButtonText: 'Cancelar',
                inputValidator: (value) => {
                    if (!value) {
                        return 'Debes seleccionar una acción';
                    }
                }
            });
            
            if (action) {
                const fullCommand = `${action} ${selectedModel}`;
                await executeOllamaCommand(fullCommand);
            }
        }
        
    } catch (error) {
        addOllamaConsoleLine(`Error al obtener modelos: ${error.message}`, 'error');
    }
}

// Limpiar consola Ollama
function clearOllamaConsole() {
    const console = document.getElementById('ollamaConsoleOutput');
    console.innerHTML = `
        <div class="console-line">
            <span class="text-success">ollama-console@web:</span><span class="text-info">~$</span> <span class="text-muted">Consola limpiada</span>
        </div>
        <div class="console-line">
            <span class="text-muted">═══════════════════════════════════════════════════</span>
        </div>
    `;
}

// Event listener para Enter en el input de comando
document.addEventListener('DOMContentLoaded', function() {
    const commandInput = document.getElementById('ollamaCommandInput');
    if (commandInput) {
        commandInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                executeCustomOllamaCommand();
            }
        });
    }
});