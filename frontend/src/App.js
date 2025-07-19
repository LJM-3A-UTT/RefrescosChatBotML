import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Componente principal del RefrescoBot
function App() {
  const [currentStep, setCurrentStep] = useState('inicio'); // 'inicio', 'chat', 'recomendacion'
  const [sesionId, setSesionId] = useState('');
  const [preguntaActual, setPreguntaActual] = useState(null);
  const [numeroPregunta, setNumeroPregunta] = useState(0);
  const [refrescosReales, setRefrescosReales] = useState([]);
  const [bebidasAlternativas, setBebidasAlternativas] = useState([]);
  const [mensajeRefrescos, setMensajeRefrescos] = useState('');
  const [mensajeAlternativas, setMensajeAlternativas] = useState('');
  const [mostrarAlternativas, setMostrarAlternativas] = useState(false);
  const [criteriosAlternativas, setCriteriosAlternativas] = useState([]);
  const [usuarioPuedeOcultar, setUsuarioPuedeOcultar] = useState(false);
  const [scoresSaludable, setScoreSaludable] = useState(0);
  const [feedbackPuntuacion, setFeedbackPuntuacion] = useState(null);
  const [mostrarFeedback, setMostrarFeedback] = useState(false);
  const [tiempoInicioPregunta, setTiempoInicioPregunta] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [presentacionSeleccionada, setPresentacionSeleccionada] = useState({}); // {bebida_id: presentacion_index}
  const [showNoMoreOptionsModal, setShowNoMoreOptionsModal] = useState(false);
  const [noMoreOptionsMessage, setNoMoreOptionsMessage] = useState('');

  // Función para iniciar una nueva sesión
  const iniciarSesion = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await axios.post(`${API}/iniciar-sesion`);
      const { sesion_id } = response.data;
      
      setSesionId(sesion_id);
      
      // Obtener la primera pregunta
      const preguntaResponse = await axios.get(`${API}/pregunta-inicial/${sesion_id}`);
      setPreguntaActual(preguntaResponse.data.pregunta);
      setNumeroPregunta(preguntaResponse.data.numero_pregunta);
      setTiempoInicioPregunta(Date.now());
      setCurrentStep('chat');
      
    } catch (err) {
      setError('Error al iniciar la sesión. Por favor, intenta de nuevo.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Función para responder una pregunta
  const responderPregunta = async (opcionSeleccionada) => {
    try {
      setLoading(true);
      
      const tiempoRespuesta = (Date.now() - tiempoInicioPregunta) / 1000; // en segundos
      
      const respuestaData = {
        pregunta_id: preguntaActual.id,
        respuesta_id: opcionSeleccionada.id,
        respuesta_texto: opcionSeleccionada.texto,
        tiempo_respuesta: tiempoRespuesta
      };
      
      const response = await axios.post(`${API}/responder/${sesionId}`, respuestaData);
      
      if (response.data.completada) {
        // Completadas todas las preguntas, obtener recomendaciones
        await obtenerRecomendaciones();
      } else {
        // Obtener siguiente pregunta
        const siguientePreguntaResponse = await axios.get(`${API}/siguiente-pregunta/${sesionId}`);
        
        if (siguientePreguntaResponse.data.finalizada) {
          // No hay más preguntas, obtener recomendaciones
          await obtenerRecomendaciones();
        } else {
          setPreguntaActual(siguientePreguntaResponse.data.pregunta);
          setNumeroPregunta(siguientePreguntaResponse.data.numero_pregunta);
          setTiempoInicioPregunta(Date.now());
        }
      }
      
    } catch (err) {
      setError('Error al procesar la respuesta. Por favor, intenta de nuevo.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Función para obtener recomendaciones
  const obtenerRecomendaciones = async () => {
    try {
      setLoading(true);
      
      const response = await axios.get(`${API}/recomendacion/${sesionId}`);
      setRefrescosReales(response.data.refrescos_reales || []);
      setBebidasAlternativas(response.data.bebidas_alternativas || []);
      setMensajeRefrescos(response.data.mensaje_refrescos || '');
      setMensajeAlternativas(response.data.mensaje_alternativas || '');
      setMostrarAlternativas(response.data.mostrar_alternativas || false);
      setCriteriosAlternativas(response.data.criterios_alternativas || []);
      setUsuarioPuedeOcultar(response.data.usuario_puede_ocultar || false);
      setScoreSaludable(response.data.score_saludable || 0);
      
      // Inicializar presentaciones seleccionadas (primera por defecto)
      const presentacionesIniciales = {};
      [...(response.data.refrescos_reales || []), ...(response.data.bebidas_alternativas || [])].forEach(bebida => {
        presentacionesIniciales[bebida.id] = 0;
      });
      setPresentacionSeleccionada(presentacionesIniciales);
      
      setCurrentStep('recomendacion');
      
    } catch (err) {
      setError('Error al obtener recomendaciones. Por favor, intenta de nuevo.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Función para cambiar presentación seleccionada
  const cambiarPresentacion = (bebidaId, index) => {
    setPresentacionSeleccionada(prev => ({
      ...prev,
      [bebidaId]: index
    }));
  };

  // Función para obtener datos de presentación actual
  const obtenerPresentacionActual = (bebida) => {
    const indiceSeleccionado = presentacionSeleccionada[bebida.id] || 0;
    return bebida.presentaciones[indiceSeleccionado] || bebida.presentaciones[0];
  };

  // Función para puntuar una bebida
  const puntuarBebida = async (bebidaId, puntuacion) => {
    try {
      const presentacionActual = obtenerPresentacionActual(
        [...refrescosReales, ...bebidasAlternativas].find(b => b.id === bebidaId)
      );
      
      const puntuacionData = {
        puntuacion: puntuacion,
        comentario: "Puntuación desde la interfaz"
      };
      
      const response = await axios.post(`${API}/puntuar/${sesionId}/${bebidaId}`, puntuacionData);
      
      // Mostrar feedback del aprendizaje
      if (response.data.feedback_aprendizaje) {
        setFeedbackPuntuacion(response.data.feedback_aprendizaje);
        setMostrarFeedback(true);
        
        // Ocultar feedback después de 8 segundos
        setTimeout(() => {
          setMostrarFeedback(false);
        }, 8000);
      }
      
      // Actualizar la puntuación en la interfaz
      const actualizarPuntuacion = (lista) => 
        lista.map(bebida => 
          bebida.id === bebidaId 
            ? { ...bebida, puntuacion_usuario: puntuacion }
            : bebida
        );
      
      setRefrescosReales(prev => actualizarPuntuacion(prev));
      setBebidasAlternativas(prev => actualizarPuntuacion(prev));
      
    } catch (err) {
      setError('Error al guardar la puntuación.');
      console.error('Error:', err);
    }
  };

  // Función para obtener recomendaciones alternativas
  const obtenerAlternativas = async () => {
    try {
      setLoading(true);
      
      const response = await axios.get(`${API}/recomendaciones-alternativas/${sesionId}`);
      
      if (response.data.sin_mas_opciones) {
        // No hay más opciones disponibles - mostrar modal amigable
        const mensaje = response.data.mensaje || 'No hay más opciones disponibles en tu categoría';
        setNoMoreOptionsMessage(mensaje);
        setShowNoMoreOptionsModal(true);
      } else {
        // Hay nuevas recomendaciones disponibles
        const nuevasRecomendaciones = response.data.recomendaciones_adicionales || [];
        const tipoRecomendaciones = response.data.tipo_recomendaciones || 'refrescos_tradicionales';
        
        // Inicializar presentaciones para las nuevas bebidas
        const nuevasPresentaciones = {};
        nuevasRecomendaciones.forEach(bebida => {
          nuevasPresentaciones[bebida.id] = 0;
        });
        
        setPresentacionSeleccionada(prev => ({
          ...prev,
          ...nuevasPresentaciones
        }));
        
        // Determinar a qué lista agregar las nuevas bebidas basándose en el tipo
        if (tipoRecomendaciones.includes('alternativas') || tipoRecomendaciones.includes('saludables')) {
          // Son alternativas saludables, agregar a bebidasAlternativas
          setBebidasAlternativas(prev => [...prev, ...nuevasRecomendaciones]);
          setMensajeAlternativas(response.data.mensaje || 'Nuevas alternativas disponibles:');
        } else {
          // Son refrescos regulares, agregar a refrescosReales
          setRefrescosReales(prev => [...prev, ...nuevasRecomendaciones]);
          setMensajeRefrescos(response.data.mensaje || 'Más refrescos disponibles:');
        }
      }
      
    } catch (err) {
      // En caso de error también mostrar modal amigable
      setNoMoreOptionsMessage('No pudimos cargar más opciones en este momento. ¡Prueba a empezar un nuevo juego!');
      setShowNoMoreOptionsModal(true);
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Función para reiniciar el chat
  const reiniciarChat = () => {
    setCurrentStep('inicio');
    setSesionId('');
    setPreguntaActual(null);
    setNumeroPregunta(0);
    setRefrescosReales([]);
    setBebidasAlternativas([]);
    setMensajeRefrescos('');
    setMensajeAlternativas('');
    setMostrarAlternativas(false);
    setCriteriosAlternativas([]);
    setUsuarioPuedeOcultar(false);
    setScoreSaludable(0);
    setFeedbackPuntuacion(null);
    setMostrarFeedback(false);
    setPresentacionSeleccionada({});
    setError('');
  };

  // Función para obtener color de probabilidad
  const obtenerColorProbabilidad = (probabilidad) => {
    if (probabilidad >= 80) return '#4CAF50'; // Verde
    if (probabilidad >= 60) return '#FF9800'; // Naranja
    if (probabilidad >= 40) return '#FFC107'; // Amarillo
    return '#f44336'; // Rojo
  };

  // Componente de inicio
  const PantallaInicio = () => (
    <div className="pantalla-inicio">
      <div className="hero-section">
        <div className="bot-avatar">
          <div className="bot-icon">🤖</div>
        </div>
        <h1 className="titulo-principal">RefrescoBot ML</h1>
        <p className="subtitulo">
          ¡Hola! Soy tu asistente personal con Inteligencia Artificial para encontrar la bebida perfecta para ti.
        </p>
        <p className="descripcion">
          Te haré {6} preguntas sobre tu día, tus rutinas y tus preferencias. 
          Basándome en tus respuestas, calcularé la probabilidad de que te guste cada refresco usando algoritmos de Machine Learning.
        </p>
        <button 
          className="btn-iniciar" 
          onClick={iniciarSesion}
          disabled={loading}
        >
          {loading ? 'Iniciando...' : '¡Comenzar Análisis!'}
        </button>
      </div>
    </div>
  );

  // Componente de chat
  const PantallaChat = () => (
    <div className="pantalla-chat">
      <div className="chat-header">
        <div className="progreso-bar">
          <div 
            className="progreso-fill" 
            style={{ width: `${(numeroPregunta / 6) * 100}%` }}
          ></div>
        </div>
        <p className="progreso-texto">Pregunta {numeroPregunta} de {6}</p>
      </div>
      
      <div className="chat-content">
        <div className="pregunta-container">
          <div className="bot-message">
            <div className="bot-avatar-small">🤖</div>
            <div className="message-bubble">
              <p className="pregunta-texto">{preguntaActual?.pregunta}</p>
            </div>
          </div>
          
          <div className="opciones-container">
            {preguntaActual?.opciones.map((opcion, index) => (
              <button
                key={opcion.id}
                className="opcion-btn"
                onClick={() => responderPregunta(opcion)}
                disabled={loading}
              >
                {opcion.texto}
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {loading && (
        <div className="loading-indicator">
          <div className="spinner"></div>
          <p>Analizando con Inteligencia Artificial...</p>
        </div>
      )}
    </div>
  );

  // Componente para mostrar una bebida
  const BebidaCard = ({ bebida, esRefresco }) => {
    const presentacionActual = obtenerPresentacionActual(bebida);
    
    // Verificar que la probabilidad exista para evitar el error
    const probabilidad = bebida.probabilidad ?? 50.0; // Valor por defecto si no existe
    
    return (
      <div className="bebida-card">
        <div className="probabilidad-header">
          <div 
            className="probabilidad-badge"
            style={{ backgroundColor: obtenerColorProbabilidad(probabilidad) }}
          >
            {probabilidad.toFixed(1)}% de compatibilidad
          </div>
        </div>
        
        <div className="bebida-image">
          <img 
            src={`${BACKEND_URL}${presentacionActual.imagen_local}`}
            alt={`${bebida.nombre} ${presentacionActual.ml}ml`}
          />
        </div>
        
        <div className="bebida-info">
          <h3 className="bebida-nombre">{bebida.nombre}</h3>
          <p className="bebida-sabor">Sabor: {presentacionActual.sabor || 'Original'}</p>
          <p className="bebida-descripcion">{presentacionActual.descripcion_presentacion}</p>
          
          <div className="presentaciones-selector">
            <label className="presentaciones-label">Elige tu presentación:</label>
            <div className="presentaciones-grid">
              {bebida.presentaciones.map((presentacion, index) => (
                <button
                  key={index}
                  className={`presentacion-btn ${
                    presentacionSeleccionada[bebida.id] === index ? 'activa' : ''
                  }`}
                  onClick={() => cambiarPresentacion(bebida.id, index)}
                >
                  {presentacion.ml}ml
                  <span className="presentacion-precio">${presentacion.precio}</span>
                </button>
              ))}
            </div>
          </div>
          
          <div className="bebida-detalles">
            <div className="precio">
              <span className="precio-label">Precio:</span>
              <span className="precio-valor">${presentacionActual.precio}</span>
            </div>
            
            <div className="tipo-bebida">
              <span className={`tipo-tag ${bebida.tipo}`}>
                {bebida.tipo}
              </span>
              {bebida.es_carbonatada && <span className="caracteristica-tag">Carbonatada</span>}
              {bebida.es_azucarada && <span className="caracteristica-tag">Azucarada</span>}
            </div>
          </div>
          
          <div className="factores-clave">
            <h4>¿Por qué te lo recomiendo?</h4>
            <ul>
              {(bebida.factores_explicativos || ["Recomendación general"]).map((factor, index) => (
                <li key={index}>{factor}</li>
              ))}
            </ul>
          </div>
          
          <div className="puntuacion-section">
            <p className="puntuacion-label">¿Qué te parece esta recomendación?</p>
            <div className="estrellas-container">
              {[1, 2, 3, 4, 5].map((estrella) => (
                <button
                  key={estrella}
                  className={`estrella-btn ${
                    bebida.puntuacion_usuario && bebida.puntuacion_usuario >= estrella 
                      ? 'activa' 
                      : ''
                  }`}
                  onClick={() => puntuarBebida(bebida.id, estrella)}
                >
                  ⭐
                </button>
              ))}
            </div>
            {bebida.puntuacion_usuario && (
              <p className="puntuacion-confirmacion">
                ¡Gracias por tu puntuación de {bebida.puntuacion_usuario} estrellas!
              </p>
            )}
          </div>
        </div>
      </div>
    );
  };

  // Componente de feedback de puntuación
  const FeedbackPuntuacion = () => {
    if (!mostrarFeedback || !feedbackPuntuacion) return null;
    
    return (
      <div className="feedback-overlay">
        <div className="feedback-modal">
          <div className="feedback-header">
            <h3>🧠 Sistema Aprendiendo</h3>
            <button 
              className="feedback-close"
              onClick={() => setMostrarFeedback(false)}
            >
              ×
            </button>
          </div>
          
          <div className="feedback-content">
            <div className="feedback-main">
              <p className="feedback-mensaje">{feedbackPuntuacion.mensaje_principal}</p>
              
              <div className="feedback-detalles">
                <div className="feedback-item">
                  <span className="feedback-label">Tu puntuación:</span>
                  <span className="feedback-valor">{feedbackPuntuacion.tu_puntuacion} ⭐</span>
                </div>
                
                <div className="feedback-item">
                  <span className="feedback-label">Impacto futuro:</span>
                  <span className="feedback-valor">{feedbackPuntuacion.impacto_futuro}</span>
                </div>
                
                <div className="feedback-item">
                  <span className="feedback-label">Bebidas similares afectadas:</span>
                  <span className="feedback-valor">{feedbackPuntuacion.bebidas_similares_afectadas}</span>
                </div>
                
                <div className="feedback-item">
                  <span className="feedback-label">Nueva puntuación promedio:</span>
                  <span className="feedback-valor">{feedbackPuntuacion.nueva_puntuacion_promedio} ⭐ ({feedbackPuntuacion.total_opiniones} opiniones)</span>
                </div>
              </div>
              
              <div className="feedback-explicacion">
                <p>🔬 <strong>Cómo aprendo:</strong> Uso tu puntuación para ajustar las probabilidades de {feedbackPuntuacion.nombre_bebida} y bebidas similares ({feedbackPuntuacion.tipo_bebida}s) en futuras recomendaciones.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Componente para mostrar criterios de alternativas
  const CriteriosAlternativas = () => {
    if (!mostrarAlternativas || criteriosAlternativas.length === 0) return null;
    
    return (
      <div className="criterios-alternativas">
        <h4>🤔 ¿Por qué veo opciones saludables?</h4>
        <ul>
          {criteriosAlternativas.map((criterio, index) => (
            <li key={index}>{criterio}</li>
          ))}
        </ul>
        {usuarioPuedeOcultar && (
          <button 
            className="btn-ocultar-alternativas"
            onClick={() => setMostrarAlternativas(false)}
          >
            Ocultar opciones saludables
          </button>
        )}
      </div>
    );
  };
  const PantallaRecomendaciones = () => (
    <div className="pantalla-recomendaciones">
      <div className="recomendaciones-header">
        <h2>🎯 ¡Análisis ML Completado!</h2>
        <p className="subtitle">He calculado las probabilidades específicas para cada bebida basándome en tu perfil</p>
        {scoresSaludable > 0 && (
          <p className="score-saludable">Score de preferencias saludables: {scoresSaludable.toFixed(1)}</p>
        )}
      </div>
      
      {refrescosReales.length > 0 && (
        <div className="seccion-refrescos">
          <div className="seccion-header">
            <h3>🥤 Refrescos Recomendados Para Ti</h3>
            <p className="mensaje-seccion">{mensajeRefrescos}</p>
          </div>
          
          <div className="bebidas-grid">
            {refrescosReales.map((bebida) => (
              <BebidaCard key={bebida.id} bebida={bebida} esRefresco={true} />
            ))}
          </div>
        </div>
      )}
      
      <CriteriosAlternativas />
      
      {mostrarAlternativas && bebidasAlternativas.length > 0 && (
        <div className="seccion-alternativas">
          <div className="seccion-header">
            <h3>🌿 Opciones Saludables</h3>
            <p className="mensaje-seccion">{mensajeAlternativas}</p>
          </div>
          
          <div className="bebidas-grid">
            {bebidasAlternativas.map((bebida) => (
              <BebidaCard key={bebida.id} bebida={bebida} esRefresco={false} />
            ))}
          </div>
        </div>
      )}
      
      <div className="acciones-finales">
        <button className="btn-alternativas" onClick={obtenerAlternativas} disabled={loading}>
          {loading ? 'Cargando...' : 'Mostrar más opciones'}
        </button>
        <button className="btn-reiniciar" onClick={reiniciarChat}>
          Nuevo análisis
        </button>
        {usuarioPuedeOcultar && !mostrarAlternativas && (
          <button 
            className="btn-mostrar-alternativas"
            onClick={() => setMostrarAlternativas(true)}
          >
            Ver opciones saludables
          </button>
        )}
      </div>
      
      <FeedbackPuntuacion />
    </div>
  );

  // Función para reiniciar el juego
  const reiniciarJuego = () => {
    setShowNoMoreOptionsModal(false);
    setCurrentStep('inicio');
    setSesionId('');
    setPreguntaActual(null);
    setNumeroPregunta(0);
    setRefrescosReales([]);
    setBebidasAlternativas([]);
    setMensajeRefrescos('');
    setMensajeAlternativas('');
    setMostrarAlternativas(false);
    setCriteriosAlternativas([]);
    setUsuarioPuedeOcultar(false);
    setScoreSaludable(0);
    setFeedbackPuntuacion(null);
    setMostrarFeedback(false);
    setTiempoInicioPregunta(null);
    setLoading(false);
    setError('');
    setPresentacionSeleccionada({});
    setNoMoreOptionsMessage('');
  };

  // Componente Modal para "Sin más opciones"
  const ModalSinMasOpciones = () => (
    <div className="modal-overlay" onClick={() => setShowNoMoreOptionsModal(false)}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button 
          className="modal-close" 
          onClick={() => setShowNoMoreOptionsModal(false)}
        >
          ×
        </button>
        <div className="modal-icon">🍹</div>
        <h2 className="modal-title">¡Has explorado todas las opciones!</h2>
        <p className="modal-message">
          {noMoreOptionsMessage}
          <br/><br/>
          ¿Qué te gustaría hacer ahora?
        </p>
        <div className="modal-buttons">
          <button 
            className="modal-btn modal-btn-primary"
            onClick={reiniciarJuego}
          >
            🎮 Jugar de nuevo
          </button>
          <button 
            className="modal-btn modal-btn-secondary"
            onClick={() => setShowNoMoreOptionsModal(false)}
          >
            📋 Ver recomendaciones actuales
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="App">
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={() => setError('')}>Cerrar</button>
        </div>
      )}
      
      {showNoMoreOptionsModal && <ModalSinMasOpciones />}
      
      {currentStep === 'inicio' && <PantallaInicio />}
      {currentStep === 'chat' && <PantallaChat />}
      {currentStep === 'recomendacion' && <PantallaRecomendaciones />}
    </div>
  );
}

export default App;