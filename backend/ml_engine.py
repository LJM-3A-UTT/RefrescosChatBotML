"""
ML Engine para RefrescoBot ML
Implementa Machine Learning real usando scikit-learn

Componentes:
- Supervised Learning: RandomForestRegressor para predicción de preferencias
- Unsupervised Learning: KMeans para clustering de usuarios
- Feature Engineering: Codificación de respuestas y características de bebidas
- Model Persistence: Guardado/cargado de modelos usando joblib
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MLEngine:
    """
    Engine principal de Machine Learning para RefrescoBot
    
    Características:
    - Supervised Learning para predicción de ratings
    - Unsupervised Learning para clustering de usuarios
    - Feature engineering automático
    - Persistencia de modelos
    - Aprendizaje incremental
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Modelos ML
        self.preference_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2
        )
        self.clustering_model = KMeans(
            n_clusters=5,  # 5 tipos de usuarios
            random_state=42,
            n_init=10
        )
        
        # Encoders para features categóricas
        self.label_encoders = {}
        
        # Datos de entrenamiento
        self.training_data = []
        self.feature_names = []
        
        # Estado del modelo
        self.is_trained = False
        self.model_version = "1.0.0"
        self.last_training = None
        
        # Cargar modelos existentes si existen
        self.load_models()
    
    def encode_user_responses(self, responses: Dict[str, Any]) -> np.ndarray:
        """
        Codifica las respuestas del usuario en features numéricas
        
        Args:
            responses: Diccionario con respuestas del usuario
            
        Returns:
            Array numpy con features codificadas
        """
        features = []
        feature_names = []
        
        # Categorías principales para encoding
        categories = {
            'consumo_base': ['nunca', 'ocasional', 'semanal', 'frecuente', 'diario'],
            'fisico': ['inactivo', 'sedentario', 'moderado', 'activo', 'muy_activo'],
            'preferencias_dulzura': ['natural', 'poco_dulce', 'equilibrado', 'dulce_moderado', 'muy_dulce'],
            'estado_animo': ['tranquilo', 'relajado', 'equilibrado', 'ocupado', 'estresante'],
            'temporal': ['noche', 'tarde', 'almuerzo', 'media_manana', 'manana'],
            'aventurero': ['muy_conservador', 'conservador', 'moderado', 'aventurero', 'muy_aventurero'],
            'salud_importancia': ['no_importa', 'poco_importante', 'moderado', 'importante', 'muy_importante']
        }
        
        # Codificar cada categoría
        for category, values in categories.items():
            # Buscar la respuesta correspondiente en el diccionario de respuestas
            response_value = None
            for resp_key, resp_val in responses.items():
                if category in resp_key or any(keyword in resp_val.lower() for keyword in ['dulce', 'activo', 'consumo', 'frecuencia']):
                    response_value = resp_val
                    break
            
            if response_value and response_value in values:
                # Codificación ordinal (0-4)
                encoded = values.index(response_value)
                features.append(encoded)
                feature_names.append(f"{category}_encoded")
            else:
                # Valor por defecto (neutro)
                features.append(2)  # Valor medio
                feature_names.append(f"{category}_encoded")
        
        # Features adicionales derivadas
        # Score de salud (basado en actividad física y preferencia por lo natural)
        health_score = 0
        if 'activo' in str(responses.values()).lower():
            health_score += 2
        if 'natural' in str(responses.values()).lower():
            health_score += 2
        features.append(health_score)
        feature_names.append('health_score')
        
        # Score de dulzura (extraído de preferencias)
        sweetness_score = 2  # Default neutro
        response_str = str(responses.values()).lower()
        if 'muy_dulce' in response_str:
            sweetness_score = 4
        elif 'dulce' in response_str:
            sweetness_score = 3
        elif 'natural' in response_str or 'sin azúcar' in response_str:
            sweetness_score = 0
        features.append(sweetness_score)
        feature_names.append('sweetness_preference')
        
        # Score de energía (basado en estilo de vida)
        energy_score = 2
        if 'estresante' in response_str or 'ocupado' in response_str:
            energy_score = 4
        elif 'tranquilo' in response_str:
            energy_score = 1
        features.append(energy_score)
        feature_names.append('energy_need')
        
        self.feature_names = feature_names
        return np.array(features).reshape(1, -1)
    
    def encode_beverage_features(self, bebida: Dict[str, Any]) -> np.ndarray:
        """
        Codifica las características de una bebida en features numéricas
        
        Args:
            bebida: Diccionario con información de la bebida
            
        Returns:
            Array numpy con features de la bebida
        """
        features = []
        
        # Features principales de la bebida
        features.append(bebida.get('nivel_dulzura', 5))  # 0-10
        features.append(1 if bebida.get('es_energizante', False) else 0)  # Boolean
        features.append(1 if bebida.get('es_refresco_real', True) else 0)  # Boolean
        
        # Codificación de categoría
        categoria_encoding = {
            'cola': 0, 'citricos': 1, 'frutales': 2, 
            'energeticas': 3, 'agua': 4, 'jugos': 5, 'tes': 6
        }
        features.append(categoria_encoding.get(bebida.get('categoria', 'cola'), 0))
        
        # Codificación de perfil de sabor
        sabor_encoding = {
            'dulce_clasico': 0, 'dulce_intenso': 1, 'citrico_refrescante': 2,
            'energetico_frutal': 3, 'frutal_tropical': 4, 'natural_puro': 5,
            'natural_citrico': 6, 'herbal_refrescante': 7
        }
        features.append(sabor_encoding.get(bebida.get('perfil_sabor', 'dulce_clasico'), 0))
        
        # Codificación de contenido calórico
        calorias_encoding = {'cero': 0, 'muy_bajo': 1, 'bajo': 2, 'medio': 3, 'alto': 4}
        features.append(calorias_encoding.get(bebida.get('contenido_calorias', 'medio'), 3))
        
        # Score de salud (inverso de calorías + natural)
        health_score = 4 - calorias_encoding.get(bebida.get('contenido_calorias', 'medio'), 3)
        if not bebida.get('es_refresco_real', True):
            health_score += 2
        features.append(health_score)
        
        # Precio normalizado (0-1)
        precio_norm = min(bebida.get('precio_base', 25) / 100.0, 1.0)
        features.append(precio_norm)
        
        return np.array(features)
    
    def add_training_data(self, user_responses: Dict[str, Any], 
                         bebida: Dict[str, Any], rating: float):
        """
        Añade datos de entrenamiento al conjunto
        
        Args:
            user_responses: Respuestas del usuario
            bebida: Información de la bebida
            rating: Calificación dada por el usuario (1-5)
        """
        try:
            # Codificar features del usuario
            user_features = self.encode_user_responses(user_responses)
            
            # Codificar features de la bebida
            beverage_features = self.encode_beverage_features(bebida)
            
            # Combinar features
            combined_features = np.concatenate([user_features.flatten(), beverage_features])
            
            # Añadir a datos de entrenamiento
            training_sample = {
                'features': combined_features.tolist(),
                'rating': rating,
                'timestamp': datetime.now().isoformat(),
                'user_id': user_responses.get('session_id', 'unknown'),
                'beverage_id': bebida.get('id', 'unknown')
            }
            
            self.training_data.append(training_sample)
            
            logger.info(f"Datos de entrenamiento añadidos: Usuario {training_sample['user_id']}, "
                       f"Bebida {bebida.get('nombre', 'Unknown')}, Rating {rating}")
            
        except Exception as e:
            logger.error(f"Error añadiendo datos de entrenamiento: {e}")
    
    def train_models(self, min_samples: int = 10) -> bool:
        """
        Entrena los modelos ML con los datos disponibles
        
        Args:
            min_samples: Número mínimo de muestras para entrenar
            
        Returns:
            True si el entrenamiento fue exitoso
        """
        if len(self.training_data) < min_samples:
            logger.info(f"Insuficientes datos para entrenar: {len(self.training_data)} < {min_samples}")
            return False
        
        try:
            # Preparar datos
            X = []
            y = []
            
            for sample in self.training_data:
                X.append(sample['features'])
                y.append(sample['rating'])
            
            X = np.array(X)
            y = np.array(y)
            
            # Entrenar modelo de preferencias (supervised)
            if len(X) > 5:  # Necesario para train/test split
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                
                self.preference_model.fit(X_train, y_train)
                
                # Evaluar modelo
                y_pred = self.preference_model.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                logger.info(f"Modelo de preferencias entrenado. MSE: {mse:.3f}")
            else:
                # Con pocos datos, usar todos para entrenar
                self.preference_model.fit(X, y)
                logger.info("Modelo de preferencias entrenado con datos limitados")
            
            # Entrenar modelo de clustering (unsupervised)
            # Solo usar features de usuario para clustering
            user_features_only = []
            for sample in self.training_data:
                # Tomar solo las primeras features que corresponden al usuario
                user_feat_len = len(self.feature_names) if self.feature_names else 10
                user_features_only.append(sample['features'][:user_feat_len])
            
            if len(user_features_only) >= 5:  # Mínimo para clustering
                user_features_array = np.array(user_features_only)
                self.clustering_model.fit(user_features_array)
                logger.info(f"Modelo de clustering entrenado con {len(user_features_only)} usuarios")
            
            self.is_trained = True
            self.last_training = datetime.now()
            
            # Guardar modelos
            self.save_models()
            
            return True
            
        except Exception as e:
            logger.error(f"Error entrenando modelos: {e}")
            return False
    
    def predict_preference(self, user_responses: Dict[str, Any], 
                          bebida: Dict[str, Any], tiempo_respuestas: List[float] = None) -> float:
        """
        Predice la preferencia del usuario por una bebida
        
        Args:
            user_responses: Respuestas del usuario
            bebida: Información de la bebida
            tiempo_respuestas: Lista de tiempos de respuesta para detectar usuarios de prueba
            
        Returns:
            Predicción de rating (1-5)
        """
        # Detectar tipo de usuario primero
        tipo_usuario = self._detectar_tipo_usuario(user_responses, tiempo_respuestas)
        
        # Aplicar lógica específica según tipo de usuario
        if tipo_usuario == "no_consume_refrescos":
            return self._prediccion_usuario_saludable(user_responses, bebida)
        elif tipo_usuario == "usuario_prueba":
            return self._prediccion_usuario_prueba(user_responses, bebida)
        elif not self.is_trained:
            return self._heuristic_prediction(user_responses, bebida)
        else:
            return self._prediccion_ml_avanzada(user_responses, bebida, tipo_usuario)
    
    def _detectar_tipo_usuario(self, user_responses: Dict[str, Any], 
                              tiempo_respuestas: List[float] = None) -> str:
        """
        Detecta el tipo de usuario basado en respuestas y patrones
        
        Returns:
            "regular", "usuario_prueba", "no_consume_refrescos"
        """
        response_str = str(user_responses.values()).lower()
        
        # 1. Detectar usuario que no consume refrescos (primera pregunta)
        for key, value in user_responses.items():
            if "consumo_base" in key or "frecuencia" in key.lower():
                if value in ["nunca", "casi nunca"]:
                    return "no_consume_refrescos"
        
        # 2. Detectar usuario de prueba por tiempo de respuesta
        if tiempo_respuestas and len(tiempo_respuestas) >= 3:
            promedio_tiempo = sum(tiempo_respuestas) / len(tiempo_respuestas)
            respuestas_muy_rapidas = sum(1 for t in tiempo_respuestas if t < 2.0)
            
            # Si más del 70% de respuestas son muy rápidas (menos de 2 segundos)
            if respuestas_muy_rapidas / len(tiempo_respuestas) > 0.7:
                return "usuario_prueba"
            
            # Si el promedio es menor a 3 segundos
            if promedio_tiempo < 3.0:
                return "usuario_prueba"
        
        # 3. Detectar usuario de prueba por patrones de respuesta
        if self._detectar_patron_respuesta_aleatoria(user_responses):
            return "usuario_prueba"
        
        return "regular"
    
    def detectar_tipo_usuario(self, user_responses: Dict[str, Any], 
                            tiempo_respuestas: List[float] = None) -> str:
        """
        Método público para detectar tipo de usuario
        """
        return self._detectar_tipo_usuario(user_responses, tiempo_respuestas)
        """
        Detecta si el usuario está respondiendo de forma aleatoria o siguiendo patrones
        """
        respuestas_valores = []
        for key, value in user_responses.items():
            if "pregunta_" in key:
                # Intentar extraer el índice de la respuesta si es posible
                try:
                    if isinstance(value, dict) and "respuesta_id" in value:
                        respuestas_valores.append(value["respuesta_id"])
                    elif isinstance(value, str):
                        # Buscar patrones comunes
                        if value in ["primera", "segunda", "tercera", "cuarta", "quinta"]:
                            respuestas_valores.append(["primera", "segunda", "tercera", "cuarta", "quinta"].index(value) + 1)
                except:
                    pass
        
        if len(respuestas_valores) >= 4:
            # Detectar si siempre elige la misma posición
            if len(set(respuestas_valores)) == 1:
                return True
            
            # Detectar si sigue un patrón secuencial (1,2,3,4... o 5,4,3,2...)
            if respuestas_valores == sorted(respuestas_valores) or respuestas_valores == sorted(respuestas_valores, reverse=True):
                return True
        
        return False
    
    def detectar_tipo_usuario(self, user_responses: Dict[str, Any], 
                            tiempo_respuestas: List[float] = None) -> str:
        """
        Método público para detectar tipo de usuario
        """
        return self._detectar_tipo_usuario(user_responses, tiempo_respuestas)
    def _detectar_patron_respuesta_aleatoria(self, user_responses: Dict[str, Any]) -> bool:
        """
        Detecta si el usuario está respondiendo de forma aleatoria o siguiendo patrones
        """
        respuestas_valores = []
        for key, value in user_responses.items():
            if "pregunta_" in key:
                # Intentar extraer el índice de la respuesta si es posible
                try:
                    if isinstance(value, dict) and "respuesta_id" in value:
                        respuestas_valores.append(value["respuesta_id"])
                    elif isinstance(value, str):
                        # Buscar patrones comunes
                        if value in ["primera", "segunda", "tercera", "cuarta", "quinta"]:
                            respuestas_valores.append(["primera", "segunda", "tercera", "cuarta", "quinta"].index(value) + 1)
                except:
                    pass
        
        if len(respuestas_valores) >= 4:
            # Detectar si siempre elige la misma posición
            if len(set(respuestas_valores)) == 1:
                return True
            
            # Detectar si sigue un patrón secuencial (1,2,3,4... o 5,4,3,2...)
            if respuestas_valores == sorted(respuestas_valores) or respuestas_valores == sorted(respuestas_valores, reverse=True):
                return True
        
        return False
    def _prediccion_usuario_saludable(self, user_responses: Dict[str, Any], bebida: Dict[str, Any]) -> float:
        """
        Predicción especializada para usuarios que no consumen refrescos
        """
        score = 2.0  # Base baja para refrescos
        
        # Fuertemente favorecer opciones saludables
        if not bebida.get("es_refresco_real", True):
            score = 4.0  # Base alta para alternativas
            
            # Bonus adicionales para opciones muy saludables
            if bebida.get("contenido_calorias") in ["cero", "muy_bajo"]:
                score += 0.8
            
            if bebida.get("categoria") in ["agua", "tes", "jugos"]:
                score += 0.5
            
            # Analizar otras preferencias
            response_str = str(user_responses.values()).lower()
            if "activo" in response_str:
                score += 0.3
            if "natural" in response_str:
                score += 0.4
        else:
            # Penalizar refrescos reales para estos usuarios
            score = 1.5
            if bebida.get("nivel_dulzura", 5) >= 7:
                score -= 0.3
        
        return max(1.0, min(5.0, score))
    
    def _prediccion_usuario_prueba(self, user_responses: Dict[str, Any], bebida: Dict[str, Any]) -> float:
        """
        Predicción para usuarios que están probando el sistema
        """
        # Para usuarios de prueba, mostrar variedad pero con lógica básica
        score = 3.0  # Base neutral
        
        # Mostrar tanto refrescos como alternativas con variación
        if bebida.get("categoria") in ["cola", "citricos"]:
            score += 0.5
        
        # Añadir algo de aleatoriedad controlada para que vean variedad
        import random
        random.seed(hash(str(user_responses)) % 1000)  # Reproducible pero variado
        variacion = random.uniform(-0.8, 0.8)
        score += variacion
        
        return max(1.0, min(5.0, score))
    
    def _prediccion_ml_avanzada(self, user_responses: Dict[str, Any], 
                               bebida: Dict[str, Any], tipo_usuario: str) -> float:
        """
        Predicción ML avanzada para usuarios regulares
        """
        try:
            # Codificar features
            user_features = self.encode_user_responses(user_responses)
            beverage_features = self.encode_beverage_features(bebida)
            combined_features = np.concatenate([user_features.flatten(), beverage_features]).reshape(1, -1)
            
            # Predecir usando ML
            prediction = self.preference_model.predict(combined_features)[0]
            
            # Ajustar predicción según el tipo de usuario
            if tipo_usuario == "regular":
                # Para usuarios regulares, usar predicción ML completa
                adjusted_prediction = prediction
            else:
                # Para otros casos, mezclar con heurísticas
                heuristic_pred = self._heuristic_prediction(user_responses, bebida)
                adjusted_prediction = (prediction * 0.7) + (heuristic_pred * 0.3)
            
            # Asegurar variación personalizada
            adjusted_prediction = self._aplicar_personalizacion_avanzada(
                adjusted_prediction, user_responses, bebida
            )
            
            return max(1.0, min(5.0, adjusted_prediction))
            
        except Exception as e:
            logger.error(f"Error en predicción ML avanzada: {e}")
            return self._heuristic_prediction(user_responses, bebida)
    
    def _aplicar_personalizacion_avanzada(self, prediction: float, 
                                        user_responses: Dict[str, Any], 
                                        bebida: Dict[str, Any]) -> float:
        """
        Aplica personalización avanzada basada en respuestas específicas
        """
        response_str = str(user_responses.values()).lower()
        
        # Análisis de actividad física
        if "muy_activo" in response_str or "activo" in response_str:
            if bebida.get("es_energizante", False):
                prediction += 0.8
            elif not bebida.get("es_refresco_real", True):
                prediction += 0.6
            elif bebida.get("nivel_dulzura", 5) >= 8:
                prediction -= 0.4
        
        # Análisis de preferencias de dulzura
        if "muy_dulce" in response_str:
            if bebida.get("nivel_dulzura", 5) >= 8:
                prediction += 1.0
            elif bebida.get("nivel_dulzura", 5) <= 3:
                prediction -= 0.7
        elif "natural" in response_str or "sin azúcar" in response_str:
            if bebida.get("nivel_dulzura", 5) <= 3:
                prediction += 1.0
            elif bebida.get("nivel_dulzura", 5) >= 7:
                prediction -= 0.8
        
        # Análisis de importancia de salud
        if "muy_importante" in response_str and "salud" in response_str:
            if not bebida.get("es_refresco_real", True):
                prediction += 1.2
            elif bebida.get("contenido_calorias") == "alto":
                prediction -= 0.9
        
        # Análisis de estilo de vida
        if "estresante" in response_str or "ocupado" in response_str:
            if bebida.get("es_energizante", False):
                prediction += 0.7
            elif bebida.get("categoria") == "tes":
                prediction += 0.5
        
        # Análisis de momento del día
        if "mañana" in response_str:
            if bebida.get("es_energizante", False):
                prediction += 0.6
            elif bebida.get("categoria") in ["agua", "jugos"]:
                prediction += 0.4
        
        return prediction
    
    def _heuristic_prediction(self, user_responses: Dict[str, Any], 
                            bebida: Dict[str, Any]) -> float:
        """
        Predicción heurística cuando no hay modelo ML entrenado
        """
        score = 3.0  # Base neutral
        
        # Análisis de respuestas del usuario
        response_str = str(user_responses.values()).lower()
        
        # Factor de dulzura
        sweetness_match = 0
        if 'muy_dulce' in response_str and bebida.get('nivel_dulzura', 5) >= 8:
            sweetness_match = 1.0
        elif 'natural' in response_str and bebida.get('nivel_dulzura', 5) <= 3:
            sweetness_match = 1.0
        elif 'equilibrado' in response_str and 4 <= bebida.get('nivel_dulzura', 5) <= 6:
            sweetness_match = 0.8
        
        score += sweetness_match * 1.5
        
        # Factor de salud
        health_conscious = 'importante' in response_str and 'salud' in response_str
        if health_conscious and not bebida.get('es_refresco_real', True):
            score += 1.0
        elif health_conscious and bebida.get('es_refresco_real', True):
            score -= 0.5
        
        # Factor de energía
        need_energy = 'estresante' in response_str or 'ocupado' in response_str
        if need_energy and bebida.get('es_energizante', False):
            score += 0.8
        
        # Factor de actividad física
        if 'activo' in response_str and not bebida.get('es_refresco_real', True):
            score += 0.5
        
        return max(1.0, min(5.0, score))
    
    def get_user_cluster(self, user_responses: Dict[str, Any]) -> int:
        """
        Obtiene el cluster del usuario
        
        Args:
            user_responses: Respuestas del usuario
            
        Returns:
            ID del cluster (0-4)
        """
        if not self.is_trained:
            return self._heuristic_cluster(user_responses)
        
        try:
            user_features = self.encode_user_responses(user_responses)
            cluster = self.clustering_model.predict(user_features)[0]
            return int(cluster)
        except Exception as e:
            logger.error(f"Error en clustering: {e}")
            return self._heuristic_cluster(user_responses)
    
    def _heuristic_cluster(self, user_responses: Dict[str, Any]) -> int:
        """
        Clustering heurístico basado en reglas
        """
        response_str = str(user_responses.values()).lower()
        
        # Cluster 0: Tradicionales (dulce + sedentario)
        if 'dulce' in response_str and ('sedentario' in response_str or 'inactivo' in response_str):
            return 0
        
        # Cluster 1: Saludables (activo + natural)
        if 'activo' in response_str and ('natural' in response_str or 'importante' in response_str):
            return 1
        
        # Cluster 2: Energéticos (estresante + ocupado)
        if 'estresante' in response_str or 'ocupado' in response_str:
            return 2
        
        # Cluster 3: Aventureros (pruebo cosas nuevas)
        if 'aventurero' in response_str or 'nuevas' in response_str:
            return 3
        
        # Cluster 4: Conservadores (favoritos conocidos)
        return 4
    
    def save_models(self):
        """Guarda los modelos entrenados"""
        try:
            model_data = {
                'preference_model': self.preference_model,
                'clustering_model': self.clustering_model,
                'label_encoders': self.label_encoders,
                'training_data': self.training_data,
                'feature_names': self.feature_names,
                'is_trained': self.is_trained,
                'model_version': self.model_version,
                'last_training': self.last_training.isoformat() if self.last_training else None
            }
            
            model_path = self.models_dir / 'ml_models.joblib'
            joblib.dump(model_data, model_path)
            logger.info(f"Modelos guardados en {model_path}")
            
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
    
    def load_models(self):
        """Carga los modelos guardados"""
        try:
            model_path = self.models_dir / 'ml_models.joblib'
            if model_path.exists():
                model_data = joblib.load(model_path)
                
                self.preference_model = model_data.get('preference_model', self.preference_model)
                self.clustering_model = model_data.get('clustering_model', self.clustering_model)
                self.label_encoders = model_data.get('label_encoders', {})
                self.training_data = model_data.get('training_data', [])
                self.feature_names = model_data.get('feature_names', [])
                self.is_trained = model_data.get('is_trained', False)
                self.model_version = model_data.get('model_version', self.model_version)
                
                last_training_str = model_data.get('last_training')
                if last_training_str:
                    self.last_training = datetime.fromisoformat(last_training_str)
                
                logger.info(f"Modelos cargados. Entrenado: {self.is_trained}, "
                           f"Datos: {len(self.training_data)}")
            else:
                logger.info("No se encontraron modelos guardados. Iniciando desde cero.")
                
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
    
    def get_model_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del modelo
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            'is_trained': self.is_trained,
            'training_samples': len(self.training_data),
            'model_version': self.model_version,
            'last_training': self.last_training.isoformat() if self.last_training else None,
            'feature_count': len(self.feature_names),
            'clusters': 5 if self.is_trained else 0
        }
    
    def retrain_if_needed(self, min_new_samples: int = 5, force: bool = False) -> bool:
        """
        Re-entrena los modelos si hay suficientes datos nuevos
        
        Args:
            min_new_samples: Mínimo de nuevas muestras necesarias
            force: Forzar re-entrenamiento
            
        Returns:
            True si se re-entrenó
        """
        if force or len(self.training_data) % min_new_samples == 0:
            return self.train_models()
        return False


# Instancia global del engine ML
ml_engine = MLEngine()