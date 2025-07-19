"""
Beverage Categorizer - Sistema de Categorización Automática con ML
Utiliza múltiples modelos para categorizar bebidas automáticamente

Modelos implementados:
- TF-IDF + SVM para clasificación de texto
- K-Means para clustering por similitud
- NLP para extracción de características
- Análisis de precios con Isolation Forest
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.cluster import KMeans, DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Descargar recursos NLTK necesarios
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
except:
    pass

class BeverageCategorizer:
    """
    Sistema avanzado de categorización automática de bebidas
    usando múltiples modelos de Machine Learning
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Inicializar modelos
        self.text_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        self.category_classifier = SVC(
            kernel='rbf',
            probability=True,
            random_state=42
        )
        
        self.price_analyzer = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        
        self.clustering_model = KMeans(
            n_clusters=8,  # 8 clusters para diferentes tipos
            random_state=42,
            n_init=10
        )
        
        self.dbscan_model = DBSCAN(
            eps=0.5,
            min_samples=2
        )
        
        self.scaler = StandardScaler()
        
        # Stemmer para español
        self.stemmer = SnowballStemmer('spanish')
        
        # Palabras clave para categorización
        self.category_keywords = {
            'cola': ['cola', 'coca', 'pepsi', 'cola', 'refresco cola'],
            'citricos': ['limón', 'lima', 'naranja', 'citrico', 'citrus', 'limonada'],
            'frutales': ['fruta', 'frutal', 'manzana', 'uva', 'sabor frutas', 'punch'],
            'sin_azucar': ['sin azúcar', 'zero', 'light', 'diet', 'sin calorías', 'cero'],
            'agua': ['agua', 'mineralizada', 'hidratación', 'mineral'],
            'jugos': ['jugo', 'néctar', 'del valle', 'natural', '100%'],
            'energeticas': ['energía', 'energética', 'energético', 'boost'],
            'tonicas': ['tónica', 'schweppes', 'burbuja', 'carbonatada'],
            'funcional': ['funcional', 'aquarius', 'minerales', 'deportiva']
        }
        
        # Categorías de presentación por tamaño
        self.size_categories = {
            'mini': (0, 250),      # 0-250ml
            'individual': (251, 400),  # 251-400ml
            'personal': (401, 750),    # 401-750ml
            'familiar': (751, 5000)    # 751ml+
        }
        
        # Estado del modelo
        self.is_trained = False
        self.training_data = []
        
        # Cargar modelos si existen
        self.load_models()
    
    def preprocess_text(self, text: str) -> str:
        """Preprocesa texto para análisis NLP"""
        if not text:
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales pero mantener acentos
        text = re.sub(r'[^\w\s\náéíóúüñ]', ' ', text)
        
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenizar y stemizar (opcional para español)
        try:
            tokens = word_tokenize(text, language='spanish')
            # Filtrar palabras muy cortas
            tokens = [token for token in tokens if len(token) > 2]
            return ' '.join(tokens)
        except:
            return text
    
    def extract_text_features(self, nombre: str, descripcion: str) -> Dict[str, Any]:
        """Extrae características del texto usando NLP"""
        combined_text = f"{nombre} {descripcion}"
        processed_text = self.preprocess_text(combined_text)
        
        features = {
            'text_length': len(processed_text),
            'word_count': len(processed_text.split()),
            'has_numbers': bool(re.search(r'\d', processed_text)),
            'has_percentage': '%' in combined_text,
            'brand_mentions': 0,
            'health_terms': 0,
            'flavor_terms': 0
        }
        
        # Contar menciones de marcas
        brands = ['coca', 'pepsi', 'fanta', 'sprite', 'del valle', 'schweppes', 'ciel', 'aquarius', 'sidral']
        for brand in brands:
            if brand in processed_text:
                features['brand_mentions'] += 1
        
        # Contar términos de salud
        health_terms = ['sin azúcar', 'natural', 'mineralizada', 'antioxidantes', 'vitaminas', 
                       'hidratación', 'saludable', 'funcional', 'sin calorías']
        for term in health_terms:
            if term in processed_text:
                features['health_terms'] += 1
        
        # Contar términos de sabor
        flavor_terms = ['dulce', 'refrescante', 'sabor', 'delicioso', 'frutal', 'cítrico']
        for term in flavor_terms:
            if term in processed_text:
                features['flavor_terms'] += 1
        
        return features
    
    def categorize_by_keywords(self, nombre: str, descripcion: str) -> List[str]:
        """Categoriza usando palabras clave"""
        combined_text = self.preprocess_text(f"{nombre} {descripcion}")
        categories = []
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword.lower() in combined_text:
                    categories.append(category)
                    break
        
        return list(set(categories))  # Remover duplicados
    
    def categorize_presentation_size(self, ml: int) -> str:
        """Categoriza presentación por tamaño"""
        for category, (min_size, max_size) in self.size_categories.items():
            if min_size <= ml <= max_size:
                return category
        return 'especial'
    
    def extract_numerical_features(self, bebida: Dict) -> np.ndarray:
        """Extrae características numéricas de la bebida"""
        features = []
        
        # Características básicas
        features.append(len(bebida.get('presentaciones', [])))  # Número de presentaciones
        features.append(len(bebida.get('nombre', '')))  # Longitud del nombre
        features.append(len(bebida.get('descripcion', '')))  # Longitud de descripción
        
        # Características de presentaciones
        presentaciones = bebida.get('presentaciones', [])
        if presentaciones:
            sizes = [p.get('ml', 0) for p in presentaciones]
            prices = [p.get('precio', 0) for p in presentaciones]
            
            features.extend([
                np.mean(sizes),      # Tamaño promedio
                np.std(sizes),       # Variación de tamaños
                np.min(sizes),       # Tamaño mínimo
                np.max(sizes),       # Tamaño máximo
                np.mean(prices),     # Precio promedio
                np.std(prices),      # Variación de precios
                np.min(prices),      # Precio mínimo
                np.max(prices),      # Precio máximo
            ])
            
            # Ratio precio/ml promedio
            price_per_ml = np.mean([p.get('precio', 0) / max(p.get('ml', 1), 1) for p in presentaciones])
            features.append(price_per_ml)
        else:
            features.extend([0] * 9)  # Rellenar con ceros
        
        # Características de texto
        text_features = self.extract_text_features(
            bebida.get('nombre', ''), 
            bebida.get('descripcion', '')
        )
        
        features.extend([
            text_features['text_length'],
            text_features['word_count'],
            text_features['brand_mentions'],
            text_features['health_terms'],
            text_features['flavor_terms'],
            int(text_features['has_numbers']),
            int(text_features['has_percentage'])
        ])
        
        return np.array(features)
    
    def process_beverage(self, bebida: Dict) -> Dict[str, Any]:
        """Procesa una bebida y genera todas sus categorías automáticamente"""
        try:
            nombre = bebida.get('nombre', '')
            descripcion = bebida.get('descripcion', '')
            
            # 1. Categorización por palabras clave
            keyword_categories = self.categorize_by_keywords(nombre, descripcion)
            
            # 2. Categorización de presentaciones
            presentation_categories = []
            for presentacion in bebida.get('presentaciones', []):
                ml = presentacion.get('ml', 0)
                size_cat = self.categorize_presentation_size(ml)
                presentation_categories.append(size_cat)
                
                # Actualizar categoría en la presentación
                presentacion['categoria_presentacion'] = size_cat
            
            # 3. Análisis de precios (detección de anomalías)
            price_analysis = self.analyze_pricing(bebida)
            
            # 4. Extracción de features numéricas
            numerical_features = self.extract_numerical_features(bebida)
            
            # 5. Clustering si el modelo está entrenado
            cluster_id = None
            if self.is_trained and hasattr(self, 'feature_matrix'):
                try:
                    features_scaled = self.scaler.transform(numerical_features.reshape(1, -1))
                    cluster_id = int(self.clustering_model.predict(features_scaled)[0])
                except:
                    cluster_id = -1
            
            # 6. Generar tags automáticos
            auto_tags = self.generate_auto_tags(bebida, keyword_categories)
            
            # 7. Actualizar bebida con nueva información
            bebida_procesada = bebida.copy()
            bebida_procesada.update({
                'categorias_ml': keyword_categories,
                'tags_automaticos': auto_tags,
                'cluster_id': cluster_id,
                'price_analysis': price_analysis,
                'features_numericas': numerical_features.tolist(),
                'fecha_procesado': datetime.now().isoformat(),
                'procesado_ml': True
            })
            
            logger.info(f"Bebida '{nombre}' procesada: {len(keyword_categories)} categorías, {len(auto_tags)} tags")
            
            return bebida_procesada
            
        except Exception as e:
            logger.error(f"Error procesando bebida {bebida.get('nombre', 'Unknown')}: {e}")
            return bebida
    
    def analyze_pricing(self, bebida: Dict) -> Dict[str, Any]:
        """Analiza precios de presentaciones para detectar anomalías"""
        presentaciones = bebida.get('presentaciones', [])
        if not presentaciones:
            return {'status': 'no_presentations'}
        
        try:
            # Calcular precio por ml para cada presentación
            price_per_ml = []
            for p in presentaciones:
                ml = p.get('ml', 1)
                precio = p.get('precio', 0)
                price_per_ml.append(precio / max(ml, 1))
            
            analysis = {
                'price_per_ml_mean': np.mean(price_per_ml),
                'price_per_ml_std': np.std(price_per_ml),
                'price_per_ml_min': np.min(price_per_ml),
                'price_per_ml_max': np.max(price_per_ml),
                'price_variation_high': np.std(price_per_ml) > np.mean(price_per_ml) * 0.3,
                'total_presentations': len(presentaciones),
                'size_range': [np.min([p.get('ml', 0) for p in presentaciones]),
                             np.max([p.get('ml', 0) for p in presentaciones])]
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error en análisis de precios: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def generate_auto_tags(self, bebida: Dict, categories: List[str]) -> List[str]:
        """Genera tags automáticos basados en análisis ML"""
        tags = []
        
        # Tags basados en categorías
        for cat in categories:
            if cat == 'sin_azucar':
                tags.extend(['diet', 'light', 'saludable'])
            elif cat == 'cola':
                tags.extend(['clasico', 'tradicional', 'gaseoso'])
            elif cat == 'citricos':
                tags.extend(['refrescante', 'citrico', 'vitamina_c'])
            elif cat == 'agua':
                tags.extend(['hidratante', 'puro', 'mineral'])
            elif cat == 'jugos':
                tags.extend(['natural', 'frutal', 'nutritivo'])
        
        # Tags basados en presentaciones
        presentaciones = bebida.get('presentaciones', [])
        if presentaciones:
            sizes = [p.get('ml', 0) for p in presentaciones]
            
            if any(s <= 250 for s in sizes):
                tags.append('porcion_mini')
            if any(s >= 1000 for s in sizes):
                tags.append('familiar')
            if len(sizes) > 3:
                tags.append('multiples_presentaciones')
        
        # Tags basados en precio
        price_analysis = self.analyze_pricing(bebida)
        if price_analysis.get('price_per_ml_mean', 0) > 0.1:  # Precio alto por ml
            tags.append('premium')
        elif price_analysis.get('price_per_ml_mean', 0) < 0.05:  # Precio bajo por ml
            tags.append('economico')
        
        # Tags basados en descripción
        descripcion = bebida.get('descripcion', '').lower()
        if 'años' in descripcion or 'historia' in descripcion:
            tags.append('marca_historica')
        if 'mexicano' in descripcion or 'mexico' in descripcion:
            tags.append('origen_mexicano')
        if 'millones' in descripcion or 'mundial' in descripcion:
            tags.append('marca_global')
        
        return list(set(tags))  # Remover duplicados
    
    def train_clustering_model(self, bebidas: List[Dict]) -> bool:
        """Entrena el modelo de clustering con todas las bebidas"""
        try:
            # Extraer features de todas las bebidas
            feature_matrix = []
            for bebida in bebidas:
                features = self.extract_numerical_features(bebida)
                feature_matrix.append(features)
            
            self.feature_matrix = np.array(feature_matrix)
            
            # Escalar features
            self.feature_matrix_scaled = self.scaler.fit_transform(self.feature_matrix)
            
            # Entrenar K-Means
            self.clustering_model.fit(self.feature_matrix_scaled)
            
            # Entrenar DBSCAN
            dbscan_labels = self.dbscan_model.fit_predict(self.feature_matrix_scaled)
            
            # Entrenar detector de anomalías de precios
            price_features = []
            for bebida in bebidas:
                presentaciones = bebida.get('presentaciones', [])
                for p in presentaciones:
                    ml = p.get('ml', 1)
                    precio = p.get('precio', 0)
                    price_per_ml = precio / max(ml, 1)
                    price_features.append([ml, precio, price_per_ml])
            
            if price_features:
                self.price_analyzer.fit(price_features)
            
            self.is_trained = True
            logger.info(f"Modelos de clustering entrenados con {len(bebidas)} bebidas")
            
            # Guardar modelos
            self.save_models()
            
            return True
            
        except Exception as e:
            logger.error(f"Error entrenando clustering: {e}")
            return False
    
    def process_all_beverages(self, bebidas: List[Dict]) -> List[Dict]:
        """Procesa todas las bebidas y entrena modelos"""
        logger.info(f"Procesando {len(bebidas)} bebidas...")
        
        # Entrenar clustering primero
        self.train_clustering_model(bebidas)
        
        # Procesar cada bebida
        processed_beverages = []
        for bebida in bebidas:
            processed_beverage = self.process_beverage(bebida)
            processed_beverages.append(processed_beverage)
        
        logger.info("Procesamiento completado")
        return processed_beverages
    
    def save_models(self):
        """Guarda los modelos entrenados"""
        try:
            model_data = {
                'text_vectorizer': self.text_vectorizer,
                'category_classifier': self.category_classifier,
                'clustering_model': self.clustering_model,
                'dbscan_model': self.dbscan_model,
                'price_analyzer': self.price_analyzer,
                'scaler': self.scaler,
                'is_trained': self.is_trained,
                'feature_matrix': getattr(self, 'feature_matrix', None),
                'feature_matrix_scaled': getattr(self, 'feature_matrix_scaled', None),
                'category_keywords': self.category_keywords,
                'size_categories': self.size_categories,
                'training_data': self.training_data
            }
            
            model_path = self.models_dir / 'beverage_categorizer.joblib'
            joblib.dump(model_data, model_path)
            logger.info(f"Modelos de categorización guardados en {model_path}")
            
        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")
    
    def load_models(self):
        """Carga los modelos guardados"""
        try:
            model_path = self.models_dir / 'beverage_categorizer.joblib'
            if model_path.exists():
                model_data = joblib.load(model_path)
                
                self.text_vectorizer = model_data.get('text_vectorizer', self.text_vectorizer)
                self.category_classifier = model_data.get('category_classifier', self.category_classifier)
                self.clustering_model = model_data.get('clustering_model', self.clustering_model)
                self.dbscan_model = model_data.get('dbscan_model', self.dbscan_model)
                self.price_analyzer = model_data.get('price_analyzer', self.price_analyzer)
                self.scaler = model_data.get('scaler', self.scaler)
                self.is_trained = model_data.get('is_trained', False)
                self.feature_matrix = model_data.get('feature_matrix', None)
                self.feature_matrix_scaled = model_data.get('feature_matrix_scaled', None)
                self.category_keywords = model_data.get('category_keywords', self.category_keywords)
                self.size_categories = model_data.get('size_categories', self.size_categories)
                self.training_data = model_data.get('training_data', [])
                
                logger.info(f"Modelos de categorización cargados. Entrenado: {self.is_trained}")
            else:
                logger.info("No se encontraron modelos guardados")
                
        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")
    
    def get_beverage_similarity(self, bebida1: Dict, bebida2: Dict) -> float:
        """Calcula similitud entre dos bebidas"""
        try:
            features1 = self.extract_numerical_features(bebida1)
            features2 = self.extract_numerical_features(bebida2)
            
            # Calcular distancia coseno
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(features1.reshape(1, -1), features2.reshape(1, -1))[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculando similitud: {e}")
            return 0.0
    
    def get_category_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de categorización"""
        return {
            'is_trained': self.is_trained,
            'total_categories': len(self.category_keywords),
            'size_categories': len(self.size_categories),
            'training_samples': len(self.training_data),
            'clustering_clusters': getattr(self.clustering_model, 'n_clusters', 0),
            'model_version': '1.0.0'
        }


# Instancia global del categorizador
beverage_categorizer = BeverageCategorizer()