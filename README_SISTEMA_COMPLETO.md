# RefrescoBot ML - Sistema Completo

## 🚀 Inicio Rápido

### Opción 1: Usar el Script Principal (RECOMENDADO)
```bash
python start.py
```
Esto abre un menú interactivo con todas las opciones disponibles.

### Opción 2: Scripts Independientes

#### 1. **Inicializar Sistema Completo**
```bash
python initialize_system.py
```
- Corrige estructura de bebidas automáticamente
- Inicializa base de datos (preserva sesiones existentes)
- Procesa bebidas con ML avanzado
- Genera datos de entrenamiento inicial

#### 2. **Panel de Administración**
```bash
python admin_system.py
```
- Estadísticas del sistema
- Gestión de base de datos
- Gestión de modelos ML
- Diagnósticos

#### 3. **Sistema de Testing**
```bash
python testing_system.py
```
- Tests del backend
- Tests de Machine Learning
- Tests del frontend
- Tests de integración

## 📊 Estructura Actual

### Bebidas Disponibles
- **Total**: 26 bebidas
- **Refrescos reales**: 14 (Coca-Cola, Fanta, Peñafiel, etc.)
- **Alternativas saludables**: 12 (Ciel, Aquarius, Del Valle, etc.)
- **Presentaciones**: 70 presentaciones únicas
- **Campo sabor**: Agregado a todas las presentaciones

### Configuración Granular (config.py)
```python
# Configuración inicial
MAX_REFRESCOS_RECOMENDADOS = 3
MAX_ALTERNATIVAS_SALUDABLES_INICIAL = 3

# Configuración de "más opciones"
MAX_ALTERNATIVAS_SALUDABLES_ADICIONAL = 3
MAX_REFRESCOS_ADICIONALES = 3

# Por tipo de usuario
MAX_ALTERNATIVAS_USUARIO_SALUDABLE = 4
MAX_REFRESCOS_USUARIO_TRADICIONAL = 3
```

## 🔧 Funcionalidades Principales

### 1. **Botón "Mostrar más opciones" Corregido**
- ✅ Funciona para usuarios regulares (muestra más refrescos)
- ✅ Funciona para usuarios saludables (muestra más alternativas)
- ✅ Respeta configuraciones granulares
- ✅ Backend devuelve `recomendaciones_adicionales` correctamente

### 2. **Mejoras Visuales**
- ✅ Imágenes centradas en tarjetas de presentación
- ✅ Tamaño aumentado de 150px a 180px
- ✅ Efectos hover y gradientes mejorados
- ✅ Mejor renderizado con object-fit: contain

### 3. **Limpieza Selectiva de BD**
- ✅ Solo limpia preguntas y bebidas en startup
- ✅ **PRESERVA sesiones para aprendizaje continuo**
- ✅ Mantiene puntuaciones y datos de entrenamiento ML

### 4. **Campo Sabor en Presentaciones**
- ✅ Cada presentación tiene campo `sabor`
- ✅ Sabores apropiados por categoría:
  - Cola: "Cola Original"
  - Cítricos: "Naranja", "Limón", "Toronja"
  - Agua: "Natural", "Tónica"
  - Etc.

## 🤖 Machine Learning Mejorado

### Variedad en Recomendaciones
El sistema ahora proporciona verdadera variedad cuando los usuarios tienen patrones de respuesta diferentes:
- **Usuarios tradicionales**: Ven refrescos variados según preferencias
- **Usuarios saludables**: Ven alternativas variadas según estilo de vida
- **Usuarios mixtos**: Ven combinación balanceada

### Configuraciones ML
- `ML_MIN_TRAINING_SAMPLES = 10`
- `ML_RETRAIN_THRESHOLD = 5`
- `KMEANS_N_CLUSTERS = 5`

## 📁 Estructura de Archivos Consolidada

### Scripts Principales (Solo usar estos)
```
start.py              # Script principal - USAR ESTE
initialize_system.py  # Inicialización completa
admin_system.py       # Panel de administración
testing_system.py     # Sistema de testing
fix_bebidas_structure.py  # Corrección de estructura
```

### Backend
```
backend/
├── server.py         # Servidor FastAPI principal
├── config.py         # Configuración (EDITABLE)
├── data/
│   ├── bebidas.json  # 26 bebidas con estructura corregida
│   └── preguntas.json
├── ml_engine.py      # Motor ML principal
├── beverage_categorizer.py  # Categorización automática
├── image_analyzer.py # Análisis de imágenes
├── presentation_rating_system.py  # Sistema de puntuación
├── data_manager.py   # Gestión de datos (limpieza selectiva)
└── static/images/bebidas/  # Imágenes reales
```

### Frontend
```
frontend/
├── src/
│   ├── App.js        # Componente principal (botón "más opciones" corregido)
│   └── App.css       # Estilos mejorados
├── package.json
└── .env              # URL del backend
```

## ⚙️ Configuración

### Variables de Entorno
```bash
# backend/.env
MONGO_URL=mongodb+srv://LJM:ljm542136@cluster0.7mlbi.mongodb.net/refrescos_chat_bot
DB_NAME=refrescos_chat_bot

# frontend/.env
REACT_APP_BACKEND_URL=http://localhost:8001
```

### Configuración Personalizable (config.py)
Puedes modificar estas variables sin tocar código:
- Número de bebidas mostradas inicialmente
- Número de bebidas por "más opciones"
- Configuración específica por tipo de usuario
- Parámetros de ML
- Mensajes del sistema

## 🧪 Testing

### Verificaciones Automáticas
- ✅ 26 bebidas cargadas correctamente
- ✅ Presentation IDs únicos
- ✅ Campo sabor en todas las presentaciones
- ✅ Botón "más opciones" para ambos tipos de usuarios
- ✅ Configuraciones granulares aplicadas
- ✅ Variedad en recomendaciones ML

### Ejecutar Tests
```bash
python testing_system.py
# Opciones:
# 1. Tests backend básicos
# 2. Tests Machine Learning
# 3. Tests frontend automatizados
# 4. Tests de integración
# 5. Tests de rendimiento
# 6. Ejecutar TODOS los tests
```

## 📝 Problemas Conocidos Resueltos

### ✅ Botón "Más opciones" no funcionaba para refrescos
**Problema**: Solo funcionaba para bebidas saludables
**Solución**: Corregido manejo de respuesta en frontend

### ✅ Siempre mostraba las mismas bebidas
**Problema**: Lógica ML no proporcionaba variedad
**Solución**: Mejorada lógica de recomendación y configuraciones granulares

### ✅ Presentation IDs duplicados
**Problema**: Múltiples presentaciones con mismo ID
**Solución**: Script automático de corrección de estructura

### ✅ Falta campo sabor
**Problema**: Presentaciones sin información de sabor
**Solución**: Campo agregado automáticamente con valores coherentes

### ✅ Limpieza de BD borraba todo
**Problema**: Se perdía el aprendizaje en cada reinicio
**Solución**: Limpieza selectiva que preserva sesiones

## 🔗 URLs del Sistema

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **Documentación API**: http://localhost:8001/docs
- **Admin Stats**: http://localhost:8001/admin/stats

## 🚨 Solución de Problemas

### Si el backend no inicia:
```bash
python admin_system.py
# Seleccionar "5. Diagnósticos del Sistema"
```

### Si aparecen bebidas duplicadas:
```bash
python fix_bebidas_structure.py
```

### Si hay problemas con ML:
```bash
python admin_system.py
# Seleccionar "3. Gestión de Machine Learning"
# Seleccionar "2. Reentrenar todos los modelos"
```

### Para limpiar solo sesiones (si es necesario):
```bash
python admin_system.py
# Seleccionar "2. Gestión de Base de Datos"
# Seleccionar "1. Limpiar SOLO sesiones"
```

## 💡 Mejores Prácticas

1. **Usar siempre `python start.py`** para iniciar el sistema
2. **No modificar directamente bebidas.json** - usar scripts de administración
3. **Personalizar configuraciones en `config.py`** en lugar de código
4. **Ejecutar tests antes de cambios importantes**
5. **Las sesiones se preservan automáticamente** para aprendizaje continuo

## 🎯 Próximos Pasos Sugeridos

1. Agregar más bebidas usando el panel de administración
2. Entrenar modelos ML con más datos reales
3. Implementar más tipos de sabores específicos
4. Agregar analytics avanzados de usuarios
5. Implementar cache para mejor rendimiento