"""
Configuración del RefrescoBot ML
Modifica estos valores para personalizar el comportamiento del sistema
"""

# ===== CONFIGURACIÓN DE PREGUNTAS =====
TOTAL_PREGUNTAS = 6  # Expandido de 6 a 18 para mayor variedad y precisión
MIN_PREGUNTAS_FIJA = 1  # Siempre incluir al menos 1 pregunta fija sobre refrescos

# ===== CONFIGURACIÓN DEL ALGORITMO ML =====
PROBABILIDAD_BASE = 50.0  # Probabilidad inicial para todas las bebidas (%)
PROBABILIDAD_MINIMA = 5.0  # Probabilidad mínima que puede tener una bebida (%)
PROBABILIDAD_MAXIMA = 95.0  # Probabilidad máxima que puede tener una bebida (%)

# ===== CONFIGURACIÓN DE MACHINE LEARNING REAL =====
ML_MIN_TRAINING_SAMPLES = 10  # Mínimo de muestras para entrenar modelos ML
ML_RETRAIN_THRESHOLD = 5  # Cada cuántas nuevas muestras re-entrenar
KMEANS_N_CLUSTERS = 5  # Número de clusters para segmentación de usuarios
AUTO_CLEAN_DB_ON_STARTUP = True  # Limpiar y recargar DB en cada inicio

# ===== CONFIGURACIÓN DE APRENDIZAJE COLABORATIVO =====
BONUS_PUNTUACION_ALTA = 15.0  # Bonus para bebidas con 4.5+ estrellas
BONUS_PUNTUACION_BUENA = 10.0  # Bonus para bebidas con 4.0+ estrellas
BONUS_PUNTUACION_REGULAR = 5.0  # Bonus para bebidas con 3.5+ estrellas
PENALIZACION_PUNTUACION_BAJA = -8.0  # Penalización para bebidas con menos de 2.5 estrellas

# Factor de confianza basado en el número de puntuaciones
PUNTUACIONES_MAXIMA_CONFIANZA = 10  # Número de puntuaciones para máxima confianza

# ===== CONFIGURACIÓN DE RECOMENDACIONES =====
MAX_REFRESCOS_RECOMENDADOS = 3  # Máximo número de refrescos a recomendar (reducido de 5 a 3)
MAX_ALTERNATIVAS_RECOMENDADAS = 3  # Máximo número de alternativas a recomendar inicialmente
MAX_RECOMENDACIONES_ADICIONALES = 3  # Máximo número de recomendaciones alternativas adicionales

# ===== CONFIGURACIÓN ESPECÍFICA PARA ALTERNATIVAS SALUDABLES =====
MAX_ALTERNATIVAS_SALUDABLES_INICIAL = 3  # Alternativas saludables mostradas inicialmente
MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL = 3  # Alternativas saludables adicionales por click
MAX_REFRESCOS_ADICIONALES = 3  # Refrescos adicionales por click para usuarios regulares

# ===== CONFIGURACIÓN POR TIPO DE USUARIO =====
# Para usuarios que NO consumen refrescos (solo alternativas saludables)
MAX_ALTERNATIVAS_USUARIO_SALUDABLE = 4  # Más alternativas para usuarios saludables
# Para usuarios regulares tradicionales (refrescos principalmente)
MAX_REFRESCOS_USUARIO_TRADICIONAL = 3  # Refrescos para usuarios tradicionales

# ===== CONFIGURACIÓN DE DETECCIÓN DE USUARIOS CURIOSOS =====
TIEMPO_RESPUESTA_RAPIDA = 0.50  # Segundos - respuestas más rápidas se consideran sospechosas
TIEMPO_RESPUESTA_LENTA = 30.0  # Segundos - respuestas más lentas se consideran sospechosas

# ===== MENSAJES DEL SISTEMA =====
MENSAJE_SIN_ALTERNATIVAS = "Lo siento, por el momento no tengo más opciones alternativas disponibles. ¡Pero puedes intentar de nuevo más tarde cuando tengamos nuevos productos!"
MENSAJE_REFRESCOS_NORMALES = "Basándome en tu personalidad y respuestas, aquí están tus refrescos ideales:"
MENSAJE_ALTERNATIVAS_SALUDABLES = "También podrían interesarte estas opciones más saludables:"
MENSAJE_NO_REFRESCOS = "Como prefieres opciones más saludables, estas bebidas son perfectas para ti:"

# ===== CONFIGURACIÓN DE COLORES PARA PROBABILIDADES =====
# Colores para los badges de probabilidad en el frontend
COLOR_PROBABILIDAD_ALTA = '#4CAF50'  # Verde para 80%+
COLOR_PROBABILIDAD_MEDIA_ALTA = '#FF9800'  # Naranja para 60-79%
COLOR_PROBABILIDAD_MEDIA = '#FFC107'  # Amarillo para 40-59%
COLOR_PROBABILIDAD_BAJA = '#f44336'  # Rojo para menos de 40%

# ===== INSTRUCCIONES DE USO =====
"""
Para cambiar el número de preguntas:
1. Modifica TOTAL_PREGUNTAS (línea 7)
2. Reinicia el servidor backend

Para ajustar las probabilidades:
1. Modifica los valores de PROBABILIDAD_BASE, PROBABILIDAD_MINIMA, PROBABILIDAD_MAXIMA
2. Ajusta los bonus/penalizaciones de aprendizaje colaborativo
3. Reinicia el servidor backend

Para cambiar el número de recomendaciones:
1. MAX_REFRESCOS_RECOMENDADOS: Refrescos mostrados inicialmente
2. MAX_ALTERNATIVAS_RECOMENDADAS: Alternativas mostradas inicialmente
3. MAX_ALTERNATIVAS_SALUDABLES_INICIAL: Alternativas saludables iniciales
4. MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL: Alternativas saludables por click en "más opciones"
5. MAX_REFRESCOS_ADICIONALES: Refrescos adicionales por click para usuarios regulares
6. MAX_ALTERNATIVAS_USUARIO_SALUDABLE: Más alternativas para usuarios saludables
7. MAX_REFRESCOS_USUARIO_TRADICIONAL: Refrescos para usuarios tradicionales
8. Reinicia el servidor backend

Para cambiar mensajes del sistema:
1. Modifica las variables MENSAJE_*
2. Reinicia el servidor backend

Para cambiar colores de probabilidad:
1. Modifica las variables COLOR_PROBABILIDAD_*
2. Actualiza también los colores en el frontend (App.js función obtenerColorProbabilidad)
"""