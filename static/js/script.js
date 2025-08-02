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

// Función para mostrar razonamiento en tiempo real
function mostrarRazonamientoTiempoReal(modeloSeleccionado, pregunta) {
    if (!modeloSeleccionado) return;
    
    // Crear contenedor temporal para el razonamiento
    const chatBody = document.getElementById('chatBody');
    const tempContainer = document.createElement('div');
    tempContainer.className = 'message ia-message mb-3';
    tempContainer.innerHTML = `
        <div class="thinking-real-time bg-info bg-opacity-10 border border-info rounded p-3">
            <h6 class="mb-2"><i class="fas fa-brain me-1"></i>Razonamiento en tiempo real...</h6>
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
    
    // Simular pasos de razonamiento progresivos
    setTimeout(() => {
        agregarPasoRazonamiento(`🔍 Analizando pregunta: "${pregunta}"`);
    }, 500);
    
    setTimeout(() => {
        if (modeloSeleccionado === 'deepseek-r1:8b') {
            agregarPasoRazonamiento("🧠 Iniciando razonamiento avanzado paso a paso");
        } else if (modeloSeleccionado === 'phi3') {
            agregarPasoRazonamiento("⚡ Procesamiento rápido y eficiente activado");
        } else {
            agregarPasoRazonamiento("🤖 Procesando con modelo de IA especializado");
        }
    }, 1000);
    
    setTimeout(() => {
        const internetHabilitado = document.getElementById('permitirInternet').checked;
        if (internetHabilitado) {
            agregarPasoRazonamiento("🌐 Verificando si necesita búsqueda web...");
        } else {
            agregarPasoRazonamiento("📚 Consultando base de conocimientos...");
        }
    }, 1500);
    
    // Para consultas de noticias, agregar más pasos específicos
    if (pregunta.toLowerCase().includes('noticias') || pregunta.toLowerCase().includes('hoy')) {
        setTimeout(() => {
            agregarPasoRazonamiento("📰 Detectada consulta de noticias actuales");
        }, 2000);
        
        setTimeout(() => {
            if (document.getElementById('permitirInternet').checked) {
                agregarPasoRazonamiento("🔄 Activando modo agente para búsqueda web");
            }
        }, 2500);
    }
}

// Función para agregar paso de razonamiento
function agregarPasoRazonamiento(paso) {
    if (!currentThinkingContainer) return;
    
    const stepsContainer = currentThinkingContainer.querySelector('#thinking-steps');
    const stepElement = document.createElement('div');
    stepElement.className = 'thinking-step mb-1 p-2 border-start border-3 border-info bg-white rounded-end';
    stepElement.innerHTML = `
        <small class="text-muted">${new Date().toLocaleTimeString()}</small><br>
        ${paso}
    `;
    
    stepsContainer.appendChild(stepElement);
    currentThinkingContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
}

// Función para finalizar razonamiento en tiempo real
function finalizarRazonamientoTiempoReal() {
    if (currentThinkingContainer) {
        const indicator = currentThinkingContainer.querySelector('.thinking-indicator');
        if (indicator) {
            indicator.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <small class="text-muted"><i class="fas fa-check-circle text-success me-1"></i>Razonamiento completado</small>
                    <button class="btn btn-sm btn-outline-secondary" onclick="ocultarRazonamiento()" title="Ocultar razonamiento">
                        <i class="fas fa-eye-slash"></i>
                    </button>
                </div>
            `;
        }
        
        // Cambiar el título para indicar que el proceso terminó
        const titleElement = currentThinkingContainer.querySelector('h6');
        if (titleElement) {
            titleElement.innerHTML = '<i class="fas fa-brain me-1"></i>Proceso de razonamiento completado';
        }
        
        // NO remover automáticamente el contenedor - dejarlo visible
        // El usuario puede ocultarlo manualmente si quiere
        
        // Solo limpiar las variables de control
        currentThinkingSteps = [];
        // currentThinkingContainer = null; // Mantener la referencia para poder ocultarlo después
    }
}

// Nueva función para ocultar el razonamiento manualmente
function ocultarRazonamiento() {
    if (currentThinkingContainer && currentThinkingContainer.parentNode) {
        currentThinkingContainer.style.transition = 'opacity 0.3s ease';
        currentThinkingContainer.style.opacity = '0';
        setTimeout(() => {
            if (currentThinkingContainer && currentThinkingContainer.parentNode) {
                currentThinkingContainer.remove();
            }
            currentThinkingContainer = null;
        }, 300);
    }
}

// Función para mostrar el proceso de razonamiento real del agente
function mostrarProcesoRazonamientoReal(pensamientos, modelo) {
    if (!pensamientos || pensamientos.length === 0) return;
    
    // Actualizar el contenedor existente con los pensamientos reales
    if (currentThinkingContainer) {
        const stepsContainer = currentThinkingContainer.querySelector('#thinking-steps');
        if (stepsContainer) {
            // Limpiar pasos simulados
            stepsContainer.innerHTML = '';
            
            // Agregar pensamientos reales
            pensamientos.forEach((pensamiento, index) => {
                const stepElement = document.createElement('div');
                stepElement.className = 'thinking-step mb-1 p-2 border-start border-3 border-success bg-white rounded-end';
                stepElement.innerHTML = `
                    <small class="text-muted">Paso ${index + 1}</small><br>
                    <strong>${pensamiento}</strong>
                `;
                stepsContainer.appendChild(stepElement);
            });
            
            // Actualizar el título
            const titleElement = currentThinkingContainer.querySelector('h6');
            if (titleElement) {
                const esDeepSeek = modelo === 'deepseek-r1:8b';
                titleElement.innerHTML = `<i class="fas fa-brain me-1"></i>${esDeepSeek ? 'Razonamiento DeepSeek R1' : 'Proceso de razonamiento del agente'}`;
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
    
    // Mostrar razonamiento en tiempo real
    mostrarRazonamientoTiempoReal(modelo, pregunta);
    
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