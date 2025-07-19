"""
RefrescoBot ML - Servidor Principal
Sistema de recomendación de bebidas con Machine Learning real

Características:
- ML real con RandomForest y KMeans
- Recomendaciones personalizadas
- Aprendizaje desde ratings de usuarios
- Separación inteligente de refrescos vs alternativas
- Base de datos auto-limpiada en startup
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json
import random
from bson import ObjectId
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Añadir el directorio backend al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos locales
from config import *
from ml_engine import ml_engine
from data_manager import initialize_system_data
from beverage_categorizer import beverage_categorizer
from image_analyzer import image_analyzer
from presentation_rating_system import presentation_rating_system

# Cargar variables de entorno
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configuración de MongoDB
mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Crear aplicación FastAPI
app = FastAPI(title="RefrescoBot ML API", version="2.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory=str(ROOT_DIR / "static")), name="static")

# Modelos Pydantic
class SesionChat(BaseModel):
    session_id: str = ""
    respuestas: Dict[str, Any] = {}
    preguntas_mostradas: List[int] = []
    recomendaciones_mostradas: List[int] = []
    fecha_creacion: datetime = None
    completada: bool = False
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.session_id:
            self.session_id = str(uuid.uuid4())
        if not self.fecha_creacion:
            self.fecha_creacion = datetime.now()

class RespuestaUsuario(BaseModel):
    pregunta_id: int
    respuesta_id: int
    respuesta_texto: str
    tiempo_respuesta: Optional[float] = 0.0

class PuntuacionBebida(BaseModel):
    puntuacion: int
    comentario: Optional[str] = ""

class PuntuacionPresentacion(BaseModel):
    presentation_id: str
    puntuacion: int
    comentario: Optional[str] = ""

# Utilidades
def custom_json_serializer(obj):
    """Serializar ObjectId de MongoDB"""
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

class MongoJSONResponse(JSONResponse):
    """Respuesta JSON que maneja ObjectId de MongoDB"""
    def render(self, content: Any) -> bytes:
        return json.dumps(content, default=custom_json_serializer).encode("utf-8")

async def process_beverages_with_ml():
    """Procesa todas las bebidas con los nuevos módulos ML"""
    try:
        # Obtener todas las bebidas
        bebidas = await db.bebidas.find({}).to_list(None)
        logger.info(f"Procesando {len(bebidas)} bebidas con ML...")
        
        # Procesar con beverage categorizer
        processed_beverages = beverage_categorizer.process_all_beverages(bebidas)
        
        # Procesar imágenes de cada bebida
        for bebida in processed_beverages:
            try:
                image_analysis = image_analyzer.analyze_beverage_images(bebida)
                bebida['features_imagen'] = image_analysis
                
                # Categorizar cada presentación y añadir IDs únicos
                for i, presentacion in enumerate(bebida.get('presentaciones', [])):
                    if 'presentation_id' not in presentacion:
                        presentacion['presentation_id'] = f"{bebida['id']}_{presentacion.get('ml', i)}"
                    
                    # Añadir categorización automática a cada presentación
                    ml_size = beverage_categorizer.categorize_presentation_size(presentacion.get('ml', 0))
                    presentacion['categoria_ml'] = ml_size
                    
                logger.info(f"Procesado: {bebida['nombre']} - {len(bebida.get('presentaciones', []))} presentaciones")
                
            except Exception as e:
                logger.error(f"Error procesando imágenes de {bebida['nombre']}: {e}")
        
        # Actualizar bebidas en la base de datos
        for bebida in processed_beverages:
            await db.bebidas.update_one(
                {"id": bebida["id"]},
                {"$set": bebida}
            )
        
        logger.info("Procesamiento ML completado")
        
    except Exception as e:
        logger.error(f"Error en procesamiento ML: {e}")

# Eventos de la aplicación
@app.on_event("startup")
async def startup_event():
    """Inicializar sistema en startup"""
    logger.info("Iniciando RefrescoBot ML...")
    
    try:
        # Inicializar base de datos si está configurado
        if AUTO_CLEAN_DB_ON_STARTUP:
            logger.info("Inicializando base de datos desde archivos JSON...")
            await initialize_system_data(db, clean_first=True)
        
        # Procesar bebidas con ML automático (categorización e imágenes)
        logger.info("Procesando bebidas con ML avanzado...")
        await process_beverages_with_ml()
        
        # Verificar estado del ML engine
        stats = ml_engine.get_model_stats()
        logger.info(f"ML Engine iniciado: {stats}")
        
        # Verificar estado de los nuevos módulos ML
        categorizer_stats = beverage_categorizer.get_category_stats()
        image_stats = image_analyzer.get_analysis_stats()
        presentation_stats = presentation_rating_system.get_system_stats()
        
        logger.info(f"Beverage Categorizer: {categorizer_stats}")
        logger.info(f"Image Analyzer: {image_stats}")
        logger.info(f"Presentation Rating System: {presentation_stats}")
        
        logger.info("RefrescoBot ML iniciado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Guardar modelos ML en shutdown"""
    logger.info("Cerrando RefrescoBot ML...")
    
    try:
        # Guardar todos los modelos ML
        ml_engine.save_models()
        beverage_categorizer.save_models()
        image_analyzer.save_analysis_cache()
        presentation_rating_system.save_models()
        
        # Cerrar conexión a MongoDB
        client.close()
        
        logger.info("RefrescoBot ML cerrado exitosamente")
        
    except Exception as e:
        logger.error(f"Error en shutdown: {e}")

# Endpoints de la API
@app.post("/api/iniciar-sesion")
async def iniciar_sesion():
    """Inicia una nueva sesión de chat"""
    try:
        sesion = SesionChat()
        
        # Insertar en base de datos
        sesion_dict = sesion.dict()
        await db.sesiones_chat.insert_one(sesion_dict)
        
        logger.info(f"Nueva sesión iniciada: {sesion.session_id}")
        
        return {
            "sesion_id": sesion.session_id,
            "mensaje": "¡Hola! Soy RefrescoBot ML, tu asistente personal para encontrar la bebida perfecta. Te haré algunas preguntas para conocerte mejor."
        }
        
    except Exception as e:
        logger.error(f"Error iniciando sesión: {e}")
        raise HTTPException(status_code=500, detail="Error iniciando sesión")

@app.get("/api/pregunta-inicial/{sesion_id}")
async def obtener_pregunta_inicial(sesion_id: str):
    """Obtiene la pregunta fija inicial sobre consumo de refrescos"""
    try:
        # Verificar que la sesión existe
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Obtener pregunta fija
        pregunta_fija = await db.preguntas.find_one({"es_fija": True})
        if not pregunta_fija:
            raise HTTPException(status_code=404, detail="Pregunta inicial no encontrada")
        
        # Marcar pregunta como mostrada
        await db.sesiones_chat.update_one(
            {"session_id": sesion_id},
            {"$addToSet": {"preguntas_mostradas": pregunta_fija["id"]}}
        )
        
        return MongoJSONResponse(content={
            "pregunta": pregunta_fija,
            "numero_pregunta": 1,
            "total_preguntas": TOTAL_PREGUNTAS
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo pregunta inicial: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo pregunta")

@app.get("/api/siguiente-pregunta/{sesion_id}")
async def obtener_siguiente_pregunta(sesion_id: str):
    """Obtiene la siguiente pregunta aleatoria"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        preguntas_mostradas = sesion.get("preguntas_mostradas", [])
        
        # Verificar si ya se completaron todas las preguntas
        if len(preguntas_mostradas) >= TOTAL_PREGUNTAS:
            return {"finalizada": True, "mensaje": "Todas las preguntas completadas"}
        
        # Obtener preguntas disponibles (excluyendo las ya mostradas)
        preguntas_disponibles = await db.preguntas.find({
            "es_fija": False,
            "id": {"$nin": preguntas_mostradas}
        }).to_list(None)
        
        if not preguntas_disponibles:
            return {"finalizada": True, "mensaje": "No hay más preguntas disponibles"}
        
        # Seleccionar pregunta aleatoria
        pregunta_seleccionada = random.choice(preguntas_disponibles)
        
        # Marcar como mostrada
        await db.sesiones_chat.update_one(
            {"session_id": sesion_id},
            {"$addToSet": {"preguntas_mostradas": pregunta_seleccionada["id"]}}
        )
        
        numero_pregunta = len(preguntas_mostradas) + 1
        
        return MongoJSONResponse(content={
            "pregunta": pregunta_seleccionada,
            "numero_pregunta": numero_pregunta,
            "total_preguntas": TOTAL_PREGUNTAS
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo siguiente pregunta: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo pregunta")

@app.post("/api/responder/{sesion_id}")
async def responder_pregunta(sesion_id: str, respuesta: RespuestaUsuario):
    """Registra la respuesta del usuario a una pregunta"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Obtener información de la pregunta
        pregunta = await db.preguntas.find_one({"id": respuesta.pregunta_id})
        if not pregunta:
            raise HTTPException(status_code=404, detail="Pregunta no encontrada")
        
        # Encontrar la opción seleccionada
        opcion_seleccionada = None
        for opcion in pregunta["opciones"]:
            if opcion["id"] == respuesta.respuesta_id:
                opcion_seleccionada = opcion
                break
        
        if not opcion_seleccionada:
            raise HTTPException(status_code=400, detail="Opción de respuesta no válida")
        
        # Guardar respuesta en la sesión
        clave_respuesta = f"pregunta_{respuesta.pregunta_id}_{pregunta['categoria']}"
        respuesta_completa = {
            "pregunta_id": respuesta.pregunta_id,
            "pregunta_texto": pregunta["pregunta"],
            "respuesta_id": respuesta.respuesta_id,
            "respuesta_texto": respuesta.respuesta_texto,
            "respuesta_valor": opcion_seleccionada["valor"],
            "categoria": pregunta["categoria"],
            "peso_algoritmo": pregunta.get("peso_algoritmo", 1.0),
            "tiempo_respuesta": respuesta.tiempo_respuesta,
            "timestamp": datetime.now()
        }
        
        await db.sesiones_chat.update_one(
            {"session_id": sesion_id},
            {"$set": {f"respuestas.{clave_respuesta}": respuesta_completa}}
        )
        
        # Verificar si se completaron todas las preguntas
        sesion_actualizada = await db.sesiones_chat.find_one({"session_id": sesion_id})
        total_respondidas = len(sesion_actualizada["preguntas_mostradas"])
        
        if total_respondidas >= TOTAL_PREGUNTAS:
            await db.sesiones_chat.update_one(
                {"session_id": sesion_id},
                {"$set": {"completada": True}}
            )
            return {"mensaje": "Respuesta registrada. ¡Listo para las recomendaciones!", "completada": True}
        else:
            return {"mensaje": "Respuesta registrada", "completada": False}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando respuesta: {e}")
        raise HTTPException(status_code=500, detail="Error registrando respuesta")

@app.get("/api/recomendacion/{sesion_id}")
async def obtener_recomendaciones(sesion_id: str):
    """Obtiene recomendaciones ML personalizadas para el usuario"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        if not sesion.get("completada", False):
            raise HTTPException(status_code=400, detail="Sesión no completada")
        
        respuestas = sesion.get("respuestas", {})
        if not respuestas:
            raise HTTPException(status_code=400, detail="No hay respuestas registradas")
        
        # Obtener todas las bebidas
        bebidas = await db.bebidas.find({}).to_list(None)
        if not bebidas:
            raise HTTPException(status_code=404, detail="No hay bebidas disponibles")
        
        # Preparar respuestas para ML
        user_responses = {}
        tiempo_respuestas = []
        for key, respuesta in respuestas.items():
            user_responses[respuesta["categoria"]] = respuesta["respuesta_valor"]
            if "tiempo_respuesta" in respuesta:
                tiempo_respuestas.append(respuesta["tiempo_respuesta"])
        user_responses["session_id"] = sesion_id
        
        # Determinar cluster de usuario ANTES de usarlo
        cluster_usuario = ml_engine.get_user_cluster(user_responses)
        
        # Calcular predicciones ML para cada bebida con tiempos de respuesta
        bebidas_con_prediccion = []
        for bebida in bebidas:
            try:
                prediccion = ml_engine.predict_preference(user_responses, bebida, tiempo_respuestas)
                bebida_con_pred = bebida.copy()
                bebida_con_pred["prediccion_ml"] = prediccion
                bebida_con_pred["probabilidad"] = min(95.0, max(5.0, prediccion * 20))  # Convertir a 0-100
                bebidas_con_prediccion.append(bebida_con_pred)
            except Exception as e:
                logger.warning(f"Error prediciendo para bebida {bebida['nombre']}: {e}")
                bebida_con_pred = bebida.copy()
                bebida_con_pred["prediccion_ml"] = 3.0
                bebida_con_pred["probabilidad"] = 60.0
                bebidas_con_prediccion.append(bebida_con_pred)
        
        # Determinar tipo de usuario basado en consumo de refrescos  
        usuario_no_consume_refrescos = False
        usuario_prefiere_alternativas = False
        
        for key, respuesta in respuestas.items():
            if "consumo_base" in respuesta.get("categoria", ""):
                valor = respuesta.get("respuesta_valor", "")
                # Usuarios que NO consumen refrescos (solo alternativas)
                if valor in ["no_consume_refrescos"]:
                    usuario_no_consume_refrescos = True
                # Usuarios que prefieren alternativas pero consumen refrescos ocasionalmente
                elif valor in ["prefiere_alternativas"]:
                    usuario_prefiere_alternativas = True
                break
        
        # Separar refrescos reales de alternativas
        refrescos_reales = [b for b in bebidas_con_prediccion if b["es_refresco_real"]]
        alternativas = [b for b in bebidas_con_prediccion if not b["es_refresco_real"]]
        
        # Lógica especial para diferentes tipos de usuarios
        if usuario_no_consume_refrescos:
            # Solo mostrar alternativas saludables, ordenadas por predicción
            alternativas.sort(key=lambda x: x["prediccion_ml"], reverse=True)
            top_refrescos = []  # No mostrar refrescos reales
            top_alternativas = alternativas[:MAX_ALTERNATIVAS_USUARIO_SALUDABLE]  # Más alternativas para usuarios saludables
            mostrar_alternativas = True
            mensaje_principal = MENSAJE_NO_REFRESCOS
        elif usuario_prefiere_alternativas:
            # Usuario prefiere alternativas pero ocasionalmente consume refrescos
            # Mostrar SOLO alternativas inicialmente, pero permitir refrescos en "más opciones"
            alternativas.sort(key=lambda x: x["prediccion_ml"], reverse=True)
            top_refrescos = []  # No mostrar refrescos inicialmente
            top_alternativas = alternativas[:MAX_ALTERNATIVAS_SALUDABLES_INICIAL * 2]  # Más alternativas
            mostrar_alternativas = True
            mensaje_principal = "Te recomendamos estas alternativas saludables (si quieres refrescos, presiona 'más opciones'):"
        else:
            # Usuario regular: determinar si mostrar alternativas o solo refrescos
            refrescos_reales.sort(key=lambda x: x["prediccion_ml"], reverse=True)
            alternativas.sort(key=lambda x: x["prediccion_ml"], reverse=True)
            
            # ¿Debe mostrar alternativas en lugar de refrescos?
            mostrar_alternativas = determinar_mostrar_alternativas(user_responses, cluster_usuario)
            
            if mostrar_alternativas:
                # Usuario consciente de salud: mostrar SOLO alternativas
                top_refrescos = []
                top_alternativas = alternativas[:MAX_ALTERNATIVAS_SALUDABLES_INICIAL]
                mensaje_principal = "Basado en tu perfil saludable, aquí están tus alternativas recomendadas:"
            else:
                # Usuario tradicional: solo refrescos
                top_refrescos = refrescos_reales[:MAX_REFRESCOS_RECOMENDADOS]
                top_alternativas = []
                mensaje_principal = MENSAJE_REFRESCOS_NORMALES
        
        # Generar explicaciones ML
        for bebida in top_refrescos + top_alternativas:
            bebida["factores_explicativos"] = generar_explicacion_ml(user_responses, bebida)
            
            # Añadir información de categorización automática
            bebida["categorias_automaticas"] = bebida.get("categorias_ml", [])
            bebida["tags_ml"] = bebida.get("tags_automaticos", [])
            
            # Añadir información de las mejores presentaciones para esta bebida
            if bebida.get("presentaciones"):
                mejor_presentacion = None
                mejor_score = 0
                
                for presentacion in bebida["presentaciones"]:
                    try:
                        pred_presentacion = presentation_rating_system.predict_presentation_rating(
                            presentacion, bebida, user_responses
                        )
                        score = pred_presentacion.get("predicted_rating", 3.0) * pred_presentacion.get("confidence", 0.5)
                        
                        if score > mejor_score:
                            mejor_score = score
                            mejor_presentacion = {
                                "presentation_id": presentacion.get("presentation_id"),
                                "ml": presentacion.get("ml"),
                                "precio": presentacion.get("precio"),
                                "categoria": presentacion.get("categoria_presentacion"),
                                "prediccion": pred_presentacion
                            }
                    except Exception as e:
                        logger.warning(f"Error prediciendo presentación: {e}")
                
                if mejor_presentacion:
                    bebida["mejor_presentacion_para_usuario"] = mejor_presentacion
        
        # Actualizar recomendaciones mostradas
        ids_recomendadas = [b["id"] for b in top_refrescos + top_alternativas]
        await db.sesiones_chat.update_one(
            {"session_id": sesion_id},
            {"$set": {"recomendaciones_mostradas": ids_recomendadas}}
        )
        
        return MongoJSONResponse(content={
            "refrescos_reales": top_refrescos,
            "bebidas_alternativas": top_alternativas if mostrar_alternativas else [],
            "mostrar_alternativas": mostrar_alternativas,
            "cluster_usuario": cluster_usuario,
            "mensaje_refrescos": mensaje_principal,
            "mensaje_alternativas": MENSAJE_ALTERNATIVAS_SALUDABLES,
            "usuario_no_consume_refrescos": usuario_no_consume_refrescos,
            "criterios_ml": {
                "modelo_entrenado": ml_engine.is_trained,
                "muestras_entrenamiento": len(ml_engine.training_data),
                "cluster_usuario": cluster_usuario,
                "tiempo_promedio_respuesta": sum(tiempo_respuestas) / len(tiempo_respuestas) if tiempo_respuestas else 0,
                "tipo_usuario_detectado": ml_engine.detectar_tipo_usuario(user_responses, tiempo_respuestas)
            },
            "ml_avanzado": {
                "categorizacion_automatica": beverage_categorizer.get_category_stats(),
                "analisis_imagenes": image_analyzer.get_analysis_stats(),
                "sistema_presentaciones": presentation_rating_system.get_system_stats(),
                "total_bebidas_categorizadas": len([b for b in bebidas if b.get("procesado_ml", False)]),
                "mensaje_ml": "Sistema ML avanzado activado: categorización automática, análisis de imágenes y recomendaciones por presentación específica"
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando recomendaciones: {e}")
        raise HTTPException(status_code=500, detail="Error generando recomendaciones")

@app.post("/api/puntuar/{sesion_id}/{bebida_id}")
async def puntuar_bebida(sesion_id: str, bebida_id: int, puntuacion: PuntuacionBebida):
    """Registra la puntuación del usuario y entrena el modelo ML"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Verificar bebida
        bebida = await db.bebidas.find_one({"id": bebida_id})
        if not bebida:
            raise HTTPException(status_code=404, detail="Bebida no encontrada")
        
        # Validar puntuación
        if not 1 <= puntuacion.puntuacion <= 5:
            raise HTTPException(status_code=400, detail="Puntuación debe estar entre 1 y 5")
        
        # Registrar puntuación en base de datos
        puntuacion_doc = {
            "session_id": sesion_id,
            "bebida_id": bebida_id,
            "puntuacion": puntuacion.puntuacion,
            "comentario": puntuacion.comentario,
            "timestamp": datetime.now()
        }
        
        await db.puntuaciones.insert_one(puntuacion_doc)
        
        # Actualizar estadísticas de la bebida
        await actualizar_estadisticas_bebida(bebida_id, puntuacion.puntuacion)
        
        # Añadir datos de entrenamiento al ML engine
        respuestas = sesion.get("respuestas", {})
        user_responses = {}
        for key, respuesta in respuestas.items():
            user_responses[respuesta["categoria"]] = respuesta["respuesta_valor"]
        user_responses["session_id"] = sesion_id
        
        ml_engine.add_training_data(user_responses, bebida, puntuacion.puntuacion)
        
        # Intentar re-entrenar si hay suficientes datos
        retrained = ml_engine.retrain_if_needed(ML_RETRAIN_THRESHOLD)
        
        # Generar feedback para el usuario
        feedback = generar_feedback_puntuacion(puntuacion.puntuacion, bebida, retrained)
        
        return {
            "mensaje": "Puntuación registrada exitosamente",
            "feedback_aprendizaje": feedback,
            "modelo_reentrenado": retrained,
            "stats_ml": ml_engine.get_model_stats()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando puntuación: {e}")
        raise HTTPException(status_code=500, detail="Error registrando puntuación")

@app.post("/api/puntuar-presentacion/{sesion_id}")
async def puntuar_presentacion(sesion_id: str, puntuacion: PuntuacionPresentacion):
    """Registra la puntuación específica de una presentación y entrena el modelo ML"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Validar puntuación
        if not 1 <= puntuacion.puntuacion <= 5:
            raise HTTPException(status_code=400, detail="Puntuación debe estar entre 1 y 5")
        
        # Encontrar la bebida y presentación específica
        bebida = None
        presentacion_especifica = None
        bebidas = await db.bebidas.find({}).to_list(None)
        
        for b in bebidas:
            for p in b.get('presentaciones', []):
                if p.get('presentation_id') == puntuacion.presentation_id:
                    bebida = b
                    presentacion_especifica = p
                    break
            if bebida:
                break
        
        if not bebida or not presentacion_especifica:
            raise HTTPException(status_code=404, detail="Presentación no encontrada")
        
        # Registrar puntuación específica por presentación
        puntuacion_doc = {
            "session_id": sesion_id,
            "bebida_id": bebida["id"],
            "presentation_id": puntuacion.presentation_id,
            "puntuacion": puntuacion.puntuacion,
            "comentario": puntuacion.comentario,
            "ml": presentacion_especifica.get("ml"),
            "precio": presentacion_especifica.get("precio"),
            "timestamp": datetime.now()
        }
        
        await db.puntuaciones_presentacion.insert_one(puntuacion_doc)
        
        # Actualizar estadísticas de la presentación específica
        await actualizar_estadisticas_presentacion(puntuacion.presentation_id, puntuacion.puntuacion)
        
        # Preparar respuestas del usuario
        respuestas = sesion.get("respuestas", {})
        user_responses = {}
        for key, respuesta in respuestas.items():
            user_responses[respuesta["categoria"]] = respuesta["respuesta_valor"]
        user_responses["session_id"] = sesion_id
        
        # Añadir datos al sistema de puntuación por presentación
        presentation_rating_system.add_presentation_rating(
            presentation_id=puntuacion.presentation_id,
            user_responses=user_responses,
            beverage=bebida,
            presentation=presentacion_especifica,
            rating=float(puntuacion.puntuacion),
            context={"timestamp": datetime.now().isoformat()}
        )
        
        # Entrenar modelo si hay suficientes datos
        trained = presentation_rating_system.train_models()
        
        # También añadir al ML engine principal
        ml_engine.add_training_data(user_responses, bebida, puntuacion.puntuacion)
        retrained_main = ml_engine.retrain_if_needed(ML_RETRAIN_THRESHOLD)
        
        # Generar feedback específico por presentación
        feedback = generar_feedback_presentacion(
            puntuacion.puntuacion, bebida, presentacion_especifica, trained
        )
        
        return {
            "mensaje": "Puntuación de presentación registrada exitosamente",
            "feedback_aprendizaje": feedback,
            "presentation_model_trained": trained,
            "main_model_retrained": retrained_main,
            "presentation_stats": presentation_rating_system.get_system_stats(),
            "main_ml_stats": ml_engine.get_model_stats()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registrando puntuación de presentación: {e}")
        raise HTTPException(status_code=500, detail="Error registrando puntuación")

@app.get("/api/recomendaciones-alternativas/{sesion_id}")
async def obtener_mas_recomendaciones(sesion_id: str):
    """Obtiene recomendaciones adicionales usando ML respetando la categorización saludable vs refrescos"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        if not sesion.get("completada", False):
            raise HTTPException(status_code=400, detail="Sesión no completada")
        
        recomendaciones_ya_mostradas = sesion.get("recomendaciones_mostradas", [])
        
        # Preparar respuestas para ML
        respuestas = sesion.get("respuestas", {})
        user_responses = {}
        tiempo_respuestas = []
        for key, respuesta in respuestas.items():
            user_responses[respuesta["categoria"]] = respuesta["respuesta_valor"]
            if "tiempo_respuesta" in respuesta:
                tiempo_respuestas.append(respuesta["tiempo_respuesta"])
        user_responses["session_id"] = sesion_id
        
        # Determinar tipo de usuario basado en consumo de refrescos  
        usuario_no_consume_refrescos = False
        usuario_prefiere_alternativas = False
        
        for key, respuesta in respuestas.items():
            if "consumo_base" in respuesta.get("categoria", ""):
                valor = respuesta.get("respuesta_valor", "")
                # Usuarios que NO consumen refrescos (solo alternativas)
                if valor in ["no_consume_refrescos"]:
                    usuario_no_consume_refrescos = True
                # Usuarios que prefieren alternativas pero consumen refrescos ocasionalmente
                elif valor in ["prefiere_alternativas"]:
                    usuario_prefiere_alternativas = True
                break
        
        # Determinar si debe mostrar alternativas basado en la lógica original
        cluster_usuario = ml_engine.get_user_cluster(user_responses)
        mostrar_alternativas = determinar_mostrar_alternativas(user_responses, cluster_usuario)
        
        # Obtener todas las bebidas disponibles
        bebidas_disponibles = await db.bebidas.find({
            "id": {"$nin": recomendaciones_ya_mostradas}
        }).to_list(None)
        
        if not bebidas_disponibles:
            return {
                "recomendaciones_adicionales": [],
                "sin_mas_opciones": True,
                "mensaje": MENSAJE_SIN_ALTERNATIVAS
            }
        
        # Separar bebidas por tipo
        refrescos_disponibles = [b for b in bebidas_disponibles if b.get("es_refresco_real", True)]
        alternativas_disponibles = [b for b in bebidas_disponibles if not b.get("es_refresco_real", True)]
        
        # Calcular predicciones ML para refrescos
        refrescos_con_prediccion = []
        for bebida in refrescos_disponibles:
            try:
                prediccion = ml_engine.predict_preference(user_responses, bebida, tiempo_respuestas)
                bebida_con_pred = bebida.copy()
                bebida_con_pred["prediccion_ml"] = prediccion
                bebida_con_pred["probabilidad"] = min(95.0, max(5.0, prediccion * 20))
                bebida_con_pred["factores_explicativos"] = generar_explicacion_ml(user_responses, bebida)
                
                # Añadir información de categorización automática
                bebida_con_pred["categorias_automaticas"] = bebida.get("categorias_ml", [])
                bebida_con_pred["tags_ml"] = bebida.get("tags_automaticos", [])
                
                refrescos_con_prediccion.append(bebida_con_pred)
            except Exception as e:
                logger.warning(f"Error prediciendo para refresco {bebida['nombre']}: {e}")
        
        # Calcular predicciones ML para alternativas
        alternativas_con_prediccion = []
        for bebida in alternativas_disponibles:
            try:
                prediccion = ml_engine.predict_preference(user_responses, bebida, tiempo_respuestas)
                bebida_con_pred = bebida.copy()
                bebida_con_pred["prediccion_ml"] = prediccion
                bebida_con_pred["probabilidad"] = min(95.0, max(5.0, prediccion * 20))
                bebida_con_pred["factores_explicativos"] = generar_explicacion_ml(user_responses, bebida)
                
                # Añadir información de categorización automática
                bebida_con_pred["categorias_automaticas"] = bebida.get("categorias_ml", [])
                bebida_con_pred["tags_ml"] = bebida.get("tags_automaticos", [])
                
                alternativas_con_prediccion.append(bebida_con_pred)
            except Exception as e:
                logger.warning(f"Error prediciendo para alternativa {bebida['nombre']}: {e}")
        
        # Ordenar por predicción ML
        refrescos_con_prediccion.sort(key=lambda x: x["prediccion_ml"], reverse=True)
        alternativas_con_prediccion.sort(key=lambda x: x["prediccion_ml"], reverse=True)
        
        # Lógica específica por tipo de usuario
        if usuario_no_consume_refrescos:
            # Usuario que no consume refrescos: SOLO mostrar más alternativas saludables
            top_adicionales = alternativas_con_prediccion[:MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL]
            mensaje_tipo = "Más opciones saludables perfectas para ti:"
            tipo_recomendaciones = "alternativas_saludables"
        elif usuario_prefiere_alternativas:
            # Usuario que prefiere alternativas: primer click muestra refrescos, siguientes más alternativas
            recomendaciones_previas = sesion.get("recomendaciones_adicionales_obtenidas", 0)
            if recomendaciones_previas == 0:
                # Primera vez: mostrar refrescos para dar opción
                top_adicionales = refrescos_con_prediccion[:MAX_REFRESCOS_ADICIONALES]
                mensaje_tipo = "Si cambias de opinión, aquí tienes algunos refrescos:"
                tipo_recomendaciones = "refrescos_opcionales"
            else:
                # Siguientes veces: más alternativas
                top_adicionales = alternativas_con_prediccion[:MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL]
                mensaje_tipo = "Más alternativas saludables:"
                tipo_recomendaciones = "alternativas_saludables"
        elif mostrar_alternativas:
            # Usuario regular que debe ver alternativas: mostrar MÁS alternativas
            top_adicionales = alternativas_con_prediccion[:MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL]
            mensaje_tipo = "Más alternativas saludables basadas en tus preferencias:"
            tipo_recomendaciones = "alternativas_saludables"
        else:
            # Usuario regular tradicional: mostrar MÁS refrescos
            top_adicionales = refrescos_con_prediccion[:MAX_REFRESCOS_ADICIONALES]
            mensaje_tipo = "Más refrescos que podrían gustarte:"
            tipo_recomendaciones = "refrescos_tradicionales"
        
        # Si no hay opciones del tipo determinado, intentar mostrar del otro tipo con mensaje explicativo
        if not top_adicionales:
            if tipo_recomendaciones == "alternativas_saludables" and refrescos_con_prediccion:
                top_adicionales = refrescos_con_prediccion[:MAX_REFRESCOS_ADICIONALES]
                mensaje_tipo = "No hay más alternativas saludables, pero aquí tienes otros refrescos:"
                tipo_recomendaciones = "refrescos_adicionales"
            elif tipo_recomendaciones == "refrescos_tradicionales" and alternativas_con_prediccion:
                top_adicionales = alternativas_con_prediccion[:MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL]
                mensaje_tipo = "No hay más refrescos tradicionales, pero aquí tienes alternativas saludables:"
                tipo_recomendaciones = "alternativas_adicionales"
        
        # Actualizar recomendaciones mostradas y contador de clicks
        if top_adicionales:
            nuevos_ids = [b["id"] for b in top_adicionales]
            await db.sesiones_chat.update_one(
                {"session_id": sesion_id},
                {
                    "$addToSet": {"recomendaciones_mostradas": {"$each": nuevos_ids}},
                    "$inc": {"recomendaciones_adicionales_obtenidas": 1}
                }
            )
        
        return MongoJSONResponse(content={
            "recomendaciones_adicionales": top_adicionales,
            "sin_mas_opciones": len(top_adicionales) == 0,
            "mensaje": mensaje_tipo if top_adicionales else MENSAJE_SIN_ALTERNATIVAS,
            "tipo_recomendaciones": tipo_recomendaciones,
            "usuario_no_consume_refrescos": usuario_no_consume_refrescos,
            "mostrar_alternativas": mostrar_alternativas,
            "estadisticas": {
                "refrescos_disponibles": len(refrescos_disponibles),
                "alternativas_disponibles": len(alternativas_disponibles),
                "total_recomendadas": len(top_adicionales)
            },
            "ml_info": {
                "cluster_usuario": cluster_usuario,
                "tipo_usuario_detectado": ml_engine.detectar_tipo_usuario(user_responses, tiempo_respuestas)
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo recomendaciones adicionales: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo recomendaciones")

@app.get("/api/mas-refrescos/{sesion_id}")
async def obtener_mas_refrescos(sesion_id: str):
    """Obtiene más refrescos específicamente"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        if not sesion.get("completada", False):
            raise HTTPException(status_code=400, detail="Sesión no completada")
        
        recomendaciones_ya_mostradas = sesion.get("recomendaciones_mostradas", [])
        
        # Preparar respuestas para ML
        respuestas = sesion.get("respuestas", {})
        user_responses = {}
        tiempo_respuestas = []
        for key, respuesta in respuestas.items():
            user_responses[respuesta["categoria"]] = respuesta["respuesta_valor"]
            if "tiempo_respuesta" in respuesta:
                tiempo_respuestas.append(respuesta["tiempo_respuesta"])
        user_responses["session_id"] = sesion_id
        
        # Obtener SOLO refrescos reales no mostrados
        refrescos_disponibles = await db.bebidas.find({
            "id": {"$nin": recomendaciones_ya_mostradas},
            "es_refresco_real": True
        }).to_list(None)
        
        if not refrescos_disponibles:
            return {
                "mas_refrescos": [],
                "sin_mas_opciones": True,
                "mensaje": "No hay más refrescos disponibles para mostrar"
            }
        
        # Calcular predicciones ML
        refrescos_con_prediccion = []
        for bebida in refrescos_disponibles:
            try:
                prediccion = ml_engine.predict_preference(user_responses, bebida, tiempo_respuestas)
                bebida_con_pred = bebida.copy()
                bebida_con_pred["prediccion_ml"] = prediccion
                bebida_con_pred["probabilidad"] = min(95.0, max(5.0, prediccion * 20))
                bebida_con_pred["factores_explicativos"] = generar_explicacion_ml(user_responses, bebida)
                bebida_con_pred["categorias_automaticas"] = bebida.get("categorias_ml", [])
                bebida_con_pred["tags_ml"] = bebida.get("tags_automaticos", [])
                refrescos_con_prediccion.append(bebida_con_pred)
            except Exception as e:
                logger.warning(f"Error prediciendo para refresco {bebida['nombre']}: {e}")
        
        # Ordenar por predicción ML
        refrescos_con_prediccion.sort(key=lambda x: x["prediccion_ml"], reverse=True)
        
        # Seleccionar top refrescos adicionales
        top_refrescos = refrescos_con_prediccion[:MAX_REFRESCOS_ADICIONALES]
        
        # Actualizar recomendaciones mostradas
        if top_refrescos:
            nuevos_ids = [b["id"] for b in top_refrescos]
            await db.sesiones_chat.update_one(
                {"session_id": sesion_id},
                {"$addToSet": {"recomendaciones_mostradas": {"$each": nuevos_ids}}}
            )
        
        return MongoJSONResponse(content={
            "mas_refrescos": top_refrescos,
            "sin_mas_opciones": len(top_refrescos) == 0,
            "mensaje": "Más refrescos tradicionales basados en tus preferencias:" if top_refrescos else "No hay más refrescos disponibles",
            "tipo": "refrescos_tradicionales"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo más refrescos: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo más refrescos")

@app.get("/api/mas-alternativas/{sesion_id}")
async def obtener_mas_alternativas(sesion_id: str):
    """Obtiene más alternativas saludables específicamente"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        if not sesion.get("completada", False):
            raise HTTPException(status_code=400, detail="Sesión no completada")
        
        recomendaciones_ya_mostradas = sesion.get("recomendaciones_mostradas", [])
        
        # Preparar respuestas para ML
        respuestas = sesion.get("respuestas", {})
        user_responses = {}
        tiempo_respuestas = []
        for key, respuesta in respuestas.items():
            user_responses[respuesta["categoria"]] = respuesta["respuesta_valor"]
            if "tiempo_respuesta" in respuesta:
                tiempo_respuestas.append(respuesta["tiempo_respuesta"])
        user_responses["session_id"] = sesion_id
        
        # Obtener SOLO alternativas saludables no mostradas
        alternativas_disponibles = await db.bebidas.find({
            "id": {"$nin": recomendaciones_ya_mostradas},
            "es_refresco_real": False
        }).to_list(None)
        
        if not alternativas_disponibles:
            return {
                "mas_alternativas": [],
                "sin_mas_opciones": True,
                "mensaje": "No hay más alternativas saludables disponibles para mostrar"
            }
        
        # Calcular predicciones ML
        alternativas_con_prediccion = []
        for bebida in alternativas_disponibles:
            try:
                prediccion = ml_engine.predict_preference(user_responses, bebida, tiempo_respuestas)
                bebida_con_pred = bebida.copy()
                bebida_con_pred["prediccion_ml"] = prediccion
                bebida_con_pred["probabilidad"] = min(95.0, max(5.0, prediccion * 20))
                bebida_con_pred["factores_explicativos"] = generar_explicacion_ml(user_responses, bebida)
                bebida_con_pred["categorias_automaticas"] = bebida.get("categorias_ml", [])
                bebida_con_pred["tags_ml"] = bebida.get("tags_automaticos", [])
                alternativas_con_prediccion.append(bebida_con_pred)
            except Exception as e:
                logger.warning(f"Error prediciendo para alternativa {bebida['nombre']}: {e}")
        
        # Ordenar por predicción ML
        alternativas_con_prediccion.sort(key=lambda x: x["prediccion_ml"], reverse=True)
        
        # Seleccionar top alternativas adicionales
        top_alternativas = alternativas_con_prediccion[:MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL]
        
        # Actualizar recomendaciones mostradas
        if top_alternativas:
            nuevos_ids = [b["id"] for b in top_alternativas]
            await db.sesiones_chat.update_one(
                {"session_id": sesion_id},
                {"$addToSet": {"recomendaciones_mostradas": {"$each": nuevos_ids}}}
            )
        
        return MongoJSONResponse(content={
            "mas_alternativas": top_alternativas,
            "sin_mas_opciones": len(top_alternativas) == 0,
            "mensaje": "Más alternativas saludables perfectas para ti:" if top_alternativas else "No hay más alternativas saludables disponibles",
            "tipo": "alternativas_saludables"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo más alternativas: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo más alternativas")

@app.get("/api/mejores-presentaciones/{sesion_id}")
async def obtener_mejores_presentaciones(sesion_id: str, limit: int = 10):
    """Obtiene las mejores presentaciones específicas para el usuario"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        if not sesion.get("completada", False):
            raise HTTPException(status_code=400, detail="Sesión no completada")
        
        # Preparar respuestas del usuario
        respuestas = sesion.get("respuestas", {})
        user_responses = {}
        for key, respuesta in respuestas.items():
            user_responses[respuesta["categoria"]] = respuesta["respuesta_valor"]
        user_responses["session_id"] = sesion_id
        
        # Obtener todas las bebidas
        bebidas = await db.bebidas.find({}).to_list(None)
        
        # Determinar tipo de usuario basado en consumo de refrescos  
        usuario_no_consume_refrescos = False
        usuario_prefiere_alternativas = False
        
        for key, respuesta in respuestas.items():
            if "consumo_base" in respuesta.get("categoria", ""):
                valor = respuesta.get("respuesta_valor", "")
                # Usuarios que NO consumen refrescos (solo alternativas)
                if valor in ["no_consume_refrescos"]:
                    usuario_no_consume_refrescos = True
                # Usuarios que prefieren alternativas pero consumen refrescos ocasionalmente
                elif valor in ["prefiere_alternativas"]:
                    usuario_prefiere_alternativas = True
                break
        
        # Filtrar bebidas según el tipo de usuario
        if usuario_no_consume_refrescos:
            bebidas_filtradas = [b for b in bebidas if not b.get("es_refresco_real", True)]
        else:
            bebidas_filtradas = bebidas
        
        # Obtener mejores presentaciones usando el sistema especializado
        mejores_presentaciones = presentation_rating_system.get_best_presentations_for_user(
            bebidas_filtradas, user_responses, limit
        )
        
        # Enriquecer con información adicional
        presentaciones_enriquecidas = []
        for item in mejores_presentaciones:
            bebida = item['beverage']
            presentacion = item['presentation']
            prediccion = item['prediction']
            
            # Añadir factores explicativos específicos de la presentación
            factores_explicativos = generar_explicacion_presentacion(
                user_responses, bebida, presentacion, prediccion
            )
            
            presentacion_enriquecida = {
                "bebida": bebida,
                "presentacion": presentacion,
                "prediccion_ml": prediccion,
                "factores_explicativos": factores_explicativos,
                "match_score": item['combined_score'],
                "recomendacion_tipo": "saludable" if not bebida.get("es_refresco_real", True) else "refresco"
            }
            
            presentaciones_enriquecidas.append(presentacion_enriquecida)
        
        return MongoJSONResponse(content={
            "mejores_presentaciones": presentaciones_enriquecidas,
            "total_encontradas": len(mejores_presentaciones),
            "usuario_tipo": "no_consume_refrescos" if usuario_no_consume_refrescos else "regular",
            "mensaje": f"Aquí tienes las {len(presentaciones_enriquecidas)} mejores presentaciones específicas para ti",
            "sistema_ml": {
                "presentation_model_trained": presentation_rating_system.is_trained,
                "confidence_level": "alta" if presentation_rating_system.is_trained else "media"
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo mejores presentaciones: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo presentaciones")

# Funciones auxiliares
def generar_explicacion_ml(user_responses: Dict, bebida: Dict) -> List[str]:
    """Genera explicaciones basadas en predicciones ML"""
    explicaciones = []
    
    # Convertir respuestas a string para análisis Y también extraer valores directos
    response_str = str(user_responses.values()).lower()
    response_values = []
    categories = {}
    
    # Extraer valores y categorías de respuestas
    for key, value in user_responses.items():
        if isinstance(value, str):
            response_values.append(value.lower())
            if key != "session_id":
                categories[key] = value.lower()
        elif isinstance(value, dict) and "respuesta_valor" in value:
            response_values.append(value["respuesta_valor"].lower())
            categories[value.get("categoria", key)] = value["respuesta_valor"].lower()
    
    response_text = " ".join(response_values)
    
    print(f"DEBUG - response_text: {response_text}")  # Para debugging
    print(f"DEBUG - categories: {categories}")  # Para debugging
    
    # 1. Análisis de consumo de refrescos (primera pregunta más crítica)
    consumo_nivel = categories.get("consumo_base", "")
    if "nunca" in consumo_nivel or "casi nunca" in response_text:
        if not bebida.get("es_refresco_real", True):
            explicaciones.append("Perfecta para ti que prefieres evitar los refrescos tradicionales")
        else:
            explicaciones.append("Aunque evitas refrescos, esta podría ser una excepción especial")
    elif "diario" in consumo_nivel or "frecuente" in consumo_nivel or "varias veces" in response_text:
        if bebida.get("es_refresco_real", True):
            explicaciones.append("Ideal para tu consumo habitual de refrescos")
    
    # 2. Análisis de actividad física
    actividad = categories.get("fisico", "")
    if "muy_activo" in actividad or "activo" in actividad or "activo" in response_text:
        if bebida.get("es_energizante", False):
            explicaciones.append("Perfecta para complementar tu estilo de vida activo")
        elif not bebida.get("es_refresco_real", True):
            explicaciones.append("Excelente opción saludable para deportistas como tú")
        elif bebida.get("contenido_calorias") in ["bajo", "muy_bajo"]:
            explicaciones.append("Buena opción baja en calorías para personas activas")
    elif "sedentario" in actividad or "inactivo" in actividad:
        if bebida.get("es_refresco_real", True):
            explicaciones.append("Una opción clásica perfecta para tus momentos de relajación")
    
    # 3. Análisis de preferencias de dulzura
    nivel_dulzura = bebida.get("nivel_dulzura", 5)
    preferencias = categories.get("preferencias", "")
    if "muy_dulce" in preferencias or "dulce_moderado" in preferencias or "dulce" in response_text:
        if nivel_dulzura >= 7:
            explicaciones.append("Coincide perfectamente con tu preferencia por sabores dulces")
        elif nivel_dulzura >= 5:
            explicaciones.append("Un buen equilibrio de dulzura para tu paladar")
    elif "natural" in preferencias or "poco_dulce" in preferencias or "sin azúcar" in response_text:
        if nivel_dulzura <= 3:
            explicaciones.append("Ideal para tu preferencia por sabores naturales y menos dulces")
        elif not bebida.get("es_refresco_real", True):
            explicaciones.append("Una opción más natural que se adapta a tus gustos")
    
    # 4. Análisis de importancia de la salud
    if "muy_importante" in response_text or "importante" in response_text:
        if not bebida.get("es_refresco_real", True):
            explicaciones.append("Excelente elección saludable que cuida tu bienestar")
        elif bebida.get("contenido_calorias") in ["bajo", "muy_bajo"]:
            explicaciones.append("Una opción más ligera considerando tu interés por la salud")
    
    # 5. Análisis de estilo de vida
    estado_animo = categories.get("estado_animo", "")
    if "estresante" in estado_animo or "ocupado" in estado_animo or "estrés" in response_text:
        if bebida.get("es_energizante", False):
            explicaciones.append("Te dará la energía extra que necesitas en tu día ocupado")
        elif bebida.get("categoria") == "tes":
            explicaciones.append("Perfecta para relajarte después de un día estresante")
        elif bebida.get("categoria") == "cola":
            explicaciones.append("Un clásico reconfortante para momentos intensos")
    elif "relajado" in estado_animo or "tranquilo" in estado_animo:
        if bebida.get("categoria") in ["agua", "tes", "jugos"]:
            explicaciones.append("Se adapta perfectamente a tu estilo de vida tranquilo")
        else:
            explicaciones.append("Una opción que puedes disfrutar sin prisa")
    
    # 6. Análisis por categoría de bebida (siempre añadir una explicación sobre la bebida)
    categoria = bebida.get("categoria", "")
    nombre = bebida.get("nombre", "")
    
    if categoria == "cola":
        explicaciones.append("Un clásico atemporal que nunca pasa de moda")
    elif categoria == "citricos":
        explicaciones.append("Refrescante y con ese toque cítrico que revitaliza")
    elif categoria == "frutales":
        explicaciones.append("Sabor frutal que aporta dulzura natural")
    elif categoria == "energeticas":
        explicaciones.append("Te dará el impulso extra cuando lo necesites")
    elif categoria == "agua":
        explicaciones.append("La opción más pura y esencial para hidratarte")
    elif categoria == "jugos":
        explicaciones.append("Delicioso sabor natural con beneficios nutricionales")
    elif categoria == "tes":
        explicaciones.append("Una opción relajante con beneficios para la salud")
    
    # 7. Análisis de predicción ML
    prediccion = bebida.get('prediccion_ml', 3.0)
    if prediccion >= 4.5:
        explicaciones.append("Altísima compatibilidad con tu perfil personal")
    elif prediccion >= 4.0:
        explicaciones.append("Muy alta compatibilidad con tus preferencias")
    elif prediccion >= 3.5:
        explicaciones.append("Buena compatibilidad con tu estilo de vida")
    
    # 8. Si aún no hay suficientes explicaciones, agregar por marca
    if len(explicaciones) < 2:
        if "Coca-Cola" in nombre:
            explicaciones.append("El sabor original e icónico que todo el mundo conoce")
        elif "Pepsi" in nombre:
            explicaciones.append("Sabor dulce y refrescante que destaca")
        elif "Sprite" in nombre:
            explicaciones.append("Refrescante sabor cítrico sin cafeína")
        elif "Red Bull" in nombre:
            explicaciones.append("La bebida energética por excelencia")
        elif "Fanta" in nombre:
            explicaciones.append("Sabor frutal tropical que alegra el día")
        elif "Agua" in nombre:
            explicaciones.append("La opción más pura para hidratarte adecuadamente")
        elif "Jugo" in nombre:
            explicaciones.append("Sabor natural con vitaminas y nutrientes")
        elif "Té" in nombre:
            explicaciones.append("Beneficios antioxidantes en una bebida refrescante")
    
    # 9. Garantizar al menos una explicación
    if len(explicaciones) == 0:
        if bebida.get("es_refresco_real", True):
            explicaciones.append("Una excelente opción que se adapta a tus gustos")
            explicaciones.append("Recomendada por nuestro sistema de inteligencia artificial")
        else:
            explicaciones.append("Una alternativa saludable que cuida tu bienestar")
            explicaciones.append("Opción refrescante con beneficios naturales")
    
    # Limitar a máximo 3 explicaciones para no sobrecargar la interfaz
    return explicaciones[:3]

def determinar_mostrar_alternativas(user_responses: Dict, cluster: int) -> bool:
    """
    Determina si mostrar alternativas saludables basado en respuestas específicas
    Nueva lógica expandida con 18 preguntas manteniendo priorización clara
    """
    response_str = str(user_responses.values()).lower()
    
    # PRIORIDAD 1: P4 - ¿Qué es más importante al elegir una bebida?
    # Esta es la pregunta más decisiva
    if "prioridad_sabor" in response_str:
        # Usuario prioriza sabor → SOLO refrescos
        return False
    elif "prioridad_salud" in response_str or "solo_natural" in response_str:
        # Usuario prioriza salud → SOLO alternativas
        return True
    
    # PRIORIDAD 2: P1 - Relación fundamental con refrescos
    if "no_consume_refrescos" in response_str:
        # Usuario no consume refrescos → SOLO alternativas
        return True
    elif "ama_refrescos" in response_str:
        # Usuario ama refrescos → SOLO refrescos
        return False
    elif "rechaza_refrescos" in response_str:
        # Usuario rechaza refrescos → SOLO alternativas
        return True
    
    # PRIORIDAD 3: P2 - Tipo de bebidas que busca
    if "solo_agua" in response_str or "bebidas_naturales" in response_str:
        # Usuario busca bebidas naturales → SOLO alternativas
        return True
    elif "refrescos_tradicionales" in response_str:
        # Usuario busca refrescos tradicionales → SOLO refrescos
        return False
    
    # PRIORIDAD 4: P5 - Actitud hacia refrescos
    if "evita_salud" in response_str:
        # Usuario evita por salud → SOLO alternativas
        return True
    
    # PRIORIDAD 5: P3 - Nivel de azúcar (menos decisivo)
    if "cero_azucar_natural" in response_str:
        # Usuario quiere cero azúcar natural → SOLO alternativas
        return True
    
    # PRIORIDAD 6: P6 - Situaciones de consumo (menos decisivo)
    if "ejercicio_deporte" in response_str:
        # Usuario consume durante ejercicio → SOLO alternativas
        return True
    
    # NUEVAS PRIORIDADES - P13: Factores de salud (PRIORIDAD ALTA)
    if "salud_azucar_calorias" in response_str or "salud_ingredientes_naturales" in response_str or "salud_sin_aditivos" in response_str or "salud_vitaminas_minerales" in response_str:
        # Usuario consciente de salud → SOLO alternativas
        return True
    elif "salud_no_importa" in response_str:
        # Usuario no le importa salud → SOLO refrescos
        return False
    
    # P12: Tipo de actividad (PRIORIDAD ALTA)
    if "actividad_intensa" in response_str or "actividad_moderada" in response_str:
        # Usuario activo → SOLO alternativas
        return True
    elif "trabajo_sedentario" in response_str or "actividad_relajada" in response_str:
        # Usuario sedentario → SOLO refrescos
        return False
    
    # P16: Actitud hacia cafeína (PRIORIDAD MEDIA)
    if "cafeina_evitar" in response_str or "cafeina_rechazo" in response_str:
        # Usuario evita cafeína → SOLO alternativas
        return True
    elif "cafeina_positiva" in response_str:
        # Usuario busca cafeína → SOLO refrescos energéticos
        return False
    
    # P18: Tipo de experiencia buscada (PRIORIDAD MEDIA)
    if "experiencia_hidratacion" in response_str or "experiencia_relajacion" in response_str:
        # Usuario busca hidratación/relajación → SOLO alternativas
        return True
    elif "experiencia_placer" in response_str or "experiencia_energia" in response_str:
        # Usuario busca placer/energía → SOLO refrescos
        return False
    
    # DEFAULT: Si no hay indicadores claros → SOLO refrescos (comportamiento tradicional)
    return False

async def actualizar_estadisticas_bebida(bebida_id: int, nueva_puntuacion: int):
    """Actualiza las estadísticas de puntuación de una bebida"""
    try:
        bebida = await db.bebidas.find_one({"id": bebida_id})
        if not bebida:
            return
        
        puntuacion_actual = bebida.get("puntuacion_promedio", 3.0)
        total_puntuaciones = bebida.get("total_puntuaciones", 0)
        
        # Calcular nueva puntuación promedio
        nuevo_total = total_puntuaciones + 1
        nueva_puntuacion_promedio = ((puntuacion_actual * total_puntuaciones) + nueva_puntuacion) / nuevo_total
        
        # Actualizar en base de datos
        await db.bebidas.update_one(
            {"id": bebida_id},
            {
                "$set": {
                    "puntuacion_promedio": nueva_puntuacion_promedio,
                    "total_puntuaciones": nuevo_total
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error actualizando estadísticas de bebida {bebida_id}: {e}")

async def actualizar_estadisticas_presentacion(presentation_id: str, nueva_puntuacion: int):
    """Actualiza las estadísticas de puntuación de una presentación específica"""
    try:
        # Buscar la bebida que contiene esta presentación
        bebida = await db.bebidas.find_one({
            "presentaciones.presentation_id": presentation_id
        })
        
        if not bebida:
            return
        
        # Actualizar la presentación específica
        for i, presentacion in enumerate(bebida.get("presentaciones", [])):
            if presentacion.get("presentation_id") == presentation_id:
                puntuacion_actual = presentacion.get("puntuacion_promedio", 3.0)
                total_puntuaciones = presentacion.get("total_puntuaciones", 0)
                
                # Calcular nueva puntuación promedio
                nuevo_total = total_puntuaciones + 1
                nueva_puntuacion_promedio = ((puntuacion_actual * total_puntuaciones) + nueva_puntuacion) / nuevo_total
                
                # Actualizar en base de datos
                await db.bebidas.update_one(
                    {"id": bebida["id"]},
                    {
                        "$set": {
                            f"presentaciones.{i}.puntuacion_promedio": nueva_puntuacion_promedio,
                            f"presentaciones.{i}.total_puntuaciones": nuevo_total
                        }
                    }
                )
                break
        
    except Exception as e:
        logger.error(f"Error actualizando estadísticas de presentación {presentation_id}: {e}")

def generar_explicacion_presentacion(user_responses: Dict, bebida: Dict, presentacion: Dict, prediccion: Dict) -> List[str]:
    """Genera explicaciones específicas para una presentación"""
    explicaciones = []
    
    ml = presentacion.get('ml', 0)
    precio = presentacion.get('precio', 0)
    category = presentacion.get('categoria_presentacion', 'desconocida')
    
    # Análisis por tamaño de presentación
    if category == 'mini' and ml <= 250:
        explicaciones.append(f"Presentación mini ({ml}ml) perfecta para probar sin compromiso")
    elif category == 'individual' and 251 <= ml <= 400:
        explicaciones.append(f"Tamaño individual ({ml}ml) ideal para consumo personal")
    elif category == 'personal' and 401 <= ml <= 750:
        explicaciones.append(f"Presentación personal ({ml}ml) excelente para hidratación extendida")
    elif category == 'familiar' and ml > 750:
        explicaciones.append(f"Presentación familiar ({ml}ml) perfecta para compartir")
    
    # Análisis de relación precio/ml
    if precio > 0 and ml > 0:
        precio_por_ml = precio / ml
        if precio_por_ml < 0.05:
            explicaciones.append("Excelente relación calidad-precio")
        elif precio_por_ml > 0.1:
            explicaciones.append("Presentación premium con mayor valor por ml")
    
    # Análisis de preferencias del usuario
    response_str = str(user_responses.values()).lower()
    
    if 'activo' in response_str:
        if ml <= 400:
            explicaciones.append("Tamaño portátil perfecto para tu estilo de vida activo")
        elif ml > 750:
            explicaciones.append("Ideal para mantenerte hidratado durante actividades largas")
    
    if 'familiar' in response_str or 'compartir' in response_str:
        if ml > 600:
            explicaciones.append("Tamaño ideal para disfrutar en familia")
    
    if 'económico' in response_str or 'precio' in response_str:
        if precio_por_ml < 0.06:
            explicaciones.append("Opción económica que maximiza tu inversión")
    
    # Análisis basado en la predicción ML
    rating = prediccion.get('predicted_rating', 3.0)
    confidence = prediccion.get('confidence', 0.5)
    
    if rating >= 4.5:
        explicaciones.append("Altísima compatibilidad con tus preferencias específicas")
    elif rating >= 4.0:
        explicaciones.append("Muy recomendada basada en tu perfil de preferencias")
    elif rating >= 3.5:
        explicaciones.append("Buena opción que coincide con tus gustos")
    
    if confidence > 0.8:
        explicaciones.append("Recomendación con alta confianza del sistema ML")
    
    # Análisis por categoría de bebida
    if not bebida.get('es_refresco_real', True):
        explicaciones.append("Opción saludable que cuida tu bienestar")
    
    # Garantizar al menos 2 explicaciones
    if len(explicaciones) < 2:
        explicaciones.append(f"Presentación de {ml}ml de {bebida.get('nombre', 'esta bebida')}")
        explicaciones.append("Recomendada por nuestro sistema de inteligencia artificial")
    
    return explicaciones[:3]  # Máximo 3 explicaciones

def generar_feedback_presentacion(puntuacion: int, bebida: Dict, presentacion: Dict, modelo_entrenado: bool) -> Dict:
    """Genera feedback específico para puntuación de presentación"""
    feedback = {
        "mensaje": "",
        "impacto_futuro": "",
        "aprendizaje_ml": "",
        "presentacion_info": {
            "ml": presentacion.get("ml"),
            "precio": presentacion.get("precio"),
            "categoria": presentacion.get("categoria_presentacion", "desconocida")
        }
    }
    
    presentacion_nombre = f"{bebida['nombre']} ({presentacion.get('ml')}ml)"
    
    if puntuacion >= 4:
        feedback["mensaje"] = f"¡Excelente! Te gustó mucho {presentacion_nombre}."
        feedback["impacto_futuro"] = "Te recomendaré más presentaciones similares en tamaño y precio."
        feedback["aprendizaje_ml"] = "He aprendido tus preferencias de tamaño y precio específicas."
    elif puntuacion == 3:
        feedback["mensaje"] = f"{presentacion_nombre} estuvo bien para ti."
        feedback["impacto_futuro"] = "Buscaré presentaciones que se ajusten mejor a tus gustos."
        feedback["aprendizaje_ml"] = "He registrado tu opinión sobre este tamaño de presentación."
    else:
        feedback["mensaje"] = f"Lamento que {presentacion_nombre} no haya sido de tu agrado."
        feedback["impacto_futuro"] = "Evitaré recomendarte presentaciones similares."
        feedback["aprendizaje_ml"] = "He aprendido qué tamaños y precios no prefieres."
    
    if modelo_entrenado:
        feedback["aprendizaje_ml"] += " Mi modelo de presentaciones ha sido actualizado."
    
    # Análisis específico por tamaño
    ml = presentacion.get("ml", 0)
    if ml <= 250:
        feedback["presentacion_info"]["analisis"] = "Presentación mini - ideal para probar o consumo rápido"
    elif ml <= 400:
        feedback["presentacion_info"]["analisis"] = "Presentación individual - perfecta para consumo personal"
    elif ml <= 750:
        feedback["presentacion_info"]["analisis"] = "Presentación personal - ideal para hidratación extendida"
    else:
        feedback["presentacion_info"]["analisis"] = "Presentación familiar - excelente para compartir"
    
    return feedback

def generar_feedback_puntuacion(puntuacion: int, bebida: Dict, modelo_reentrenado: bool) -> Dict:
    """Genera feedback inteligente sobre la puntuación"""
    feedback = {
        "mensaje": "",
        "impacto_futuro": "",
        "aprendizaje_ml": ""
    }
    
    if puntuacion >= 4:
        feedback["mensaje"] = f"¡Excelente! Me alegra que hayas disfrutado {bebida['nombre']}."
        feedback["impacto_futuro"] = "Ahora te recomendaré más bebidas similares a esta."
        feedback["aprendizaje_ml"] = "He aprendido que prefieres este tipo de bebidas."
    elif puntuacion == 3:
        feedback["mensaje"] = f"Entiendo que {bebida['nombre']} estuvo bien para ti."
        feedback["impacto_futuro"] = "Buscaré opciones que se ajusten mejor a tus gustos."
        feedback["aprendizaje_ml"] = "He registrado tus preferencias para mejorar."
    else:
        feedback["mensaje"] = f"Lamento que {bebida['nombre']} no haya sido de tu agrado."
        feedback["impacto_futuro"] = "Evitaré recomendarte bebidas similares."
        feedback["aprendizaje_ml"] = "He aprendido qué tipo de bebidas no prefieres."
    
    if modelo_reentrenado:
        feedback["aprendizaje_ml"] += " Mi modelo ML ha sido actualizado con tu feedback."
    
    return feedback

# Endpoints de administración
@app.get("/api/admin/stats")
async def obtener_estadisticas_admin():
    """Obtiene estadísticas del sistema para administradores"""
    try:
        # Estadísticas de sesiones
        total_sesiones = await db.sesiones_chat.count_documents({})
        sesiones_completadas = await db.sesiones_chat.count_documents({"completada": True})
        
        # Estadísticas de puntuaciones
        total_puntuaciones = await db.puntuaciones.count_documents({})
        total_puntuaciones_presentacion = await db.puntuaciones_presentacion.count_documents({})
        
        # Estadísticas ML
        ml_stats = ml_engine.get_model_stats()
        categorizer_stats = beverage_categorizer.get_category_stats()
        image_stats = image_analyzer.get_analysis_stats()
        presentation_stats = presentation_rating_system.get_system_stats()
        
        # Estadísticas de bebidas
        total_bebidas = await db.bebidas.count_documents({})
        refrescos_reales = await db.bebidas.count_documents({"es_refresco_real": True})
        bebidas_procesadas_ml = await db.bebidas.count_documents({"procesado_ml": True})
        
        # Estadísticas de presentaciones
        bebidas_con_presentaciones = await db.bebidas.find({}).to_list(None)
        total_presentaciones = sum(len(b.get('presentaciones', [])) for b in bebidas_con_presentaciones)
        
        return {
            "sesiones": {
                "total": total_sesiones,
                "completadas": sesiones_completadas,
                "tasa_completacion": (sesiones_completadas / total_sesiones * 100) if total_sesiones > 0 else 0
            },
            "puntuaciones": {
                "bebidas": total_puntuaciones,
                "presentaciones": total_puntuaciones_presentacion,
                "total": total_puntuaciones + total_puntuaciones_presentacion
            },
            "ml_engines": {
                "principal": ml_stats,
                "categorizador": categorizer_stats,
                "analizador_imagenes": image_stats,
                "sistema_presentaciones": presentation_stats
            },
            "bebidas": {
                "total": total_bebidas,
                "refrescos_reales": refrescos_reales,
                "alternativas": total_bebidas - refrescos_reales,
                "procesadas_ml": bebidas_procesadas_ml,
                "total_presentaciones": total_presentaciones
            }
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo estadísticas")

@app.post("/api/admin/reprocess-beverages")
async def reprocesar_bebidas_ml():
    """Fuerza el reprocesamiento de todas las bebidas con ML"""
    try:
        logger.info("Iniciando reprocesamiento de bebidas con ML...")
        await process_beverages_with_ml()
        
        # Obtener estadísticas actualizadas
        categorizer_stats = beverage_categorizer.get_category_stats()
        image_stats = image_analyzer.get_analysis_stats()
        
        return {
            "mensaje": "Bebidas reprocesadas exitosamente con ML",
            "stats": {
                "categorizador": categorizer_stats,
                "analizador_imagenes": image_stats
            }
        }
        
    except Exception as e:
        logger.error(f"Error reprocesando bebidas: {e}")
        raise HTTPException(status_code=500, detail="Error reprocesando bebidas")

@app.get("/api/admin/presentation-analytics/{sesion_id}")
async def obtener_analytics_presentaciones(sesion_id: str):
    """Obtiene análisis detallado de preferencias de presentación del usuario"""
    try:
        # Verificar sesión
        sesion = await db.sesiones_chat.find_one({"session_id": sesion_id})
        if not sesion:
            raise HTTPException(status_code=404, detail="Sesión no encontrada")
        
        # Obtener análisis de preferencias de tamaño
        size_analysis = presentation_rating_system.analyze_user_size_preferences(sesion_id)
        
        # Obtener puntuaciones del usuario
        puntuaciones = await db.puntuaciones_presentacion.find({
            "session_id": sesion_id
        }).to_list(None)
        
        # Calcular estadísticas
        if puntuaciones:
            ratings = [p['puntuacion'] for p in puntuaciones]
            avg_rating = sum(ratings) / len(ratings)
            rating_distribution = {i: ratings.count(i) for i in range(1, 6)}
        else:
            avg_rating = 0
            rating_distribution = {}
        
        return MongoJSONResponse(content={
            "session_id": sesion_id,
            "size_preferences": size_analysis,
            "puntuaciones_dadas": len(puntuaciones),
            "rating_promedio": avg_rating,
            "distribucion_ratings": rating_distribution,
            "puntuaciones_detalle": puntuaciones
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo analytics: {e}")
        raise HTTPException(status_code=500, detail="Error obteniendo analytics")

@app.post("/api/admin/retrain-ml")
async def reentrenar_modelo_ml():
    """Fuerza el re-entrenamiento del modelo ML"""
    try:
        success = ml_engine.train_models(min_samples=1)  # Forzar entrenamiento
        
        if success:
            return {
                "mensaje": "Modelo ML re-entrenado exitosamente",
                "stats": ml_engine.get_model_stats()
            }
        else:
            return {
                "mensaje": "No se pudo re-entrenar el modelo (datos insuficientes)",
                "stats": ml_engine.get_model_stats()
            }
            
    except Exception as e:
        logger.error(f"Error re-entrenando modelo: {e}")
        raise HTTPException(status_code=500, detail="Error re-entrenando modelo")

@app.get("/api/status")
async def obtener_status():
    """Endpoint de salud del sistema"""
    try:
        # Verificar conexión a MongoDB
        await client.admin.command('ping')
        
        # Verificar ML engine
        ml_stats = ml_engine.get_model_stats()
        
        return {
            "status": "healthy",
            "database": "connected",
            "ml_engine": ml_stats,
            "version": "2.0.0"
        }
        
    except Exception as e:
        logger.error(f"Error en status: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }