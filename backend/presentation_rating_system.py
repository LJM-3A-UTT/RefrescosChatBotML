"""
Presentation Rating System - Sistema de Puntuación por Presentación
Maneja puntuaciones específicas por presentación individual de bebidas

Funcionalidades:
- Puntuación independiente por cada presentación
- Análisis de preferencias por tamaño/precio
- Recomendaciones precisas por presentación
- ML especializado para presentaciones
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
import json
from collections import defaultdict
import uuid

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PresentationRatingSystem:
    """
    Sistema avanzado de puntuación por presentación individual
    usando múltiples modelos ML especializados
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Modelos ML especializados
        self.rating_predictor = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=3,
            min_samples_leaf=2,
            random_state=42
        )
        
        self.price_preference_model = GradientBoostingRegressor(
            n_estimators=50,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.size_preference_model = RandomForestRegressor(
            n_estimators=80,
            max_depth=8,
            random_state=42
        )
        
        self.presentation_clustering = KMeans(
            n_clusters=6,  # Mini, Individual, Personal, Familiar, Premium, Economico
            random_state=42,
            n_init=10
        )
        
        # Escaladores
        self.feature_scaler = StandardScaler()
        self.price_scaler = StandardScaler()
        
        # Encoders
        self.size_category_encoder = LabelEncoder()
        
        # Datos de entrenamiento
        self.presentation_ratings = []
        self.user_preferences = {}
        
        # Categorías de presentación
        self.size_categories = {
            'mini': {'min': 0, 'max': 250, 'typical_use': 'porcion individual pequeña'},
            'individual': {'min': 251, 'max': 400, 'typical_use': 'consumo personal'},
            'personal': {'min': 401, 'max': 750, 'typical_use': 'consumo personal extendido'},
            'familiar': {'min': 751, 'max': 3000, 'typical_use': 'compartir en familia'},
            'bulk': {'min': 3001, 'max': 10000, 'typical_use': 'eventos o stock'}
        }
        
        # Factores de preferencia por tamaño
        self.size_preference_factors = {
            'mini': {
                'convenience': 1.0,
                'portability': 1.0,
                'price_per_unit': 0.3,
                'waste_concern': 0.8
            },
            'individual': {
                'convenience': 0.9,
                'portability': 0.8,
                'price_per_unit': 0.6,
                'waste_concern': 0.9
            },
            'personal': {
                'convenience': 0.7,
                'portability': 0.6,
                'price_per_unit': 0.8,
                'waste_concern': 0.7
            },
            'familiar': {
                'convenience': 0.5,
                'portability': 0.3,
                'price_per_unit': 1.0,
                'waste_concern': 0.6
            }
        }
        
        # Estado del modelo
        self.is_trained = False
        self.model_version = "1.0.0"
        self.last_training = None
        
        # Cargar modelos existentes
        self.load_models()
    
    def categorize_presentation_size(self, ml: int) -> str:
        """Categoriza presentación por tamaño en ml"""
        for category, bounds in self.size_categories.items():
            if bounds['min'] <= ml <= bounds['max']:
                return category
        return 'especial'
    
    def extract_presentation_features(self, presentation: Dict, beverage: Dict, user_context: Dict = None) -> np.ndarray:
        """Extrae características de una presentación específica"""
        features = []
        
        # Características básicas de la presentación
        ml = presentation.get('ml', 0)
        precio = presentation.get('precio', 0)
        
        features.extend([
            ml,                                    # Tamaño en ml
            precio,                               # Precio absoluto
            precio / max(ml, 1),                  # Precio por ml
            np.log1p(ml),                         # Log del tamaño (para manejar valores grandes)
            np.log1p(precio),                     # Log del precio
        ])
        
        # Categoría de tamaño (one-hot encoding manual)
        size_category = self.categorize_presentation_size(ml)
        for category in self.size_categories.keys():
            features.append(1.0 if category == size_category else 0.0)
        
        # Características de la bebida padre
        if beverage:
            # Número total de presentaciones de esta bebida
            total_presentations = len(beverage.get('presentaciones', []))
            features.append(total_presentations)
            
            # Posición relativa de precio entre presentaciones de la misma bebida
            all_prices = [p.get('precio', 0) for p in beverage.get('presentaciones', [])]
            price_rank = sorted(all_prices).index(precio) / max(len(all_prices) - 1, 1)
            features.append(price_rank)
            
            # Posición relativa de tamaño
            all_sizes = [p.get('ml', 0) for p in beverage.get('presentaciones', [])]
            size_rank = sorted(all_sizes).index(ml) / max(len(all_sizes) - 1, 1)
            features.append(size_rank)
            
            # Características ML de la bebida
            categories_ml = beverage.get('categorias_ml', [])
            features.extend([
                len(categories_ml),                # Número de categorías ML
                1.0 if 'sin_azucar' in categories_ml else 0.0,
                1.0 if 'cola' in categories_ml else 0.0,
                1.0 if 'citricos' in categories_ml else 0.0,
                1.0 if 'agua' in categories_ml else 0.0,
                1.0 if 'jugos' in categories_ml else 0.0,
            ])
            
            # Tags automáticos
            tags_automaticos = beverage.get('tags_automaticos', [])
            features.extend([
                len(tags_automaticos),
                1.0 if 'premium' in tags_automaticos else 0.0,
                1.0 if 'economico' in tags_automaticos else 0.0,
                1.0 if 'saludable' in tags_automaticos else 0.0,
                1.0 if 'familiar' in tags_automaticos else 0.0,
            ])
        else:
            # Rellenar con ceros si no hay información de bebida
            features.extend([0.0] * 12)
        
        # Características de contexto del usuario
        if user_context:
            # Preferencias de tamaño del usuario (extraídas de respuestas)
            response_str = str(user_context.values()).lower()
            
            features.extend([
                1.0 if 'activo' in response_str else 0.0,        # Usuario activo -> prefiere portable
                1.0 if 'familiar' in response_str else 0.0,      # Contexto familiar -> prefiere grande
                1.0 if 'ocupado' in response_str else 0.0,       # Usuario ocupado -> prefiere conveniente
                1.0 if 'economico' in response_str else 0.0,     # Consciente del precio
                1.0 if 'premium' in response_str else 0.0,       # Dispuesto a pagar más
            ])
        else:
            features.extend([0.0] * 5)
        
        # Factores de preferencia por tamaño
        size_factors = self.size_preference_factors.get(size_category, {})
        features.extend([
            size_factors.get('convenience', 0.5),
            size_factors.get('portability', 0.5),
            size_factors.get('price_per_unit', 0.5),
            size_factors.get('waste_concern', 0.5),
        ])
        
        return np.array(features)
    
    def add_presentation_rating(self, presentation_id: str, user_responses: Dict, 
                              beverage: Dict, presentation: Dict, rating: float, 
                              context: Dict = None):
        """Añade una puntuación específica por presentación"""
        try:
            # Extraer características
            features = self.extract_presentation_features(presentation, beverage, user_responses)
            
            # Crear registro de entrenamiento
            rating_record = {
                'presentation_id': presentation_id,
                'user_session': user_responses.get('session_id', 'unknown'),
                'beverage_id': beverage.get('id'),
                'presentation_ml': presentation.get('ml'),
                'presentation_price': presentation.get('precio'),
                'rating': rating,
                'features': features.tolist(),
                'timestamp': datetime.now().isoformat(),
                'context': context or {}
            }
            
            self.presentation_ratings.append(rating_record)
            
            # Actualizar estadísticas de la presentación
            self.update_presentation_stats(presentation_id, rating)
            
            # Actualizar preferencias del usuario
            self.update_user_preferences(user_responses.get('session_id'), presentation, rating)
            
            logger.info(f"Rating añadido: {presentation_id} -> {rating} estrellas")
            
        except Exception as e:
            logger.error(f"Error añadiendo rating de presentación: {e}")
    
    def update_presentation_stats(self, presentation_id: str, rating: float):
        """Actualiza estadísticas específicas de una presentación"""
        try:
            # Buscar ratings existentes para esta presentación
            presentation_ratings = [r for r in self.presentation_ratings 
                                  if r['presentation_id'] == presentation_id]
            
            if presentation_ratings:
                ratings = [r['rating'] for r in presentation_ratings]
                avg_rating = np.mean(ratings)
                total_ratings = len(ratings)
                
                # Guardar estadísticas actualizadas
                stats = {
                    'presentation_id': presentation_id,
                    'average_rating': avg_rating,
                    'total_ratings': total_ratings,
                    'rating_distribution': {
                        '1_star': sum(1 for r in ratings if r == 1),
                        '2_star': sum(1 for r in ratings if r == 2),
                        '3_star': sum(1 for r in ratings if r == 3),
                        '4_star': sum(1 for r in ratings if r == 4),
                        '5_star': sum(1 for r in ratings if r == 5),
                    },
                    'last_updated': datetime.now().isoformat()
                }
                
                # Guardar en cache para acceso rápido
                if not hasattr(self, 'presentation_stats'):
                    self.presentation_stats = {}
                self.presentation_stats[presentation_id] = stats
                
        except Exception as e:
            logger.error(f"Error actualizando estadísticas de presentación: {e}")
    
    def update_user_preferences(self, user_session: str, presentation: Dict, rating: float):
        """Actualiza preferencias de usuario por tipo de presentación"""
        try:
            if user_session not in self.user_preferences:
                self.user_preferences[user_session] = {
                    'size_preferences': {},
                    'price_sensitivity': 0.0,
                    'total_ratings': 0,
                    'last_activity': datetime.now().isoformat()
                }
            
            user_prefs = self.user_preferences[user_session]
            
            # Actualizar preferencias de tamaño
            ml = presentation.get('ml', 0)
            size_category = self.categorize_presentation_size(ml)
            
            if size_category not in user_prefs['size_preferences']:
                user_prefs['size_preferences'][size_category] = []
            
            user_prefs['size_preferences'][size_category].append(rating)
            
            # Calcular sensibilidad al precio
            precio = presentation.get('precio', 0)
            price_per_ml = precio / max(ml, 1)
            
            # Si da rating alto a opciones caras por ml -> baja sensibilidad al precio
            # Si da rating bajo a opciones caras por ml -> alta sensibilidad al precio
            if price_per_ml > 0.08:  # Precio alto por ml
                if rating >= 4:
                    user_prefs['price_sensitivity'] -= 0.1
                elif rating <= 2:
                    user_prefs['price_sensitivity'] += 0.2
            
            user_prefs['total_ratings'] += 1
            user_prefs['last_activity'] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error actualizando preferencias de usuario: {e}")
    
    def train_models(self, min_samples: int = 20) -> bool:
        """Entrena los modelos ML especializados en presentaciones"""
        if len(self.presentation_ratings) < min_samples:
            logger.info(f"Insuficientes datos para entrenar: {len(self.presentation_ratings)} < {min_samples}")
            return False
        
        try:
            # Preparar datos
            X = []
            y_rating = []
            y_price_pref = []
            y_size_pref = []
            
            for record in self.presentation_ratings:
                features = record['features']
                rating = record['rating']
                
                X.append(features)
                y_rating.append(rating)
                
                # Calcular preferencia de precio (rating vs precio por ml)
                precio = record.get('presentation_price', 0)
                ml = record.get('presentation_ml', 1)
                price_per_ml = precio / max(ml, 1)
                price_preference = rating / max(price_per_ml * 100, 1)  # Normalizado
                y_price_pref.append(price_preference)
                
                # Calcular preferencia de tamaño
                size_preference = rating * (ml / 1000)  # Favorece tamaños más grandes con rating alto
                y_size_pref.append(size_preference)
            
            X = np.array(X)
            y_rating = np.array(y_rating)
            y_price_pref = np.array(y_price_pref)
            y_size_pref = np.array(y_size_pref)
            
            # Escalar features
            X_scaled = self.feature_scaler.fit_transform(X)
            
            # Entrenar modelo principal de rating
            if len(X) > 10:
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y_rating, test_size=0.2, random_state=42
                )
                
                self.rating_predictor.fit(X_train, y_train)
                
                # Evaluar
                y_pred = self.rating_predictor.predict(X_test)
                mse = mean_squared_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)
                
                logger.info(f"Modelo de rating entrenado - MSE: {mse:.3f}, R2: {r2:.3f}")
            else:
                self.rating_predictor.fit(X_scaled, y_rating)
                logger.info("Modelo de rating entrenado con datos limitados")
            
            # Entrenar modelo de preferencia de precio
            self.price_preference_model.fit(X_scaled, y_price_pref)
            
            # Entrenar modelo de preferencia de tamaño
            self.size_preference_model.fit(X_scaled, y_size_pref)
            
            # Entrenar clustering de presentaciones
            if len(X_scaled) >= 6:
                self.presentation_clustering.fit(X_scaled)
                logger.info("Clustering de presentaciones entrenado")
            
            self.is_trained = True
            self.last_training = datetime.now()
            
            # Guardar modelos
            self.save_models()
            
            logger.info(f"Sistema de puntuación por presentación entrenado con {len(X)} muestras")
            return True
            
        except Exception as e:
            logger.error(f"Error entrenando modelos de presentación: {e}")
            return False
    
    def predict_presentation_rating(self, presentation: Dict, beverage: Dict, 
                                  user_responses: Dict) -> Dict[str, float]:
        """Predice rating y preferencias para una presentación específica"""
        try:
            # Extraer características
            features = self.extract_presentation_features(presentation, beverage, user_responses)
            
            if not self.is_trained:
                # Usar heurísticas si no hay modelo entrenado
                return self._heuristic_presentation_prediction(presentation, beverage, user_responses)
            
            # Escalar características
            features_scaled = self.feature_scaler.transform(features.reshape(1, -1))
            
            # Predicciones
            rating_pred = self.rating_predictor.predict(features_scaled)[0]
            price_pref = self.price_preference_model.predict(features_scaled)[0]
            size_pref = self.size_preference_model.predict(features_scaled)[0]
            
            # Obtener cluster
            cluster = self.presentation_clustering.predict(features_scaled)[0]
            
            # Aplicar ajustes contextuales
            adjusted_rating = self._apply_contextual_adjustments(
                rating_pred, presentation, beverage, user_responses
            )
            
            return {
                'predicted_rating': max(1.0, min(5.0, adjusted_rating)),
                'price_preference_score': float(price_pref),
                'size_preference_score': float(size_pref),
                'presentation_cluster': int(cluster),
                'confidence': min(0.95, len(self.presentation_ratings) / 100.0)
            }
            
        except Exception as e:
            logger.error(f"Error prediciendo rating de presentación: {e}")
            return self._heuristic_presentation_prediction(presentation, beverage, user_responses)
    
    def _heuristic_presentation_prediction(self, presentation: Dict, beverage: Dict, 
                                         user_responses: Dict) -> Dict[str, float]:
        """Predicción heurística cuando no hay modelo entrenado"""
        base_score = 3.0
        
        ml = presentation.get('ml', 0)
        precio = presentation.get('precio', 0)
        price_per_ml = precio / max(ml, 1)
        
        response_str = str(user_responses.values()).lower()
        
        # Ajustes por tamaño
        size_category = self.categorize_presentation_size(ml)
        
        if 'activo' in response_str:
            if size_category in ['mini', 'individual']:
                base_score += 0.5  # Prefiere portabilidad
            elif size_category == 'familiar':
                base_score -= 0.3
        
        if 'familiar' in response_str or 'compartir' in response_str:
            if size_category == 'familiar':
                base_score += 0.8
            elif size_category == 'mini':
                base_score -= 0.4
        
        # Ajustes por precio
        if 'economico' in response_str or 'barato' in response_str:
            if price_per_ml < 0.05:
                base_score += 0.6
            elif price_per_ml > 0.1:
                base_score -= 0.7
        
        # Ajustes por tipo de bebida
        categories = beverage.get('categorias_ml', [])
        if 'sin_azucar' in categories and 'salud' in response_str:
            base_score += 0.4
        
        return {
            'predicted_rating': max(1.0, min(5.0, base_score)),
            'price_preference_score': 3.0,
            'size_preference_score': 3.0,
            'presentation_cluster': 0,
            'confidence': 0.3
        }
    
    def _apply_contextual_adjustments(self, base_rating: float, presentation: Dict, 
                                    beverage: Dict, user_responses: Dict) -> float:
        """Aplica ajustes contextuales específicos por presentación"""
        adjusted = base_rating
        
        ml = presentation.get('ml', 0)
        precio = presentation.get('precio', 0)
        
        # Obtener preferencias históricas del usuario
        user_session = user_responses.get('session_id')
        if user_session in self.user_preferences:
            user_prefs = self.user_preferences[user_session]
            
            # Ajuste por preferencias de tamaño históricas
            size_category = self.categorize_presentation_size(ml)
            if size_category in user_prefs.get('size_preferences', {}):
                historical_ratings = user_prefs['size_preferences'][size_category]
                if historical_ratings:
                    avg_size_rating = np.mean(historical_ratings)
                    if avg_size_rating > 3.5:
                        adjusted += 0.3
                    elif avg_size_rating < 2.5:
                        adjusted -= 0.3
            
            # Ajuste por sensibilidad al precio
            price_sensitivity = user_prefs.get('price_sensitivity', 0.0)
            price_per_ml = precio / max(ml, 1)
            
            if price_per_ml > 0.08:  # Precio alto
                adjusted += price_sensitivity * 0.5  # price_sensitivity negativo reduce rating
        
        return adjusted
    
    def get_best_presentations_for_user(self, bebidas: List[Dict], user_responses: Dict, 
                                      top_n: int = 10) -> List[Dict]:
        """Obtiene las mejores presentaciones específicas para un usuario"""
        try:
            presentation_scores = []
            
            for bebida in bebidas:
                for presentation in bebida.get('presentaciones', []):
                    prediction = self.predict_presentation_rating(presentation, bebida, user_responses)
                    
                    presentation_with_score = {
                        'beverage': bebida,
                        'presentation': presentation,
                        'prediction': prediction,
                        'combined_score': prediction['predicted_rating'] * prediction['confidence'],
                        'presentation_id': presentation.get('presentation_id', f"{bebida['id']}_{presentation['ml']}")
                    }
                    
                    presentation_scores.append(presentation_with_score)
            
            # Ordenar por score combinado
            presentation_scores.sort(key=lambda x: x['combined_score'], reverse=True)
            
            return presentation_scores[:top_n]
            
        except Exception as e:
            logger.error(f"Error obteniendo mejores presentaciones: {e}")
            return []
    
    def analyze_user_size_preferences(self, user_session: str) -> Dict[str, Any]:
        """Analiza preferencias de tamaño de un usuario específico"""
        if user_session not in self.user_preferences:
            return {'status': 'no_data'}
        
        try:
            user_prefs = self.user_preferences[user_session]
            size_prefs = user_prefs.get('size_preferences', {})
            
            analysis = {
                'preferred_sizes': [],
                'avoided_sizes': [],
                'price_sensitivity': user_prefs.get('price_sensitivity', 0.0),
                'total_ratings': user_prefs.get('total_ratings', 0)
            }
            
            for size_category, ratings in size_prefs.items():
                if ratings:
                    avg_rating = np.mean(ratings)
                    if avg_rating >= 4.0:
                        analysis['preferred_sizes'].append({
                            'category': size_category,
                            'average_rating': avg_rating,
                            'total_ratings': len(ratings)
                        })
                    elif avg_rating <= 2.0:
                        analysis['avoided_sizes'].append({
                            'category': size_category,
                            'average_rating': avg_rating,
                            'total_ratings': len(ratings)
                        })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando preferencias de usuario: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def save_models(self):
        """Guarda modelos y datos del sistema"""
        try:
            model_data = {
                'rating_predictor': self.rating_predictor,
                'price_preference_model': self.price_preference_model,
                'size_preference_model': self.size_preference_model,
                'presentation_clustering': self.presentation_clustering,
                'feature_scaler': self.feature_scaler,
                'price_scaler': self.price_scaler,
                'size_category_encoder': self.size_category_encoder,
                'presentation_ratings': self.presentation_ratings,
                'user_preferences': self.user_preferences,
                'presentation_stats': getattr(self, 'presentation_stats', {}),
                'size_categories': self.size_categories,
                'size_preference_factors': self.size_preference_factors,
                'is_trained': self.is_trained,
                'model_version': self.model_version,
                'last_training': self.last_training.isoformat() if self.last_training else None
            }
            
            model_path = self.models_dir / 'presentation_rating_system.joblib'
            joblib.dump(model_data, model_path)
            logger.info(f"Sistema de puntuación por presentación guardado en {model_path}")
            
        except Exception as e:
            logger.error(f"Error guardando sistema: {e}")
    
    def load_models(self):
        """Carga modelos y datos guardados"""
        try:
            model_path = self.models_dir / 'presentation_rating_system.joblib'
            if model_path.exists():
                model_data = joblib.load(model_path)
                
                self.rating_predictor = model_data.get('rating_predictor', self.rating_predictor)
                self.price_preference_model = model_data.get('price_preference_model', self.price_preference_model)
                self.size_preference_model = model_data.get('size_preference_model', self.size_preference_model)
                self.presentation_clustering = model_data.get('presentation_clustering', self.presentation_clustering)
                self.feature_scaler = model_data.get('feature_scaler', self.feature_scaler)
                self.price_scaler = model_data.get('price_scaler', self.price_scaler)
                self.size_category_encoder = model_data.get('size_category_encoder', self.size_category_encoder)
                self.presentation_ratings = model_data.get('presentation_ratings', [])
                self.user_preferences = model_data.get('user_preferences', {})
                self.presentation_stats = model_data.get('presentation_stats', {})
                self.size_categories = model_data.get('size_categories', self.size_categories)
                self.size_preference_factors = model_data.get('size_preference_factors', self.size_preference_factors)
                self.is_trained = model_data.get('is_trained', False)
                self.model_version = model_data.get('model_version', self.model_version)
                
                last_training_str = model_data.get('last_training')
                if last_training_str:
                    self.last_training = datetime.fromisoformat(last_training_str)
                
                logger.info(f"Sistema cargado: {len(self.presentation_ratings)} ratings, {len(self.user_preferences)} usuarios")
            else:
                logger.info("No se encontraron modelos guardados")
                
        except Exception as e:
            logger.error(f"Error cargando sistema: {e}")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema"""
        return {
            'is_trained': self.is_trained,
            'total_presentation_ratings': len(self.presentation_ratings),
            'total_users_tracked': len(self.user_preferences),
            'presentation_stats_cached': len(getattr(self, 'presentation_stats', {})),
            'size_categories': len(self.size_categories),
            'model_version': self.model_version,
            'last_training': self.last_training.isoformat() if self.last_training else None,
            'clustering_clusters': self.presentation_clustering.n_clusters
        }


# Instancia global del sistema de puntuación por presentación
presentation_rating_system = PresentationRatingSystem()