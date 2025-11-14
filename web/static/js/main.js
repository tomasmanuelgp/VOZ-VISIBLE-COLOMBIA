// VOZ VISIBLE: JavaScript para interfaz web funcional

let socket;
let lastAudioData = null;
let currentAudio = null;
const MAX_HISTORY_ITEMS = 12;
const predictionHistory = [];

// Verificar estado del sistema al cargar
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    checkSystemStatus();
    initializeTheme();
    
    // Smooth scroll para links de navegación
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Inicializar Socket.IO
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Conectado al servidor');
    });
    
    socket.on('disconnect', function() {
        console.log('Desconectado del servidor');
    });
    
    socket.on('status', function(data) {
        updateSystemStatus(data.status, data.message);
    });
}

// Verificar estado del sistema
async function checkSystemStatus() {
    const statusElement = document.getElementById('status');
    
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.status === 'ready') {
            statusElement.innerHTML = '<i class="fas fa-check-circle"></i> Sistema Listo';
            statusElement.className = 'status-indicator ready';
        } else if (data.status === 'initializing') {
            statusElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Inicializando...';
            statusElement.className = 'status-indicator initializing';
        } else {
            statusElement.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error del sistema';
            statusElement.className = 'status-indicator error';
        }
    } catch (error) {
        statusElement.innerHTML = '<i class="fas fa-times-circle"></i> Sistema no disponible';
        statusElement.className = 'status-indicator error';
    }
}

// Abrir modal de subir imagen
function openImageUpload() {
    document.getElementById('imageUploadModal').style.display = 'block';
}

// Cerrar modal de subir imagen
function closeImageUpload() {
    document.getElementById('imageUploadModal').style.display = 'none';
    document.getElementById('imageInput').value = '';
    document.getElementById('imagePreview').innerHTML = '';
    document.getElementById('analyzeBtn').disabled = true;
}

// Manejar subida de imagen
function handleImageUpload() {
    const input = document.getElementById('imageInput');
    const preview = document.getElementById('imagePreview');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            preview.innerHTML = `<img src="${e.target.result}" alt="Imagen a analizar">`;
            analyzeBtn.disabled = false;
        };
        
        reader.readAsDataURL(input.files[0]);
    }
}

// Analizar imagen (funcional)
async function analyzeImage() {
    const input = document.getElementById('imageInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (!input.files || !input.files[0]) {
        alert('Por favor seleccione una imagen');
        return;
    }
    
    // Mostrar loading
    analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analizando...';
    analyzeBtn.disabled = true;
    
    try {
        // Crear FormData para enviar archivo
        const formData = new FormData();
        formData.append('file', input.files[0]);
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showPrediction(data.word, data.confidence, data.audio);
            closeImageUpload();
        } else {
            alert('Error en la predicción: ' + data.message);
        }
    } catch (error) {
        alert('Error de conexión: ' + error.message);
    } finally {
        analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analizar Imagen';
        analyzeBtn.disabled = false;
    }
}

// Reproducir audio TTS con feedback visual
function playTTSAudio(audioData) {
    if (!audioData) return;
    
    // Guardar último audio para repetir
    lastAudioData = audioData;
    
    // Mostrar indicador de TTS
    const ttsIndicator = document.getElementById('homeTTSIndicator');
    const repeatBtn = document.getElementById('homeRepeatAudioBtn');
    
    if (ttsIndicator) {
        ttsIndicator.style.display = 'flex';
    }
    if (repeatBtn) {
        repeatBtn.style.display = 'inline-block';
    }
    
    try {
        // Detener audio anterior si está reproduciéndose
        if (currentAudio) {
            currentAudio.pause();
            currentAudio.currentTime = 0;
        }
        
        currentAudio = new Audio(audioData);
        
        // Ocultar indicador cuando termine
        currentAudio.addEventListener('ended', function() {
            if (ttsIndicator) {
                ttsIndicator.style.display = 'none';
            }
        });
        
        // Manejar errores
        currentAudio.addEventListener('error', function(e) {
            console.warn('Error reproduciendo audio:', e);
            if (ttsIndicator) {
                ttsIndicator.style.display = 'none';
            }
        });
        
        currentAudio.play().catch(error => {
            console.warn('Error reproduciendo audio:', error);
            if (ttsIndicator) {
                ttsIndicator.style.display = 'none';
            }
        });
    } catch (error) {
        console.warn('Error creando audio:', error);
        if (ttsIndicator) {
            ttsIndicator.style.display = 'none';
        }
    }
}

// Repetir último audio reproducido
function repeatLastAudio() {
    if (lastAudioData) {
        playTTSAudio(lastAudioData);
    }
}

// Mostrar resultado de predicción
function showPrediction(word, confidence, audioData = null) {
    // Actualizar texto traducido (nuevo diseño)
    const translatedText = document.getElementById('translatedText');
    if (translatedText) {
        translatedText.textContent = word;
        // Efecto de máquina de escribir
        translatedText.style.animation = 'none';
        setTimeout(() => {
            translatedText.style.animation = 'typewriter 0.5s ease';
        }, 10);
    }
    
    // También mantener compatibilidad con elementos antiguos
    const predictedWord = document.getElementById('predictedWord');
    if (predictedWord) {
        predictedWord.textContent = word;
    }
    
    const confidenceFill = document.getElementById('confidenceFill');
    const confidenceText = document.getElementById('confidenceText');
    
    if (confidenceFill && confidenceText) {
        // Actualizar barra de confianza
        const confidencePercent = Math.round(confidence * 100);
        confidenceFill.style.width = confidencePercent + '%';
        
        // Actualizar texto de confianza (puede tener formato diferente)
        if (confidenceText.textContent.includes('Confianza:')) {
            confidenceText.textContent = `Confianza: ${confidencePercent}%`;
        } else {
            confidenceText.textContent = confidencePercent + '%';
        }
        
        // Color según confianza
        confidenceFill.className = 'confidence-fill';
        if (confidence > 0.8) {
            confidenceFill.classList.add('high');
        } else if (confidence > 0.5) {
            confidenceFill.classList.add('medium');
        } else {
            confidenceFill.classList.add('low');
        }
    }
    
    // Guardar audio para repetir
    if (audioData) {
        lastAudioData = audioData;
        playTTSAudio(audioData);
    }
    
    addPredictionToHistory({
        word,
        confidence,
        timestamp: Date.now()
    });
    
    // Scroll suave a la sección de demo si existe
    const demoSection = document.getElementById('demo');
    if (demoSection) {
        demoSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// Mostrar información del modelo
async function showInfo() {
    try {
        const response = await fetch('/api/model-info');
        const data = await response.json();
        
        if (data.num_classes) {
            alert(`SIGN-AI v1.0 - Sistema Funcional

Sistema de reconocimiento de lenguaje de señas en tiempo real.

Información del Modelo:
• Características de entrada: ${data.num_features}
• Número de clases: ${data.num_classes}
• Capas del modelo: ${data.num_layers}
• Precisión: 98.75%

Características:
• Reconocimiento en tiempo real
• Análisis de imágenes subidas
• Interfaz web intuitiva
• API REST completa
• WebSocket para tiempo real

Desarrollado con TensorFlow, MediaPipe y Flask.`);
        } else {
            showInfoFallback();
        }
    } catch (error) {
        showInfoFallback();
    }
}

// Mostrar información básica
function showInfoFallback() {
    alert(`SIGN-AI v1.0

Sistema de reconocimiento de lenguaje de señas en tiempo real.

Características:
• Reconocimiento en tiempo real
• Análisis de imágenes
• Interfaz web intuitiva
• API REST completa

Desarrollado con TensorFlow, MediaPipe y Flask.`);
}

// Actualizar estado del sistema
function updateSystemStatus(status, message) {
    const statusElement = document.getElementById('status');
    if (statusElement) {
        statusElement.innerHTML = `<i class="fas fa-${getStatusIcon(status)}"></i> ${message}`;
        statusElement.className = `status-indicator ${status}`;
    }
}

// Obtener icono según estado
function getStatusIcon(status) {
    const icons = {
        'ready': 'check-circle',
        'error': 'exclamation-triangle',
        'initializing': 'spinner fa-spin',
        'missing_files': 'times-circle'
    };
    return icons[status] || 'question-circle';
}

// Cerrar modal al hacer clic fuera
window.onclick = function(event) {
    const modal = document.getElementById('imageUploadModal');
    if (event.target === modal) {
        closeImageUpload();
    }
}

// Gestión de tema (modo claro/oscuro)
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
}

function toggleTheme() {
    const currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

function applyTheme(theme) {
    const body = document.body;
    const themeIcon = document.getElementById('themeIcon');
    
    if (theme === 'dark') {
        body.classList.add('dark-theme');
        if (themeIcon) {
            themeIcon.className = 'fas fa-sun';
        }
    } else {
        body.classList.remove('dark-theme');
        if (themeIcon) {
            themeIcon.className = 'fas fa-moon';
        }
    }
}

// Historial de predicciones (Home)
function addPredictionToHistory(entry) {
    const newEntry = {
        word: entry.word || '-',
        confidence: typeof entry.confidence === 'number' ? entry.confidence : 0,
        timestamp: entry.timestamp || Date.now()
    };
    predictionHistory.unshift(newEntry);
    if (predictionHistory.length > MAX_HISTORY_ITEMS) {
        predictionHistory.pop();
    }
    renderPredictionHistory();
}

function renderPredictionHistory() {
    const historyPanel = document.getElementById('historyPanel');
    const list = document.getElementById('homePredictionHistoryList');
    if (!historyPanel || !list) return;

    if (!predictionHistory.length) {
        historyPanel.style.display = 'none';
        list.innerHTML = '<li class="history-empty">Aún no hay predicciones</li>';
        return;
    }

    historyPanel.style.display = 'block';
    list.innerHTML = '';

    predictionHistory.forEach(item => {
        const li = document.createElement('li');
        li.className = 'history-item';
        li.innerHTML = `
            <div class="history-word">${item.word}</div>
            <div class="history-meta">
                <div>${formatConfidence(item.confidence)}</div>
                <small>${formatTimestamp(item.timestamp)}</small>
            </div>
        `;
        list.appendChild(li);
    });
}

function clearPredictionHistory() {
    predictionHistory.length = 0;
    renderPredictionHistory();
}

function formatConfidence(confidence) {
    const percent = Math.round(confidence * 100);
    return `${percent}% confianza`;
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
}