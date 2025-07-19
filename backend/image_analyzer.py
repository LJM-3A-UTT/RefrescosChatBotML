"""
Image Analyzer - Análisis de Imágenes de Bebidas con CNN
Utiliza modelos pre-entrenados para extraer características visuales

Funcionalidades:
- Extracción de features visuales con CNN pre-entrenado
- Detección de colores dominantes
- Análisis de formas y presentaciones
- Categorización visual automática
"""

import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import torch
import torchvision.transforms as transforms
import torchvision.models as models
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import requests
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional, Any
import json
from datetime import datetime
import base64
import io
import warnings
warnings.filterwarnings('ignore')

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """
    Analizador de imágenes de bebidas usando CNN y visión por computadora
    """
    
    def __init__(self, models_dir: str = "models"):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        # Cargar modelo CNN pre-entrenado
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_cnn_model()
        
        # Transformaciones para el modelo
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Clustering para colores
        self.color_clusters = 8
        
        # Categorías de colores principales
        self.color_categories = {
            'rojo': [(255, 0, 0), (200, 0, 0), (255, 50, 50)],
            'azul': [(0, 0, 255), (0, 50, 200), (50, 100, 255)],
            'verde': [(0, 255, 0), (50, 200, 50), (100, 255, 100)],
            'amarillo': [(255, 255, 0), (255, 200, 0), (255, 255, 50)],
            'naranja': [(255, 165, 0), (255, 140, 0), (255, 180, 50)],
            'violeta': [(128, 0, 128), (150, 50, 150), (180, 100, 180)],
            'negro': [(0, 0, 0), (50, 50, 50), (30, 30, 30)],
            'blanco': [(255, 255, 255), (240, 240, 240), (250, 250, 250)],
            'transparente': [(200, 200, 200), (220, 220, 220), (180, 180, 180)]
        }
        
        # Patrones de presentación
        self.container_patterns = {
            'lata': ['cilindrica', 'metalica', 'pequena'],
            'botella_plastico': ['botella', 'plastico', 'transparente'],
            'botella_vidrio': ['botella', 'vidrio', 'reflectante'],
            'tetrapack': ['carton', 'rectangular', 'brick'],
            'pouch': ['flexible', 'bolsa', 'suave']
        }
        
        # Estado del modelo
        self.is_initialized = False
        self.feature_cache = {}
        
        # Inicializar
        self.initialize()
    
    def load_cnn_model(self):
        """Carga modelo CNN pre-entrenado"""
        try:
            # Usar ResNet18 pre-entrenado
            self.cnn_model = models.resnet18(pretrained=True)
            self.cnn_model.eval()
            self.cnn_model.to(self.device)
            
            # Remover la última capa para extraer features
            self.feature_extractor = torch.nn.Sequential(*list(self.cnn_model.children())[:-1])
            self.feature_extractor.eval()
            
            logger.info("Modelo CNN cargado exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando modelo CNN: {e}")
            self.cnn_model = None
            self.feature_extractor = None
    
    def initialize(self):
        """Inicializa el analizador"""
        try:
            self.is_initialized = True
            logger.info("Image Analyzer inicializado")
        except Exception as e:
            logger.error(f"Error inicializando Image Analyzer: {e}")
    
    def load_image_from_path(self, image_path: str) -> Optional[np.ndarray]:
        """Carga imagen desde ruta local"""
        try:
            # Intentar cargar desde ruta local
            local_path = Path(f"static{image_path}")
            if local_path.exists():
                image = cv2.imread(str(local_path))
                if image is not None:
                    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Si no existe localmente, intentar desde URL (si es accesible)
            if image_path.startswith('http'):
                response = requests.get(image_path, timeout=5)
                if response.status_code == 200:
                    image_array = np.frombuffer(response.content, np.uint8)
                    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                    if image is not None:
                        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            logger.warning(f"No se pudo cargar imagen: {image_path}")
            return None
            
        except Exception as e:
            logger.error(f"Error cargando imagen {image_path}: {e}")
            return None
    
    def extract_cnn_features(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Extrae features usando CNN pre-entrenado"""
        if self.feature_extractor is None:
            return None
        
        try:
            # Convertir a PIL Image
            pil_image = Image.fromarray(image)
            
            # Aplicar transformaciones
            tensor = self.transform(pil_image).unsqueeze(0).to(self.device)
            
            # Extraer features
            with torch.no_grad():
                features = self.feature_extractor(tensor)
                features = features.view(features.size(0), -1)
                features = features.cpu().numpy().flatten()
            
            return features
            
        except Exception as e:
            logger.error(f"Error extrayendo features CNN: {e}")
            return None
    
    def extract_color_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extrae características de color de la imagen"""
        try:
            # Redimensionar para acelerar procesamiento
            small_image = cv2.resize(image, (100, 100))
            
            # Convertir a formato para clustering
            pixels = small_image.reshape(-1, 3)
            
            # K-means clustering para colores dominantes
            kmeans = KMeans(n_clusters=self.color_clusters, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Obtener colores dominantes
            dominant_colors = kmeans.cluster_centers_.astype(int)
            
            # Calcular porcentajes de cada color
            labels = kmeans.labels_
            percentages = []
            for i in range(self.color_clusters):
                count = np.sum(labels == i)
                percentage = count / len(labels) * 100
                percentages.append(percentage)
            
            # Ordenar por porcentaje
            color_data = list(zip(dominant_colors, percentages))
            color_data.sort(key=lambda x: x[1], reverse=True)
            
            # Clasificar colores principales
            color_categories = self.classify_colors([color[0] for color in color_data[:3]])
            
            # Calcular métricas adicionales
            brightness = np.mean(image)
            contrast = np.std(image)
            
            return {
                'dominant_colors': [color[0].tolist() for color in color_data[:5]],
                'color_percentages': [color[1] for color in color_data[:5]],
                'color_categories': color_categories,
                'brightness': float(brightness),
                'contrast': float(contrast),
                'total_colors': self.color_clusters
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo características de color: {e}")
            return {}
    
    def classify_colors(self, colors: List[np.ndarray]) -> List[str]:
        """Clasifica colores en categorías predefinidas"""
        classified = []
        
        for color in colors:
            min_distance = float('inf')
            best_category = 'otro'
            
            for category, reference_colors in self.color_categories.items():
                for ref_color in reference_colors:
                    distance = np.linalg.norm(color - np.array(ref_color))
                    if distance < min_distance:
                        min_distance = distance
                        best_category = category
            
            classified.append(best_category)
        
        return classified
    
    def extract_shape_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extrae características de forma y contorno"""
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Aplicar filtros para mejorar detección
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Detección de bordes
            edges = cv2.Canny(blurred, 50, 150)
            
            # Encontrar contornos
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return {}
            
            # Analizar contorno principal (más grande)
            main_contour = max(contours, key=cv2.contourArea)
            
            # Calcular características del contorno
            area = cv2.contourArea(main_contour)
            perimeter = cv2.arcLength(main_contour, True)
            
            # Aproximar contorno
            epsilon = 0.02 * perimeter
            approx = cv2.approxPolyDP(main_contour, epsilon, True)
            
            # Calcular bounding box
            x, y, w, h = cv2.boundingRect(main_contour)
            aspect_ratio = w / h if h > 0 else 0
            
            # Calcular circularidad
            circularity = 4 * np.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
            
            return {
                'area': float(area),
                'perimeter': float(perimeter),
                'aspect_ratio': float(aspect_ratio),
                'circularity': float(circularity),
                'vertices': len(approx),
                'bounding_box': [int(x), int(y), int(w), int(h)],
                'shape_complexity': len(contours)
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo características de forma: {e}")
            return {}
    
    def classify_container_type(self, shape_features: Dict, color_features: Dict) -> str:
        """Clasifica el tipo de envase basado en características visuales"""
        try:
            aspect_ratio = shape_features.get('aspect_ratio', 1.0)
            circularity = shape_features.get('circularity', 0.0)
            brightness = color_features.get('brightness', 128)
            dominant_colors = color_features.get('color_categories', [])
            
            # Reglas de clasificación
            if aspect_ratio > 2.5:  # Muy alto
                if 'transparente' in dominant_colors or brightness > 200:
                    return 'botella_plastico'
                else:
                    return 'lata'
            elif aspect_ratio < 0.8:  # Muy ancho
                return 'tetrapack'
            elif circularity > 0.7:  # Muy circular
                return 'lata'
            elif 'transparente' in dominant_colors or 'blanco' in dominant_colors:
                return 'botella_plastico'
            else:
                return 'botella_vidrio'
            
        except Exception as e:
            logger.error(f"Error clasificando tipo de envase: {e}")
            return 'desconocido'
    
    def analyze_presentation_image(self, image_path: str) -> Dict[str, Any]:
        """Analiza una imagen de presentación específica"""
        try:
            # Cargar imagen
            image = self.load_image_from_path(image_path)
            if image is None:
                return {'error': 'No se pudo cargar la imagen', 'path': image_path}
            
            # Extraer características
            analysis = {
                'image_path': image_path,
                'image_size': image.shape[:2],  # (height, width)
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            # Features CNN
            cnn_features = self.extract_cnn_features(image)
            if cnn_features is not None:
                analysis['cnn_features'] = cnn_features.tolist()
                analysis['cnn_feature_size'] = len(cnn_features)
            
            # Características de color
            color_features = self.extract_color_features(image)
            analysis['color_analysis'] = color_features
            
            # Características de forma
            shape_features = self.extract_shape_features(image)
            analysis['shape_analysis'] = shape_features
            
            # Clasificación de envase
            container_type = self.classify_container_type(shape_features, color_features)
            analysis['container_type'] = container_type
            
            # Generar tags visuales
            visual_tags = self.generate_visual_tags(color_features, shape_features, container_type)
            analysis['visual_tags'] = visual_tags
            
            logger.info(f"Imagen analizada: {image_path} -> {container_type}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analizando imagen {image_path}: {e}")
            return {'error': str(e), 'path': image_path}
    
    def generate_visual_tags(self, color_features: Dict, shape_features: Dict, container_type: str) -> List[str]:
        """Genera tags automáticos basados en análisis visual"""
        tags = []
        
        # Tags por tipo de envase
        if container_type == 'lata':
            tags.extend(['metal', 'cilindrico', 'reciclable'])
        elif container_type == 'botella_plastico':
            tags.extend(['plastico', 'transparente', 'ligero'])
        elif container_type == 'botella_vidrio':
            tags.extend(['vidrio', 'premium', 'reutilizable'])
        elif container_type == 'tetrapack':
            tags.extend(['carton', 'economico', 'rectangular'])
        
        # Tags por colores dominantes
        color_categories = color_features.get('color_categories', [])
        for color in color_categories[:2]:  # Top 2 colores
            if color == 'rojo':
                tags.extend(['energetico', 'llamativo'])
            elif color == 'azul':
                tags.extend(['refrescante', 'frio'])
            elif color == 'verde':
                tags.extend(['natural', 'saludable'])
            elif color == 'amarillo':
                tags.extend(['citrico', 'brillante'])
            elif color == 'naranja':
                tags.extend(['frutal', 'vibrante'])
        
        # Tags por forma
        aspect_ratio = shape_features.get('aspect_ratio', 1.0)
        if aspect_ratio > 3.0:
            tags.append('formato_alto')
        elif aspect_ratio < 0.7:
            tags.append('formato_ancho')
        
        circularity = shape_features.get('circularity', 0.0)
        if circularity > 0.8:
            tags.append('forma_circular')
        
        # Tags por brillo
        brightness = color_features.get('brightness', 128)
        if brightness > 180:
            tags.append('empaque_brillante')
        elif brightness < 80:
            tags.append('empaque_oscuro')
        
        return list(set(tags))  # Remover duplicados
    
    def analyze_beverage_images(self, bebida: Dict) -> Dict[str, Any]:
        """Analiza todas las imágenes de una bebida"""
        try:
            image_analysis = {
                'beverage_id': bebida.get('id'),
                'beverage_name': bebida.get('nombre'),
                'total_presentations': len(bebida.get('presentaciones', [])),
                'image_analyses': [],
                'combined_features': {},
                'analysis_timestamp': datetime.now().isoformat()
            }
            
            all_visual_tags = []
            all_container_types = []
            all_color_categories = []
            
            # Analizar cada presentación
            for presentacion in bebida.get('presentaciones', []):
                image_path = presentacion.get('imagen_local', '')
                if image_path:
                    analysis = self.analyze_presentation_image(image_path)
                    
                    # Agregar info de presentación
                    analysis['presentation_info'] = {
                        'ml': presentacion.get('ml'),
                        'precio': presentacion.get('precio'),
                        'presentation_id': presentacion.get('presentation_id')
                    }
                    
                    image_analysis['image_analyses'].append(analysis)
                    
                    # Acumular datos para análisis combinado
                    if 'visual_tags' in analysis:
                        all_visual_tags.extend(analysis['visual_tags'])
                    if 'container_type' in analysis:
                        all_container_types.append(analysis['container_type'])
                    if 'color_analysis' in analysis and 'color_categories' in analysis['color_analysis']:
                        all_color_categories.extend(analysis['color_analysis']['color_categories'])
            
            # Análisis combinado
            if all_visual_tags:
                tag_counts = {}
                for tag in all_visual_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                image_analysis['combined_features'] = {
                    'common_visual_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
                    'container_types': list(set(all_container_types)),
                    'dominant_color_themes': list(set(all_color_categories[:5])),
                    'visual_consistency': len(set(all_container_types)) == 1  # Todas las presentaciones usan el mismo tipo de envase
                }
            
            logger.info(f"Análisis de imágenes completado para {bebida.get('nombre')}: {len(image_analysis['image_analyses'])} imágenes procesadas")
            
            return image_analysis
            
        except Exception as e:
            logger.error(f"Error analizando imágenes de bebida: {e}")
            return {'error': str(e), 'beverage_id': bebida.get('id')}
    
    def save_analysis_cache(self):
        """Guarda cache de análisis"""
        try:
            cache_path = self.models_dir / 'image_analysis_cache.json'
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.feature_cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Cache de análisis guardado: {len(self.feature_cache)} entradas")
        except Exception as e:
            logger.error(f"Error guardando cache: {e}")
    
    def load_analysis_cache(self):
        """Carga cache de análisis"""
        try:
            cache_path = self.models_dir / 'image_analysis_cache.json'
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    self.feature_cache = json.load(f)
                logger.info(f"Cache de análisis cargado: {len(self.feature_cache)} entradas")
        except Exception as e:
            logger.error(f"Error cargando cache: {e}")
    
    def get_image_similarity(self, image_path1: str, image_path2: str) -> float:
        """Calcula similitud entre dos imágenes usando features CNN"""
        try:
            # Cargar imágenes
            image1 = self.load_image_from_path(image_path1)
            image2 = self.load_image_from_path(image_path2)
            
            if image1 is None or image2 is None:
                return 0.0
            
            # Extraer features
            features1 = self.extract_cnn_features(image1)
            features2 = self.extract_cnn_features(image2)
            
            if features1 is None or features2 is None:
                return 0.0
            
            # Calcular similitud coseno
            from sklearn.metrics.pairwise import cosine_similarity
            similarity = cosine_similarity(features1.reshape(1, -1), features2.reshape(1, -1))[0][0]
            
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Error calculando similitud de imágenes: {e}")
            return 0.0
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del analizador"""
        return {
            'is_initialized': self.is_initialized,
            'cnn_model_loaded': self.cnn_model is not None,
            'device': str(self.device),
            'cached_analyses': len(self.feature_cache),
            'color_clusters': self.color_clusters,
            'supported_formats': ['jpg', 'jpeg', 'png', 'webp'],
            'analyzer_version': '1.0.0'
        }


# Instancia global del analizador de imágenes
image_analyzer = ImageAnalyzer()